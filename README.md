# news-image-20261125

Entry for the make.fun bounty
[news-image-20261125](https://make.fun/competitions/news-image-20261125):
"Sum up 25 November's world news in one image" ($100 pot, free entry).

## What it is

`main.py` is a pure Python 3.13 standard-library program. It draws a
newspaper front page — masthead with the date, one lead story and
eight more stories across regions and fields — with a small raster
engine (PNG writer, filled shapes, a 5x7 bitmap font) and writes it
to `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png` outside
the grader). No network, no randomness, no clock: two runs write
identical bytes (21,617 bytes, 1024x1024 PNG).

## The day's news depicted

All events that happened or were first reported on Wednesday
25 November 2026, as carried by Reuters, CNN, AFP and other wires
that day:

| Panel | Story |
|---|---|
| Lead | CIA and the U.S. Director of National Intelligence hit by a cyberattack (CNN, 25 Nov) |
| Ukraine | Zelenskyy confirms Ukraine struck Russian ships off Libya and in the Gulf of Finland |
| Russia | Putin says retaliation is inevitable as Ukraine keeps hitting Russian oil refineries |
| DR Congo | WHO evacuates staff from an Ebola hospital in Ituri amid fighting |
| U.S. courts | Huawei found guilty by a U.S. jury on 10 of 12 counts |
| Turkiye | Military helicopter crash kills five on a training flight |
| Migration | About 175 migrants missing after a boat from Senegal vanishes en route to Europe |
| France | Sarkozy and Bruni ordered to trial over the Libya corruption case |
| Thanksgiving | Trump pardons turkeys Freedom and Feathers on Thanksgiving eve |

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png
```

## License

MIT — see `LICENSE`.
