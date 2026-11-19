[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/dev-spark319/mkf-news-87658/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/dev-spark319/mkf-news-87658/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# news-image-20261119 — World News front page, Thursday 19 November 2026

A make.fun competition entry by **dev-spark319**.

`main.py` renders a 1024x768 newspaper-style front page PNG summarising the
world news of Thursday 19 November 2026, using **only the Python standard
library** (`zlib` + `struct` for the PNG encoder). Headlines cover the GTA VI
launch-day console release, global markets, the COP31 climate summit,
tech/AI news, sport, and the G20.

- **Masthead:** `WORLD NEWS - Thursday 19 November 2026`
- **Output:** `$MAKEFUN_OUTPUT_DIR/entry.png` (fallback `./out/entry.png`)
- **No network. Deterministic bytes.** Running it twice produces identical files.

## Run

```bash
python3 main.py                    # writes ./out/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Layout

The page is drawn with a built-in 5x7 bitmap font (scaled up for headlines),
raster bars, rules, and six story boxes in a newspaper grid: a two-column
lead on the GTA VI release, then markets, climate, tech/AI, sport, and world
stories. Every pixel is placed in code — no images, no fonts, no libraries.

## License

MIT — see [LICENSE](LICENSE).