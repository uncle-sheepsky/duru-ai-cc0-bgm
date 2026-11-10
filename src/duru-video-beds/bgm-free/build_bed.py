"""「BGM 만들고 무료로 드립니다」 롱폼 바탕곡 — 신작 1곡(S4 · 2026-11-01).

시간축 = 장면표 L2 §6 B안 · §2-B-4(S5 실측 재배치): ♩=90 4/4 · 83마디 = 221.333s = 6,640f@30fps(1마디 80f = 128,000 샘플@48k).
바탕 음악이 멈추는 마디 = 0–3 · 14–20 · 25–31 · 38–44 · 50–56 · 57–63(16곡 맛보기·발췌 자리). 48 = 정점 슬램 · 66 = 2차 상승.

엔진 = `playlist_melty/bgm/band.py` 저수준만 import(샘플러·보이싱·버스·master·--bus 표). 화성·선율·편곡·합성 음색은 전부 여기서 새로 쓴다
(빌더 포크·화성 이식 금지 캐넌 · band.py 의 16곡 전용 합성 악기 — 카주·휘파람·오르골·첼레스타·스틸팬·리드·퐁·보잉 — 미사용).

지문(유사성-지문-스키마 §3):
- 축1 = GIFT-DESC: I–vi7–♭VImaj7–V7(sus) 루트운동 [−3,−1,−1,+5] — vi에서 V까지 베이스가 반음 둘로 내려앉는다(♭VI 차용).
  보조 진행 = IVmaj7–I/3–ii7–V7sus [−5,+2,+5,−2](설명 구간) · 마침 = IV–♭VI–I(아이올리안 플래갈).
- 축2b = 지그재그 상승 셀(D U D U)을 마디마다 한 음씩 높여 반복(Tₖ 순차) + 호른이 거울(하행)로 대답. 코드톤 아치 회피.
- 축3 = K07: 킥{0,7}(1박 · 2박의 넷째 16분) + 스네어 탭 백비트{4,12} + 16분 셰이커(엇8분 강세) · 스트레이트.
- 66마디 D → E 장2도 전조(2차 상승).

역할(마디마다 한 명): 선율 = 비브라폰(신작 합성) · 대답 = 호른(VSCO FHornSus) · 화음 = 전자 피아노(신작 FM 합성) 또는 현 합주 패드(VSCO) ·
저음 = 둥근 베이스(신작 합성) · 타악 = 쿠션 킥(신작 합성) + 스네어 탭·셰이커 · 강세 = 팀파니 롤·튜블러 벨·심벌(슬램 한 박에만 겹침).
선율은 내레이션 틈(장면표 §2-B-4 실측 시각)에만 — 대사 위에는 깔개만 둔다.

사용: projects/site-factory/.venv/Scripts/python.exe making_playlist/bgm/build_bed.py [--tag v1] [--bus]
산출: bgm/out/<tag>/{bed.wav(정지 마스크 적용 · 최종) · mix.wav(master 원본) · stems/ · report.json}
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
from band import SR, Song, bass_note, h01, line, m2f, sos, voice  # noqa: E402
from lufs_spread import integrated_lufs  # noqa: E402  BS.1770-4 직접 구현(selftest 있음)

band.OCT["TubularBells"] = -12        # 표기보다 한 옥타브 위로 울림(음원-기법-뱅크 ep38 카드 FFT 실측 +1212c)

TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v1"
BPM, BARS = 90, 83
BAR_N = 128000                         # 1마디 샘플(48k) — 2.6667s · 80f
PLAY = [(3, 14), (20, 25), (31, 38), (44, 50), (56, 57), (63, 83)]   # 바탕 음악이 나는 마디 [시작, 끝)
LUFS_BED = -16.0                       # 바탕곡 단독 정규화 목표(믹스에서는 고정 이득 1개만 곱한다)


def B(bar, beat=0.0):
    return bar * 4 + beat


# ── 화성(마디, 박, 코드) — 다음 항목 전까지 지속. 정지 구간 앞 마디는 3박에서 마침(I)으로 착지 ─────────────
CH = [
    # H 훅 3–7 · 강 — GIFT-DESC
    (3, 0, "D"), (4, 0, "Bm7"), (5, 0, "Bbmaj7"), (6, 0, "A7sus4"), (6, 2, "A7"),
    # C 7–14 · 휴 → 중 — 보조 진행(설명) · 12 = 개그 ① 깊은 잠 · 13 마침
    (7, 0, "Gmaj7"), (8, 0, "D/F#"), (9, 0, "Em7"), (10, 0, "A7sus4"), (10, 2, "A7"),
    (11, 0, "Bm7"), (11, 2, "Bm7/A"), (12, 0, "Gmaj7"), (13, 0, "Em7"), (13, 2, "A7"), (13, 3, "D"),   # 12: 5음 코드는 voice(n=4)가 3음을 떨어뜨린다 → 4음만
    # M1 20–25 · 중 — 22 = 개그 ② 큰 ?(풀리지 않는 sus) · 23 M2 진입 · 24 마침
    (20, 0, "Bm7"), (21, 0, "Gmaj7"), (21, 2, "F#m7"), (22, 0, "E7sus4"),
    (23, 0, "Gmaj7"), (23, 2, "A7sus4"), (24, 0, "Em7"), (24, 2, "A7"), (24, 3, "D"),
    # M2 31–38 · 중
    (31, 0, "Gmaj7"), (32, 0, "D/F#"), (33, 0, "Em7"), (34, 0, "A7sus4"), (34, 2, "A7"),
    (35, 0, "Bm7"), (35, 2, "Bm7/A"), (36, 0, "Gmaj7"), (36, 2, "F#m7"), (37, 0, "Em7"), (37, 2, "A7"), (37, 3, "D"),
    # M3 44–50 · 중 → 강 — 딸림 페달 빌드 → 48 슬램(I) → 49 여운 마침
    (44, 0, "Gmaj7/A"), (45, 0, "Em7/A"), (46, 0, "F#m7/A"), (47, 0, "Gmaj7/A"), (47, 2, "A7"),
    (48, 0, "Dadd9"), (48, 2, "Bm7"), (49, 0, "Bbmaj7"), (49, 2, "A7"), (49, 3, "D"),
    # M4 56 · 휴 — 한 마디 ♭VI → I
    (56, 0, "Bbmaj7"), (56, 2, "Dadd9"),
    # G 63–71 · 중 — D 에서 주제 → 65 후반 B7sus4 피벗 → 66 E 장조(2차 상승)
    (63, 0, "D"), (64, 0, "Bm7"), (65, 0, "Bbmaj7"), (65, 2, "B7sus4"),
    (66, 0, "Eadd9"), (67, 0, "C#m7"), (68, 0, "Cmaj7"), (69, 0, "B7sus4"), (69, 2, "B7"), (70, 0, "Amaj7"), (70, 2, "B7"),
    # E 71–83 · 휴 — 잦아듦 · 76–81 자장가 재현(I–iii–♭VI–V) · 마침 IV–♭VI–I
    (71, 0, "Eadd9"), (72, 0, "C#m7"), (73, 0, "Amaj7"), (74, 0, "B7sus4"), (74, 2, "B7"), (75, 0, "E"), (75, 2, "E/G#"),
    (76, 0, "E"), (77, 0, "G#m7"), (78, 0, "Cmaj7"), (79, 0, "B7"), (80, 0, "Amaj7"), (81, 0, "Cmaj7"), (82, 0, "Eadd9"),
]
band.QUAL.setdefault("add9", (0, 4, 7, 14))


def chord_spans():
    """[(b0, b1, sym)] 박 단위. 정지 구간 경계에서 끊는다."""
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


# ── 편곡표 — 마디마다 (타악 단계, 화음 악기·꼴, 저음 꼴) ─────────────────────────────────────────────
# 타악: 0 없음 · 1 셰이커만 · 2 탭+셰이커 · 3 킥+탭+셰이커(K07) · 4 정점(K07 + 셰이커 강세 강하게)
# 화음: "ep2" 전자피아노 두 번(0·10) · "ep4" 네 번(0·6·10·14) · "pad" 현 합주 · "hold" 마디 전체 한 번 · "" 없음
# 저음: "g" 그루브(0·7·10) · "l" 긴 음(코드마다 하나) · "" 없음
ARR = {}
for bar in range(3, 7):
    ARR[bar] = (3, "ep4", "g")                                    # H 강 — 대사가 이어져 선율 대신 화음 리듬(네 번)이 몸을 만든다
for bar, v in {7: (0, "pad", "l"), 8: (0, "pad", "l"), 9: (1, "pad", "l"), 10: (1, "pad", "l"),
               11: (2, "ep2", "g"), 12: (0, "pad", "l"), 13: (2, "ep2", "g")}.items():
    ARR[bar] = v                                                  # C 휴 → 중 · 12 개그 ① 최소 편성
for bar, v in {20: (2, "ep2", "g"), 21: (2, "ep2", "g"), 22: (0, "hold", "l"), 23: (3, "ep2", "g"), 24: (3, "ep2", "g")}.items():
    ARR[bar] = v                                                  # M1 · 22 개그 ② 최소 편성
for bar in range(31, 38):
    ARR[bar] = (3 if bar >= 33 else 2, "ep2", "g")               # M2 중
for bar, v in {44: (1, "ep2", "l"), 45: (2, "ep2", "l"), 46: (2, "ep2", "l"), 47: (3, "ep4", "g"),
               48: (4, "ep4", "g"), 49: (4, "ep4", "g")}.items():
    ARR[bar] = v                                                  # M3 빌드 → 슬램 → 여운
ARR[56] = (0, "hold", "l")                                        # M4 휴 한 마디
for bar in range(63, 66):
    ARR[bar] = (3, "ep2", "g")                                    # G 따뜻하게
for bar in range(66, 71):
    ARR[bar] = (3, "ep4", "g")                                    # G 2차 상승(전조) — 대사 뒤 68–70 선율 무대
for bar, v in {71: (2, "ep2", "g"), 72: (1, "ep2", "l"), 73: (0, "pad", "l"), 74: (0, "pad", "l"), 75: (0, "pad", "l")}.items():
    ARR[bar] = v                                                  # E 잦아듦
for bar in range(76, 83):
    ARR[bar] = (0, "pad" if bar >= 80 else "ep2", "l")             # 엔드스크린 자장가 재현 → 82 마침

# 셈여림(마디별 음량 배수 — 편곡의 일부, 대사에 반응하지 않는 고정 악보값). 아크 = 장면표 §6 B안 에너지 열.
DYN = {**{b: 1.0 for b in range(3, 7)},                          # H 강
       **{b: 0.62 for b in range(7, 11)}, 11: 0.7, 12: 0.5, 13: 0.8,   # C 휴 → 중
       **{b: 0.85 for b in range(20, 25)}, 22: 0.6,               # M1 · 개그 ②
       **{b: 0.85 for b in range(31, 38)},                        # M2
       44: 0.8, 45: 0.85, 46: 0.9, 47: 1.0, 48: 1.05, 49: 0.9,     # M3 빌드 → 정점 → 여운
       56: 0.65,                                                  # M4 휴
       63: 0.88, 64: 0.9, 65: 0.92, 66: 0.92, 67: 0.9, **{b: 0.72 for b in range(68, 71)},   # G 따뜻하게 → 2차 상승(정점보다 한 단계 아래)
       71: 0.75, 72: 0.68, 73: 0.5, 74: 0.55, 75: 0.55,           # E 잦아듦
       **{b: 0.5 for b in range(76, 82)}, 82: 0.3}                # 엔드스크린 자장가 → 마침


def dyn(b):
    return DYN.get(int(b // 4), 1.0)


# ── 신작 합성 음색(이 곡 전용) ─────────────────────────────────────────────────────────────────────
def adsr_tail(n, a, dur_n, rel):
    e = np.ones(n)
    ka = min(n, max(1, int(a * SR)))
    e[:ka] = np.linspace(0, 1, ka) ** 1.5
    kr = int(rel * SR)
    if dur_n < n:
        k1 = min(n, dur_n + kr)
        e[dur_n:k1] *= np.linspace(1, 0, k1 - dur_n) ** 2
        e[k1:] = 0
    return e


def vibes(midi, dur, vel=0.8, motor=5.4, depth=0.28, ring=0.9, phase=0.0):
    """비브라폰: 막대 모드(1 · 4 · 10배) + 공명관이 키우는 기음에만 모터 트레몰로 + 말렛 툭. 댐퍼는 dur+ring 에서 내린다."""
    f = m2f(midi)
    hold = dur + ring
    n = int((hold + 0.25) * SR)
    t = np.arange(n) / SR
    trem = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * motor * t + phase))
    fund = np.sin(2 * np.pi * f * t) * np.exp(-t / 2.4) * trem
    y = fund + (0.10 + 0.10 * vel) * np.sin(2 * np.pi * 4.0 * f * t) * np.exp(-t / 0.32)
    if 10 * f < 16000:
        y += 0.03 * vel * np.sin(2 * np.pi * 10.0 * f * t) * np.exp(-t / 0.05)
    k = int(0.004 * SR)
    seed = int(midi * 7 + vel * 100)
    thump = sosfilt(sos(2200, "lowpass"), np.random.default_rng(seed).standard_normal(k)) * np.linspace(1, 0, k)
    y[:k] += 0.25 * vel * thump
    return y * adsr_tail(n, 0.0015, int(hold * SR), 0.22) * (0.35 + 0.65 * vel) * 0.5


def epiano(midi, dur, vel=0.7):
    """전자 피아노(FM 톤바): 1:1 변조 지수가 어택에서 빨리 줄고, 높은 '팅' 부분음이 짧게 붙는다."""
    f = m2f(midi)
    n = int((dur + 0.35) * SR)
    t = np.arange(n) / SR
    idx = (0.9 + 1.8 * vel) * np.exp(-t / 0.28) + 0.25
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    if 14 * f < 15000:
        y += 0.10 * vel * np.sin(2 * np.pi * 14 * f * t) * np.exp(-t / 0.018)
    y *= np.exp(-t / 2.2)
    y = sosfilt(sos(5200, "lowpass"), y)
    return y * adsr_tail(n, 0.002, int(dur * SR), 0.14) * (0.4 + 0.6 * vel) * 0.32


def round_bass(midi, dur, vel=0.8):
    """둥근 베이스: 사인 + 약한 2·3배음(작은 스피커에서도 음정이 들리게) + 어택에만 밝은 톱니."""
    f = m2f(midi)
    n = int((dur + 0.1) * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    body = np.sin(ph) + 0.28 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    saw = 2 * ((f * t) % 1.0) - 1
    pluck = sosfilt(sos(900, "lowpass"), saw) * np.exp(-t / 0.045) * 0.5
    env = 0.72 + 0.28 * np.exp(-t / 0.35)
    return (body * env + pluck) * adsr_tail(n, 0.004, int(dur * SR), 0.07) * (0.5 + 0.5 * vel) * 0.45


def cushion_kick(vel=0.8):
    """쿠션 킥: 115 → 54Hz 낮은 쓸기 + 둥근 꼬리 + 아주 작은 클릭."""
    n = int(0.36 * SR)
    t = np.arange(n) / SR
    f = 54 + 61 * np.exp(-t / 0.028)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.15)
    k = int(0.003 * SR)
    y[:k] += 0.15 * sosfilt(sos(1800, "lowpass"), np.random.default_rng(3).standard_normal(k))
    return y * (0.55 + 0.45 * vel) * 0.8


_SHK = [sosfilt(band.butter(2, [4200, 11000], btype="band", fs=SR, output="sos"),
                np.random.default_rng(40 + i).standard_normal(int(0.1 * SR))) for i in range(4)]


def shaker(vel, b):
    y = _SHK[int(h01(b, 9) * 4) % 4].copy()
    t = np.arange(len(y)) / SR
    env = np.minimum(1, t / 0.007) * np.exp(-np.maximum(0, t - 0.007) / 0.032)
    return y * env * vel * 0.18


def put(song, bus, y, b, pan=0.0, gain=1.0, send=0.0, human=0.004):
    t = song.pos(b) + (h01(b, len(bus), 13) * 2 - 1) * human
    song.add(bus, y, t, pan=pan, gain=gain, send=send)


# ── 성부 ───────────────────────────────────────────────────────────────────────────────────────
def drums(s):
    for bar, (lv, _, _) in ARR.items():
        if lv == 0:
            continue
        for k in range(16):
            b = B(bar, k / 4)
            g = dyn(b)
            if lv >= 3 and k in (0, 7):
                put(s, "kick", cushion_kick(0.9 if k == 0 else 0.7), b, gain=g, human=0.002)
            if lv >= 2 and k in (4, 12):
                band.perc(s, 37, b, amp=(1.0 if k == 12 else 0.85) * g, pan=0.08, vel=70 if lv < 4 else 96, send=0.10)
            acc = (0.55, 0.22, 0.85, 0.22)[k % 4] * (1.25 if lv == 4 else 1.0)
            if lv == 1 and k % 2:
                continue                                          # 셰이커만일 때는 8분
            put(s, "perc", shaker(acc, b), b, pan=-0.25, gain=g, send=0.04)


def span_end(b):
    return next(b1 for b0, b1, x in SPANS if b0 <= b < b1)


def hits(bar, pattern):
    """리듬 꼴(16분 위치, 길이 박, 꼬리표) + 그 마디 안 코드가 바뀌는 자리(꼬리표 'chg' — 마침 화음이 빠지지 않게).
    → [(박, 길이 박, 꼬리표)] — 길이는 다음 타격·코드 끝에서 자른다."""
    pts = {B(bar, k / 4): (d, tag) for k, d, tag in pattern}
    for b0, _, _ in SPANS:
        if B(bar) <= b0 < B(bar + 1) and b0 not in pts:
            pts[b0] = (4.0, "chg")
    order = sorted(p for p in pts if chord_at(p) is not None)
    out = []
    for i, b in enumerate(order):
        d, tag = pts[b]
        nxt = order[i + 1] if i + 1 < len(order) else B(bar + 1)
        out.append((b, min(b + d, span_end(b), nxt if tag == "chg" else span_end(b)) - b, tag))
    return out


def bass(s):
    for bar, (_, _, st) in ARR.items():
        if not st:
            continue
        if st == "l":
            for b0, b1, sym in SPANS:
                if B(bar) <= b0 < B(bar + 1):
                    put(s, "bass", round_bass(bass_note(sym, 33, 50), (b1 - b0) * s.beat * 0.92, 0.7), b0, gain=dyn(b0))
            continue
        for b, d, which in hits(bar, ((0, 1.5, "root"), (7, 0.6, "root8"), (10, 1.2, "fifth"))):
            sym = chord_at(b)
            m = bass_note(sym, 33, 50, "fifth" if which == "fifth" else "root")
            if which == "root8":
                m = m + 12 if m + 12 <= 55 else m
            put(s, "bass", round_bass(m, d * s.beat * 0.9, 0.85 if which in ("root", "chg") else 0.65), b, gain=dyn(b))


def harmony(s):
    prev_ep, prev_pad = None, None
    for bar, (_, st, _) in sorted(ARR.items()):
        if st in ("ep2", "ep4", "hold"):
            pat = {"ep2": ((0, 1.75, "a"), (10, 1.4, "b")), "ep4": ((0, 1.25, "a"), (6, 0.5, "b"), (10, 0.9, "b"), (14, 0.45, "b")),
                   "hold": ((0, 4.0, "a"),)}[st]
            for b, d, tag in hits(bar, pat):
                v = voice(chord_at(b), 54, 74, prev_ep, n=4)
                prev_ep = v
                for i, m in enumerate(v):
                    vel = (0.45 if tag == "b" else 0.62) + 0.04 * i
                    put(s, "harm", epiano(m, d * s.beat * 0.97, vel), b + i * 0.012, pan=-0.35 + 0.23 * i, gain=dyn(b), send=0.18)
        elif st == "pad":
            for b0, b1, sym in SPANS:
                if B(bar) <= b0 < B(bar + 1):
                    v = voice(sym, 57, 76, prev_pad, n=4)
                    prev_pad = v
                    for i, m in enumerate(v):
                        name = "CelloEnsSusVib-Quiet" if m < 60 else ("ViolaEnsSusVib-Quiet" if m < 67 else "ViolinEnsSusVib-Quiet")
                        band.inst(s, "pad", name, m, b0, (b1 - b0) * 0.97, vel=70, amp=dyn(b0), pan=-0.4 + 0.27 * i,
                                  send=0.32, human=0.0, rel=0.45, attack=0.28)


# 선율 · 대답 — (마디, 박 시작, 악보 줄). 대사 틈에만(장면표 §2-B-4 실측 시각을 주석에).
LEAD = [
    (6, 0, "r:1 E5:.5 A4:.5 C#5:.5 B4:.5 E5:1"),                 # NH-4 끝 6.14 → 훅 꼬리(지그재그 D U D U · 2박 C# = sus4 가 3도로 풀림)
    (11, 0, "r:1 D6:.5 B5:.5 A5:.5 F#5:.5 E5:1"),                 # NA-3 끝 11.07 「소리도 작게」 → 내려앉기
    (12, 0, "A5:1 E5:1 B4:2"),                                    # 개그 ① 깊은 잠 Z — 4도씩 하품
    (22, 0, "r:.5 B5:.5 r:.5 E6:2.5"),                            # 개그 ② 큰 ? — 4도 올림(물음 억양)
    (24, 0, "r:2 F#5:.5 E5:.5 D5:1"),                             # N4-4 끝 24.45 → 마침
    (37, 0, "r:1 A5:.5 F#5:.5 B5:.5 G5:.5 F#5:1"),                # C2 끝 37.18 → 마침
    (46, 2, "A5:2 B5:2"),                                         # 46.5 · 47 반 마디마다 한 음(대장 줄 강조와 같은 박) → 47.5 부터는 팀파니 롤이 넘겨받는다(상승 몸짓은 한 번에 하나)
    (48, 0, "D6:2"),                                              # 슬램 박(벨과 한 번 겹침)
    (49, 0, "r:.5 F5:.5 D5:.5 A5:.5 G5:.5 C#5:.5 D5:1"),          # 여운 — 주제 셀 압축 → 마침
    (56, 0, "r:3 A5:.5 F#5:.5"),                                  # N4-8 끝 56.74 → 꼬리
    (68, 0, "r:.5 G5:.5 E5:.5 B5:.5 G5:.5 D6:1.5"),               # N6-4 끝 67.97 → 선율 무대(E 장조 ♭VI)
    (69, 0, "r:.5 F#5:.5 E5:.5 B5:.5 A5:.5 D#6:1.5"),
    (70, 0, "E6:1 r:.5 C#6:.5 B5:.5 G#5:.5 F#5:1"),
    (73, 0, "r:.5 B5:1 G#5:1 E5:1.5"),                            # 잠 두루(대사 없음) — 자장가 조각
    (75, 1.5, "G#5:.5 B5:2"),                                     # N7-3 끝 75.15 → 재현 예고
    (76, 0, "r:1 G#5:1 E5:1 A5:1 | F#5:1 B5:3"),                  # 엔드스크린 — 주제 셀을 두 배 길이로
    (78, 0, "r:1 G5:1 E5:1 B5:1 | A5:1 D#6:3"),
    (81, 2, "G5:1 B5:1"),
    (82, 0, "E6:4"),
]
RESP = [
    (21, 2, "A4:.5 B4:.5 C#5:1"),                                 # N4-3 끝 21.38 → 「여러 종류로?」 받아 올리기
    (49, 0, "F4:2 E4:1 F#4:1"),                                   # 여운 안쪽 대선율
    (69, 2, "B4:1 A4:1 | G#4:2 F#4:2"),                           # 선율 무대 — 거울(하행) 대답
    (80, 0, "C#5:2 B4:2 | C5:2 B4:2 | G#4:4"),                    # 마침 IV–♭VI–I
]


def melody(s):
    for bar, bt, txt in LEAD:
        for i, (b, d, m) in enumerate(line(txt, start=B(bar, bt))):
            vel = 0.85 if bar == 48 else (0.75 if bar in (49, 68, 69, 70) else 0.55)   # 정점 박 > 선율 무대 > 대사 틈 꼬리
            if bar == 11:
                vel *= 1 - 0.12 * i                                  # 「작게」 — 한 음씩 여리게
            ring = 2.2 if bar >= 76 or bar in (12, 22, 73) else 0.6
            put(s, "lead", vibes(m, d * s.beat, vel, ring=ring, phase=h01(b, m)), b, pan=0.2, gain=dyn(b), send=0.28)
    for bar, bt, txt in RESP:
        for b, d, m in line(txt, start=B(bar, bt)):
            band.inst(s, "resp", "FHornSus", m, b, d * 0.95, vel=64, amp=dyn(b), pan=-0.15, send=0.3, rel=0.3, attack=0.05)


def accents(s):
    # 47.5 → 48: 팀파니 롤(A) 크레센도를 슬램 다운비트에서 끊는다 — 빌드의 상승 몸짓은 이것 하나
    roll = band.sample_note("TimpaniRolls", 45, 2 * s.beat, vel=110, rr=1, release=0.01)
    k = int(2 * s.beat * SR)
    roll = roll[:k] * np.geomspace(0.12, 1.0, k)
    s.add("fx", roll, s.pos(B(47, 2)), pan=0.0, send=0.12)
    # 48 슬램 한 박 — 팀파니 D · 튜블러 벨 D · 심벌 · 호른+현 화음(더블링은 이 한 박에만)
    s.add("fx", band.sample_note("Timpani", 50, 1.5, vel=120, rr=2, release=0.4) * 1.0, s.pos(B(48)), send=0.15)
    band.inst(s, "fx", "TubularBells", 74, B(48), 3.0, vel=110, amp=1.0, pan=0.1, send=0.3, human=0.0, rel=1.2)
    band.perc(s, 49, B(48), amp=0.8, vel=110, dur=3.0, send=0.2, bus="fx")
    for m in (62, 66, 69):
        band.inst(s, "slam", "FHornSus", m, B(48), 1.6, vel=90, amp=1.0, pan=-0.1, send=0.3, human=0.0, rel=0.35)
    for m in (57, 64, 74):
        band.inst(s, "slam", "ViolinEnsSusVib-Quiet" if m >= 67 else ("ViolaEnsSusVib-Quiet" if m >= 60 else "CelloEnsSusVib-Quiet"),
                  m, B(48), 1.8, vel=90, amp=1.0, pan=0.2, send=0.3, human=0.0, rel=0.4, attack=0.01)
    # 65.5 → 66: 뒤집은 매단 심벌로 들어 올리고 66 다운비트에 벨 E(2차 상승 — 슬램보다 한 단계 작게)
    s_ = band.sfz("GM-StylePerc")
    r = [r for r in s_["regions"] if r["lokey"] <= 51 <= r["hikey"]][0]
    cym = band.wav(str(Path(s_["base"]) / s_["dpath"] / r["sample"]))[: int(2 * s.beat * SR)][::-1].copy()
    cym *= np.linspace(0, 1, len(cym)) ** 2 * 10 ** (r["volume"] / 20)
    s.add("fx", cym * 0.7, s.pos(B(66)) - len(cym) / SR, pan=-0.2, send=0.1)
    band.inst(s, "fx", "TubularBells", 76, B(66), 3.0, vel=90, amp=0.7, pan=0.1, send=0.3, human=0.0, rel=1.2)
    # 82 마침 — 벨 E 한 번(선물 벨 세 번째)
    band.inst(s, "fx", "TubularBells", 76, B(82), 4.0, vel=70, amp=0.18, pan=0.1, send=0.35, human=0.0, rel=1.5)


# 버스 이득 — `--bus` 표(이득 1.0 원음)를 균형 목표(원본 버스 LUFS: 선율 −20 · 대답/화음 −26 · 저음 −24 · 타악 −35)에 맞춘 값.
# v1 원음 실측: 선율 −11 · 호른 −10 · 전자피아노 −14 · 현 −9.5 · 베이스 −16.3 · 킥 −18 · 셰이커+탭 −30.5 · 슬램 화음 −8.6
GAINS = {"lead": 0.35, "resp": 0.16, "harm": 0.25, "pad": 0.15, "bass": 0.41, "kick": 0.28, "perc": 0.6, "fx": 0.9, "slam": 0.15}
SECTIONS = [("H", 3, 4), ("C-thin", 7, 4), ("C-mid", 11, 3), ("M1", 20, 5), ("M2", 31, 7), ("M3-build", 44, 4),
            ("SLAM", 48, 2), ("M4", 56, 1), ("G-warm", 63, 3), ("G-lift", 66, 5), ("E-calm", 71, 5), ("E-lull", 76, 6), ("END", 82, 1)]


def stop_mask(n):
    """정지 구간 = 0. 재생 구간 끝 0.15s 는 0 으로 내려앉고, 마지막 마디(82)는 끝 1.0s 동안 페이드."""
    m = np.zeros(n)
    for a, b in PLAY:
        i0, i1 = a * BAR_N, b * BAR_N
        m[i0:i1] = 1.0
        f = int((1.0 if b == BARS else 0.15) * SR)
        m[i1 - f:i1] *= np.linspace(1, 0, f) ** 2
    return m


def main():
    s = Song(f"bed_{TAG}", "BGM 만들고 무료로 드립니다 — 바탕곡", bpm=BPM, bar=4, bars=BARS, swing=0.5, tail=0.0, lufs=LUFS_BED)
    s.N = BARS * BAR_N                                             # 마디-프레임-샘플 3중 정수: 83 × 128,000
    for name, b0, nb in SECTIONS:
        s.section(name, b0, nb)
    drums(s)
    bass(s)
    harmony(s)
    melody(s)
    accents(s)
    out = HERE / "out" / TAG
    rep = band.master(s, GAINS, rev_rt=1.6, rev_wet=0.22, out_dir=out, tp_target=-1.5)
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
    stop_peak = max(float(np.abs(y[a * BAR_N:b * BAR_N]).max()) for a, b in
                    [(0, 3), (14, 20), (25, 31), (38, 44), (50, 56), (57, 63)])
    fin = {"bed_lufs": round(integrated_lufs(y, SR), 2), "bed_true_peak_db": round(tp, 2), "post_mask_gain_db": round(20 * math.log10(g), 2),
           "samples": len(y), "frames_30fps": len(y) / SR * 30, "section_lufs_bs1770": sec,
           "stop_zone_peak_dbfs": round(20 * math.log10(stop_peak + 1e-12), 1)}
    rep.update(fin)
    (out / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(fin, ensure_ascii=False))


if __name__ == "__main__":
    main()
