#!/usr/bin/env python3
"""独立HTMLページを生成する。python3 generate_pages.py"""

import json
import re
from pathlib import Path

from server import STATUS_DATABASE, status_payload

BASE_DIR = Path(__file__).parent

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HTTP {status}</title>
  <link rel="stylesheet" href="style.css">
  <script>window.__STATUS_CODE__='{code}';</script>
</head>
<body class="status-{class_digit}">
  <div class="container">
    <div class="status-code" contenteditable="true" spellcheck="false" inputmode="numeric">{code}</div>
    <div class="tip">{status} {phrase} - {description}</div>
    <div class="http-status">HTTP/1.1 {status} {phrase}</div>
  </div>
  <script src="status-data.js"></script>
  <script src="app.js"></script>
</body>
</html>
"""


def generate_page(code: str, filename: str) -> None:
    payload = status_payload(code)
    status = payload['status']
    html = TEMPLATE.format(
        code=code,
        status=status,
        phrase=payload['phrase'],
        description=payload['description'].split(' - ', 1)[-1],
        class_digit=str(status)[0],
    )
    (BASE_DIR / filename).write_text(html, encoding='utf-8')
    print(f"  ✅ {filename}")


def main() -> None:
    print("📄 独立HTMLページを生成中...\n")

    generate_page('200', 'index.html')

    for code in sorted(STATUS_DATABASE.keys(), key=int):
        if code == '200':
            continue
        generate_page(code, f'{code}.html')

    print(f"\n✨ 完了: index.html + {len(STATUS_DATABASE) - 1} 個の {{code}}.html")


if __name__ == '__main__':
    main()
