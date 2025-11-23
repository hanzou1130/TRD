#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなMarkdown to HTML変換ツール
外部ライブラリ不要で基本的な変換をサポート
"""

import re
from pathlib import Path
import sys

def convert_markdown_to_html(md_content: str) -> str:
    """
    MarkdownをHTMLに変換（基本機能のみ）
    """
    html = md_content

    # コードブロック（```で囲まれた部分）
    def replace_code_block(match):
        lang = match.group(1) if match.group(1) else ''
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'

    html = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, html, flags=re.DOTALL)

    # 見出し
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # 太字・斜体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # インラインコード
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # リンク
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # リスト
    lines = html.split('\n')
    in_ul = False
    in_ol = False
    result_lines = []

    for line in lines:
        # 番号なしリスト
        if re.match(r'^- ', line):
            if not in_ul:
                result_lines.append('<ul>')
                in_ul = True
            result_lines.append(f'<li>{line[2:]}</li>')
        # 番号付きリスト
        elif re.match(r'^\d+\. ', line):
            if not in_ol:
                result_lines.append('<ol>')
                in_ol = True
            line_text = re.sub(r'^\d+\. ', '', line)
            result_lines.append(f'<li>{line_text}</li>')
        else:
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            result_lines.append(line)

    if in_ul:
        result_lines.append('</ul>')
    if in_ol:
        result_lines.append('</ol>')

    html = '\n'.join(result_lines)

    # 段落（空行で区切られたテキスト）
    paragraphs = html.split('\n\n')
    result_paragraphs = []

    for para in paragraphs:
        para = para.strip()
        if para:
            # HTMLタグで始まっていない場合のみ<p>で囲む
            if not re.match(r'^<[a-z]', para):
                result_paragraphs.append(f'<p>{para}</p>')
            else:
                result_paragraphs.append(para)

    html = '\n'.join(result_paragraphs)

    # 改行をbrタグに（pre/code内以外）
    html = re.sub(r'(?<!>)\n(?!<)', '<br>\n', html)

    return html

def create_html_page(title: str, body_html: str) -> str:
    """
    完全なHTMLページを生成
    """
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans',
                         'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}

        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}

        h2 {{
            color: #764ba2;
            font-size: 1.8em;
            margin-top: 35px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e1e4e8;
        }}

        h3 {{
            color: #555;
            font-size: 1.3em;
            margin-top: 25px;
            margin-bottom: 12px;
        }}

        p {{
            margin: 15px 0;
            line-height: 1.8;
        }}

        code {{
            background-color: #f6f8fa;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            color: #d73a49;
            border: 1px solid #e1e4e8;
        }}

        pre {{
            background-color: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        pre code {{
            background-color: transparent;
            color: #abb2bf;
            padding: 0;
            border: none;
            font-size: 0.95em;
        }}

        ul, ol {{
            margin: 15px 0 15px 30px;
        }}

        li {{
            margin: 8px 0;
            line-height: 1.6;
        }}

        strong {{
            color: #667eea;
            font-weight: 600;
        }}

        a {{
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s;
        }}

        a:hover {{
            border-bottom-color: #667eea;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #e1e4e8;
        }}

        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: #f6f8fa;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e1e4e8;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_html}
        <div class="footer">
            <p>Generated from Markdown | TRD Project</p>
        </div>
    </div>
</body>
</html>"""

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python simple_md_to_html.py <input.md> [output.html]")
        return

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"エラー: {input_file} が見つかりません")
        return

    # 出力ファイル名を決定
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.with_suffix('.html')

    # Markdownを読み込み
    print(f"読み込み中: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # HTMLに変換
    print("HTML変換中...")
    body_html = convert_markdown_to_html(md_content)
    main()
