# RH850 Flash Memory Database - 使用ガイド

## 概要

RH850 Flash Memory Interface PDFの高速データベース化ツール群です。

## クイックスタート

### 1. データベースを構築

```powershell
# 超高速ビルダーを使用（推奨）
python Database\pdf_to_db_ultra_fast.py

# 約9秒で完了、出力: RH850_FlashMemory_IF_Fast.db
```

### 2. データベースを検索

```powershell
# クエリヘルパーのデモを実行
python Database\query_helper.py
```

Pythonで使用:

```python
from query_helper import QueryHelper

with QueryHelper() as qh:
    # FTS検索
    results = qh.search_fts('flash memory')

    # コンテキスト付き検索
    results = qh.search_with_context('FLMD', limit=5)

    # 統計情報
    stats = qh.get_statistics()
```

### 3. パフォーマンス測定

```powershell
# ベンチマークを実行
python Database\benchmark_queries.py
```

## 作成ツール

| ツール | 説明 | 用途 |
|--------|------|------|
| `pdf_to_db_ultra_fast.py` | 超高速ビルダー | DB構築（マルチスレッド） |
| `query_helper.py` | クエリヘルパー | 高度な検索・分析 |
| `benchmark_queries.py` | ベンチマーク | 性能測定・比較 |
| `check_db_status.py` | 状態確認 | DB情報表示 |

## パフォーマンス

- **ビルド時間**: 9秒（98ページ）
- **処理速度**: 10.6ページ/秒
- **クエリ速度**: ほとんど < 1ms
- **データベースサイズ**: 約0.6MB

## 主な機能

### query_helper.py

- ✅ FTS全文検索（ランク付き）
- ✅ 正規表現検索
- ✅ コンテキスト抽出
- ✅ JSON/Markdown エクスポート
- ✅ 統計情報取得

### pdf_to_db_ultra_fast.py

- ✅ マルチスレッド処理（4ワーカー）
- ✅ 最適化PRAGMA設定
- ✅ 128MB キャッシュ
- ✅ 256MB メモリマップI/O
- ✅ 拡張スキーマ（sections, keywords）

## 詳細

詳しい使用方法と結果は [walkthrough.md](file:///c:/Users/baoma/.gemini/antigravity/brain/7739868d-af21-46bc-aab0-6be99fef4c24/walkthrough.md) を参照してください。
