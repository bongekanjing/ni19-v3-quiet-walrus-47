#!/usr/bin/env bash
set -euo pipefail
CHROME=/root/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(dirname "$HERE")"
python3 "$HERE/poster.py"
"$CHROME" --headless=new --no-sandbox --hide-scrollbars --window-size=1024,1024 \
  --enable-unsafe-swiftshader --virtual-time-budget=8000 \
  --screenshot=/tmp/poster_raw.png "file://$HERE/poster.html"
python3 - "$ROOT" <<'PY'
import sys, pathlib
from PIL import Image
root = pathlib.Path(sys.argv[1])
im = Image.open('/tmp/poster_raw.png').convert('RGB')
if im.size != (1024, 1024):
    sys.exit('screenshot is %sx%s, expected 1024x1024: the page must fit the square' % im.size)
out = root / 'entry.png'
im.save(out, 'PNG', optimize=True)
print('entry.png', out.stat().st_size, 'bytes', im.size)
PY
