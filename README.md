# ConnectionsBench

Benchmark suite evaluating LLM performance on NYT Connections puzzles. Tests semantic grouping and lateral reasoning
across 1000+ puzzles with built-in difficulty tiers. Tracks model accuracy by tier: Yellow (easy) → Purple (hard).

## Status

- [x] Project scaffold
- [x] Data pipeline
- [x] Models
- [x] Loader
- [x] Scorer
- [x] Runner
- [ ] CLI
- [ ] First benchmark run
- [ ] Results + leaderboard

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/roman-collinge/ConnectionsBench
cd ConnectionsBench
uv sync
```

## Usage

### Fetch dataset

On first run, backfills all puzzles from 2023-06-12 (first puzzle date) to today:

```bash
uv run python scripts/fetch_puzzles.py
```

Subsequent runs append only new puzzles. Optionally specify a custom output path:

```bash
uv run python scripts/fetch_puzzles.py --data-file path/to/connections.json
```

Image-based puzzles are stored with `"has_images": true` and empty `words`/`groups` — they are excluded automatically at
benchmark run time.

### Run benchmark

_Coming soon — see [Status](#status)._

## Results

_Coming soon._

## Methodology

NYT Connections presents 16 words to be partitioned into 4 groups of 4, each sharing a common theme. Groups are
difficulty-tiered: Yellow (straightforward) → Green → Blue → Purple (lateral, tricky).

Each model receives the 16 words and must return 4 groups in a single attempt with no hints. Scoring is exact
set-match — a group is correct only if all 4 members are right.

**Prompt design:** Words are presented as a comma-separated list in randomised order
per run. Shuffling prevents exploitation of positional patterns. NYT returns words
in difficulty order (Yellow→Purple), so a model with training data exposure could
use position as a signal rather than semantic reasoning.

**Metrics:**

- `solve_rate` — % of puzzles fully solved
- `avg_groups_correct` — mean groups correct per puzzle (0–4)
- Per-tier accuracy (Yellow / Green / Blue / Purple)
- `purple_gap` — Yellow accuracy minus Purple accuracy, a proxy for reasoning depth vs pattern matching

Image-based puzzles are excluded from all benchmark runs.

**Contamination analysis:** NYT Connections launched June 2023. Puzzles published after a model's training cutoff
isolate genuine reasoning from memorised answers. Pre- vs post-cutoff performance split is a core research contribution
of this benchmark.

## Contributing

Open an issue or PR. If adding a new model runner, follow the pattern (soon coming) and include results in your PR.

## License

MIT License

Copyright (c) 2026 Roman Collinge

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.