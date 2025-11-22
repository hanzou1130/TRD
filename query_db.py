#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RH850ハードウェアマニュアルデータベース検索ツール
高速な全文検索とクエリインターフェース
"""

import sqlite3
import json
import time
import sys
from typing import List, Tuple, Dict, Any

DB_PATH = r"c:/Users/baoma/TRD/RH850F1KM_HardwareManual.db"

class ManualDatabase:
    """マニュアルデータベース検索クラス"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """全文検索を実行"""
        start_time = time.time()

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                p.page_num,
                p.char_count,
                snippet(pages_fts, 1, '【', '】', '...', 30) as snippet,
                rank
            FROM pages_fts
            JOIN pages p ON pages_fts.page_num = p.page_num
            WHERE pages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                'page_num': row['page_num'],
                'char_count': row['char_count'],
                'snippet': row['snippet'],
                'rank': row['rank']
            })

        elapsed = time.time() - start_time
        return results, elapsed

    def get_page(self, page_num: int) -> Dict[str, Any]:
        """特定のページの内容を取得"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE page_num = ?', (page_num,))
        row = cursor.fetchone()

        if not row:
            return None

        # そのページのテーブルも取得
        cursor.execute('SELECT * FROM tables WHERE page_num = ?', (page_num,))
        tables = []
        for table_row in cursor.fetchall():
            tables.append({
                'index': table_row['table_index'],
                'content': json.loads(table_row['content'])
            })

        return {
            'page_num': row['page_num'],
            'text': row['text'],
            'char_count': row['char_count'],
            'table_count': row['table_count'],
            'tables': tables
        }

    def get_metadata(self) -> Dict[str, str]:
        """メタデータを取得"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM metadata')
        return {row['key']: row['value'] for row in cursor.fetchall()}

    def get_statistics(self) -> Dict[str, Any]:
        """データベース統計情報を取得"""
        cursor = self.conn.cursor()

        stats = {}
        stats['total_pages'] = cursor.execute('SELECT COUNT(*) FROM pages').fetchone()[0]
        stats['total_tables'] = cursor.execute('SELECT COUNT(*) FROM tables').fetchone()[0]
        stats['total_chars'] = cursor.execute('SELECT SUM(char_count) FROM pages').fetchone()[0]
        stats['avg_chars_per_page'] = stats['total_chars'] // stats['total_pages']

        return stats

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

def print_search_results(results: List[Dict], elapsed: float):
    """検索結果を表示"""
    print(f"\n検索結果: {len(results)}件 (検索時間: {elapsed*1000:.2f}ms)\n")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n[{i}] ページ {result['page_num']} (文字数: {result['char_count']}, スコア: {result['rank']:.4f})")
        print(f"    {result['snippet']}")

    print("\n" + "=" * 80)

def print_page_content(page_data: Dict):
    """ページ内容を表示"""
    if not page_data:
        print("ページが見つかりません")
        return

    print(f"\n{'='*80}")
    print(f"ページ {page_data['page_num']}")
    print(f"文字数: {page_data['char_count']}, テーブル数: {page_data['table_count']}")
    print(f"{'='*80}\n")

    # テキストを表示（最初の1000文字）
    text = page_data['text']
    if len(text) > 1000:
        print(text[:1000] + "\n... (省略) ...\n")
    else:
        print(text + "\n")

    # テーブルを表示
    if page_data['tables']:
        print(f"\n--- テーブル ({len(page_data['tables'])}個) ---")
        for table in page_data['tables']:
            print(f"\nテーブル {table['index'] + 1}:")
            content = table['content']
            if len(content) > 5:
                print(f"  (行数: {len(content)}, 最初の5行のみ表示)")
                for row in content[:5]:
                    print(f"  {row}")
            else:
                for row in content:
                    print(f"  {row}")

def interactive_mode(db: ManualDatabase):
    """対話モード"""
    print("\n" + "="*80)
    print("RH850マニュアル検索システム - 対話モード")
    print("="*80)
    print("\nコマンド:")
    print("  search <キーワード>  : 全文検索")
    print("  page <番号>         : ページ内容を表示")
    print("  stats               : 統計情報を表示")
    print("  meta                : メタデータを表示")
    print("  quit                : 終了")
    print()

    while True:
        try:
            cmd = input("\n> ").strip()

            if not cmd:
                continue

            if cmd == "quit":
                break

            parts = cmd.split(maxsplit=1)
            command = parts[0].lower()

            if command == "search":
                if len(parts) < 2:
                    print("使用法: search <キーワード>")
                    continue
                query = parts[1]
                results, elapsed = db.search(query)
                print_search_results(results, elapsed)

            elif command == "page":
                if len(parts) < 2:
                    print("使用法: page <番号>")
                    continue
                try:
                    page_num = int(parts[1])
                    page_data = db.get_page(page_num)
                    print_page_content(page_data)
                except ValueError:
                    print("エラー: ページ番号は数値で指定してください")

            elif command == "stats":
                stats = db.get_statistics()
                print(f"\n--- データベース統計 ---")
                print(f"総ページ数: {stats['total_pages']}")
                print(f"総テーブル数: {stats['total_tables']}")
                print(f"総文字数: {stats['total_chars']:,}")
                print(f"平均文字数/ページ: {stats['avg_chars_per_page']:,}")

            elif command == "meta":
                metadata = db.get_metadata()
                print(f"\n--- メタデータ ---")
                for key, value in sorted(metadata.items()):
                    print(f"{key}: {value}")

            else:
                print(f"不明なコマンド: {command}")

        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"エラー: {e}")

def benchmark_mode(db: ManualDatabase):
    """ベンチマークモード"""
    print("\n" + "="*80)
    print("ベンチマークモード")
    print("="*80 + "\n")

    test_queries = [
        "RH850",
        "starter kit",
        "BLDC",
        "motor",
        "connector",
        "power supply",
        "LED",
        "switch"
    ]

    total_time = 0
    for query in test_queries:
        results, elapsed = db.search(query, limit=5)
        total_time += elapsed
        print(f"クエリ: '{query}' -> {len(results)}件 ({elapsed*1000:.2f}ms)")

    avg_time = total_time / len(test_queries)
    print(f"\n平均検索時間: {avg_time*1000:.2f}ms")
    print(f"総検索時間: {total_time*1000:.2f}ms")

def main():
    """メイン関数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--benchmark":
        mode = "benchmark"
    else:
        mode = "interactive"

    try:
        db = ManualDatabase(DB_PATH)

        if mode == "benchmark":
            benchmark_mode(db)
        else:
            interactive_mode(db)

        db.close()
        print("\n終了しました。")

    except sqlite3.OperationalError as e:
        print(f"エラー: データベースが見つかりません: {DB_PATH}")
        print(f"まず 'python pdf_to_db.py' を実行してデータベースを作成してください。")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
