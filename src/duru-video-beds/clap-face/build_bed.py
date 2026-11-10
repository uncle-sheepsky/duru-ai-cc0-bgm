"""박수·얼굴 제작기 바탕곡 — 신작 1곡(2026-11-09). ♩112.5 4/4 · 1마디 = 2.1333s = 64f = 102,400샘플@48k · 8분음표 = 12,800샘플.
마디·슬램·말 없는 구간은 tools/l2_timeline.py place()(TTS 실측 반영)에서 읽는다 — 손으로 적지 않는다.
생각 = 넣기와 빼기. 2장은 악기가 쌓여 번잡해지다 「이건 아니야…」에서 멈춘다. 4장은 매 마디 끝 박을 통째로 비운다(박수 사이의 빈 시간).
5장은 악기를 하나씩 덜어 「좋은데?」에 닿는다. 8장은 같은 조의 낯선 화음으로 비틀고, 9장에서 원래 화음으로 돌아와 「이거지!」 뒤 두 마디가 전곡 정점.
지문(대장 대조는 gate_bed.py G1): PICK I–iii–IV–♭VII `[+4,+1,+5,+2]`(Fmaj7–Am7–B♭maj7–E♭) · BACK I–iii–vi–IV `[+4,+5,−4,−5]` · DRIFT i–♭III–♭VI–V `[+3,+5,−1,+5]` · 16분 격자 킥 {0,7,11} + 손뼉 {4,12}.
역할: 8분 = 마림바 · 저음 = 첼로 앙상블 피치카토 · 안쪽 = 비올라 피치카토 · 층 = 바순 스타카토 · 실로폰(저역) · 지속 = 비올라 앙상블 조용히 · 선율 = 오보에(말 없는 구간만, 최고 F5) · 강세 = 팀파니.
저수준만 공용: playlist_melty/bgm/band.py(VSCO 2 CE CC0 샘플러·보이싱·마스터). 화성·편곡·선율은 신작.
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
BAR_N = 102400
P = T.place()
BARS = round(P[-1]["t1"] / T.BAR)
ROWS = {r["id"]: r for c in P for r in c["rows"] if r["id"] != "[X]"}
BAR_OF = lambda i: int(round(ROWS[i]["t0"] / T.BAR))
BAR_FLOOR = lambda i: int(ROWS[i]["t0"] // T.BAR)
CH = [(c["ch"].split()[0], round(c["t0"] / T.BAR), round(c["t1"] / T.BAR)) for c in P]
XS = [(c["ch"].split()[0], r["text"], round(r["t0"] / T.BAR), round(r["t1"] / T.BAR)) for c in P for r in c["rows"] if r["id"] == "[X]"]
SL = {k: BAR_OF(k) for k in ("NH-5", "N2-13", "N5-15", "N9-8")}
X = {x[1].split(" — ")[-1][:3]: (x[2], x[3]) for x in XS}
GOOD = next((x[2], x[3]) for x in XS if x[1].startswith("감상 — 8장"))
PAIR = next((x[2], x[3]) for x in XS if x[1].startswith("감상 — 두"))
ALL17 = next((x[2], x[3]) for x in XS if x[1].startswith("감상 — 17"))
THIS = next((x[2], x[3]) for x in XS if x[1].startswith("감상 — 이거지"))
GAP = next((x[2], x[3]) for x in XS if x[1].startswith("재현"))
END = next((x[2], x[3]) for x in XS if x[1].startswith("끝"))
PEAK = THIS[0]
PICK = ["Fmaj7", "Am7", "Bbmaj7", "Eb"]
BACK = ["Fmaj7", "Am7", "Dm7", "Bbmaj7"]
DRIFT = ["Fm7", "Abmaj7", "Dbmaj7", "C7"]
KICK = (0, 7, 11)
CLAP = (4, 12)
# 오보에 — 화음마다 한 마디(최고 F5)
MEL = {"Fmaj7": "C5:1 A4:.5 C5:.5 F5:1 E5:1", "Am7": "E5:1.5 C5:.5 A4:2", "Bbmaj7": "D5:1 Bb4:.5 D5:.5 F5:1 D5:1", "Eb": "Eb5:1 G4:.5 Bb4:.5 Eb5:2", "Dm7": "F5:1 D5:.5 F5:.5 A4:2"}


def chap(bar):
    return next(k for k, a, b in CH if a <= bar < b)


def a0(bar):
    return next(a for k, a, _ in CH if k == chap(bar))


def b1(bar):
    return next(b for k, _, b in CH if k == chap(bar))


def inside(bar, span):
    return span[0] <= bar < span[1]


def chord_at(bar, beat):
    """(화음 기호). 2장은 번잡해지면서 한 마디에 두 번 바뀐다."""
    c = chap(bar)
    n = bar - a0(bar)
    if bar == BARS - 1:
        return "Fmaj7"
    if c == "8":
        return DRIFT[n % 4]
    if c in ("6", "10", "11"):
        return BACK[n % 4]
    if c == "2" and bar >= a0(bar) + 8 and bar < SL["N2-13"]:
        return PICK[(n * 2 + (1 if beat >= 2 else 0)) % 4]
    return PICK[n % 4]


# 층 편성(장별 기본) — 값 = 음량 배율. 0 = 안 나옴
BASE = {
    "H": dict(mar=0.55, piz=0.0, bsn=0.0, kick=0.0, clap=0.0, xyl=0.0, pad=0.8, bass=0.5),
    "1": dict(mar=0.7, piz=0.45, bsn=0.0, kick=0.45, clap=0.0, xyl=0.0, pad=0.7, bass=0.8),
    "2": dict(mar=0.7, piz=0.45, bsn=0.0, kick=0.5, clap=0.0, xyl=0.0, pad=0.6, bass=0.85),
    "3": dict(mar=0.75, piz=0.5, bsn=0.7, kick=0.6, clap=0.5, xyl=0.0, pad=0.55, bass=0.9),
    "4": dict(mar=0.7, piz=0.5, bsn=0.0, kick=0.55, clap=0.45, xyl=0.0, pad=0.5, bass=0.85),
    "5": dict(mar=0.72, piz=0.5, bsn=0.65, kick=0.6, clap=0.5, xyl=0.5, pad=0.55, bass=0.9),
    "6": dict(mar=0.55, piz=0.4, bsn=0.0, kick=0.4, clap=0.3, xyl=0.0, pad=0.7, bass=0.75),
    "7": dict(mar=0.7, piz=0.45, bsn=0.0, kick=0.45, clap=0.35, xyl=0.0, pad=0.55, bass=0.8),
    "8": dict(mar=0.0, piz=0.5, bsn=0.45, kick=0.0, clap=0.0, xyl=0.0, pad=0.85, bass=0.75),
    "9": dict(mar=0.5, piz=0.3, bsn=0.0, kick=0.0, clap=0.0, xyl=0.0, pad=0.8, bass=0.7),
    "10": dict(mar=0.6, piz=0.4, bsn=0.0, kick=0.4, clap=0.3, xyl=0.0, pad=0.65, bass=0.8),
    "11": dict(mar=0.45, piz=0.25, bsn=0.0, kick=0.0, clap=0.0, xyl=0.0, pad=0.85, bass=0.6),
}


def plan(bar):
    c = chap(bar)
    g = dict(BASE[c])
    n = bar - a0(bar)
    if c == "H":
        if bar < BAR_FLOOR("NH-6"):
            g["mar"] = 0.0
        if bar == SL["NH-5"]:
            g.update(mar=0.0, pad=0.4)
    if c == "2":
        # 넣기: 8마디마다 한 층씩 — 말과 무관하게 점점 번잡
        if n >= 6:
            g["xyl"] = 0.45
        if n >= 10:
            g["bsn"] = 0.6
            g["kick"] = 0.65
        if n >= 14:
            g["clap"] = 0.5
            g["xyl"] = 0.6
        if bar >= SL["N2-13"]:
            g.update(mar=0.0 if bar == SL["N2-13"] else 0.5, piz=0.0, bsn=0.0, kick=0.0, clap=0.0, xyl=0.0, pad=0.85, bass=0.0 if bar == SL["N2-13"] else 0.7)
    if c == "5":
        # 빼기: 대사가 뺄 때마다 한 층씩 — N5-4 실로폰 · N5-6 바순 · N5-10 비올라 · N5-13 킥
        if bar >= BAR_FLOOR("N5-4"):
            g["xyl"] = 0.0
        if bar >= BAR_FLOOR("N5-6"):
            g["bsn"] = 0.0
        if bar >= BAR_FLOOR("N5-10"):
            g["piz"] = 0.0
        if bar >= BAR_FLOOR("N5-13"):
            g["kick"] = 0.0
            g["clap"] = 0.0
    if c == "9" and bar >= BAR_FLOOR("N9-4") and bar < SL["N9-8"]:
        # 돌아오기: 조금씩 채움
        k = (bar - BAR_FLOOR("N9-4")) / max(1, SL["N9-8"] - BAR_FLOOR("N9-4"))
        g["piz"] = 0.3 + 0.2 * k
        g["kick"] = 0.45 * k
    if inside(bar, GOOD) or inside(bar, PAIR) or inside(bar, ALL17):
        g.update(mar=0.8, piz=0.55, kick=0.6, clap=0.5, pad=0.75, bass=0.95)
    if inside(bar, THIS):
        g.update(mar=1.0, piz=0.7, bsn=0.6, kick=0.85, clap=0.75, pad=1.0, bass=1.1)
    if c == "9" and bar >= THIS[1]:
        g.update(mar=0.6, piz=0.4, kick=0.4, clap=0.3, pad=0.7, bass=0.8)
    if inside(bar, END):
        k = (bar - END[0]) / max(1, END[1] - END[0] - 1)
        g.update(mar=0.6 * (1 - 0.7 * k), piz=0.3 * (1 - k), kick=0.0, clap=0.0, pad=0.9, bass=0.7)
    return g


ARP = (0, 2, 1, 3, 2, 1, 3, 2)


def main():
    s = Song(f"bed_{TAG}", "박수·얼굴 제작기 바탕곡", bpm=T.BPM, bar=4, bars=BARS, swing=0.5, tail=0.0, lufs=-16.0)
    s.N = BARS * BAR_N
    prev = None
    slam_bars = set(SL.values())
    for bar in range(BARS):
        g = plan(bar)
        c = chap(bar)
        gap_bar = c == "4" and bar < b1(bar)          # 4장: 마지막 박을 통째로 비운다
        last = bar == BARS - 1
        B0 = bar * 4
        # 지속 — 비올라 앙상블(조용히). 마지막 박 비움 장에서도 끊지 않는다(곡이 무음이 되면 빈 구간이 깨짐)
        sym0 = chord_at(bar, 0)
        pv = voice(sym0, 53, 69, prev, n=4)
        prev = pv
        for m in pv:
            band.inst(s, "pad", "ViolaEnsSusVib-Quiet", m, B0, (2.75 if gap_bar else 3.9) if not last else 3.4, vel=64, amp=g["pad"], pan=0.0, send=0.3, human=0.0, rel=0.2 if gap_bar else 0.4, attack=0.12)
        for beat in range(4):
            sym = chord_at(bar, beat)
            if gap_bar and beat == 3:
                continue
            # 저음 — 첼로 피치카토(1·3박, 3박은 5도)
            if beat in (0, 2) and g["bass"] > 0 and not last:
                which = "root" if beat == 0 else "fifth"
                band.inst(s, "bass", "CelloEnsPizz", bass_note(sym, 36, 52, which=which), B0 + beat, 1.2, vel=100 if beat == 0 else 84, amp=g["bass"], pan=0.0, send=0.08, human=0.0, rel=0.1)
        # 마림바 8분(마지막 박 비움 장은 앞 6칸만)
        if g["mar"] > 0:
            cv = voice(sym0, 58, 74, None, n=4)
            for k in range(8 if not gap_bar else 6):
                sym_k = chord_at(bar, k // 2)
                v = cv if sym_k == sym0 else voice(sym_k, 58, 74, None, n=4)
                band.inst(s, "mar", "Marimba", v[ARP[k] % len(v)], B0 + k / 2, 0.6, vel=88 if k % 4 == 0 else 72, amp=g["mar"] * (1.0 if k % 2 == 0 else 0.82), pan=-0.18, send=0.16, human=0.0, rel=0.1)
        # 비올라 피치카토 — 뒷박 화음
        if g["piz"] > 0:
            for k in ((1, 3) if not gap_bar else (1,)):
                v = voice(chord_at(bar, k), 57, 72, None, n=3)
                for m in v:
                    band.inst(s, "piz", "ViolaEnsPizz", m, B0 + k, 0.5, vel=80, amp=g["piz"] * 0.6, pan=0.2, send=0.14, human=0.0, rel=0.08)
        # 바순 — 튀어 오르는 넓은 간격
        if g["bsn"] > 0:
            r = bass_note(sym0, 43, 55)
            for k, iv in ((0, 0), (0.75, 12), (1.5, 7), (2.5, 12)):
                if gap_bar and k >= 3:
                    continue
                band.inst(s, "bsn", "BassoonStac", r + iv, B0 + k, 0.45, vel=86, amp=g["bsn"], pan=-0.25, send=0.12, human=0.0, rel=0.06)
        # 실로폰 — 낮은 칸, 2장·5장 번잡할 때만
        if g["xyl"] > 0:
            v = voice(sym0, 67, 79, None, n=3)
            for k in range(6):
                band.inst(s, "xyl", "Xylophone", v[k % len(v)], B0 + 0.25 + k * 0.5, 0.3, vel=70, amp=g["xyl"] * 0.5, pan=0.3, send=0.12, human=0.0, rel=0.06)
        # 타악 — 16분 격자
        if not last:
            for k in range(16):
                b = B0 + k / 4
                if gap_bar and k >= 12:
                    continue
                if k in KICK and g["kick"] > 0:
                    band.perc(s, 36, b, amp=g["kick"], vel=96 if k == 0 else 80, send=0.04, dur=0.5, human=0.0, bus="kick")
                if k in CLAP and g["clap"] > 0:
                    band.perc(s, 39, b, amp=g["clap"], pan=0.05, vel=96, send=0.1, dur=0.4, human=0.0, bus="clap")
        # 슬램 — 팀파니 한 번(역할당 한 명)
        if bar in slam_bars:
            k_fx = 1.0 if bar == SL["N9-8"] else 0.8
            y = band.sample_note("Timpani", 41, 1.4, vel=118, rr=3, release=0.3)
            kk = int(np.argmax(np.abs(y) > 0.15 * np.abs(y).max()))
            s.add("fx", y * k_fx, max(0, s.pos(B0) - kk / SR), send=0.15)
    # 오보에 — 말 없는 구간만
    for span, amp, vel in ((GOOD, 0.85, 82), (PAIR, 0.8, 78), (ALL17, 0.8, 78), (THIS, 1.0, 92), (END, 0.75, 72)):
        for bar in range(span[0], span[1]):
            if bar == BARS - 1:
                continue
            sym = chord_at(bar, 0)
            for t, d, m in line(MEL[sym], start=bar * 4):
                band.inst(s, "oboe", "OboeSusVib", m, t, d * 1.02, vel=vel, amp=amp, pan=0.08, send=0.3, human=0.0, rel=0.3, attack=0.03)
    gains = {"pad": 0.42, "bass": 0.9, "mar": 0.55, "piz": 0.5, "bsn": 0.55, "xyl": 0.4, "kick": 0.55, "clap": 0.4, "oboe": 0.8, "fx": 0.8}
    out = HERE / "out" / TAG
    rep = band.master(s, gains, rev_rt=1.5, rev_wet=0.2, out_dir=out, fade_out=2.2, tp_target=-1.5)
    from scipy.io import wavfile
    sr, x = wavfile.read(out / "mix.wav")
    wavfile.write(out / "bed.wav", SR, x)
    info = {"bars": BARS, "slams": SL, "peak": PEAK, "chapters": CH, "rests": XS, "tp": rep.get("true_peak_db")}
    (out / "report.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: info[k] for k in ("bars", "slams", "peak", "tp")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
