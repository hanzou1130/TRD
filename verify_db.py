#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース検証スクリプト
"""

import sqlite3

DB_PATH = r"c:/Users/baoma/TRD/rh850_manual.db"

def verify_database():
    """データベースの整合性を検証"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("データベース検証レポート")
    print("=" * 60 + "\n")

    # 基本統計
    page_count = cursor.execute('SELECT COUNT(*) FROM pages').fetchone()[0]
    table_count = cursor.execute('SELECT COUNT(*) FROM tables').fetchone()[0]
    metadata_count = cursor.execute('SELECT COUNT(*) FROM metadata').fetchone()[0]
    fts_count = cursor.execute('SELECT COUNT(*) FROM pages_fts').fetchone()[0]

    print(f"[1] 基本統計:")
    print(f"    ページ数: {page_count}")
    print(f"    テーブル数: {table_count}")
    print(f"    メタデータ数: {metadata_count}")
    print(f"    FTS5レコード数: {fts_count}")

    # 整合性チェック
    print(f"\n[2] 整合性チェック:")
    if page_count == 32:
        print(f"    [OK] ページ数が正しい (32ページ)")
    else:
        print(f"    [ERROR] ページ数が不正 (期待: 32, 実際: {page_count})")

    if page_count == fts_count:
        print(f"    [OK] FTS5インデックスが完全")
    else:
        print(f"    [ERROR] FTS5インデックスが不完全")

    # サンプル検索テスト
    print(f"\n[3] サンプル検索テスト:")
    test_queries = ["RH850", "starter", "kit", "motor", "LED"]

    for query in test_queries:
        cursor.execute('''
            SELECT COUNT(*) FROM pages_fts WHERE pages_fts MATCH ?
        ''', (query,))
        count = cursor.fetchone()[0]
        print(f"    '{query}': {count}件")

    # テーブル抽出検証
    print(f"\n[4] テーブル抽出検証:")
    cursor.execute('SELECT page_num, COUNT(*) as cnt FROM tables GROUP BY page_num ORDER BY cnt DESC LIMIT 5')
    print(f"    テーブルが最も多いページ:")
    for row in cursor.fetchall():
        print(f"      ページ {row[0]}: {row[1]}個のテーブル")

    # メタデータ検証
    print(f"\n[5] メタデータ検証:")
    cursor.execute("SELECT value FROM metadata WHERE key = 'Title'")
    title = cursor.fetchone()
    if title:
        print(f"    タイトル: {title[0]}")

    cursor.execute("SELECT value FROM metadata WHERE key = 'Author'")
    author = cursor.fetchone()
    if author:
        print(f"    著者: {author[0]}")

    print(f"\n" + "=" * 60)
    print("[OK] データベース検証完了")
    print("=" * 60)

    conn.close()

if __name__ == "__main__":
    verify_database()
