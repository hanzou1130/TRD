import markdown
import sys
from pathlib import Path

def convert_md_to_html(md_file: str, output_file: str = None):
    """
    MarkdownファイルをHTMLに変換

    Args:
        md_file: 入力Markdownファイル
        output_file: 出力HTMLファイル（省略時は同名の.html）
    """
    md_path = Path(md_file)

    if not md_path.exists():
        print(f"エラー: {md_file} が見つかりません")
        return

    # 出力ファイル名を決定
    if output_file is None:
        output_file = md_path.with_suffix('.html')

    # Markdownを読み込み
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # HTMLに変換（拡張機能を有効化）
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc']
    )

    # 完全なHTMLドキュメントとして出力
    full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_path.stem}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            color: #e74c3c;
        }}
        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            color: #ecf0f1;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        ul, ol {{
            margin: 15px 0;
        }}
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""

    # HTMLファイルを保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"✅ 変換完了: {output_file}")
    print(f"   入力: {md_path.name}")
    print(f"   出力: {Path(output_file).name}")
    print(f"   サイズ: {len(full_html):,} bytes")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # デフォルト
        md_file = "PDF_DATABASE_README.md"
        output_file = None

    convert_md_to_html(md_file, output_file)
