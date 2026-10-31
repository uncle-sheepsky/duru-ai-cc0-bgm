# Zone out with Duru (1 hour) — 16 tracks · CC0 1.0

▶ Video: [멍 때리기 플레이리스트 · 1시간 / Zone-out playlist · 1 hour](https://youtu.be/nQNfS5DZUiM)

두루랑 멍 때리며 쉬어 가는 1시간 — 영상에 쓴 오리지널 16곡의 작곡 코드입니다. / The code that composed the 16 original tracks.
**CC0 1.0** — free for anything, no attribution required.

Each song is one Python script: chords, melodies and arrangement are written per song; `band.py` is only the shared
low-level part (sampler, notation parser, chord voicing, a few synthesized instruments, mixer/master, loudness gates).
Running a script writes `out/<tag>/mix.wav`. Rebuilding is deterministic (bit-identical WAV).

```bash
pip install numpy scipy pyloudnorm
# VSCO 2 Community Edition SFZ (CC0): https://github.com/sgossner/VSCO-2-CE
export VSCO_SFZ_DIR=/path/to/VSCO-2-CE-SFZ        # folder containing *.sfz
python t01_melty_afternoon.py --tag v1            # track 1
python tracks/t02_polka.py                        # tracks 2–16
```

| # | script | title | key · meter · tempo | stage* |
|---|---|---|---|---|
| 1 | `t01_melty_afternoon.py` | 흐물흐물 오후 (Melty Afternoon) | F · 4/4 swing · 112 | LIGHT |
| 2 | `tracks/t02_*.py` | 콧방울 폴카 (Nose-Bubble Polka) | B♭ · 2/4 · 120 | LIGHT |
| 3 | `tracks/t03_*.py` | 짝짝이 양말 행진곡 (Mismatched Socks March) | G · 4/4 · 100 | LIGHT |
| 4 | `tracks/t04_*.py` | 베개 왈츠 (Pillow Waltz) | E♭ · 3/4 · 96 | DEEP |
| 5 | `tracks/t05_*.py` | 늘어진 양말 블루스 (Droopy Socks Blues) | C · 12/8 · ♩.=60 | DEEP |
| 6 | `tracks/t06_*.py` | 졸린 보사 (Sleepy Bossa) | D · 4/4 · 120 | DEEP |
| 7 | `tracks/t07_*.py` | 이불 하바네라 (Blanket Habanera) | Dm · 2/4 · 66 | DEEP |
| 8 | `tracks/t08_*.py` | 꼬르륵 칼립소 (Tummy-Rumble Calypso) | C · 4/4 · 104 | LIGHT |
| 9 | `tracks/t09_*.py` | 뒤척뒤척 스카 (Toss-and-Turn Ska) | F · 4/4 · 152 | LIGHT |
| 10 | `tracks/t10_*.py` | 구름 위 5박자 (Five Beats on a Cloud) | A · 5/4 · 104 | DREAM |
| 11 | `tracks/t11_*.py` | 우유 한 잔 녹턴 (Warm Milk Nocturne) | E · 4/4 · 66 | DREAM |
| 12 | `tracks/t12_*.py` | 깡총 슬립지그 (Hop-Hop Slip Jig) | D mixolydian · 9/8 · ♩.=116 | LIGHT |
| 13 | `tracks/t13_*.py` | 부스러기 찰스턴 (Crumbly Charleston) | A♭ · 4/4 · 168 | LIGHT |
| 14 | `tracks/t14_*.py` | 하품 미뉴에트 (Yawning Minuet) | G · 3/4 · 104 | DEEP |
| 15 | `tracks/t15_*.py` | 달팽이 행진 (Snail March) | Am · 4/4 · 64 | DEEP |
| 16 | `tracks/t16_*.py` | 별똥별 휘파람 (Shooting-Star Whistle) | C · 12/8 · ♩.=52 | DREAM |

\*The playlist follows a sleep curve: LIGHT tracks −14 LUFS, DEEP −16, DREAM −16.5 (quieter as sleep deepens).
Integrity: [`MANIFEST.txt`](MANIFEST.txt) (durations + SHA-256 of the released FLAC/MP3).
Video, background art and the Duru character are **not** part of this CC0 release — only the music and this code.
