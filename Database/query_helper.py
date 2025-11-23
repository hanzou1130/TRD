#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベースクエリヘルパーユーティリティ
高速検索、ファジー検索、コンテキスト抽出機能
"""

import sqlite3
import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import json

# デフォルトDBパスを修正（Databaseフォルダ内）
DB_PATH = r"c:/Users/baoma/TRD/Database/RH850_FlashMemory_IF_Fast.db"

class QueryHelper:
    """データベースクエリヘルパークラス"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self):
        """データベースに接続"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"データベースが見つかりません: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 辞書形式で結果を取得

        # 読み取り専用最適化
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA query_only=ON')
        cursor.execute('PRAGMA cache_size=-64000')  # 64MB

    def close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ========== 基本検索 ==========

    def search_fts(self, query: str, limit: int = 10) -> List[Dict]:
        """
        FTS全文検索

        Args:
            query: 検索クエリ
            limit: 結果の最大数

        Returns:
            検索結果のリスト
        """
        cursor = self.conn.cursor()

        sql = '''
            SELECT p.page_num, p.text, p.char_count, p.table_count
            FROM pages_fts fts
            JOIN pages p ON fts.page_num = p.page_num
            WHERE fts.text MATCH ?
            ORDER BY rank
            LIMIT ?
        '''

        results = cursor.execute(sql, (query, limit)).fetchall()
        return [dict(row) for row in results]

    def search_like(self, query: str, limit: int = 10) -> List[Dict]:
        """
        LIKE検索（部分一致）

        Args:
            query: 検索クエリ
            limit: 結果の最大数

        Returns:
            検索結果のリスト
        """
        cursor = self.conn.cursor()

        sql = '''
            SELECT page_num, text, char_count, table_count
            FROM pages
            WHERE text LIKE ?
            LIMIT ?
        '''

        pattern = f'%{query}%'
        results = cursor.execute(sql, (pattern, limit)).fetchall()
        return [dict(row) for row in results]

    def search_regex(self, pattern: str, limit: int = 10) -> List[Dict]:
        """
        正規表現検索

        Args:
            pattern: 正規表現パターン
            limit: 結果の最大数

        Returns:
            検索結果のリスト
        """
        cursor = self.conn.cursor()

        sql = 'SELECT page_num, text, char_count, table_count FROM pages'
        all_pages = cursor.execute(sql).fetchall()

        regex = re.compile(pattern, re.IGNORECASE)
        results = []

        for row in all_pages:
            if regex.search(row['text']):
                results.append(dict(row))
                if len(results) >= limit:
                    break

        return results

    # ========== コンテキスト抽出 ==========

    def get_context(self, page_num: int, query: str, context_chars: int = 200) -> List[str]:
        """
        検索語の前後のコンテキストを抽出

        Args:
            page_num: ページ番号
            query: 検索語
            context_chars: コンテキストの文字数

        Returns:
            コンテキストのリスト
        """
        cursor = self.conn.cursor()

        sql = 'SELECT text FROM pages WHERE page_num = ?'
        result = cursor.execute(sql, (page_num,)).fetchone()

        if not result:
            return []

        text = result['text']
        contexts = []

        # クエリの出現位置を検索
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)

            context = text[start:end]
            # マッチ部分をハイライト
            context = context.replace(match.group(), f"**{match.group()}**")
            contexts.append(context)

        return contexts

    def search_with_context(self, query: str, limit: int = 10, context_chars: int = 150) -> List[Dict]:
        """
        検索結果とコンテキストを取得

        Args:
            query: 検索クエリ
            limit: 結果の最大数
            context_chars: コンテキストの文字数

        Returns:
            検索結果とコンテキストのリスト
        """
        results = self.search_fts(query, limit)

        for result in results:
            contexts = self.get_context(result['page_num'], query, context_chars)
            result['contexts'] = contexts

        return results

    # ========== 統計・分析 ==========

    def get_statistics(self) -> Dict:
        """
        データベース統計情報を取得

        Returns:
            統計情報の辞書
        """
        cursor = self.conn.cursor()

        stats = {}

        # ページ統計
        stats['total_pages'] = cursor.execute('SELECT COUNT(*) FROM pages').fetchone()[0]
        stats['total_chars'] = cursor.execute('SELECT SUM(char_count) FROM pages').fetchone()[0]
        stats['total_tables'] = cursor.execute('SELECT COUNT(*) FROM tables').fetchone()[0]
        stats['avg_chars_per_page'] = stats['total_chars'] // stats['total_pages'] if stats['total_pages'] > 0 else 0

        # ページ範囲
        page_range = cursor.execute('SELECT MIN(page_num), MAX(page_num) FROM pages').fetchone()
        stats['page_range'] = {'min': page_range[0], 'max': page_range[1]}

        # 最大文字数のページ
        max_page = cursor.execute('SELECT page_num, char_count FROM pages ORDER BY char_count DESC LIMIT 1').fetchone()
        if max_page:
            stats['max_chars_page'] = {'page_num': max_page[0], 'char_count': max_page[1]}

        # テーブルが最も多いページ
        max_tables_page = cursor.execute('SELECT page_num, table_count FROM pages ORDER BY table_count DESC LIMIT 1').fetchone()
        if max_tables_page:
            stats['max_tables_page'] = {'page_num': max_tables_page[0], 'table_count': max_tables_page[1]}

        return stats

    def get_page(self, page_num: int) -> Optional[Dict]:
        """
        特定のページ情報を取得

        Args:
            page_num: ページ番号

        Returns:
            ページ情報の辞書、存在しない場合はNone
        """
        cursor = self.conn.cursor()

        sql = 'SELECT * FROM pages WHERE page_num = ?'
        result = cursor.execute(sql, (page_num,)).fetchone()

        if not result:
            return None

        page_data = dict(result)

        # テーブル情報を追加
        tables_sql = 'SELECT table_index, content FROM tables WHERE page_num = ? ORDER BY table_index'
        tables = cursor.execute(tables_sql, (page_num,)).fetchall()
        page_data['tables'] = [json.loads(row['content']) for row in tables]

        return page_data

    def get_pages_with_tables(self) -> List[int]:
        """
        テーブルを含むページ番号のリストを取得

        Returns:
            ページ番号のリスト
        """
        cursor = self.conn.cursor()

        sql = 'SELECT DISTINCT page_num FROM tables ORDER BY page_num'
        results = cursor.execute(sql).fetchall()

        return [row[0] for row in results]

    # ========== エクスポート ==========

    def export_to_json(self, results: List[Dict], output_path: str):
        """
        結果をJSONファイルにエクスポート

        Args:
            results: 検索結果
            output_path: 出力ファイルパス
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"[OK] {len(results)}件の結果を {output_path} にエクスポートしました")

    def export_to_markdown(self, results: List[Dict], output_path: str, query: str = ""):
        """
        結果をMarkdownファイルにエクスポート

        Args:
            results: 検索結果
            output_path: 出力ファイルパス
            query: 検索クエリ（タイトル用）
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 検索結果: {query}\n\n")
            f.write(f"**総件数**: {len(results)}\n\n")
            f.write("---\n\n")

            for i, result in enumerate(results, 1):
                f.write(f"## {i}. ページ {result['page_num']}\n\n")
                f.write(f"- **文字数**: {result['char_count']}\n")
                f.write(f"- **テーブル数**: {result['table_count']}\n\n")

                if 'contexts' in result and result['contexts']:
                    f.write("### コンテキスト\n\n")
                    for ctx in result['contexts']:
                        f.write(f"> {ctx}\n\n")

                f.write("---\n\n")

        print(f"[OK] {len(results)}件の結果を {output_path} にエクスポートしました")


def main():
    """使用例"""
    with QueryHelper() as qh:
        print("=" * 70)
        print("クエリヘルパー デモ")
        print("=" * 70)

        # 統計情報
        print("\n■ データベース統計:")
        stats = qh.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # FTS検索
        print("\n■ FTS検索 ('flash memory'):")
        results = qh.search_with_context('flash memory', limit=3)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. ページ {result['page_num']} ({result['char_count']} chars)")
            if result['contexts']:
                print(f"   コンテキスト: {result['contexts'][0][:100]}...")

        # テーブルを含むページ
        print("\n■ テーブルを含むページ:")
        table_pages = qh.get_pages_with_tables()
        print(f"  総数: {len(table_pages)}")
        print(f"  ページ: {table_pages[:10]}..." if len(table_pages) > 10 else f"  ページ: {table_pages}")

        print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
