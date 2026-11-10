"""「AI가 만든 T-스핀은 가짜였습니다」 롱폼 바탕곡 — 신작 1곡(S4 · 2026-11-04).

시간축 = L2-장면표 · tools/timeline.json(S5 실측): ♩=90 4/4 · 59마디 = 157.333s = 4,720f@30fps(1마디 80f = 128,000 샘플@48k).
바탕 음악이 멈추는 마디 = 0–3(숏츠 원음) · 41–45(실물리 시연 · 코로베이니키). 슬램 = 3 · 19 · 34. 본 정점 = 38–40 네 번 실패 → 40.0 다섯째 성공.

엔진 = playlist_melty/bgm/band.py 저수준만 import(샘플러·보이싱·버스·master). 화성·선율·편곡은 여기서 새로 쓴다(빌더 포크·화성 이식 금지 캐넌).

생각 = 수사물. 가짜를 파는 동안 A 단조, 진짜를 찾은 순간(40.0) 같은 으뜸음의 A 장조로 풀린다. 1~2장의 밝음은 C 장조 — 나란한 조의 「가짜 안심」.
지문(유사성-지문-스키마 §3):
- 축1 = CASE i–♭II–♭VII–V [+1,−3,−3,+5] · CLIMB i–iiø–♭III–V7 [+2,+1,+4,+5](판정기·정점: 네 번 올라가 다섯째에 으뜸으로 — 시도 횟수와 같은 구조)
  FALSE-UP I–iii–ii–V [+4,−2,+5,+5](거짓 안심) · REAL I–iii–vi–V [+4,+5,−2,+5](진짜) · 하행 꼴 IV–iii–ii–V–I [−1,−2,+5,+5,+5]는 2장(C)과 엔딩(A)에 같은 모양으로.
- 축2 = 쉼표 뒤 위로 도약 → 짧게 반음 내려옴 셀. 단조(G)로 들려주다 엔딩에서 G#로 고쳐 부른다.
- 축3 = K0914: 킥{0,9,14} · 8분 하이햇 · 스트레이트.

역할(마디마다 한 명): 선율 = 클라리넷(대사 틈에만) · 대답 = 바순 스타카토(3-3-2) · 화음 = 현 피치카토 / 첼로 트레몰로 / 하프 / 현 합주 ·
저음 = 콘트라베이스 피치카토(워킹) · 타악 = 킥·림·하이햇 + 합성 틱 · 말렛 = 마림바(체크 12칸) · 실로폰(후보 쏟아짐) · 강세 = 팀파니·트롬본(슬램 한 박).

사용: projects/site-factory/.venv/Scripts/python.exe making_tetris/bgm/build_bed.py [--tag v1]
산출: bgm/out/<tag>/{bed.wav(정지 마스크 적용 · 최종) · mix.wav · stems/ · report.json}
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import sosfilt

HERE = Path(__file__).resolve().parent


sys.path.insert(0, str(HERE.parents[1] / "duru-zoneout-1h"))  # band.py · sfz_sampler.py
sys.path.insert(0, str(HERE.parent))
import band  # noqa: E402
from band import SR, Song, bass_note, h01, line, sos, voice  # noqa: E402
from lufs_spread import integrated_lufs  # noqa: E402

band.OCT["TubularBells"] = -12         # 표기보다 한 옥타브 위로 울림(음원-기법-뱅크 ep38 카드 실측)

TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v1"
BPM, BARS = 90, 59
BAR_N = 128000
PLAY = [(3, 41), (45, 59)]             # 바탕 음악이 나는 마디 [시작, 끝)
LUFS_BED = -16.0


def B(bar, beat=0.0):
    return bar * 4 + beat


# ── 화성(마디, 박, 코드) — 다음 항목 전까지 지속 ───────────────────────────────────────────────
CH = [
    # H 3–6 · CASE — 3 슬램
    (3, 0, "Am"), (4, 0, "Bb"), (4, 2, "G"), (5, 0, "E7sus4"), (5, 2, "E7"),
    # 1장 6–11 · FALSE-UP(C 장조 — 쉽게 올라간다)
    (6, 0, "Cmaj7"), (7, 0, "Em7"), (8, 0, "Dm7"), (9, 0, "G7sus4"), (9, 2, "G7"), (10, 0, "Cmaj7"), (10, 2, "Am7"),
    # 2장 11–15 · 하행 꼴 → 14 거짓 안심
    (11, 0, "Fmaj7"), (12, 0, "Em7"), (13, 0, "Dm7"), (13, 2, "G7"), (14, 0, "Cadd9"),
    # 3장 15–20 · CASE 얇게 → 19 슬램
    (15, 0, "Am"), (16, 0, "Bb"), (17, 0, "G"), (18, 0, "E7"), (19, 0, "Am"),
    # 4장 20–25
    (20, 0, "Fmaj7"), (21, 0, "Dm7"), (22, 0, "Bm7b5"), (23, 0, "E7sus4"), (23, 2, "E7"), (24, 0, "Am"),
    # 5장 25–32 · CLIMB → 30 체크 12칸
    (25, 0, "Am7"), (26, 0, "Bm7b5"), (27, 0, "Cmaj7"), (28, 0, "E7"), (29, 0, "Am7"), (30, 0, "Bm7b5"), (30, 2, "Cmaj7"), (31, 0, "E7sus4"), (31, 2, "E7"),
    # 6장 32–41 · 탐색 → 34 슬램 → 쏟아짐 → 수렴 → 네 번 실패 → 40 다섯째 성공(A 장조)
    (32, 0, "Am"), (33, 0, "Bb"), (33, 2, "E7"), (34, 0, "Am"), (34, 2, "Fmaj7"), (35, 0, "G"), (35, 2, "Am"),
    (36, 0, "Am"), (37, 0, "E7sus4"), (37, 2, "E7"),
    (38, 0, "Am"), (38, 2, "Bm7b5"), (39, 0, "C"), (39, 2, "E7"), (40, 0, "A"),
    # 7장 45–47
    (45, 0, "Dmaj7"), (45, 2, "E7sus4"), (46, 0, "Aadd9"),
    # 8장 47–59 · REAL → 52 주제(장조) → 56 하행 꼴(2장과 같은 모양) → 58 마침
    (47, 0, "A"), (48, 0, "C#m7"), (49, 0, "F#m7"), (50, 0, "E7sus4"), (50, 2, "E7"), (51, 0, "A"),
    (52, 0, "A"), (53, 0, "C#m7"), (54, 0, "F#m7"), (55, 0, "E7sus4"), (55, 2, "E7"),
    (56, 0, "Dmaj7"), (57, 0, "C#m7"), (57, 1, "Bm7"), (57, 2, "E7"), (58, 0, "Aadd9"),
]


def chord_spans():
    out = []
    for i, (bar, bt, sym) in enumerate(CH):
        b0 = B(bar, bt)
        nxt = B(*CH[i + 1][:2]) if i + 1 < len(CH) else B(BARS)
        end = next(B(e) for s, e in PLAY if s <= bar < e)
        out.append((b0, min(nxt, end), sym))
    return out


SPANS = chord_spans()


def chord_at(b):
    for b0, b1, sym in SPANS:
        if b0 <= b < b1:
            return sym
    return None


def spans_in(bar):
    return [(b0, b1, sym) for b0, b1, sym in SPANS if B(bar) <= b0 < B(bar + 1)]


# ── 편곡표 — 마디: (타악, 화음, 저음, 셈여림) ─────────────────────────────────────────────────
# 타악: 0 없음 · 1 틱만 · 2 햇+림(12) · 3 킥+햇+림(4·12)
# 화음: "pz2" 피치카토 0·10 · "pz4" 피치카토 0·6·10·14 · "trem" 첼로 트레몰로 · "pad" 현 합주 · "harp" 하프 8분 · "" 없음
# 저음: "w" 워킹 · "l" 긴 음 · "" 없음
ARR = {
    3: (1, "trem", "l", 0.70), 4: (2, "pz2", "w", 0.72), 5: (2, "pz2", "w", 0.75),                # H 긴장 — 대사가 빽빽해 화음 리듬만
    6: (3, "pz2", "w", 0.80), 7: (3, "pz2", "w", 0.80), 8: (3, "pz2", "w", 0.82), 9: (3, "pz4", "w", 0.85), 10: (3, "pz4", "w", 0.85),   # 1장 만든 방법
    11: (2, "pz2", "w", 0.68), 12: (2, "pz2", "w", 0.68), 13: (2, "pz2", "w", 0.72), 14: (2, "pz4", "w", 0.66),   # 2장 → 거짓 안심
    15: (1, "trem", "l", 0.50), 16: (1, "trem", "l", 0.55), 17: (1, "trem", "l", 0.60), 18: (1, "trem", "l", 0.68),   # 3장 어둡게 얇게
    19: (0, "trem", "l", 0.70),
    20: (0, "pad", "l", 0.48), 21: (0, "pad", "l", 0.48), 22: (0, "pad", "l", 0.50), 23: (0, "pad", "l", 0.52), 24: (0, "pad", "l", 0.55),   # 4장 왜 몰랐을까
    25: (1, "pz2", "l", 0.58), 26: (2, "pz2", "w", 0.62), 27: (2, "pz2", "w", 0.66), 28: (3, "pz2", "w", 0.72), 29: (3, "pz2", "w", 0.76),
    30: (3, "pz4", "w", 0.82), 31: (3, "pz4", "w", 0.86),                                          # 5장 판정기
    32: (1, "trem", "l", 0.68), 33: (1, "trem", "l", 0.78),                                        # 6장 탐색 — 틱이 빨라진다
    34: (2, "", "l", 0.88), 35: (3, "pz4", "w", 0.88), 36: (1, "trem", "l", 0.66), 37: (1, "trem", "l", 0.74),   # 슬램 → 쏟아짐 → 수렴
    38: (0, "", "", 1.0), 39: (0, "", "", 1.0), 40: (0, "", "", 1.0),                              # 본 정점 = accents()
    45: (0, "pad", "l", 0.48), 46: (0, "pad", "l", 0.54),                                          # 7장 끝
    47: (1, "harp", "l", 0.50), 48: (2, "harp", "w", 0.54), 49: (2, "harp", "w", 0.56), 50: (2, "harp", "w", 0.58), 51: (3, "harp", "w", 0.60),   # 8장 드립니다
    52: (3, "harp", "w", 0.64), 53: (3, "harp", "w", 0.64), 54: (3, "harp", "w", 0.66), 55: (3, "harp", "w", 0.66),   # 엔드스크린 주제
    56: (3, "harp", "w", 0.66), 57: (3, "harp", "w", 0.60), 58: (0, "pad", "l", 0.50),              # 하행 꼴 → 마침
}


def dyn(b):
    return ARR.get(int(b // 4), (0, "", "", 1.0))[3]


# ── 합성 틱(이 곡 전용) — 시계처럼 째깍. 샘플이 아니라 짧은 공진 ───────────────────────────────
def tick(vel, hi):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    f = 2300 if hi else 1700
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.009) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.004)
    return sosfilt(sos(600, "highpass"), y) * vel * 0.5


def hit(s, bus, name, m, b, dur_b, vel, amp, pan=0.0, send=0.3, rel=0.3, th=0.1, norm=None, attack=0.0):
    """박에 소리가 오도록 샘플 앞 여백(피크 th 도달까지)만큼 당겨 놓는다 — 슬램과 피치카토. 어택이 느린 금관·합주 피치카토는 th=0.3.
    norm = 첫 0.2s RMS 를 이 값에 맞춘다 — 샘플이 음높이마다 크기가 달라(클라리넷 C#6 +9dB · 콘트라베이스 C·G +6dB) 마디 음량이 튄다."""
    y = band.sample_note(name, m, dur_b * s.beat, vel=vel, rr=int(h01(b, m) * 9) + 1, release=rel, attack=attack)
    e = np.abs(y).max(axis=-1) if y.ndim == 2 else np.abs(y)
    k = int(np.argmax(e > th * e.max()))
    if norm:
        y = y / (np.sqrt(np.mean(y[k:k + int(0.2 * SR)] ** 2)) + 1e-9) * norm
    s.add(bus, y * amp, max(0.0, s.pos(b) - k / SR), pan=pan, send=send)


# ── 성부 ───────────────────────────────────────────────────────────────────────────────────
def drums(s):
    for bar, (lv, _, _, _) in ARR.items():
        if lv == 0:
            continue
        for k in range(16):
            b = B(bar, k / 4)
            g = dyn(b)
            if lv == 1:
                step = 1 if bar == 33 else 2                     # 33마디는 16분으로 — 34 슬램까지 조인다
                if k % step == 0:
                    s.add("perc", tick(0.9 if k % 4 == 0 else 0.6, k % 8 == 0), s.pos(b), pan=0.2, gain=g, send=0.05)
                continue
            if k % 2 == 0:
                band.perc(s, 42, b, amp=(0.85 if k % 4 == 0 else 0.6) * g, pan=0.22, vel=70, send=0.03, dur=0.2)
            if k == 12 or (lv >= 3 and k == 4):
                band.perc(s, 37, b, amp=0.8 * g, pan=-0.08, vel=74, send=0.1, dur=0.4)
            if lv >= 3 and k in (0, 9, 14):
                band.perc(s, 36, b, amp=(1.0 if k == 0 else 0.72) * g, vel=88, send=0.0, dur=0.5, bus="kick")


def bass(s):
    for bar, (_, _, st, _) in ARR.items():
        if st == "l":
            for b0, b1, sym in spans_in(bar):
                hit(s, "bass", "ContrabassPizz", bass_note(sym, 33, 50), b0, min((b1 - b0), 4) * 0.95, 84, dyn(b0), send=0.08, rel=0.2, th=0.3, norm=0.10)
        elif st == "w":
            sp = spans_in(bar)
            nxt = chord_at(B(bar + 1)) or sp[-1][2]
            nr = bass_note(nxt, 36, 50)
            for j, (b0, b1, sym) in enumerate(sp):
                r, fifth = bass_note(sym, 33, 48), bass_note(sym, 33, 48, "fifth")
                beats = int(round(b1 - b0))
                seq = {4: [r, fifth, r + 12 if r + 12 <= 50 else r, nr - 1 if nr - 1 >= 33 else nr + 1],
                       3: [r, fifth, nr + 1], 2: [r, fifth], 1: [r]}[beats]
                if beats == 2 and j == len(sp) - 1:
                    seq = [r, nr - 1 if nr - 1 >= 33 else nr + 1]
                for i, m in enumerate(seq):
                    hit(s, "bass", "ContrabassPizz", m, b0 + i, 0.9, 92 if i == 0 else 78, dyn(b0) * (1.0 if i == 0 else 0.8), send=0.08, rel=0.12, th=0.3, norm=0.10)


def harmony(s):
    prev = {}
    for bar, (_, st, _, _) in sorted(ARR.items()):
        for b0, b1, sym in spans_in(bar):
            g = dyn(b0)
            if st in ("pz2", "pz4"):
                pts = {"pz2": (0, 10), "pz4": (0, 6, 10, 14)}[st]
                hits = [B(bar, k / 4) for k in pts if b0 <= B(bar, k / 4) < b1] or [b0]
                for b in hits:
                    v = voice(sym, 57, 74, prev.get("pz"), n=3)
                    prev["pz"] = v
                    for i, m in enumerate(v):
                        name = "ViolinEnsPizz" if m >= 65 else "ViolaEnsPizz"
                        hit(s, "harm", name, m, b + i * 0.012, 0.9, 84, g, pan=-0.3 + 0.3 * i, send=0.2, rel=0.2, th=0.3)
            elif st == "trem":
                v = voice(sym, 45, 62, prev.get("tr"), n=3)
                prev["tr"] = v
                for i, m in enumerate(v):
                    name = "CelloEnsTrem" if m < 57 else "ViolaEnsTrem"
                    band.inst(s, "pad", name, m, b0, (b1 - b0) * 0.98, vel=72, amp=g, pan=-0.3 + 0.3 * i, send=0.3, human=0.0, rel=0.4, attack=0.12)
            elif st == "pad":
                v = voice(sym, 55, 74, prev.get("pad"), n=4)
                prev["pad"] = v
                for i, m in enumerate(v):
                    name = "CelloEnsSusVib-Quiet" if m < 60 else ("ViolaEnsSusVib-Quiet" if m < 67 else "ViolinEnsSusVib-Quiet")
                    band.inst(s, "pad", name, m, b0, (b1 - b0) * 0.97, vel=68, amp=g, pan=-0.4 + 0.27 * i, send=0.32, human=0.0, rel=0.45, attack=0.28)
            elif st == "harp":
                v = voice(sym, 57, 80, prev.get("hp"), n=4)
                prev["hp"] = v
                order = (0, 2, 1, 3, 2, 3, 1, 2)
                for k in range(int(round((b1 - b0) * 2))):
                    b = b0 + k * 0.5
                    i = order[int((b - B(bar)) * 2) % 8] % len(v)
                    band.inst(s, "harp", "Harp", v[i], b, 1.6, vel=70 if k % 2 == 0 else 58, amp=g, pan=-0.25 + 0.17 * i, send=0.3, rel=0.5)


# 선율 — 대사 틈에만(실측 줄 끝을 주석에). 같은 셀을 G로 부르다 46부터 G#.
LEAD = [
    (14, 1, "G4:.5 C5:1 B4:.5 G4:1"),                             # N2-3 끝 14.18 → 거짓 안심(C 장조)
    (24, 0, "r:.5 E5:.5 A5:1.5 G5:.5 E5:1"),                      # N4-4 끝 23.95 → 단조 셀
    (40, 2, "E5:.5 A5:1.5"),                                      # 다섯째 성공 뒤 — 장조로 처음 올라가는 두 음
    (46, 0, "r:.5 E5:.5 A5:1.5 G#5:.5 E5:1"),                     # N7-1 끝 46.07 → 같은 셀을 G#로 고쳐 부름
    (51, 2, "A4:.5 C#5:.5 E5:1"),                                 # N8-3 끝 51.16 → 주제 예고
    (52, 0, "r:.5 E5:.5 A5:1.5 G#5:.5 E5:1"),                     # 엔드스크린 주제
    (53, 0, "r:.5 E5:.5 B5:1.5 G#5:.5 E5:1"),
    (54, 0, "r:.5 F#5:.5 C#6:1.5 B5:.5 A5:1"),
    (55, 0, "B5:1 A5:.5 G#5:.5 F#5:1 E5:1"),
    (56, 0, "r:.5 F#5:.5 A5:.5 C#6:1 B5:.5 A5:1"),
    (57, 0, "G#5:1 F#5:1 G#5:.5 E5:.5 B4:.5 D5:.5"),
    (58, 0, "C#5:1 A4:3"),
]
# 대답 — 바순 스타카토 3-3-2. 대사 아래 낮은 음역으로 기어간다.
RESP = [
    (15, 0, "A3:.5 r:1 C4:.5 r:1 E4:.5 r:.5"),
    (16, 0, "Bb3:.5 r:1 D4:.5 r:1 F4:.5 r:.5"),
    (17, 0, "G3:.5 r:1 B3:.5 r:1 D4:.5 r:.5"),
    (18, 0, "E3:.5 r:1 G#3:.5 r:1 D4:.5 E4:.5"),
    (32, 0, "A3:.5 r:1 C4:.5 r:1 E4:.5 r:.5"),
    (33, 0, "Bb3:.5 r:1 D4:.5 r:.5 E3:.5 r:.5 G#3:.5"),
]
# 말렛 — 마림바: 테스트 12칸 = 8분 12개(30.0–31.5) · 실로폰: 후보 72개가 쏟아질 때 16분(34.5–35.5)
CHECKS = "A4 B4 C5 D5 E5 F5 G5 A5 B5 C6 D6 E6".split()
FLOOD = "A5 C6 E6 A6 F5 A5 C6 F6 G5 B5 D6 G6 A5 C6 E6 A6".split()


def melody(s):
    for bar, bt, txt in LEAD:
        for b, d, m in line(txt, start=B(bar, bt)):
            assert b + d <= B(bar + 1) + 1e-6, (bar, txt)
            vel = 70 if bar == 58 else (82 if bar >= 52 or bar == 40 else 66)
            hit(s, "lead", "ClarinetSus", m, b, d * 0.96, vel, dyn(b), pan=0.15, send=0.28, rel=0.22, norm=0.10, attack=0.012)
    for bar, bt, txt in RESP:
        for b, d, m in line(txt, start=B(bar, bt)):
            assert b + d <= B(bar + 1) + 1e-6, (bar, txt)     # 악보 줄이 제 마디를 넘으면 다음 다운비트를 더럽힌다
            band.inst(s, "resp", "BassoonStac", m, b, d, vel=78, amp=dyn(b), pan=-0.18, send=0.2, rel=0.1)
    for i, n in enumerate(CHECKS):
        b = B(30, i * 0.5)
        band.inst(s, "mari", "Marimba", band.nm(n), b, 0.8, vel=62 + i * 2, amp=dyn(b), pan=-0.3 + 0.05 * i, send=0.18, rel=0.2)
    for i, n in enumerate(FLOOD):
        b = B(34, 2 + i * 0.25)
        band.inst(s, "xylo", "Xylophone", band.nm(n), b, 0.4, vel=60, amp=dyn(b), pan=0.3 * math.sin(i), send=0.2, rel=0.12)


def roll(s, bar_to, midi, amp):
    """다음 다운비트 0.05s 앞에서 끊는다 — 짧은 숨이 타격을 세운다."""
    y = band.sample_note("TimpaniRolls", midi, 2 * s.beat, vel=100, rr=1, release=0.01)
    k = int(2 * s.beat * SR)
    s.add("fx", y[:k] * np.geomspace(0.12, 1.0, k) * amp * np.minimum(1, (k - np.arange(k)) / (0.01 * SR)), s.pos(B(bar_to)) - k / SR - 0.05, pan=0.0, send=0.12)


def stab(s, bar, beat, sym, amp, timp, ta, dur=1.3):
    """트롬본·호른 화음 + 팀파니 한 번(슬램·시도). 낮게 묶어 대사 음역을 비운다."""
    b = B(bar, beat)
    hit(s, "fx", "Timpani", timp, b, 1.5 / s.beat, 118, ta, send=0.15, rel=0.4)
    v = voice(sym, 45, 64, None, n=3)
    for i, m in enumerate(v):
        name = "TromboneSus" if m < 58 else "FHornSus"
        hit(s, "stab", name, m, b, dur, 96, amp, pan=-0.2 + 0.2 * i, th=0.3)


def accents(s):
    # 슬램 셋 — 대사 다운비트(NH-2 · N3-5 · N6-3)
    stab(s, 3, 0, "Am", 0.30, 45, 0.70)
    roll(s, 19, 45, 0.5)
    stab(s, 19, 0, "Am", 0.35, 45, 0.85)
    roll(s, 34, 45, 0.6)
    stab(s, 34, 0, "Am", 0.40, 45, 0.95)
    # 본 정점 — 킥 시도 넷(화음이 네 번 올라간다) · 다섯째 = 40.0 A 장조
    roll(s, 38, 45, 0.7)
    for (bar, beat, sym, timp), amp in zip([(38, 0, "Am", 45), (38, 2, "Bm7b5", 47), (39, 0, "C", 48), (39, 2, "E7", 52)], (0.8, 0.88, 0.96, 1.04)):
        stab(s, bar, beat, sym, amp, timp, amp, dur=1.6)
    roll(s, 40, 52, 0.8)
    hit(s, "fx", "Timpani", 45, B(40), 2.0 / s.beat, 127, 1.15, send=0.15, rel=0.5)
    band.inst(s, "fx", "TubularBells", 69, B(40), 3.0, vel=115, amp=1.0, pan=0.1, send=0.3, human=0.0, rel=1.2)
    band.perc(s, 49, B(40), amp=0.8, vel=110, dur=2.6, send=0.2, bus="fx")
    for m in (33, 45, 52, 57):
        hit(s, "slam", "TromboneSus" if m >= 40 else "TubaSus", m, B(40), 3.4, 108, 1.1, pan=-0.15, rel=0.5)
    for m in (61, 64, 69):
        hit(s, "slam", "FHornSus", m, B(40), 3.4, 104, 1.1, rel=0.5)
    for m in (69, 73, 76, 81):
        band.inst(s, "slam", "ViolinEnsSusVib", m, B(40), 3.6, vel=100, amp=0.9, pan=0.25, send=0.32, human=0.0, rel=0.5, attack=0.02)
    # 마침 — 벨 한 번
    band.inst(s, "fx", "TubularBells", 69, B(58), 3.0, vel=70, amp=0.22, pan=0.1, send=0.35, human=0.0, rel=1.5)


# 1차 --bus 표 기준 교정: 베이스 +10 · 킥 −6 · 하프 +8 · 바순 +6 · 실로폰 −5 · 시도 스탭 +10 dB
GAINS = {"lead": 0.75, "resp": 0.50, "harm": 0.30, "harp": 0.75, "pad": 0.20, "bass": 1.00, "kick": 0.18, "perc": 0.55, "mari": 0.50, "xylo": 0.12, "fx": 0.85, "slam": 0.16, "stab": 0.50}
SECTIONS = [("H", 3, 3), ("1", 6, 5), ("2", 11, 4), ("3", 15, 4), ("S19", 19, 1), ("4", 20, 5), ("5", 25, 7), ("6a", 32, 2), ("S34", 34, 2), ("6b", 36, 2),
            ("KICK", 38, 2), ("PEAK", 40, 1), ("7", 45, 2), ("8", 47, 5), ("END", 52, 6), ("LAST", 58, 1)]


def stop_mask(n):
    m = np.zeros(n)
    for a, b in PLAY:
        i0, i1 = a * BAR_N, b * BAR_N
        m[i0:i1] = 1.0
        f = int((1.0 if b == BARS else 0.15) * SR)
        m[i1 - f:i1] *= np.linspace(1, 0, f) ** 2
    return m


def main():
    s = Song(f"bed_{TAG}", "T-스핀 롱폼 바탕곡", bpm=BPM, bar=4, bars=BARS, swing=0.5, tail=0.0, lufs=LUFS_BED)
    s.N = BARS * BAR_N
    for name, b0, nb in SECTIONS:
        s.section(name, b0, nb)
    drums(s)
    bass(s)
    harmony(s)
    melody(s)
    accents(s)
    out = HERE / "out" / TAG
    rep = band.master(s, GAINS, rev_rt=1.5, rev_wet=0.2, out_dir=out, tp_target=-1.5)
    sr, x = wavfile.read(out / "mix.wav")
    x = x.astype(np.float64) / 32768.0
    y = x * stop_mask(len(x))[:, None]
    g = 10 ** ((LUFS_BED - integrated_lufs(y, SR)) / 20)
    y *= g
    tp = band.true_peak_db(y)
    wavfile.write(out / "bed.wav", SR, (np.clip(y, -1, 1) * 32767).astype(np.int16))
    sec = {}
    for name, b0, nb in SECTIONS:
        v = integrated_lufs(y[b0 * BAR_N:(b0 + nb) * BAR_N], SR)
        sec[name] = round(v, 2) if v is not None else None
    fin = {"bed_lufs": round(integrated_lufs(y, SR), 2), "bed_true_peak_db": round(tp, 2), "post_mask_gain_db": round(20 * math.log10(g), 2),
           "samples": len(y), "frames_30fps": len(y) / SR * 30, "section_lufs_bs1770": sec}
    rep.update(fin)
    (out / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(fin, ensure_ascii=False))


if __name__ == "__main__":
    main()
