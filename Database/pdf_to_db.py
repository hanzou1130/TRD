#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RH850ハードウェアマニュアルPDFをSQLiteデータベースに変換
高速な全文検索（FTS5）をサポート
"""

import sqlite3
import pdfplumber
import json
from pathlib import Path
from typing import List, Dict, Any
import time

# 設定
PDF_PATH = r"c:/Users/baoma/TRD/Renesas/r12ut0004ed0110-rh850f1km-s1.pdf"
DB_PATH = r"c:/Users/baoma/TRD/RH850F1KMS1_Board.db"

class PDFDatabaseBuilder:
    """PDFからデータベースを構築するクラス"""

    def __init__(self, pdf_path: str, db_path: str):
        self.pdf_path = pdf_path
        self.db_path = db_path
        self.conn = None

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
        """PDFからデータを抽出してデータベースに保存"""
        print(f"PDFを開いています: {self.pdf_path}")

        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"総ページ数: {total_pages}")

            # メタデータを保存
            self._store_metadata(pdf.metadata)

            # 各ページを処理
            cursor = self.conn.cursor()
            pages_data = []
            tables_data = []
            fts_data = []

            for i, page in enumerate(pdf.pages, 1):
                # テキスト抽出
                text = page.extract_text() or ""
                char_count = len(text)

                # テーブル抽出
                tables = page.extract_tables()
                table_count = len(tables)

                # ページデータを追加
                pages_data.append((i, text, char_count, table_count))
                fts_data.append((i, text))

                # テーブルデータを追加
                for idx, table in enumerate(tables):
                    table_json = json.dumps(table, ensure_ascii=False)
                    tables_data.append((i, idx, table_json))

                # 進捗表示
                if i % 5 == 0 or i == total_pages:
                    print(f"  処理中: {i}/{total_pages} ページ ({i*100//total_pages}%)")

            # バッチ挿入
            print("データベースに挿入中...")
            cursor.executemany('INSERT INTO pages VALUES (?, ?, ?, ?)', pages_data)
            cursor.executemany('INSERT INTO tables (page_num, table_index, content) VALUES (?, ?, ?)', tables_data)
            cursor.executemany('INSERT INTO pages_fts (page_num, text) VALUES (?, ?)', fts_data)

            self.conn.commit()
            print(f"[OK] {total_pages}ページ、{len(tables_data)}個のテーブルを保存しました")

    def _store_metadata(self, metadata: Dict[str, Any]):
        """メタデータを保存"""
        cursor = self.conn.cursor()
        metadata_items = [(k, str(v)) for k, v in metadata.items()]
        cursor.executemany('INSERT OR REPLACE INTO metadata VALUES (?, ?)', metadata_items)
        self.conn.commit()
        print(f"[OK] {len(metadata_items)}個のメタデータを保存しました")

    def create_indexes(self):
        """パフォーマンス向上のためのインデックスを作成"""
        cursor = self.conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tables_page ON tables(page_num)')
        self.conn.commit()
        print("[OK] インデックスを作成しました")

    def build(self):
        """データベースを構築"""
        start_time = time.time()

        # 既存のDBを削除
        db_file = Path(self.db_path)
        if db_file.exists():
            db_file.unlink()
            print(f"既存のデータベースを削除しました: {self.db_path}")

        # データベース接続
        self.conn = sqlite3.connect(self.db_path)
        print(f"データベースを作成: {self.db_path}\n")

        try:
            # スキーマ作成
            self.create_schema()

            # データ抽出と保存
            self.extract_and_store()

            # インデックス作成
            self.create_indexes()

            # 統計情報を表示
            self._print_statistics()

            elapsed = time.time() - start_time
            print(f"\n[OK] データベース構築完了！ (所要時間: {elapsed:.2f}秒)")

        finally:
            if self.conn:
                self.conn.close()

    def _print_statistics(self):
        """データベース統計情報を表示"""
        cursor = self.conn.cursor()

        page_count = cursor.execute('SELECT COUNT(*) FROM pages').fetchone()[0]
        table_count = cursor.execute('SELECT COUNT(*) FROM tables').fetchone()[0]
        total_chars = cursor.execute('SELECT SUM(char_count) FROM pages').fetchone()[0]

        print(f"\n--- データベース統計 ---")
        print(f"ページ数: {page_count}")
        print(f"テーブル数: {table_count}")
        print(f"総文字数: {total_chars:,}")

def main():
    """メイン関数"""
    print("=" * 60)
    print("RH850 PDFデータベース構築ツール")
    print("=" * 60 + "\n")

    builder = PDFDatabaseBuilder(PDF_PATH, DB_PATH)
    builder.build()

if __name__ == "__main__":
    main()
