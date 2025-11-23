#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベースクエリパフォーマンスベンチマーク
検索速度の測定とレポート生成
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any
import statistics

# 比較対象のデータベース
DB_ORIGINAL = r"c:/Users/baoma/TRD/RH850_FlashMemory_IF.db"
DB_FAST = r"c:/Users/baoma/TRD/RH850_FlashMemory_IF_Fast.db"

class QueryBenchmark:
    """クエリベンチマーククラス"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.results = []

    def connect(self):
        """データベースに接続"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"データベースが見つかりません: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA cache_size=-64000')  # 64MB

    def close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()

    def benchmark_query(self, name: str, sql: str, params: tuple = (), iterations: int = 10) -> Dict:
        """
        クエリのベンチマーク

        Args:
            name: ベンチマーク名
            sql: SQLクエリ
            params: パラメータ
            iterations: 実行回数

        Returns:
            ベンチマーク結果
        """
        cursor = self.conn.cursor()
        times = []

        for _ in range(iterations):
            start_time = time.time()
            cursor.execute(sql, params)
            results = cursor.fetchall()
            end_time = time.time()

            elapsed = (end_time - start_time) * 1000  # ミリ秒
            times.append(elapsed)

        result = {
            'name': name,
            'sql': sql,
            'params': params,
            'iterations': iterations,
            'result_count': len(results),
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'stdev_time': statistics.stdev(times) if len(times) > 1 else 0
        }

        self.results.append(result)
        return result

    def run_benchmarks(self):
        """標準ベンチマークを実行"""
        print(f"\n[ベンチマーク] {Path(self.db_path).name}")
        print("=" * 70)

        # 1. FTS検索
        print("\n1. FTS全文検索...")
        self.benchmark_query(
            "FTS: 'flash'",
            "SELECT COUNT(*) FROM pages_fts WHERE text MATCH ?",
            ('flash',),
            iterations=20
        )

        self.benchmark_query(
            "FTS: 'memory'",
            "SELECT COUNT(*) FROM pages_fts WHERE text MATCH ?",
            ('memory',),
            iterations=20
        )

        self.benchmark_query(
            "FTS: 'flash AND memory'",
            "SELECT COUNT(*) FROM pages_fts WHERE text MATCH ?",
            ('flash AND memory',),
            iterations=20
        )

        # 2. LIKE検索
        print("2. LIKE検索...")
        self.benchmark_query(
            "LIKE: '%flash%'",
            "SELECT COUNT(*) FROM pages WHERE text LIKE ?",
            ('%flash%',),
            iterations=10
        )

        self.benchmark_query(
            "LIKE: '%memory%'",
            "SELECT COUNT(*) FROM pages WHERE text LIKE ?",
            ('%memory%',),
            iterations=10
        )

        # 3. JOIN検索
        print("3. JOIN検索...")
        self.benchmark_query(
            "JOIN: pages with tables",
            """SELECT p.page_num, COUNT(t.id) as table_count
               FROM pages p
               LEFT JOIN tables t ON p.page_num = t.page_num
               GROUP BY p.page_num""",
            iterations=5
        )

        # 4. 集計クエリ
        print("4. 集計クエリ...")
        self.benchmark_query(
            "Aggregation: page statistics",
            """SELECT
                 COUNT(*) as total_pages,
                 SUM(char_count) as total_chars,
                 AVG(char_count) as avg_chars,
                 MAX(char_count) as max_chars
               FROM pages""",
            iterations=20
        )

        # 5. ページ取得
        print("5. ページ取得...")
        self.benchmark_query(
            "SELECT: single page",
            "SELECT * FROM pages WHERE page_num = ?",
            (50,),
            iterations=50
        )

        self.benchmark_query(
            "SELECT: page range",
            "SELECT * FROM pages WHERE page_num BETWEEN ? AND ?",
            (1, 10),
            iterations=20
        )

        print("\n[完了] ベンチマーク実行完了")

    def print_results(self):
        """ベンチマーク結果を表示"""
        print(f"\n{'='*70}")
        print("ベンチマーク結果")
        print(f"{'='*70}\n")

        for result in self.results:
            print(f"■ {result['name']}")
            print(f"  結果数: {result['result_count']}")
            print(f"  平均時間: {result['avg_time']:.3f}ms")
            print(f"  中央値: {result['median_time']:.3f}ms")
            print(f"  最小/最大: {result['min_time']:.3f}ms / {result['max_time']:.3f}ms")
            print(f"  標準偏差: {result['stdev_time']:.3f}ms")
            print()

    def get_summary(self) -> Dict:
        """ベンチマーク結果のサマリーを取得"""
        if not self.results:
            return {}

        avg_times = [r['avg_time'] for r in self.results]

        return {
            'total_benchmarks': len(self.results),
            'overall_avg_time': statistics.mean(avg_times),
            'overall_median_time': statistics.median(avg_times),
            'fastest_query': min(self.results, key=lambda x: x['avg_time'])['name'],
            'slowest_query': max(self.results, key=lambda x: x['avg_time'])['name'],
            'min_avg_time': min(avg_times),
            'max_avg_time': max(avg_times)
        }


def compare_databases():
    """2つのデータベースを比較"""
    print("=" * 70)
    print("データベース パフォーマンス比較")
    print("=" * 70)

    benchmarks = {}

    # オリジナルDBのベンチマーク
    if Path(DB_ORIGINAL).exists():
        print(f"\n[1] オリジナルDB: {Path(DB_ORIGINAL).name}")
        bm_orig = QueryBenchmark(DB_ORIGINAL)
        bm_orig.connect()
        bm_orig.run_benchmarks()
        bm_orig.close()
        benchmarks['original'] = bm_orig
    else:
        print(f"\n[スキップ] オリジナルDBが見つかりません: {DB_ORIGINAL}")

    # 高速化DBのベンチマーク
    if Path(DB_FAST).exists():
        print(f"\n[2] 高速化DB: {Path(DB_FAST).name}")
        bm_fast = QueryBenchmark(DB_FAST)
        bm_fast.connect()
        bm_fast.run_benchmarks()
        bm_fast.close()
        benchmarks['fast'] = bm_fast
    else:
        print(f"\n[スキップ] 高速化DBが見つかりません: {DB_FAST}")

    # 結果を表示
    for db_type, bm in benchmarks.items():
        bm.print_results()

    # 比較レポート
    if len(benchmarks) == 2:
        print(f"\n{'='*70}")
        print("比較レポート")
        print(f"{'='*70}\n")

        orig_summary = benchmarks['original'].get_summary()
        fast_summary = benchmarks['fast'].get_summary()

        speedup = orig_summary['overall_avg_time'] / fast_summary['overall_avg_time']

        print(f"全体平均時間:")
        print(f"  オリジナル: {orig_summary['overall_avg_time']:.3f}ms")
        print(f"  高速化版: {fast_summary['overall_avg_time']:.3f}ms")
        print(f"  速度向上: {speedup:.2f}x 高速" if speedup > 1 else f"  速度変化: {1/speedup:.2f}x 遅い")
        print()

        print(f"最速クエリ:")
        print(f"  オリジナル: {orig_summary['fastest_query']} ({orig_summary['min_avg_time']:.3f}ms)")
        print(f"  高速化版: {fast_summary['fastest_query']} ({fast_summary['min_avg_time']:.3f}ms)")
        print()

        print(f"最遅クエリ:")
        print(f"  オリジナル: {orig_summary['slowest_query']} ({orig_summary['max_avg_time']:.3f}ms)")
        print(f"  高速化版: {fast_summary['slowest_query']} ({fast_summary['max_avg_time']:.3f}ms)")
        print()

        # 詳細比較
        print("クエリ別比較:")
        for i, (orig_result, fast_result) in enumerate(zip(benchmarks['original'].results, benchmarks['fast'].results)):
            if orig_result['name'] == fast_result['name']:
                if fast_result['avg_time'] > 0:
                    query_speedup = orig_result['avg_time'] / fast_result['avg_time']
                    print(f"  {orig_result['name']}:")
                    print(f"    {orig_result['avg_time']:.3f}ms → {fast_result['avg_time']:.3f}ms ", end="")
                    if query_speedup > 1:
                        print(f"({query_speedup:.2f}x 高速)")
                    else:
                        print(f"({1/query_speedup:.2f}x 遅い)")
                else:
                    print(f"  {orig_result['name']}:")
                    print(f"    {orig_result['avg_time']:.3f}ms → 測定不可能なほど高速 (< 0.001ms)")


def main():
    """メイン関数"""
    compare_databases()


if __name__ == "__main__":
    main()
