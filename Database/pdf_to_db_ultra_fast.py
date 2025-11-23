#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大規模PDFをSQLiteデータベースに変換（超高速版）
マルチスレッド対応、最適化PRAGMA、進捗保存機能付き
"""

import sqlite3
import pdfplumber
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 設定
PDF_PATH = r"c:/Users/baoma/TRD/Renesas/r01uh0622ej0130-rh850f1kh_rh850f1km_rh850f1k-flashmemory-if.pdf"
DB_PATH = r"c:/Users/baoma/TRD/RH850_FlashMemory_IF_Fast.db"
BATCH_SIZE = 200  # 200ページごとにコミット（高速化）
MAX_WORKERS = 4   # 並列処理スレッド数

class UltraFastPDFDatabaseBuilder:
    """超高速PDF用データベース構築クラス"""

    def __init__(self, pdf_path: str, db_path: str, batch_size: int = 200, max_workers: int = 4):
        self.pdf_path = pdf_path
        self.db_path = db_path
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.conn = None
        self.total_pages = 0
        self.start_time = None
        self.lock = threading.Lock()

    def setup_database(self):
        """データベースの初期設定（超高速版）"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # 超高速パフォーマンス最適化
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA cache_size=-128000')  # 128MB（2倍に増加）
        cursor.execute('PRAGMA temp_store=MEMORY')
        cursor.execute('PRAGMA mmap_size=268435456')  # 256MB メモリマップI/O
        cursor.execute('PRAGMA page_size=8192')  # 8KBページサイズ
        cursor.execute('PRAGMA locking_mode=EXCLUSIVE')  # 排他ロックモード

        print("[設定] データベース超高速最適化完了")
        print("  - WALモード有効")
        print("  - キャッシュサイズ: 128MB")
        print("  - メモリマップI/O: 256MB")
        print("  - ページサイズ: 8KB")
        print("  - 排他ロックモード: 有効")

    def create_schema(self):
        """データベーススキーマを作成（拡張版）"""
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

        # セクションテーブル（新機能）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_num INTEGER,
                level INTEGER,
                title TEXT,
                FOREIGN KEY (page_num) REFERENCES pages(page_num)
            )
        ''')

        # キーワードテーブル（新機能）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                keyword TEXT PRIMARY KEY,
                frequency INTEGER,
                pages TEXT
            )
        ''')

        # FTS5全文検索テーブル（最適化版）
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                page_num UNINDEXED,
                text,
                tokenize='unicode61 remove_diacritics 2'
            )
        ''')

        self.conn.commit()
        print("[OK] データベーススキーマを作成しました（拡張機能付き）")

    def _process_page(self, page_data: Tuple[int, Any]) -> Tuple[int, str, int, int, List]:
        """ページを処理（ワーカースレッド用）"""
        page_num, page = page_data

        try:
            # テキスト抽出
            text = page.extract_text() or ""
            char_count = len(text)

            # テーブル抽出
            tables = page.extract_tables()
            table_count = len(tables)

            # テーブルをJSON化
            tables_json = []
            for idx, table in enumerate(tables):
                table_json = json.dumps(table, ensure_ascii=False)
                tables_json.append((page_num, idx, table_json))

            return (page_num, text, char_count, table_count, tables_json)

        except Exception as e:
            print(f"\n[警告] ページ {page_num} の処理中にエラー: {e}")
            return (page_num, "", 0, 0, [])

    def extract_and_store_parallel(self):
        """PDFからデータを抽出してデータベースに保存（並列処理版）"""
        print(f"\n[開始] PDFを開いています: {Path(self.pdf_path).name}")

        with pdfplumber.open(self.pdf_path) as pdf:
            self.total_pages = len(pdf.pages)
            print(f"[情報] 総ページ数: {self.total_pages:,}")
            print(f"[情報] 並列ワーカー数: {self.max_workers}")

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

            # ページデータを準備
            page_data_list = [(i+1, page) for i, page in enumerate(pdf.pages)]

            # 並列処理でページを処理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_page = {executor.submit(self._process_page, page_data): page_data[0]
                                  for page_data in page_data_list}

                processed_count = 0
                for future in as_completed(future_to_page):
                    page_num, text, char_count, table_count, tables_json = future.result()

                    total_chars += char_count
                    total_tables += table_count

                    # バッチに追加
                    with self.lock:
                        pages_batch.append((page_num, text, char_count, table_count))
                        fts_batch.append((page_num, text))
                        tables_batch.extend(tables_json)

                        processed_count += 1

                        # バッチコミット
                        if processed_count % self.batch_size == 0 or processed_count == self.total_pages:
                            batch_count += 1

                            # データベースに挿入
                            cursor.executemany('INSERT OR REPLACE INTO pages VALUES (?, ?, ?, ?)', pages_batch)
                            if tables_batch:
                                cursor.executemany('INSERT INTO tables (page_num, table_index, content) VALUES (?, ?, ?)', tables_batch)
                            cursor.executemany('INSERT OR REPLACE INTO pages_fts (page_num, text) VALUES (?, ?)', fts_batch)
                            self.conn.commit()

                            # 進捗報告
                            self._print_progress(processed_count, total_chars, total_tables, batch_count)

                            # バッチをクリア
                            pages_batch = []
                            tables_batch = []
                            fts_batch = []

            print("=" * 70)
            print(f"\n[完了] {self.total_pages:,}ページ、{total_tables:,}個のテーブルを保存しました")
            print(f"[完了] 総文字数: {total_chars:,}")

    def _store_metadata(self, metadata: Dict[str, Any]):
        """メタデータを保存"""
        cursor = self.conn.cursor()
        metadata_items = [(k, str(v)) for k, v in metadata.items()]
        metadata_items.append(('build_time', datetime.now().isoformat()))
        metadata_items.append(('builder_version', 'ultra_fast_v1.0'))
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
        """インデックスを作成（拡張版）"""
        print("\n[処理] インデックスを作成中...")
        cursor = self.conn.cursor()

        # 既存のインデックス
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tables_page ON tables(page_num)')

        # 新しいインデックス（パフォーマンス向上）
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_char_count ON pages(char_count)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_table_count ON pages(table_count)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sections_page ON sections(page_num)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sections_level ON sections(level)')

        self.conn.commit()
        print("[OK] インデックスを作成しました（拡張版）")

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

        # ファイルサイズ
        import os
        db_size = os.path.getsize(self.db_path)
        print(f"DBファイルサイズ: {db_size:,} bytes ({db_size/1024/1024:.2f} MB)")
        print(f"{'='*70}")

    def build(self):
        """データベースを構築（超高速版）"""
        self.start_time = time.time()

        print("=" * 70)
        print("超高速PDF データベース構築ツール")
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

            # データ抽出と保存（並列処理）
            self.extract_and_store_parallel()

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
            import traceback
            traceback.print_exc()
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    """メイン関数"""
    builder = UltraFastPDFDatabaseBuilder(PDF_PATH, DB_PATH, BATCH_SIZE, MAX_WORKERS)
    builder.build()

if __name__ == "__main__":
    main()
