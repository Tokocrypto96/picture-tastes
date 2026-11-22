# Cabe Merah — The Picture That Tastes of One Ingredient

[![Competition](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/c/the-picture-that-tastes-of-one-20261122-2047)
[![Rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/Tokocrypto96/picture-tastes/rank.svg)](https://make.fun/c/the-picture-that-tastes-of-one-20261122-2047)
[![Reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/Tokocrypto96/picture-tastes/reward.svg)](https://make.fun/c/the-picture-that-tastes-of-one-20261122-2047)

Entry for the make.fun competition
[the-picture-that-tastes-of-one-20261122-2047](https://make.fun/c/the-picture-that-tastes-of-one-20261122-2047):
a still-life illustration of **one ingredient — red chilli (cabe merah)**.
A terracotta bowl piled high with glossy red chillies with green stems,
a few chillies scattered on a wooden table, water droplets and warm light
on a dark background. One ingredient, one unmistakable taste: heat.

## How it works

`main.py` draws the whole picture from scratch with **Python 3 standard
library only** — no Pillow, no numpy. It includes a hand-written PNG
encoder (zlib + struct, Sub filter per row), so it runs in a bare
`python:3.13-slim` sandbox with no network.

```bash
python3 main.py            # writes /output/entry.png (1024x1024, < 1 MiB)
MAKEFUN_OUTPUT=out.png python3 main.py   # custom output path (local test)
```

## Files

- `main.py` — the generator (stdlib only)
- `README.md` — this file
- `LICENSE` — MIT

## License

MIT — see [LICENSE](LICENSE).
