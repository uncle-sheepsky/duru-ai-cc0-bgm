"""흐물두루 플레이리스트 — 지능하락 BGM 데모 v1 「흐물흐물 오후」.

목표 결 = 치이카와·아즈망가(쿠리코더)·동숲 오후 계열: 뒤뚱거리는 오움파, 반복음 멍청 모티프, 장난감 같은 색, 개그 SFX.
악기 = VSCO 2 CE(CC0) 실제 악기 + 이 편 신작 합성(카주·슬라이드 휘슬). 빌더 포크 없음 — 샘플 재생기만 원리 재작성.

지문(유사성-지문-스키마 §3 대조):
  축1 = 하강5도권 래그타임 III7–VI7–II7–V7–(I) `[+5,+5,+5,+5]`(B) + I 위 상행 라인클리셰 I–I+–I6–I7(내성부 d=+1)→IV–iv6–I–V7(A)
        대장 미사용 archetype(하강5도권) · 상행 라인클리셰는 heist 하행(d=−1)과 반대 방향
  축3 = WADDLE8sw — 튜바 {0,8,14}(1·3박 + 4박 뒷8분 반음 픽업) + 엇박 팍{4,12} · 스윙8분. 대장 킥세트·8swing 조합 전무
  조합ID = RAG×WADDLE8sw (신규) · 컨투어 = 반복음+반음 이웃(정적 페달+장식) / B는 하강 폭포 — 아치 회피
하이라이트 역할당 한 명: 리듬(타악 한 벌) / 저음(튜바 하나) / 화음(한 악기) / 선율(콜 하나 ↔ 리스폰스 하나).
출력: bgm/out/<tag>/mix.wav · stems/ · report.json
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
from scipy.io import wavfile
from scipy.signal import butter, resample_poly, sosfilt, fftconvolve


def find_root(p):
    for d in [p, *p.parents]:
        if (d / ".akashic-root").exists():
            return d
    return None   # 공개 저장소(센티넬 없음): 같은 폴더의 sfz_sampler.py + 환경변수 VSCO_SFZ_DIR


HERE = Path(__file__).resolve().parent
ROOT = find_root(HERE)
sys.path.insert(0, str(HERE))
if ROOT:
    sys.path.insert(0, str(ROOT / "projects/duru/영상소스/assets/bgm"))
from sfz_sampler import load_sfz  # noqa: E402

VSCO = (Path(os.environ["VSCO_SFZ_DIR"]) if os.environ.get("VSCO_SFZ_DIR")
        else ROOT / "projects/duru/영상 제작 기초 자료/음원/VSCO-2-CE-SFZ" if ROOT else HERE / "VSCO-2-CE-SFZ")
TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v1"
OUT = HERE / "out" / TAG

SR = 48000
BPM = 112
BEAT = 60 / BPM
SWING = 0.62          # 8분 앞박이 박의 62% (가벼운 셔플)
BARS = 50
TAIL = 3.5
N = int((BARS * 4 * BEAT + TAIL) * SR)


# ── 결정론 해시 ─────────────────────────────────────────────────────────────
def h01(*k):
    x = 0
    for v in k:
        x = (x * 1000003 + int(round(v * 1000))) & 0xFFFFFFFF
    x = (x ^ (x >> 16)) * 0x45D9F3B & 0xFFFFFFFF
    return ((x ^ (x >> 16)) & 0xFFFFFF) / 0xFFFFFF


def pos(b):
    """박 → 초. 8분 뒷박을 SWING 비율로 민다(16분은 앞·뒤 반쪽 안에서 비례)."""
    k = math.floor(b + 1e-9)
    fr = b - k
    if fr < 0.5:
        fr = fr / 0.5 * SWING
    else:
        fr = SWING + (fr - 0.5) / 0.5 * (1 - SWING)
    return (k + fr) * BEAT


def m2f(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def sos(fc, kind, order=2):
    return butter(order, fc, btype=kind, fs=SR, output="sos")


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


# ── 버스 ────────────────────────────────────────────────────────────────────
class Bus:
    def __init__(self, name):
        self.name = name
        self.L = np.zeros(N)
        self.R = np.zeros(N)

    def add(self, y, t, pan=0.0, gain=1.0):
        i = int(round(t * SR))
        if i >= N:
            return
        if i < 0:
            y, i = y[-i:], 0
        y = y[: N - i] * gain
        a = (pan + 1) * math.pi / 4
        self.L[i:i + len(y)] += y * math.cos(a)
        self.R[i:i + len(y)] += y * math.sin(a)


BUS = {k: Bus(k) for k in ["bass", "perc", "chord", "lead", "resp", "color", "sfx"]}
REV = Bus("rev")


# ── VSCO 샘플 재생기(48k) — 속도 레이어 고정·라운드로빈·릴리즈 컷 ─────────────
_SFZ, _WAV = {}, {}
SHIFT = {}
OCT = {"Glockenspiel": -12, "Xylophone": -12,   # VSCO 표기보다 한 옥타브 위로 울림(ep38 FFT 실측 +1212c)
       "PiccoloStac": -12}                          # 피콜로도 표기보다 한 옥타브 위(이 편 실측 +1198c)
CENT = {"ClarinetStac": 14}                         # 스타카토 클라리넷 6음 실측 평균 약 −14센트 → 보정


def sfz(name):
    if name not in _SFZ:
        _SFZ[name] = load_sfz(str(next(VSCO.rglob(f"{name}.sfz"))))
    return _SFZ[name]


def wav(path):
    if path not in _WAV:
        sr, d = wavfile.read(path)
        dt = d.dtype
        d = d.astype(np.float64)
        if d.ndim > 1:
            d = d.mean(1)
        d /= {np.dtype(np.int16): 32768.0, np.dtype(np.int32): 2147483648.0}.get(dt, 1.0)
        if sr != SR:
            g = math.gcd(SR, sr)
            d = resample_poly(d, SR // g, sr // g)
        _WAV[path] = d
    return _WAV[path]


def region(name, midi, vel, rr):
    s = sfz(name)
    regs = [r for r in s["regions"] if r["lovel"] <= vel <= r["hivel"]] or s["regions"]
    best = min(abs(r["pk"] - midi) for r in regs)
    c = [r for r in regs if abs(r["pk"] - midi) == best]
    c = [r for r in c if r["lokey"] <= midi <= r["hikey"]] or c
    r = c[rr % len(c)]
    SHIFT[name] = max(SHIFT.get(name, 0), abs(midi - r["pk"]))
    return s, r


def sample_note(name, midi, dur, vel=96, rr=0, release=0.08, attack=0.0):
    midi = midi + OCT.get(name, 0)
    s, r = region(name, midi, vel, rr)
    src = wav(os.path.join(s["base"], s["dpath"], r["sample"]))
    ratio = 2 ** (((midi - r["pk"]) + (r["tune"] + CENT.get(name, 0)) / 100) / 12)
    n = int((dur + release) * SR)
    idx = np.arange(n) * ratio
    idx = idx[idx < len(src) - 1]
    i0 = idx.astype(int)
    fr = idx - i0
    y = np.pad(src[i0] * (1 - fr) + src[i0 + 1] * fr, (0, n - len(idx)))
    if attack > 0:
        a = int(attack * SR)
        y[:a] *= np.linspace(0, 1, a) ** 2
    k0 = int(dur * SR)
    y[k0:] *= np.linspace(1, 0, n - k0) ** 2
    return y * 10 ** (r["volume"] / 20)


def glide_note(name, m0, m1, dur, g0, g1, vel=96, release=0.15):
    """지속음 샘플을 음높이 곡선(m0→m1, g0~g1초 구간)으로 읽는다 — 하품 트롬본."""
    s, r = region(name, m0, vel, 0)
    src = wav(os.path.join(s["base"], s["dpath"], r["sample"]))
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    q = np.clip((t - g0) / (g1 - g0), 0, 1)
    q = q * q * (3 - 2 * q)
    m = m0 + (m1 - m0) * q
    ratio = 2 ** ((m - r["pk"] + r["tune"] / 100) / 12)
    idx = np.cumsum(ratio)
    idx = idx[idx < len(src) - 1]
    i0 = idx.astype(int)
    fr = idx - i0
    y = np.pad(src[i0] * (1 - fr) + src[i0 + 1] * fr, (0, n - len(idx)))
    k0 = int(dur * SR)
    y[k0:] *= np.linspace(1, 0, n - k0) ** 2
    return y * 10 ** (r["volume"] / 20)


def inst(bus, name, midi, b, dur_b, vel=96, amp=1.0, pan=0.0, send=0.18, human=0.006, rel=0.08, attack=0.0):
    rr = int(h01(b, midi) * 97) + 1
    y = sample_note(name, midi, dur_b * BEAT, vel=vel, rr=rr, release=rel, attack=attack)
    y *= amp * (0.9 + 0.1 * h01(midi, b, 3))
    t = pos(b) + (h01(b, midi, 7) * 2 - 1) * human
    BUS[bus].add(y, t, pan=pan)
    if send:
        REV.add(y, t, pan=pan, gain=send)


def perc(key, b, amp=1.0, pan=0.0, vel=100, send=0.08, dur=1.2, human=0.004):
    s = sfz("GM-StylePerc")
    regs = [r for r in s["regions"] if r["lokey"] <= key <= r["hikey"]]
    lay = [r for r in regs if r["lovel"] <= vel <= r["hivel"]] or regs
    r = lay[int(h01(b, key) * 997) % len(lay)]
    y = wav(os.path.join(s["base"], s["dpath"], r["sample"]))[: int(dur * SR)].copy()
    k = int(0.04 * SR)
    y[-k:] *= np.linspace(1, 0, k)
    y *= amp * 10 ** (r["volume"] / 20)
    t = pos(b) + (h01(b, key, 5) * 2 - 1) * human
    BUS["perc"].add(y, t, pan=pan)
    if send:
        REV.add(y, t, pan=pan, gain=send)


# ── 이 편 신작 합성: 카주 · 슬라이드 휘슬 ─────────────────────────────────
def polyblep_saw(phase_inc):
    """위상 증가량 배열(주기당 0~1) → 밴드리밋 톱니."""
    ph = np.cumsum(phase_inc) % 1.0
    y = 2 * ph - 1
    dt = phase_inc
    m1 = ph < dt
    t1 = ph[m1] / dt[m1]
    y[m1] -= t1 + t1 - t1 * t1 - 1
    m2 = ph > 1 - dt
    t2 = (ph[m2] - 1) / dt[m2]
    y[m2] -= t2 * t2 + t2 + t2 + 1
    return y


def kazoo_phrase(notes, seed=0):
    """notes = [(t0초, dur초, midi)] 레가토 한 줄. 허밍 톱니 → 막 떨림(tanh) → 포먼트(음 'ㅜ~ㅓ') → 숨소리."""
    t_end = max(t0 + d for t0, d, _ in notes) + 0.12
    n = int(t_end * SR)
    t = np.arange(n) / SR
    f = np.full(n, m2f(notes[0][2]))
    amp = np.zeros(n)
    for i, (t0, d, m) in enumerate(notes):
        a, b_ = int(t0 * SR), int((t0 + d) * SR)
        f[a:] = m2f(m)
        seg = np.arange(b_ - a) / SR
        env = np.minimum(1, seg / 0.018) * np.minimum(1, (d - seg) / 0.035).clip(0, 1)
        amp[a:b_] = np.maximum(amp[a:b_], env)
        # 음머리 스쿱(−45센트 → 0, 45ms)
        k = min(b_ - a, int(0.045 * SR))
        f[a:a + k] *= 2 ** (-0.45 / 12 * (1 - np.arange(k) / k))
    # 포르타멘토(25ms 평활)
    w = int(0.025 * SR)
    f = np.convolve(np.pad(f, (w, w), mode="edge"), np.ones(w) / w, mode="same")[w:-w]
    # 비브라토 5.6Hz ±14센트, 음 시작 후 0.15s부터 서서히
    vib_env = np.zeros(n)
    for t0, d, _ in notes:
        a, b_ = int(t0 * SR), int((t0 + d) * SR)
        seg = np.arange(b_ - a) / SR
        vib_env[a:b_] = np.clip((seg - 0.15) / 0.25, 0, 1)
    f *= 2 ** (0.14 / 12 * vib_env * np.sin(2 * np.pi * 5.6 * t + seed))
    src = polyblep_saw(f / SR)
    buzz = np.tanh(2.6 * src + 0.35 * src ** 2)
    y = (1.0 * bp(buzz, 520, 780) + 0.75 * bp(buzz, 980, 1350) + 0.45 * bp(buzz, 2300, 3100)
         + 0.10 * sosfilt(sos(3500, "highpass"), buzz))
    rng = np.random.default_rng(seed + 11)
    y += 0.035 * bp(rng.standard_normal(n), 2500, 6000) * amp
    y = sosfilt(sos(4800, "lowpass", 4), y) * amp   # 막 떨림 치찰을 깎는다(1차 실측 중심 4.1kHz = 클라리넷의 2배)
    return y / (np.abs(y).max() + 1e-9)


def slide_whistle(m0, m1, dur, seed=0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    q = t / dur
    m = m0 + (m1 - m0) * (q * q * (3 - 2 * q))
    f = m2f(m) * 2 ** (0.12 / 12 * np.sin(2 * np.pi * 6.2 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) + 0.08 * np.sin(2 * ph)
    rng = np.random.default_rng(seed + 3)
    y += 0.06 * bp(rng.standard_normal(n), 1500, 5000)
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06).clip(0, 1)
    return y * env * 0.5


def sfx_pop():
    """코풍선 '퐁' — 짧은 위로 튀는 사인 + 클릭."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 500 + 1400 * (1 - np.exp(-t / 0.012))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035)
    y[:40] += np.linspace(0.8, 0, 40)
    return y * 0.6


# ── 화성 ────────────────────────────────────────────────────────────────────
# 이름: (중음 보이싱, 튜바 근음, 튜바 5음)
CH = {
    "F":    ((57, 60, 65), 41, 36), "F+":  ((57, 61, 65), 41, 37), "F6":  ((57, 62, 65), 41, 36),
    "F7":   ((57, 63, 65), 41, 36), "Bb":  ((58, 62, 65), 34, 41), "Bbm6": ((61, 65, 67), 34, 41),
    "C7":   ((55, 58, 64), 36, 43), "A7":  ((55, 61, 64), 33, 40), "D7":  ((54, 60, 62), 38, 33),
    "G7":   ((53, 59, 62), 31, 38), "Gb":  ((54, 58, 61), 30, 37),
}
# 마디별 (박, 코드) — 50마디
A_CH = [[(0, "F")], [(0, "F+")], [(0, "F6")], [(0, "F7")], [(0, "Bb")], [(0, "Bbm6")], [(0, "F"), (2, "C7")], [(0, "F"), (2, "C7")]]
B_CH = [[(0, "A7")], [(0, "A7")], [(0, "D7")], [(0, "D7")], [(0, "G7")], [(0, "G7")], [(0, "C7")], [(0, "C7")]]
SECTIONS = [  # (이름, 시작마디, 길이)
    ("intro", 0, 4), ("A1", 4, 8), ("A2", 12, 8), ("B", 20, 8), ("A3", 28, 8), ("yawn", 36, 4), ("A4", 40, 8), ("tag", 48, 2),
]
PROG = ([[(0, "F")], [(0, "F")], [(0, "C7")], [(0, "C7")]] + A_CH + A_CH + B_CH + A_CH
        + [[(0, "Bb")], [(0, "Bbm6")], [(0, "F")], [(0, "C7")]] + A_CH + [[(0, "F"), (2, "Gb"), (3, "F")], [(0, "F")]])
assert len(PROG) == BARS


def chord_at(bar, beat):
    c = PROG[bar][0][1]
    for b0, name in PROG[bar]:
        if beat >= b0:
            c = name
    return c


def sec_of(bar):
    for name, s0, ln in SECTIONS:
        if s0 <= bar < s0 + ln:
            return name, bar - s0
    return "end", 0


# ── 선율(섹션 상대 박) ─────────────────────────────────────────────────────
# 콜: 라인클리셰 이동음(C→C#)을 반복음으로 · 리스폰스: 다음 이동음(D→Eb)을 낮게 따라함 = 바보 릴레이
CALL = [(0, .5, 72), (.5, .5, 72), (1, 1.2, 72), (3.5, .5, 69),
        (4, .5, 73), (4.5, .5, 73), (5, 1.2, 73),
        (16, .5, 77), (16.5, .5, 74), (17, .5, 70), (17.5, .5, 74), (18, 1.0, 77), (19.5, .5, 75),
        (20, 2.2, 73), (22.5, .5, 72), (23, .5, 70), (23.5, .5, 67),
        (24, .5, 69), (24.5, .5, 72), (25, 1.0, 69), (26, .5, 70), (26.5, .5, 67), (27, 1.0, 64),
        (28, 1.6, 65)]
RESP = [(8, .5, 62), (8.5, .5, 62), (9, 1.2, 62), (11.5, .5, 60),
        (12, .5, 63), (12.5, .5, 63), (13, 1.6, 63),
        (30, .5, 53), (30.5, .5, 48), (31, .7, 41)]
# B — 하강 폭포(DDD↑↑) 실제 시퀀스 T−7 · 클라리넷은 가이드톤 반음 하강(C#→C→B→B♭)
B_LEAD = [(0, .5, 69), (.5, .5, 67), (1, .5, 64), (1.5, .5, 61), (2, .5, 62), (2.5, 1.0, 64),
          (8, .5, 74), (8.5, .5, 72), (9, .5, 69), (9.5, .5, 66), (10, .5, 67), (10.5, 1.0, 69),
          (16, .5, 67), (16.5, .5, 65), (17, .5, 62), (17.5, .5, 59), (18, .5, 60), (18.5, 1.0, 62),
          (24, .5, 72), (24.5, .5, 70), (25, .5, 67), (25.5, .5, 64)]
B_GUIDE = [(0, 7.5, 61), (8, 7.5, 60), (16, 7.5, 59), (24, 1.8, 58)]


def play_line(bus, name, line, base_bar, vel=96, amp=1.0, oct_=0, pan=0.0, send=0.18, stac=1.0, rel=0.08):
    for b, d, m in line:
        inst(bus, name, m + oct_, base_bar * 4 + b, d * stac, vel=vel, amp=amp, pan=pan, send=send, rel=rel)


# ── 편곡 ────────────────────────────────────────────────────────────────────
def arrange():
    gp_b0, gp_b1 = 27 * 4 + 1.5, 27 * 4 + 4.0   # 전체 정지(general pause) 박 구간 — B 끝 개그
    for bar in range(BARS):
        sec, k = sec_of(bar)
        b0 = bar * 4
        nxt = PROG[bar + 1][0][1] if bar + 1 < BARS else "F"
        # 튜바 — WADDLE {0, 2박, 3.5박 픽업}
        if sec not in ("yawn", "tag"):
            c0 = CH[chord_at(bar, 0)]
            c2 = CH[chord_at(bar, 2)]
            amp = 2.5 * {"intro": 0.85, "A3": 1.15}.get(sec, 1.0)   # 튜바 샘플이 작다(스템 실측 −8dB) → 오움이 들리게
            inst("bass", "TubaStac", c0[1], b0, 0.9, vel=100, amp=amp, send=0.06, rel=0.06)
            m2 = c2[2] if chord_at(bar, 2) == chord_at(bar, 0) else c2[1]
            if not (gp_b0 <= b0 + 2 < gp_b1):
                inst("bass", "TubaStac", m2, b0 + 2, 0.9, vel=96, amp=amp * 0.92, send=0.06, rel=0.06)
            if not (gp_b0 <= b0 + 3.5 < gp_b1) and (sec != "intro" or k >= 2):
                tgt = CH[nxt][1]
                inst("bass", "TubaStac", tgt - 1, b0 + 3.5, 0.4, vel=88, amp=amp * 0.7, send=0.05, rel=0.04)
        elif sec == "yawn":
            inst("bass", "TubaSus", CH[chord_at(bar, 0)][1], b0, 3.6, vel=70, amp=0.75, send=0.12, rel=0.3)

        # 타악 — 리듬 한 벌
        if sec in ("intro", "A1", "A2", "A3", "A4"):
            for bb in (0, 2):
                perc(77, b0 + bb, amp=0.45, pan=-0.15)                  # 로그드럼 저 '톡'
            if not (sec == "intro" and k < 1):
                for bb in (1, 3):
                    perc(76, b0 + bb, amp=0.38, pan=0.2)               # 로그드럼 고 '탁'
            if sec in ("A2", "A3", "A4"):
                for bb in (1.5, 3.5):
                    perc(75, b0 + bb, amp=0.22 if sec != "A3" else 0.3, pan=0.35)   # 클라베스 엇박
        if sec == "B":
            for bb in np.arange(0, 4, 0.5):
                if not (gp_b0 <= b0 + bb < gp_b1):
                    perc(37, b0 + bb, amp=0.22 if bb % 1 == 0 else 0.14, pan=0.1, vel=60)   # 스네어 탭 셔플
            for bb in (1, 3):
                if not (gp_b0 <= b0 + bb < gp_b1):
                    perc(76, b0 + bb, amp=0.3, pan=0.2)

        # 화음 '팍' — 엇박(1·3박) — 한 섹션 한 악기
        if sec not in ("yawn", "tag") and not (sec == "intro" and k < 2):
            for bb in (1, 3):
                if gp_b0 <= b0 + bb < gp_b1:
                    continue
                notes = CH[chord_at(bar, bb)][0]
                if sec in ("A2",):
                    for j, m in enumerate(notes):                        # 하프 스트럼 = 우쿨렐레 결
                        inst("chord", "Harp", m + 12, b0 + bb + j * 0.035, 0.45, vel=90, amp=0.68, pan=0.25, send=0.2, rel=0.12)
                elif sec in ("B", "A3"):
                    for m in notes:
                        inst("chord", "UprightPiano", m, b0 + bb, 0.32, vel=88, amp=0.5 if sec == "B" else 0.8, pan=0.2, send=0.15, rel=0.06)
                else:
                    for m in notes:
                        inst("chord", "ViolinEnsPizz", m + 12, b0 + bb, 0.4, vel=96, amp=0.55, pan=0.25, send=0.18)

    # 선율
    play_line("lead", "ClarinetStac", CALL, 4, amp=0.95, pan=-0.1)
    play_line("resp", "BassoonStac", RESP, 4, amp=1.0, oct_=0, pan=0.15)
    play_line("lead", "FluteSusNV", CALL, 12, amp=1.15, pan=-0.1, stac=0.85, rel=0.1)     # 리코더 결(비브라토 없음)
    play_line("resp", "ClarinetStac", RESP[:7], 12, amp=1.0, oct_=12, pan=0.15)
    play_line("resp", "BassoonStac", RESP[7:], 12, amp=0.9, pan=0.15)
    for b, d, m in CALL:                                                   # 글로켄 — 마디 첫 음만 반짝
        if b % 4 == 0:
            inst("color", "Glockenspiel", m + 12, 12 * 4 + b, 0.6, vel=80, amp=0.8, pan=0.3, send=0.25, rel=0.4)
    play_line("lead", "BassoonStac", B_LEAD, 20, amp=0.5, oct_=-12, pan=-0.05)
    play_line("resp", "ClarinetSus", B_GUIDE, 20, vel=70, amp=0.4, pan=0.2, rel=0.25)
    # A3 피크 — 카주 콜 ↔ 피콜로 리스폰스
    kz = [(pos(28 * 4 + b), d * BEAT * 0.95, m) for b, d, m in CALL]
    y = kazoo_phrase(kz, seed=3)
    BUS["lead"].add(y * 0.33, 0.0, pan=0.0)
    REV.add(y * 0.33, 0.0, gain=0.18)
    play_line("resp", "PiccoloStac", RESP[:7], 28, amp=0.65, oct_=12, pan=0.4)
    play_line("resp", "BassoonStac", RESP[7:], 28, amp=1.0, pan=0.15)
    # yawn — 마림바 느린 분산화음 + 플루트 반템포 라인클리셰 + 하품 트롬본
    for bar in range(36, 40):
        notes = CH[chord_at(bar, 0)][0]
        for j, m in enumerate(notes + (notes[0] + 12,)):
            inst("color", "Marimba", m + 12, bar * 4 + j * 0.5, 1.2, vel=70, amp=0.9, pan=0.15 - 0.1 * j, send=0.3, rel=0.5)
    for j, m in enumerate((72, 73, 74, 75)):
        inst("lead", "FluteSusNV", m, 36 * 4 + j * 2, 1.8, vel=70, amp=0.55, pan=-0.1, send=0.3, rel=0.3)
    yt = glide_note("TromboneSus", 65, 58, 2.4 * BEAT * 1.2, 0.35, 2.2, vel=80)
    BUS["resp"].add(yt * 0.55, pos(39 * 4), pan=0.2)
    REV.add(yt * 0.55, pos(39 * 4), gain=0.25)
    # A4 — 클라리넷 콜 ↔ 플루트 리스폰스(마무리)
    play_line("lead", "ClarinetStac", CALL, 40, amp=0.85, pan=-0.1)
    play_line("resp", "FluteSusNV", RESP[:7], 40, amp=0.6, oct_=12, pan=0.15, stac=0.85)
    play_line("resp", "BassoonStac", RESP[7:], 40, amp=0.9, pan=0.15)
    # tag — F … G♭(♭II 미끄러짐) … F, 마지막 '퐁'
    for b, name, a in ((48 * 4, "F", 0.6), (48 * 4 + 2, "Gb", 0.55), (48 * 4 + 3, "F", 0.6)):
        for m in CH[name][0]:
            inst("chord", "UprightPiano", m, b, 0.5 if name != "F" or b < 48 * 4 + 3 else 2.5, vel=90, amp=a, send=0.2, rel=0.3)
        inst("bass", "TubaStac", CH[name][1], b, 0.6, vel=100, amp=1.0, send=0.08)
    inst("color", "Glockenspiel", 89, 48 * 4 + 3, 2.0, vel=90, amp=0.4, pan=0.3, send=0.35, rel=1.2)
    BUS["sfx"].add(slide_whistle(84, 67, 1.1, seed=2) * 0.5, pos(48 * 4 + 3.5), pan=0.3)
    BUS["sfx"].add(sfx_pop() * 0.6, pos(49 * 4 + 2), pan=-0.2)

    # 개그 SFX — 인트로 끝 슬라이드 업 · B 끝 정지 → 귀로 긁기 + 슬라이드 업
    BUS["sfx"].add(slide_whistle(67, 86, 0.75, seed=1) * 0.5, pos(3 * 4 + 3) - 0.1, pan=-0.2)
    perc(72, gp_b0 + 1.0, amp=0.7, pan=0.3, dur=0.6)
    BUS["sfx"].add(slide_whistle(65, 88, 0.6, seed=4) * 0.5, pos(gp_b1) - 0.6, pan=-0.25)
    # A1·A3 4마디째 끝 — 작은 '퐁'(코풍선 동기 장난)
    for bar in (11, 35):
        BUS["sfx"].add(sfx_pop() * 0.35, pos(bar * 4 + 3.5), pan=0.3)


# ── 믹스·마스터 ────────────────────────────────────────────────────────────
def room_ir(rt=1.1, seed=5):
    n = int(rt * 1.2 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    env = np.exp(-6.9 * t / rt)
    L = rng.standard_normal(n) * env
    R = rng.standard_normal(n) * env
    L = sosfilt(sos(5200, "lowpass"), L)
    R = sosfilt(sos(5200, "lowpass"), R)
    pre = int(0.015 * SR)
    L = np.pad(L, (pre, 0))[:n]
    R = np.pad(R, (pre, 0))[:n]
    return L / np.sqrt((L ** 2).sum()), R / np.sqrt((R ** 2).sum())


def limiter(x, ceiling=0.89, look=0.004, rel=0.06):
    """룩어헤드 피크 리미터: 필요 이득의 구간 최소(앞을 봄) → 즉시 어택·지수 릴리즈 → 짧은 평활."""
    from scipy.ndimage import minimum_filter1d
    a = np.abs(x).max(1)
    g = np.minimum(1, ceiling / np.maximum(a, 1e-9))
    w = int(look * SR)
    g = minimum_filter1d(g, size=2 * w + 1, origin=-w // 2)
    coef = math.exp(-1 / (rel * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i, v in enumerate(g):
        cur = v if v < cur else v + (cur - v) * coef
        out[i] = cur
    out = np.convolve(np.pad(out, (w, w), mode="edge"), np.ones(w) / w, mode="same")[w:-w]
    return x * out[:, None]


def true_peak_db(x):
    up = resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.abs(up).max() + 1e-12)


def main():
    arrange()
    irL, irR = room_ir()
    revL = fftconvolve(REV.L, irL)[:N]
    revR = fftconvolve(REV.R, irR)[:N]
    gains = {"bass": 1.0, "perc": 0.9, "chord": 0.8, "lead": 1.0, "resp": 0.95, "color": 0.8, "sfx": 0.5}
    L = sum(BUS[k].L * g for k, g in gains.items()) + 0.32 * revL
    R = sum(BUS[k].R * g for k, g in gains.items()) + 0.32 * revR
    st = np.stack([L, R], 1)
    st = sosfilt(sos(35, "highpass", 4), st, axis=0)
    meter = pyln.Meter(SR)
    for _ in range(3):
        lufs = meter.integrated_loudness(st)
        st *= 10 ** ((-14.0 - lufs) / 20)
        st = limiter(st, ceiling=10 ** (-1.3 / 20))
    lufs = meter.integrated_loudness(st)
    tp = true_peak_db(st)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stems").mkdir(exist_ok=True)
    wavfile.write(OUT / "mix.wav", SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
    for k in gains:
        s = np.stack([BUS[k].L, BUS[k].R], 1)
        wavfile.write(OUT / "stems" / f"{k}.wav", SR, (np.clip(s, -1, 1) * 32767).astype(np.int16))
    # 섹션 라운드니스(아크) · 저역 몫
    secs = {}
    for name, s0, ln in SECTIONS:
        a, b = int(pos(s0 * 4) * SR), int(pos((s0 + ln) * 4) * SR)
        try:
            secs[name] = round(meter.integrated_loudness(st[a:b]), 1)
        except Exception:
            secs[name] = None
    from scipy.signal import welch
    fq, p = welch(st.mean(1), SR, nperseg=8192)
    low = float(p[fq < 60].sum() / p.sum())
    rep = {"tag": TAG, "bpm": BPM, "swing": SWING, "bars": BARS, "dur_s": round(N / SR, 2),
           "music_s": round(BARS * 4 * BEAT, 3), "lufs": round(lufs, 2), "true_peak_db": round(tp, 2),
           "section_lufs": secs, "below60Hz_share": round(low, 4), "max_resample_semitones": SHIFT,
           "fingerprint": "RAG×WADDLE8sw"}
    (OUT / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
