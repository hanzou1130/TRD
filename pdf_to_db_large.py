#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大規模PDFをSQLiteデータベースに変換（最適化版）
4668ページのRH850マニュアル用
"""

import sqlite3
import pdfplumber
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 設定
PDF_PATH = r"c:/Users/baoma/TRD/Renesas/REN_r01uh0684jj0130-rh850f1kh-rh850f1km_MAH_20210930.pdf"
DB_PATH = r"c:/Users/baoma/TRD/rh850_mah_manual.db"
BATCH_SIZE = 100  # 100ページごとにコミット

class LargePDFDatabaseBuilder:
    """大規模PDF用データベース構築クラス"""

    def __init__(self, pdf_path: str, db_path: str, batch_size: int = 100):
        self.pdf_path = pdf_path
        self.db_path = db_path
        self.batch_size = batch_size
        self.conn = None
        self.total_pages = 0
        self.start_time = None

    def setup_database(self):
        """データベースの初期設定"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # パフォーマンス最適化
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA cache_size=-64000')  # 64MB
        cursor.execute('PRAGMA temp_store=MEMORY')

        print("[設定] データベース最適化完了")
        print("  - WALモード有効")
        print("  - キャッシュサイズ: 64MB")

    def create_schema(self):
        """データベーススキーマを作成"""
        cursor = self.conn.cursor()

        # ページテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                page_num INTEGER PRIMARY KEY,
                text TEXT,
                char_count INTEGER,
                table_count INTEGER
            )
        ''')

        # テーブルテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_num INTEGER,
                table_index INTEGER,
                content TEXT,
                FOREIGN KEY (page_num) REFERENCES pages(page_num)
            )
        ''')

        # メタデータテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # FTS5全文検索テーブル
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                page_num UNINDEXED,
                text,
                tokenize='unicode61 remove_diacritics 2'
            )
        ''')

        self.conn.commit()
        print("[OK] データベーススキーマを作成しました")

    def extract_and_store(self):
        """PDFからデータを抽出してデータベースに保存（バッチ処理）"""
        print(f"\n[開始] PDFを開いています: {Path(self.pdf_path).name}")

        with pdfplumber.open(self.pdf_path) as pdf:
            self.total_pages = len(pdf.pages)
            print(f"[情報] 総ページ数: {self.total_pages:,}")

            # メタデータを保存
            self._store_metadata(pdf.metadata)

            # バッチ処理
            cursor = self.conn.cursor()
            batch_count = 0
            total_tables = 0
            total_chars = 0

            pages_batch = []
            tables_batch = []
            fts_batch = []

            print(f"\n[処理] バッチサイズ: {self.batch_size}ページ")
            print("=" * 70)

            for i, page in enumerate(pdf.pages, 1):
                try:
                    # テキスト抽出
                    text = page.extract_text() or ""
                    char_count = len(text)
                    total_chars += char_count

                    # テーブル抽出
                    tables = page.extract_tables()
                    table_count = len(tables)
                    total_tables += table_count

                    # バッチに追加
                    pages_batch.append((i, text, char_count, table_count))
                    fts_batch.append((i, text))

                    for idx, table in enumerate(tables):
                        table_json = json.dumps(table, ensure_ascii=False)
                        tables_batch.append((i, idx, table_json))

                    # バッチコミット
                    if i % self.batch_size == 0 or i == self.total_pages:
                        batch_count += 1

                        # データベースに挿入
                        cursor.executemany('INSERT INTO pages VALUES (?, ?, ?, ?)', pages_batch)
                        cursor.executemany('INSERT INTO tables (page_num, table_index, content) VALUES (?, ?, ?)', tables_batch)
                        cursor.executemany('INSERT INTO pages_fts (page_num, text) VALUES (?, ?)', fts_batch)
                        self.conn.commit()

                        # 進捗報告
                        self._print_progress(i, total_chars, total_tables, batch_count)

                        # バッチをクリア
                        pages_batch = []
                        tables_batch = []
                        fts_batch = []

                except Exception as e:
                    print(f"\n[警告] ページ {i} の処理中にエラー: {e}")
                    continue

            print("=" * 70)
            print(f"\n[完了] {self.total_pages:,}ページ、{total_tables:,}個のテーブルを保存しました")
            print(f"[完了] 総文字数: {total_chars:,}")

    def _store_metadata(self, metadata: Dict[str, Any]):
        """メタデータを保存"""
        cursor = self.conn.cursor()
        metadata_items = [(k, str(v)) for k, v in metadata.items()]
        cursor.executemany('INSERT OR REPLACE INTO metadata VALUES (?, ?)', metadata_items)
        self.conn.commit()
        print(f"[OK] {len(metadata_items)}個のメタデータを保存しました")

    def _print_progress(self, current_page: int, total_chars: int, total_tables: int, batch_count: int):
        """進捗状況を表示"""
        elapsed = time.time() - self.start_time
        progress = current_page / self.total_pages * 100
        pages_per_sec = current_page / elapsed if elapsed > 0 else 0
        remaining_pages = self.total_pages - current_page
        eta_seconds = remaining_pages / pages_per_sec if pages_per_sec > 0 else 0

        print(f"[進捗] バッチ #{batch_count}: {current_page:,}/{self.total_pages:,}ページ ({progress:.1f}%)")
        print(f"       速度: {pages_per_sec:.1f}ページ/秒 | 経過: {self._format_time(elapsed)} | 残り: {self._format_time(eta_seconds)}")
        print(f"       文字数: {total_chars:,} | テーブル: {total_tables:,}")
        print()

    def _format_time(self, seconds: float) -> str:
        """秒を読みやすい形式に変換"""
        if seconds < 60:
            return f"{seconds:.0f}秒"
        elif seconds < 3600:
            return f"{seconds/60:.1f}分"
        else:
            return f"{seconds/3600:.1f}時間"

    def create_indexes(self):
        """インデックスを作成"""
        print("\n[処理] インデックスを作成中...")
        cursor = self.conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tables_page ON tables(page_num)')
        self.conn.commit()
        print("[OK] インデックスを作成しました")

    def print_statistics(self):
        """統計情報を表示"""
        cursor = self.conn.cursor()

        page_count = cursor.execute('SELECT COUNT(*) FROM pages').fetchone()[0]
        table_count = cursor.execute('SELECT COUNT(*) FROM tables').fetchone()[0]
        total_chars = cursor.execute('SELECT SUM(char_count) FROM pages').fetchone()[0]

        print(f"\n{'='*70}")
        print("データベース統計")
        print(f"{'='*70}")
        print(f"ページ数: {page_count:,}")
        print(f"テーブル数: {table_count:,}")
        print(f"総文字数: {total_chars:,}")
        print(f"平均文字数/ページ: {total_chars//page_count:,}")
        print(f"{'='*70}")

    def build(self):
        """データベースを構築"""
        self.start_time = time.time()

        print("=" * 70)
        print("大規模PDF データベース構築ツール")
        print("=" * 70)
        print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 既存のDBを削除
        db_file = Path(self.db_path)
        if db_file.exists():
            db_file.unlink()
            print(f"[削除] 既存のデータベースを削除しました")

        # データベース接続と設定
        self.setup_database()

        try:
            # スキーマ作成
            self.create_schema()

            # データ抽出と保存
            self.extract_and_store()

            # インデックス作成
            self.create_indexes()

            # 統計情報を表示
            self.print_statistics()

            # 完了
            elapsed = time.time() - self.start_time
            print(f"\n[完了] データベース構築完了！")
            print(f"[完了] 総処理時間: {self._format_time(elapsed)}")
            print(f"[完了] 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except KeyboardInterrupt:
            print("\n\n[中断] ユーザーによって中断されました")
            self.conn.commit()
            print("[保存] 処理済みデータを保存しました")
        except Exception as e:
            print(f"\n[エラー] {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    """メイン関数"""
    builder = LargePDFDatabaseBuilder(PDF_PATH, DB_PATH, BATCH_SIZE)
    builder.build()

if __name__ == "__main__":
    main()
