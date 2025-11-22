# RH850 PDFデータベース検索システム

RH850/F1KM-S1 Starter Kit V3ハードウェアマニュアルの高速検索システム

## 概要

このプロジェクトは、RH850ハードウェアマニュアルPDF（32ページ）をSQLiteデータベースに変換し、高速な全文検索を可能にします。

**パフォーマンス:**
- 平均検索時間: **0.39ms**
- 32ページ、36テーブル、57,604文字を完全にインデックス化

## 必要な環境

```bash
pip install pdfplumber
```

## 使い方

### 1. データベースの構築

```bash
python pdf_to_db.py
```

約9秒でデータベースが構築されます。

### 2. 検索インターフェースの起動

```bash
python query_db.py
```

**利用可能なコマンド:**
- `search <キーワード>` - 全文検索
- `page <番号>` - ページ内容を表示
- `stats` - 統計情報を表示
- `meta` - メタデータを表示
- `quit` - 終了

### 3. ベンチマーク実行

```bash
python query_db.py --benchmark
```

### 4. データベース検証

```bash
python verify_db.py
```

## ファイル構成

- `pdf_to_db.py` - PDFからデータベースを構築
- `query_db.py` - 対話型検索インターフェース
- `verify_db.py` - データベース整合性検証
- `rh850_manual.db` - SQLiteデータベース（生成後）
- `Renesas/r12ut0004ed0110-rh850f1km-s1.pdf` - 元のPDFファイル

## 技術スタック

- **Python 3**
- **SQLite3** with FTS5（全文検索）
- **pdfplumber** - PDF解析ライブラリ

## データベーススキーマ

- `pages` - ページごとのテキストコンテンツ
- `tables` - 抽出されたテーブルデータ（JSON形式）
- `metadata` - PDFメタデータ
- `pages_fts` - FTS5全文検索インデックス

## ライセンス

このプロジェクトはTRDリポジトリの一部です。
