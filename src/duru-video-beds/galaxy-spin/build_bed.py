"""은하 충돌 메이킹 롱폼 바탕곡 — 신작 1곡(2026-11-08). 6/8 ♩.=60 · 1마디 = 2.0s = 60f = 96,000샘플@48k · 8분음표 = 16,000샘플.
마디·슬램·말 없는 구간은 tools/l2_timeline.py place()(TTS 실측 반영)에서 읽는다 — 손으로 적지 않는다.
생각 = 도는 방향을 뒤집는다. 화음 순환을 정방향으로 돌다가 대사 「바꾼 건 은하가 도는 방향이에요」 슬램에서 **같은 화음을 거꾸로** 돌고, 8분음표 아르페지오의 도는 모양도 뒤집는다.
지문(2026-11-08 대장 대조): ORBIT I–♭III–IV–♭VI `[+3,+2,+3,+4]`(Cmaj7–E♭maj7–Fmaj7–A♭maj7) · 그 역행 ORBIT-R ♭VI–IV–♭III–I `[−3,−2,−3,−4]` · 6/8 ♩.60 격자 킥 {0,4}(8분 6칸) + 통나무 북 {3} + 탬버린 흔들기 8분 = ORBIT×K04@68.
역할(이전 메이킹 바탕곡과 다른 음색): 화음 = 파이프 오르간(작게) · 8분 아르페지오 = 클라리넷 스타카토 저음역 · 저음 = 콘트라베이스 지속음 · 선율 = 플루트(말 없는 구간만, 최고 D5) · 강세 = 튜블러 벨 + 팀파니.
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
BAR_N = 96000
E8 = 6      # 마디당 8분음표 수
P = T.place()
BARS = round(P[-1]["t1"] / T.BAR)
ROWS = {r["id"]: r for c in P for r in c["rows"] if r["id"] != "[X]"}
BAR_OF = lambda i: int(round(ROWS[i]["t0"] / T.BAR))
BAR_FLOOR = lambda i: int(ROWS[i]["t0"] // T.BAR)
CH = [(c["ch"].split()[0], round(c["t0"] / T.BAR), round(c["t1"] / T.BAR)) for c in P]
XS = [(c["ch"].split()[0], r["text"], round(r["t0"] / T.BAR), round(r["t1"] / T.BAR)) for c in P for r in c["rows"] if r["id"] == "[X]"]
SL = {k: BAR_OF(k) for k in ("N3-2", "N6-1")}
REST = [(x[2], x[3]) for x in XS if x[0] == "3"][0]                    # 3장 끝 — 말 없음 · 플루트 선율 · 전곡 정점
PAYOFF = [(x[2], x[3]) for x in XS if x[0] == "6" and x[1].startswith("완성본")][0]
END0 = [x[2] for x in XS if x[1].startswith("엔드")][0]
PEAK = REST[0]
EMPTY = (next(a for k, a, _ in CH if k == "5"), BAR_FLOOR("N5-5"))     # 「텅 비어 보였어요」 — 오르간·저음만
FORWARD = ["Cmaj7", "Ebmaj7", "Fmaj7", "Abmaj7"]
RETRO = ["Abmaj7", "Fmaj7", "Ebmaj7", "Cmaj7"]
ST = {"H": 0.5, "1": 0.58, "2": 0.66, "3": 0.72, "4": 0.56, "5": 0.6, "6": 0.74}
KICK = (0, 4)
LOG = (3,)
# 플루트 선율(화음마다 한 마디 · 6/8) — 화음음으로 짜서 평행 진행과 부딪히지 않게. 최고 D5
MEL = {"Cmaj7": "B4:3 G4:1 E4:2", "Ebmaj7": "G4:1 Bb4:2 D5:3", "Fmaj7": "C5:3 A4:3", "Abmaj7": "C5:2 Bb4:1 G4:3"}


def B(bar, e=0.0):
    return bar * E8 + e


def chap(bar):
    return next(k for k, a, b in CH if a <= bar < b)


def a0(bar):
    return next(a for k_, a, _ in CH if k_ == chap(bar))


def chord(bar):
    if bar == BARS - 1 or bar == SL["N6-1"]:
        return "Cmaj7"
    if bar == SL["N3-2"] - 1:
        return "Cmaj7"                                   # 다음 마디 A♭로 — 반음계 3도 이동이 슬램의 색 변화
    if SL["N3-2"] <= bar < REST[1]:
        return RETRO[(bar - SL["N3-2"]) % 4]
    return FORWARD[(bar - a0(bar)) % 4]


def arp_order(bar):
    """8분 6개 — 앞 셋·뒤 셋이 각각 한 바퀴. 슬램부터 3장 끝까지는 도는 모양을 뒤집는다."""
    return (3, 2, 1, 0, 1, 2) if SL["N3-2"] <= bar < REST[1] else (0, 1, 2, 3, 2, 1)


def main():
    s = Song(f"bed_{TAG}", "은하 충돌 메이킹 바탕곡", bpm=T.BPM, bar=E8, bars=BARS, swing=0.5, tail=0.0, lufs=-16.0)
    s.N = BARS * BAR_N
    prev = None
    for bar in range(BARS):
        sym, c = chord(bar), chap(bar)
        g = ST[c]
        slam = bar in SL.values()
        rest = REST[0] <= bar < REST[1]
        pay = PAYOFF[0] <= bar < PAYOFF[1]
        end = bar >= END0
        empty = EMPTY[0] <= bar < EMPTY[1]
        hook = c == "H"
        # 3장: 슬램 뒤 정점까지 조금씩 커진다
        s3 = SL["N3-2"]
        build = c == "3" and s3 < bar < PEAK
        if build:
            g *= 0.9 + 0.32 * (bar - s3) / max(1, PEAK - s3)
        if rest and bar == PEAK:
            g = 1.0
        elif rest:
            g = 0.92
        if pay:
            g = 0.86
        if end:
            g = 0.6
        last = bar == BARS - 1
        # 화음 — 작은 오르간 지속음
        pv = voice(sym, 52, 70, prev, n=4)
        prev = pv
        for m in pv:
            band.inst(s, "organ", "OrganQuiet", m, B(bar), 5.7 if not last else 5.2, vel=72, amp=g * (1.0 if not (slam or rest) else 1.15), pan=0.0, send=0.3, human=0.0, rel=0.35, attack=0.08)
        # 저음 — 콘트라베이스 지속음(점4분마다, 빈 구간은 마디당 한 번)
        r = bass_note(sym, 28, 43)
        for e in ((0,) if empty or last else (0, 3)):
            dur = 5.6 if empty or last else 2.8
            band.inst(s, "bass", "ContrabassSusNV", r, B(bar, e), dur, vel=88 if e == 0 else 76, amp=g * (1.0 if e == 0 else 0.8), pan=0.0, send=0.08, human=0.0, rel=0.25, attack=0.02)
        # 클라리넷 스타카토 아르페지오 — 도는 모양. 훅 앞부분·빈 구간은 쉼
        hook_on = not hook or bar >= BAR_FLOOR("NH-6")
        if hook_on and not empty and not last:
            cv = voice(sym, 57, 74, None, n=4)
            order = arp_order(bar)
            for k in range(E8):
                if slam and k > 2:
                    break                                 # 슬램 마디는 앞 셋만 — 벨·팀파니가 들리게
                band.inst(s, "arp", "ClarinetStac", cv[order[k] % len(cv)], B(bar, k), 0.85, vel=70 if k % 3 == 0 else 58, amp=g * 0.85, pan=-0.28 + 0.1 * k, send=0.22, human=0.0, rel=0.08)
        # 타악 — 1장 끝부터 · 3장 슬램 직전 마디는 쉼(숨) · 빈 구간·마지막 마디 쉼
        pre_slam = bar == SL["N3-2"] - 1
        perc_on = c not in ("H", "1") and not empty and not last and not pre_slam
        if perc_on:
            for k in range(E8):
                b = B(bar, k)
                if k in KICK:
                    band.perc(s, 36, b, amp=0.85 * g, vel=98 if k == 0 else 80, send=0.04, dur=0.5, human=0.0, bus="kick")
                if k in LOG and c != "4":
                    band.perc(s, 77, b, amp=0.7 * g, pan=-0.12, vel=70, send=0.14, dur=0.6, human=0.0, bus="perc")
                if k % 3 == 0 or (rest or pay or c == "2"):
                    band.perc(s, 53, b, amp=(0.5 if k % 3 == 0 else 0.3) * g, pan=0.22, vel=70, send=0.03, dur=0.3, human=0.0, bus="tamb")
        # 슬램: 튜블러 벨 + 팀파니 + 저음 옥타브(역할당 한 명)
        if slam:
            bell = 68 if sym.startswith("Ab") else 72
            y = band.sample_note("TubularBells", bell, 2.4, vel=108, rr=2, release=0.5)
            kk = int(np.argmax(np.abs(y) > 0.15 * np.abs(y).max()))
            k_fx = 1.0 if bar == SL["N3-2"] else 0.6      # 끝 슬램은 3장 정점보다 작게
            s.add("fx", y * 0.9 * k_fx, max(0, s.pos(B(bar)) - kk / SR), send=0.25)
            root_t = 44 if sym.startswith("Ab") else 48
            y = band.sample_note("Timpani", root_t, 1.6, vel=118, rr=3, release=0.3)
            kk = int(np.argmax(np.abs(y) > 0.15 * np.abs(y).max()))
            s.add("fx", y * 1.0 * k_fx, max(0, s.pos(B(bar)) - kk / SR), send=0.15)
    # 플루트 선율 — 3장 끝 말 없는 구간 · 완성본 구간 · 엔드스크린(마지막 마디 전까지 · 간격을 두고)
    for a, b, amp, vel in ((REST[0], REST[1], 1.0, 88), (PAYOFF[0], PAYOFF[1], 0.92, 84), (END0, BARS - 1, 0.7, 72)):
        for bar in range(a, b):
            if a == END0 and (bar - END0) % 2 == 1:
                continue                                  # 엔드스크린 = 한 마디 건너 숨
            for t, d, m in line(MEL[chord(bar)], start=B(bar)):
                band.inst(s, "flute", "FluteSusVib", m, t, d * 1.05, vel=vel, amp=amp, pan=0.12, send=0.3, human=0.0, rel=0.35, attack=0.05)
    gains = {"organ": 0.42, "bass": 0.95, "arp": 0.55, "kick": 0.55, "perc": 0.45, "tamb": 0.35, "fx": 0.75, "flute": 0.7}
    out = HERE / "out" / TAG
    rep = band.master(s, gains, rev_rt=1.8, rev_wet=0.22, out_dir=out, fade_out=1.5, tp_target=-1.5)
    from scipy.io import wavfile
    sr, x = wavfile.read(out / "mix.wav")
    wavfile.write(out / "bed.wav", SR, x)
    info = {"bars": BARS, "slams": SL, "peak": PEAK, "rest": REST, "payoff": PAYOFF, "empty": EMPTY, "end0": END0, "chapters": CH, "tp": rep.get("true_peak_db"), "section": rep.get("section_lufs")}
    (out / "report.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: info[k] for k in ("bars", "slams", "peak", "rest", "payoff", "empty", "end0", "tp")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
