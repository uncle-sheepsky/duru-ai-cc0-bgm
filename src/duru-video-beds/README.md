# Duru video background tracks — composer code (CC0)

The background music written for individual videos on the channel, as used in those videos.
**CC0 1.0** — free for anything, no attribution required. Music and code only; the videos and the Duru character are not part of this release.

Some tracks have long silent stretches. Those are the spots where the video plays other audio (a short clip, a demo section, a playlist excerpt). The files are left exactly as used. The silent stretches are listed below.

Sounds: instrument samples from **VSCO 2 Community Edition (CC0)** plus code-synthesized parts. No other audio goes in.

| folder | MP3 | video | key · meter · tempo | silence |
|---|---|---|---|---|
| `bgm-free/` | [`duru-bed-bgm-free`](../../mp3/duru-bed-bgm-free.mp3) | [클로드한테 시켜봤습니다 | 파이썬으로 BGM 만들기](https://youtu.be/cfq1DbHfPcg) | D → E major · 4/4 · ♩90 | 0:00–0:08, 0:37–0:53, 1:07–1:23, 1:41–1:57, 2:13–2:29, 2:32–2:48 |
| `tspin-fake/` | [`duru-bed-tspin-fake`](../../mp3/duru-bed-tspin-fake.mp3) | [AI가 만든 거짓말에 속지 않으려면](https://youtu.be/aJgK9TF4Hzg) | A minor → A major · 4/4 · ♩90 | 0:00–0:08, 1:49–2:00 |
| `frame-gap/` | [`duru-bed-frame-gap`](../../mp3/duru-bed-frame-gap.mp3) | [노히트라던 탄막을 다시 검사해봤습니다](https://youtu.be/phQ7-AZkc2o) | A minor · 4/4 · ♩100 | 0:00–0:12, 2:26–2:46 |
| `danmaku-short/` | [`duru-danmaku-short`](../../mp3/duru-danmaku-short.mp3) | [노히트라던 탄막을 다시 검사해봤습니다](https://youtu.be/phQ7-AZkc2o) | see build_bgm.py | — |
| `rhythm-perspective/` | [`duru-bed-rhythm-perspective`](../../mp3/duru-bed-rhythm-perspective.mp3) | [CSS코드로 만든 리듬게임 연출, 원근감이 살도록 고쳐보기](https://youtu.be/ySvz8jbyN48) | G · 4/4 · ♩90 | 0:00–0:03 |
| `galaxy-spin/` | [`duru-bed-galaxy-spin`](../../mp3/duru-bed-galaxy-spin.mp3) | [별 만 개를 다 계산하지 않고 은하를 부딪혀 봤습니다](https://youtu.be/hzaGPEUVoyI) | C · 6/8 · ♩.=60 | — |
| `clap-face/` | [`duru-bed-clap-face`](../../mp3/duru-bed-clap-face.mp3) | [AI가 망친 두루를 되찾은 방법](https://youtu.be/xdjCyGcwCdg) | F · 4/4 · ♩112.5 | — |
| `brainmap-leftpanel/` | [`duru-bed-brainmap-leftpanel`](../../mp3/duru-bed-brainmap-leftpanel.mp3) | *검사는 다 통과했는데, 왼쪽 화면이 2분 넘게 그대로였습니다* (video not public yet) | B♭ major (C major in part 6) · 4/4 · ♩112.5 | — |
| `colorkit-template/` | [`duru-bed-colorkit-template`](../../mp3/duru-bed-colorkit-template.mp3) | *내 영상을 아무 캐릭터로나 만들 수 있게 바꿨습니다* (video not public yet) | F major · 4/4 · ♩150 · son montuno | — |

## Rebuild

```bash
pip install numpy scipy pyloudnorm
# VSCO 2 Community Edition SFZ (CC0): https://github.com/sgossner/VSCO-2-CE
export VSCO_SFZ_DIR=/path/to/VSCO-2-CE-SFZ        # folder containing *.sfz
cd galaxy-spin && python build_bed.py --tag v1    # writes out/v1/bed.wav
```

`clap-face` uses `--tag v3`. `brainmap-leftpanel` uses `--tag v7`. `colorkit-template` uses `--tag v2`. `danmaku-short` is `python build_bgm.py --tag v3` and writes `out/v3/mix.wav`.
`frame-gap` imports instrument functions from `danmaku-short/build_bgm.py`.

The shared sampler and mixer (`band.py`, `sfz_sampler.py`) live in [`../duru-zoneout-1h/`](../duru-zoneout-1h/). `lufs_spread.py` is the loudness meter.
`timing.json` holds the bar and line timings the music follows. It is a frozen copy of values measured from the narration, so the scripts run without the narration files.

Rebuilding gives the same WAV, byte for byte. Hashes are in [`MANIFEST.txt`](MANIFEST.txt).
