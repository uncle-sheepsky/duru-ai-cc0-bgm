"""탄막 메이킹 롱폼 바탕곡 — 신작 1곡(2026-11-05). ♩100 4/4 · 1마디 = 2.4s = 72f = 115,200샘플. 마디·슬램은 편-계약 · narration/words.json 에서 읽는다.
저수준만 공용: playlist_melty/bgm/band.py(샘플러·보이싱·마스터) · 칩·삼각파·벽 합성은 remake/bgm/build_bgm.py 함수 import. 화성·선율·편곡은 신작.
생각 = 조사. 빈틈을 파고드는 동안 A 단조, 0.86px 슬램에서 으뜸화음이 온전히 닫히고, 엔딩은 같은 으뜸음 장조.
지문: CLUE i–v–♭VI–iv [−5,+1,−3,−5] · LIFT ♭VI–♭III–♭VII–V [−5,−5,−3,+1] · 킥 {0,5,8} + 림 {4,12} + 8분 셰이커 = CLUE×K058.
역할: 저음 = 삼각파 · 화음 = 벽(대사 밑, 저역) · 말렛 = 마림바 8분 · 선율 = 칩(말 없는 구간만, A4~E6) · 강세 = 팀파니·크래시.
사용: <venv> bgm/build_bed.py [--tag v1]
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy.signal import sosfilt

HERE = Path(__file__).resolve().parent
EP = HERE
sys.path.insert(0, str(HERE.parents[1] / "duru-zoneout-1h"))  # band.py · sfz_sampler.py
sys.path.insert(0, str(HERE.parent))
import band  # noqa: E402
from band import SR, Song, bass_note, line, sos, voice  # noqa: E402

_s = importlib.util.spec_from_file_location("danmaku_bgm", EP.parent / "danmaku-short/build_bgm.py")
Z = importlib.util.module_from_spec(_s)
_sa = sys.argv
sys.argv = ["x"]
_s.loader.exec_module(Z)
sys.argv = _sa
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v1"
_t = json.loads((EP / "timing.json").read_text(encoding="utf-8"))  # 내레이션 실측으로 정한 시간표(값만)
K, W = _t["K"], _t["W"]
BARS = K["length"]["bars"]
BAR_N = 115200
CH = {c["id"]: c for c in K["chapters"]}
LT = {L["id"]: L for L in W["lines"]}
BAR_OF = lambda i: int(round(LT[i]["t0"] / 2.4))
SL = {k: BAR_OF(k) for k in ("NH-3", "N2-4", "N3-5", "N4-4", "N6-5")}
PEAK0 = SL["N4-4"] - 3
TACET = [(0, SL["NH-3"]), (CH["7"]["bar0"], CH["7"]["bar1"])]
END0 = BARS - 8
CLUE, LIFT = ["Am", "Em", "F", "Dm"], ["F", "C", "G", "E7"]
ST = {"H": 0.6, "1": 0.72, "2": 0.62, "3": 0.82, "4": 0.78, "5": 0.82, "6": 0.66, "8": 0.7}


def B(bar, beat=0.0):
    return bar * 4 + beat


def chap(bar):
    return next(k for k, c in CH.items() if c["bar0"] <= bar < c["bar1"])


def tacet(bar):
    return any(a <= bar < b for a, b in TACET)


def chord(bar):
    c = chap(bar)
    if PEAK0 <= bar < SL["N4-4"]:
        return ["Dm", "E7sus4", "E7"][bar - PEAK0]
    if bar in SL.values():
        return "Am"
    if bar >= END0:
        return ["A", "E", "F#m7", "D"][(bar - END0) % 4] if bar < BARS - 1 else "A"
    if bar >= END0 - 1:
        return "E7"
    prog = LIFT if c in ("3", "5") else CLUE
    return prog[(bar - CH[c]["bar0"]) % 4]


def main():
    s = Song(f"bed_{TAG}", "탄막 메이킹 바탕곡", bpm=100, bar=4, bars=BARS, swing=0.5, tail=0.0, lufs=-16.0)
    s.N = BARS * BAR_N
    prev = None
    for bar in range(BARS):
        if tacet(bar):
            continue
        sym = chord(bar)
        c = chap(bar)
        g = ST[c]
        peak = PEAK0 <= bar < SL["N4-4"]
        slam = bar in SL.values()
        end = bar >= END0
        if peak:
            g = 0.8 + 0.1 * (bar - PEAK0)
        t0, dur = s.pos(B(bar)), 4 * s.beat
        # 저음
        r = bass_note(sym, 33, 48)
        if peak or slam or end:
            s.add("bass", Z.tri_bass(r, dur * 0.95, rel=0.05), t0, gain=g)
        else:
            for st, v in ((0, 1.0), (5, 0.75), (8, 0.9)):
                s.add("bass", Z.tri_bass(r, 0.42), s.pos(B(bar, st / 4)), gain=g * v)
        # 벽: 대사 밑 저역
        prev = voice(sym, 45, 62, prev, n=4)
        for pan, sd in ((-0.6, 1), (0.6, 2)):
            y = Z.wall_voice(prev, dur + 0.02, seed=bar * 10 + sd)
            n = len(y)
            y = sosfilt(sos(2600 if peak else 1300, "lowpass"), y) * np.minimum(1, np.arange(n) / (0.04 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.04 * SR))
            s.add("wall", y, t0, pan=pan, gain=g * (1.2 if peak else 1.0), send=0.2)
        # 타악
        if c != "H" and not end and not slam:
            for k in range(16):
                b = B(bar, k / 4)
                if k in (0, 5, 8) and not (c == "6" and bar < SL["N6-5"]):
                    s.add("kick", Z.kick(1.0 if k == 0 else 0.8), s.pos(b), gain=g)
                if k in (4, 12):
                    band.perc(s, 37, b, amp=0.8 * g, pan=-0.08, vel=74, send=0.1, dur=0.4, human=0.0)
                if k % 2 == 0:
                    s.add("hat", Z.hat(0.7 if k % 4 else 0.45, seed=bar * 16 + k), s.pos(b), pan=0.2, gain=g)
        # 마림바 8분
        vv = voice(sym, 57, 74, None, n=3)
        order = (0, 1, 2, 1, 0, 2, 1, 2)
        for k in range(8):
            if slam and k > 1:
                break
            v = vv[order[k] % len(vv)]
            band.inst(s, "mari", "Marimba", v, B(bar, k * 0.5), 0.6, vel=84 if (peak or end) else 66, amp=g * (1.3 if (peak or end) else 0.7), pan=-0.25 + 0.07 * k, send=0.2, human=0.002, rel=0.2)
        # 슬램
        if slam:
            y = band.sample_note("Timpani", 45, 1.2, vel=122, rr=1, release=0.3)
            k = int(np.argmax(np.abs(y) > 0.15 * np.abs(y).max()))
            s.add("fx", y * 1.1, max(0, t0 - k / SR), send=0.15)
            band.perc(s, 49, B(bar), amp=0.8, vel=112, dur=2.0, send=0.18, human=0.0, bus="crash")
            s.add("kick", Z.kick(1.0), t0, gain=1.1)
            w = 2 * s.beat / 4
            s.add("fx", Z.whip(w), t0 - w, gain=0.4, send=0.05)
    # 본 정점 선율: 말 없는 세 마디
    for i, txt in enumerate(("A4:1 C5:1 E5:1 A5:1", "B4:1 D5:1 E5:1 B5:1", "E5:.5 G#5:.5 B5:1 E6:2")):
        for b, d, m in line(txt, start=B(PEAK0 + i)):
            Z.add_lead(s, m, b, d, 0.7 + 0.1 * i, duty=0.5, vib=0.12)
    s.add("fx", Z.riser(3 * 4 * s.beat), s.pos(B(PEAK0)), gain=0.32, send=0.2)
    # 엔드스크린 선율(장조)
    MOT = ["A4:1 C#5:1 E5:2", "E5:1 D5:1 B4:2", "C#5:1 E5:1 A5:2", "F#5:1 E5:1 D5:2"]
    for i in range(BARS - 1 - END0):
        for b, d, m in line(MOT[i % 4], start=B(END0 + i)):
            Z.add_lead(s, m, b, d, 0.5, duty=0.5, vib=0.1)
    for b, d, m in line("A4:4", start=B(BARS - 1)):
        Z.add_lead(s, m, b, d, 0.4, duty=0.5)
    gains = {"lead": 0.5, "wall": 0.34, "bass": 0.34, "kick": 0.5, "perc": 0.5, "hat": 0.2, "mari": 2.2, "fx": 0.7, "crash": 0.5}
    out = HERE / "out" / TAG
    rep = band.master(s, gains, rev_rt=1.2, rev_wet=0.18, out_dir=out, fade_out=1.2, tp_target=-1.5)
    # 정지 구간 완전 무음
    from scipy.io import wavfile
    sr, x = wavfile.read(out / "mix.wav")
    x = x.astype(np.float64) / 32768
    m = np.ones(len(x))
    for a, b in TACET:
        i0, i1 = a * BAR_N, b * BAR_N
        m[i0:i1] = 0
        if i0 > 0:
            f = int(0.3 * SR)
            m[i0 - f:i0] *= np.linspace(1, 0, f)
    wavfile.write(out / "bed.wav", SR, (np.clip(x * m[:, None], -1, 1) * 32767).astype(np.int16))
    (out / "report.json").write_text(json.dumps({"bars": BARS, "slams": SL, "peak0": PEAK0, "tacet": TACET, "section": rep.get("section_lufs")}, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"bars": BARS, "slams": SL, "peak0": PEAK0, "tp": rep.get("true_peak_db")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
