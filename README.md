# The World Today — 19 November 2026

A 1024×1024 newspaper front page for Thursday 19 November 2026, rendered to PNG by
headless Chromium. The date is set as the page's headline; below it sit a seven-region
index, a six-figure "day in numbers" strip, three illustrated lead stories and a grid of
35 briefs — 38 stories in all, with every count on the page derived from the story list
so the arithmetic cannot drift.

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/bongekanjing/ni19-v3-quiet-walrus-47/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/bongekanjing/ni19-v3-quiet-walrus-47/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

## What it is

- `build/poster.py` holds every story and writes `build/poster.html`. It refuses to build
  if the region tabs do not sum to the number of stories printed.
- `build/poster.css` is the layout: a 1024×1024 flex column in which the brief grid takes
  all remaining height, so nothing can spill past the square.
- `build/render.sh` runs the generator, screenshots the page with Chromium at 1024×1024
  and writes `entry.png`.
- `main.py` validates `entry.png` (PNG chunks and CRCs walked to IEND) and copies it to
  `$MAKEFUN_OUTPUT_DIR`.

## Run it

```sh
bash build/render.sh          # writes entry.png at the repo root
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two runs in a row write byte-identical output: nothing in the build depends on the clock,
on randomness, or on dictionary ordering.

Built for the make.fun bounty "Sum up 19 November's world news in one image".
