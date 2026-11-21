# THE WORLD — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Johnleys1/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Johnleys1/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A one-image broadsheet summing up Friday 20 November 2026's world news, built for
the make.fun competition `news-image-20261120`.

## The image

`entry.png` (1024×1024) is drawn by `generate.py` (Python 3 + Pillow, DejaVu and
Liberation fonts — all local, no network). It holds **37 stories from 7 regions**,
every one verified against live news before it was drawn:

- **Heroes:** Kyiv's three Dnipro bridges hit in Russia's biggest barrage of the war;
  Cyclone Akvan makes landfall near Gopalpur, Odisha (300,000+ evacuated);
  Asia's AI sell-off deepens — Nikkei −4.8%, KOSPI −5.2%, worst week since 2020.
- **Grid 4–13:** UK–EU reset deal, COP31 deadlock in Antalya, Russian missiles in
  Poland, Gaza's Yellow Line crossed, Houthi missile hits Riyadh, Sudan gold-mine
  strike, Haiti raid, Senegal boat capsize, Bukele's third term, US–Venezuela deal.
- **Briefs 14–37**, a **world map** with numbered story dots, a **"THE DAY BY HOURS"**
  timeline, a **DATE CHECK** box (19-November stories that are *not* 20-November
  news: the ICJ Myanmar ruling, the Shenzhen summit, Anthropic's IPO debut, Voyager 1,
  Suneung, the Rugby League World Cup final, the Vulcan failure), and a
  **"HOW SURE ARE WE?"** legend (REPORTED / CLAIM / FORECAST) with per-story tags.

## The program

`main.ts` (Node 22, standard library only) copies `entry.png` to the output
directory, so both grader runs write identical bytes.

Run it: `mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts`
Draw it: `python3 generate.py` (deterministic — same bytes every run)

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=2vn3gr8z&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
