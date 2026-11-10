"""리듬게임 메이킹 롱폼 바탕곡 — 신작 1곡(2026-11-06). ♩90 4/4 · 1마디 = 2.6667s = 80f = 128,000샘플@48k.
마디·슬램·말 없는 구간은 tools/l2_timeline.py place()(TTS 실측 반영)에서 읽는다 — 손으로 적지 않는다.
생각 = 소실점. 맨 윗음 D를 붙박이로 두고(먼 한 점) 베이스가 그 점을 향해 다가온다.
지문(2026-11-06 사전 대조 OK): CONVERGE I–iii–♭III–ii `[+4,−1,−1,−2]`(G–Bm–B♭–Am) · TURN vi–IV–♭VII–V `[−4,+5,−3,+2]`(Em–C–F–D)
 · 킥 {0,10,13} + 사이드스틱 {4,12} + 16분 하이햇(엇8분 강세) = CONVERGE×K0A13.
역할(이전 메이킹 바탕곡과 다른 음색): 저음 = 콘트라베이스 피치카토 · 화음 = 하프 8분 아르페지오 + 현 피치카토 2·4박
 · 붙박이 윗음 = 뮤트 호른 지속 · 선율 = 업라이트 피아노(말 없는 구간만, 최고 D5) · 강세 = 팀파니 + 크래시 + 피아노 저음 옥타브.
저수준만 공용: playlist_melty/bgm/band.py(VSCO 2 CE 샘플러·보이싱·마스터). 화성·편곡·선율은 신작.
사용: <site-factory venv> bgm/build_bed.py [--tag v1]
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE
sys.path.insert(0, str(HERE.parents[1] / "duru-zoneout-1h"))  # band.py · sfz_sampler.py
sys.path.insert(0, str(HERE.parent))
import band  # noqa: E402
from band import SR, Song, bass_note, line, voice  # noqa: E402

import types  # noqa: E402
_t = json.loads((EP / "timing.json").read_text(encoding="utf-8"))  # 내레이션 실측으로 정한 시간표(값만)
T = types.SimpleNamespace(BAR=_t["BAR"], BPM=_t["BPM"], place=lambda: _t["place"])
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v1"
BAR_N = 128000
P = T.place()
BARS = round(P[-1]["t1"] / T.BAR)
ROWS = {r["id"]: r for c in P for r in c["rows"] if r["id"] != "[X]"}
BAR_OF = lambda i: int(round(ROWS[i]["t0"] / T.BAR))
CH = [(c["ch"].split()[0], round(c["t0"] / T.BAR), round(c["t1"] / T.BAR)) for c in P]
XS = [(c["ch"].split()[0], r["text"], round(r["t0"] / T.BAR), round(r["t1"] / T.BAR)) for c in P for r in c["rows"] if r["id"] == "[X]"]
SL = {k: BAR_OF(k) for k in ("NH-3", "N2-4", "N3-6", "N3-9", "N6-1")}
PEAK = SL["N3-9"]
TACET = [(0, 1)]                                                       # 훅 첫 마디 = ep14 게임 음악(NH-1 밑) — 바탕곡 쉼
REST = [(x[2], x[3]) for x in XS if x[0] == "3"][0]                    # 정점 뒤 휴식(말 없음) = 피아노 선율
END0 = [x[2] for x in XS if x[1].startswith("엔드")][0]
CONVERGE = ["G", "Bm", "Bb", "Am7"]
TURN = ["Em", "C", "F", "D"]
ST = {"H": 0.55, "1": 0.66, "2": 0.62, "3": 0.74, "4": 0.6, "5": 0.7, "6": 0.72}
KICK = (0, 10, 13)


def B(bar, beat=0.0):
    return bar * 4 + beat


def chap(bar):
    return next(k for k, a, b in CH if a <= bar < b)


def tacet(bar):
    return any(a <= bar < b for a, b in TACET)


def chord(bar):
    c = chap(bar)
    if bar == PEAK or bar in SL.values() or bar == BARS - 1:
        return "G"
    if c == "3" and bar < PEAK:
        k = bar - next(a for k_, a, _ in CH if k_ == "3")
        return TURN[k % 4] if PEAK - bar > 1 else "D"
    a0 = next(a for k_, a, _ in CH if k_ == c)
    return CONVERGE[(bar - a0) % 4]


def main():
    s = Song(f"bed_{TAG}", "리듬게임 메이킹 바탕곡", bpm=90, bar=4, bars=BARS, swing=0.5, tail=0.0, lufs=-16.0)
    s.N = BARS * BAR_N
    for bar in range(BARS):
        if tacet(bar):
            continue
        sym, c = chord(bar), chap(bar)
        g = ST[c]
        slam, peak = bar in SL.values(), bar == PEAK
        rest = REST[0] <= bar < REST[1]
        end = bar >= END0
        build = c == "3" and bar < PEAK
        if build:
            g *= 0.85 + 0.25 * (bar - next(a for k_, a, _ in CH if k_ == "3")) / max(1, PEAK - next(a for k_, a, _ in CH if k_ == "3"))
        if peak:
            g = 1.0
        # 저음: 콘트라베이스 피치카토 — 킥 자리
        r = bass_note(sym, 31, 45)
        for k in KICK:
            if c == "H" and k:
                continue
            band.inst(s, "bass", "ContrabassPizz", r if k != 13 else r + 12 if r + 12 <= 50 else r, B(bar, k / 4), 0.9, vel=96 if k == 0 else 80, amp=g * (1.0 if k == 0 else 0.8), pan=0.0, send=0.08, human=0.0, rel=0.12)
        # 하프 8분 아르페지오(아래→위→아래) — 대사 밑에선 음역을 낮게
        hv = voice(sym, 50, 69, None, n=4)
        order = (0, 1, 2, 3, 2, 1, 2, 3) if not rest else (0, 2, 3, 2, 1, 2, 3, 2)
        for k in range(8):
            if slam and k > 0:
                break
            band.inst(s, "harp", "Harp", hv[order[k] % len(hv)], B(bar, k * 0.5), 1.2, vel=78 if (peak or end) else 64, amp=g * 0.9, pan=-0.3 + 0.08 * k, send=0.22, human=0.0, rel=0.3)
        # 현 피치카토 2·4박 화음
        if c != "H" and not slam:
            pv = voice(sym, 55, 72, None, n=3)
            for bt in (1, 3):
                for m in pv:
                    band.inst(s, "pizz", "ViolinEnsPizz", m, B(bar, bt), 0.5, vel=70, amp=g * 0.55, pan=0.25, send=0.15, human=0.0, rel=0.1)
        # 붙박이 윗음 D(소실점) — 뮤트 호른 지속. 대사 구간은 낮게, 3장 빌드에서 커진다
        if c in ("2", "3", "5", "6") and not slam:
            band.inst(s, "horn", "FHornMute", 62 if not (peak or end) else 74, B(bar), 3.9, vel=60 if not build else 80, amp=g * (0.5 if not build else 0.75), pan=-0.1, send=0.3, human=0.0, rel=0.4, attack=0.15)
        # 타악: 1장부터 · 정점 휴식·엔드스크린 끝 마디 제외
        if c != "H" and not slam and bar < BARS - 1:
            for k in range(16):
                b = B(bar, k / 4)
                if k in KICK:
                    band.perc(s, 36, b, amp=0.9 * g, vel=100 if k == 0 else 84, send=0.04, dur=0.5, human=0.0, bus="kick")
                if k in (4, 12):
                    band.perc(s, 37, b, amp=0.75 * g, pan=-0.08, vel=80, send=0.1, dur=0.4, human=0.0)
                if c == "5" and k % 4 == 0:
                    band.perc(s, 76, b, amp=0.45 * g, pan=0.3, vel=90, send=0.05, dur=0.3, human=0.0)   # 5장 = 메트로놈 박
                if build or peak or end or c in ("4", "5"):
                    band.perc(s, 42, b, amp=(0.55 if k % 4 == 2 else 0.3) * g, pan=0.18, vel=70, send=0.02, dur=0.2, human=0.0, bus="hat")
        # 슬램: 팀파니 + 크래시 + 피아노 저음 옥타브
        if slam:
            y = band.sample_note("Timpani", 43, 1.4, vel=120, rr=2, release=0.3)
            kk = int(np.argmax(np.abs(y) > 0.15 * np.abs(y).max()))
            s.add("fx", y * 1.0, max(0, s.pos(B(bar)) - kk / SR), send=0.15)
            band.perc(s, 49, B(bar), amp=0.75, vel=110, dur=2.4, send=0.18, human=0.0, bus="crash")
            for m in (31, 43):
                band.inst(s, "piano", "UprightPiano", m, B(bar), 3.5, vel=100, amp=0.9, send=0.2, human=0.0, rel=0.6)
    # 정점(N3-9): 피아노 선율이 붙박이 D5 에서 G4 로 내려와 베이스 G 와 만난다(옥타브 수렴)
    for b, d, m in line("D5:1 C5:1 Bb4:1 G4:1", start=B(PEAK)):
        band.inst(s, "piano", "UprightPiano", m, b, d * 1.4, vel=92, amp=1.1, pan=0.1, send=0.25, human=0.0, rel=0.4)
    # 정점 뒤 휴식(말 없음): 같은 수렴 동기를 두 번 — 위 D 붙박이, 베이스가 다가온다
    for i in range(REST[1] - REST[0]):
        for b, d, m in line(["D5:2 D5:1 C5:1", "D5:2 C5:1 B4:1"][i % 2], start=B(REST[0] + i)):
            band.inst(s, "piano", "UprightPiano", m, b, d * 1.2, vel=80, amp=0.95, pan=0.1, send=0.25, human=0.0, rel=0.4)
    # 엔드스크린: 피아노 선율(장조 · 최고 D5) → 마지막 마디 G 지속
    MOT = ["B4:1 D5:1 D5:2", "D5:1 B4:1 F#4:2", "D5:1 C5:1 Bb4:2", "C5:1 A4:1 B4:2"]
    for i in range(BARS - 1 - END0):
        for b, d, m in line(MOT[i % 4], start=B(END0 + i)):
            band.inst(s, "piano", "UprightPiano", m, b, d * 1.1, vel=76, amp=0.85, pan=0.1, send=0.25, human=0.0, rel=0.4)
    for m in (43, 55, 59, 62, 67):
        band.inst(s, "piano", "UprightPiano", m, B(BARS - 1), 4.0, vel=70, amp=0.7, send=0.3, human=0.0, rel=1.0)
    gains = {"bass": 0.9, "harp": 0.7, "pizz": 0.55, "horn": 0.6, "kick": 0.7, "perc": 0.5, "hat": 0.35, "fx": 0.7, "crash": 0.45, "piano": 0.75}
    out = HERE / "out" / TAG
    rep = band.master(s, gains, rev_rt=1.3, rev_wet=0.2, out_dir=out, fade_out=1.5, tp_target=-1.5)
    from scipy.io import wavfile
    sr, x = wavfile.read(out / "mix.wav")
    x = x.astype(np.float64) / 32768
    m = np.ones(len(x))
    for a, b in TACET:
        m[a * BAR_N:b * BAR_N] = 0
    wavfile.write(out / "bed.wav", SR, (np.clip(x * m[:, None], -1, 1) * 32767).astype(np.int16))
    info = {"bars": BARS, "slams": SL, "peak": PEAK, "rest": REST, "end0": END0, "tacet": TACET, "chapters": CH, "tp": rep.get("true_peak_db"), "section": rep.get("section_lufs")}
    (out / "report.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: info[k] for k in ("bars", "slams", "peak", "rest", "end0", "tacet", "tp")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
