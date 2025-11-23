#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース状態確認スクリプト
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = r"c:/Users/baoma/TRD/RH850_FlashMemory_IF.db"

def check_database_status():
    """データベースの状態を確認"""
    if not Path(DB_PATH).exists():
        print("[エラー] データベースが見つかりません")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("データベース状態確認")
    print("=" * 70)

    # ファイルサイズ
    file_size = os.path.getsize(DB_PATH)
    print(f"\nファイルサイズ: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    # テーブル一覧
    print("\n■ テーブル一覧:")
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
    for table in tables:
        table_name = table[0]
        if not table_name.startswith('sqlite_'):
            count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"  - {table_name}: {count:,} rows")

    # ページ統計
    print("\n■ ページ統計:")
    page_count = cursor.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    total_chars = cursor.execute("SELECT SUM(char_count) FROM pages").fetchone()[0] or 0
    total_tables = cursor.execute("SELECT COUNT(*) FROM tables").fetchone()[0]
    avg_chars = total_chars // page_count if page_count > 0 else 0

    print(f"  総ページ数: {page_count:,}")
    print(f"  総文字数: {total_chars:,}")
    print(f"  平均文字数/ページ: {avg_chars:,}")
    print(f"  テーブル数: {total_tables:,}")

    # インデックス一覧
    print("\n■ インデックス一覧:")
    indexes = cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name;").fetchall()
    for idx in indexes:
        if not idx[0].startswith('sqlite_'):
            print(f"  - {idx[0]}")

    # PRAGMA設定
    print("\n■ PRAGMA設定:")
    journal_mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
    synchronous = cursor.execute("PRAGMA synchronous").fetchone()[0]
    cache_size = cursor.execute("PRAGMA cache_size").fetchone()[0]

    print(f"  journal_mode: {journal_mode}")
    print(f"  synchronous: {synchronous}")
    print(f"  cache_size: {cache_size}")

    # 検索テスト
    print("\n■ 検索パフォーマンステスト:")
    import time
    check_database_status()
