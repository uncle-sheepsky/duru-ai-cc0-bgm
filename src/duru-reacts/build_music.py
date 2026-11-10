"""「건드리면 반응하는 두루」 롱폼 애니메이션 — 음악 v2 「정리판」(신작 1곡 · 사용자 「완전히 새 곡」 2026-11-09).
♩150 · 4/4 · 1마디 = 1.6s = 48f = 76,800샘플@48k. 시간은 전부 ../timeline.json 의 큐(박)에서 읽는다 — 손으로 적지 않는다.

v1(build_music_v1.py · out/v1) = 사용자 판정 「음악이 좀 난잡한 것 같아」(2026-11-09). 실측: 음 개수는 승인곡(ep38 v2.1)보다 적었지만(초당 2.3 대 4.6)
0.4초마다 소리 밝기가 튀는 폭이 2·3막에서 1.2옥타브(승인곡 0.47) — 반 마디마다 높은 피치카토 ↔ 낮은 클라리넷이 번갈고, 손짓마다 다른 악기가 한 번씩 끼어들었다.
v2 가 바꾼 것(곡의 생각·화음·시간표는 그대로):
  ① 바탕이 끊기지 않는다 — 저음(1·3박) + 화음(2·4박)이 막 내내 깔린다.
  ② 배역 고정 — 커서 = 솔로 바이올린 피치카토, 두루 = 클라리넷. 한 번씩 끼어들던 바순·튜바·트롬본·플루트·하프·달리기 음형·끌어오기 바람 소리 삭제.
  ③ 주고받기를 반 마디 → 마디 단위로, 선율은 긴 음(1박·반박·반박·2박)으로.
  ④ 북 = 「쿵 짝 쿵 짝」 기본형. 킥 {0,8,12}(1·3·4박) · 스네어 탭 2·4박. 엇박 스피카토·16분 킥·클라베 장식 삭제(클라베는 진짜 노크에만).

생각 = 「거울 → 나란히 → 자리 바꿈」.
  커서가 부르는 동기 = 화음의 3–5–6–5음(올라갔다 내려옴), 두루가 받는 동기 = 그 거울 5–3–2–3음(내려갔다 올라옴).
  1막: 같은 동기를 **단조**로, 커서는 앞 두 음만 내고 두루는 받지 않는다(낮은 클라리넷으로 퉁명하게).
  2막: 같은 으뜸음 **장조**. 두루가 처음으로 거울 대답을 한다.  3막: 둘이 **나란히**(3도) 같이 부른다.
  5막: 합주.  6막: **자리 바꿈** — 두루가 먼저 부르고 커서가 받는다 → 빗살 자장가.
지문(gate_music.py G1 이 문서 파싱으로 대조):
  HOME I–II–IV–I `[+2,+3,−5]`(D–E–G–D) · SHY i–iv–♭II–V7 `[+5,−4,+6,+5]`(Dm–Gm–E♭–A7) · PLAY vi–II–IV–I `[+5,+3,−5,−3]`(Bm–E–G–D)
  CARE I–iii–ii–IV `[+4,−2,+3,−5]`(D–F#m–Em–G) · 빌드 베이스 `[+1,+1,0,+5]` · 사과 다리 `[−5,−5,0,+5]`
  격자 STEP8 = 킥 {0,8,12}(1·3·4박) + 스네어 탭 {4,12} · 스트레이트(탬버린은 v3 까지 있었으나 「박자를 해친다」로 삭제).
음색: VSCO 2 CE(CC0) — 솔로 바이올린 피치카토 · 클라리넷 · 콘트라베이스 피치카토 · 비올라 피치카토 · 조용한 비올라/첼로 지속음 · 오보에(4막) · 호른 + 바이올린 합주(정점) ·
  팀파니 · 튜블러 벨 · 타악(스네어 · 탬버린 · 클라베 · 큰북 · 심벌) + 이 편 신작 합성(둥근 킥 · 빗살 · 부채 바람 · 딸깍). 저수준만 공용: playlist_melty/bgm/band.py.
누르는 순간마다 소리: 손짓마다 커서의 피치카토 한 음(또는 그 손짓의 소리)이 붙는다 — gate G5 가 손짓 시각마다 온셋을 잰다.
사용: <site-factory venv> bgm/build_music.py [--tag v2]
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import sosfilt

HERE = Path(__file__).resolve().parent
EP = HERE.parent
ROOT = next(d for d in [HERE, *HERE.parents] if (d / ".akashic-root").exists())
sys.path.insert(0, str(ROOT / "projects/duru/영상소스/playlist_melty/bgm"))
import band  # noqa: E402
from band import SR, Song, bass_note, voice  # noqa: E402

TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "v4"
# 배역 악기(사용자 2026-11-09: v2 를 듣고 「피치카토 바꾸자 마림바 가보자」) — 커서 = 마림바. 화음 「짝」은 --chord 로 고른다(pizz = 비올라 뜯기 · piano = 업라이트 피아노).
CUR_INST = sys.argv[sys.argv.index("--cur") + 1] if "--cur" in sys.argv else "Marimba"
CHORD_INST = {"pizz": "ViolaEnsPizz", "piano": "VSUpright1"}[sys.argv[sys.argv.index("--chord") + 1] if "--chord" in sys.argv else "piano"]
TL = json.loads((EP / "timeline.json").read_text(encoding="utf-8"))
M, C = TL["meta"], TL["cues"]
BARS, BPB = M["bars"], M["bpb"]
BAR_N = M["spb"] * BPB

# ── 화음 지도(마디 → 화음) ────────────────────────────────────────────────────
HOME, SHY, PLAY, CARE = ["D", "E", "G", "D"], ["Dm", "Gm", "Eb", "A7"], ["Bm", "E", "G", "D"], ["D", "F#m", "Em", "G"]
CH = {}
for b in range(0, 4):
    CH[b] = "Dm"
for b in range(4, 16):
    CH[b] = SHY[(b - 4) % 4]
CH.update({16: "Gm", 17: "Dm/A", 18: "A7sus4", 19: "A7"})
for b in range(20, 36):
    CH[b] = HOME[(b - 20) % 4]
for b in range(36, 44):
    CH[b] = PLAY[(b - 36) % 4]
for b in range(44, 48):
    CH[b] = HOME[b - 44]
for b in range(48, 52):
    CH[b] = PLAY[b - 48]
for b in range(52, 56):
    CH[b] = HOME[b - 52]
for b in range(56, 68):
    CH[b] = CARE[(b - 56) % 4]
CH.update({68: "Em7", 69: "G", 70: "G", 71: "G#dim7", 72: "D/A", 73: "A7"})
for b in range(74, 78):
    CH[b] = HOME[b - 74]
CH.update({78: "G", 79: "D", 80: "D", 81: "D", 82: "G/D", 83: "D"})
for b in range(84, 92):
    CH[b] = HOME[(b - 84) % 4]
SIX = {"D": 9, "E": 9, "G": 9, "Bm": 8, "F#m": 8, "Em": 9, "Dm": 8, "Gm": 8, "Eb": 9, "A7": 8, "Em7": 9}   # 동기의 「6음」(단화음은 낮은 6음)
KICK, SNARE = (0, 8, 12), (4, 12)
ACT_GAIN = {"knock": 1.0, "shy": 0.85, "gifts": 0.85, "play": 1.05, "care": 0.58, "peak": 1.12, "turn": 0.66}
S16 = 0.25
TH = [(0, 1.0), (1, 0.5), (1.5, 0.5), (2, 2.0)]        # 주제 리듬(박, 길이) — 한 마디에 네 음: 길게 · 짧게 · 짧게 · 길게


def B(bar, beat=0.0):
    return bar * BPB + beat


def bar_of(beat):
    return int(beat // BPB)


def root_of(sym, base):
    r, q, _ = band.chord(sym.split("/")[0])
    return base + ((r - base) % 12), q


def call_notes(sym, base=62):
    """부르는 동기 3–5–6–5 (올라갔다 내려옴)."""
    r, q = root_of(sym, base)
    return [r + q[1], r + 7, r + SIX[sym.split("/")[0]], r + 7]


def resp_notes(sym, base=62):
    """받는 동기 5–3–2–3 (부르는 동기의 거울: +3,+2,−2 → −3,−2,+2)."""
    r, q = root_of(sym, base)
    return [r + 7, r + q[1], r + 2, r + q[1]]


def under_call(sym, base=62):
    """부르는 동기와 나란히 가는 아래 성부 1–3–4–3 (3도 아래). 4음은 이 곡 음계(라장조 + II 화음의 G#) 안으로."""
    r, q = root_of(sym, base)
    f = r + 5
    if f % 12 not in (2, 4, 6, 7, 9, 11, 1, 8):
        f += 1
    return [r, r + q[1], f, r + q[1]]


def under_resp(sym, base=62):
    """받는 동기와 나란히 가는 아래 성부 3–1–7–1 (3도 아래)."""
    r, q = root_of(sym, base)
    return [r + q[1], r, r - 1, r]


# ── 이 편 신작 합성 ──────────────────────────────────────────────────────────
def env_ar(n, a, r):
    e = np.ones(n)
    ka, kr = min(n, int(a * SR)), min(n, int(r * SR))
    if ka:
        e[:ka] = np.linspace(0, 1, ka)
    if kr:
        e[n - kr:] *= np.linspace(1, 0, kr)
    return e


def soft_kick(amp=1.0):
    """둥근 킥: 사인 96→54Hz 낙하 + 아주 짧은 톡. 바닥을 54Hz 에 둬서 안 들리는 저역이 헤드룸을 먹지 않게."""
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    f = 54 + 42 * np.exp(-t / 0.028)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.075)
    y[:48] += np.linspace(0.35, 0, 48) * np.sin(2 * np.pi * 1800 * t[:48])
    return y * env_ar(n, 0.001, 0.03) * amp


def tine(freq, dur=1.8, amp=1.0):
    """빗살(작은 엄지 피아노): 기음 + 살짝 어긋난 높은 부분음 둘이 금방 죽음 + 엄지 튕기는 톡."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.9) + 0.22 * np.sin(2 * np.pi * 3.01 * freq * t) * np.exp(-t / 0.16)
         + 0.10 * np.sin(2 * np.pi * 6.2 * freq * t) * np.exp(-t / 0.05))
    g = np.random.default_rng(int(freq))
    k = int(0.006 * SR)
    y[:k] += 0.18 * band.bp(g.standard_normal(k + 2000), 900, 2600)[1000:1000 + k] * np.linspace(1, 0, k)
    return y * env_ar(n, 0.002, 0.08) * amp * 0.26


def swish(amp=1.0, seed=2):
    """부채 한 번: 훅 — 바로 시작해서 0.3초에 걸쳐 잦아드는 바람."""
    n = int(0.34 * SR)
    g = np.random.default_rng(seed)
    x = band.bp(g.standard_normal(n + 4000), 500, 2400)[2000:2000 + n]
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.006) * np.exp(-t / 0.085)
    return x / (np.abs(x).max() + 1e-9) * env * amp * 0.5


def click(amp=1.0):
    """스탠드 스위치: 딸깍(두 번의 아주 짧은 톡)."""
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 2300 * t) * np.exp(-t / 0.004)
    k = int(0.045 * SR)
    y[k:] += 0.7 * np.sin(2 * np.pi * 1500 * t[:n - k]) * np.exp(-t[:n - k] / 0.006)
    return y * amp * 0.6


def add_at(s, bus, y, beat, gain=1.0, pan=0.0, send=0.0, lead=None):
    """소리 y 의 온셋(또는 lead 초)이 정확히 그 박에 오게 놓는다."""
    if lead is None:
        k = int(np.argmax(np.abs(y) > 0.15 * np.abs(y).max()))
        lead = k / SR
    s.add(bus, y, max(0.0, s.pos(beat) - lead), pan=pan, gain=gain, send=send)


def hit(s, bus, name, midi, beat, dur_b, vel=90, amp=1.0, pan=0.0, send=0.15, rel=0.1):
    """샘플 한 음을 **온셋이 그 박에 오게** 놓는다(어택이 느린 악기를 손짓에 맞출 때)."""
    y = band.sample_note(name, midi, dur_b * s.beat, vel=vel, rr=int(band.h01(beat, midi) * 97) + 1, release=rel)
    w = int(0.002 * SR)
    head = y[: int(0.12 * SR)]
    env = np.sqrt(np.convolve(head ** 2, np.ones(w) / w, mode="same"))[::w]
    d = env[3:] - env[:-3]
    lead = (int(np.argmax(d)) + 1.5) * w / SR
    add_at(s, bus, y * amp, beat, pan=pan, send=send, lead=lead)


def pz(s, midi, beat, vel=96, amp=1.0, pan=0.18, bus="cur", dur=0.8, send=0.16):
    """커서의 목소리 — 마림바(v2 까지는 솔로 바이올린 피치카토). 박에 정확히."""
    mar = CUR_INST == "Marimba"
    hit(s, bus, CUR_INST, midi, beat, max(dur, 1.2) if mar else dur, vel=vel, amp=amp * (0.9 + 0.1 * band.h01(midi, beat, 3)), pan=pan, send=send, rel=0.3 if mar else 0.25)


def cl(s, midi, beat, dur, vel=84, amp=1.0, stac=False, pan=-0.18, send=0.2):
    """두루의 목소리 — 클라리넷(기본 = 이어 부는 소리 · stac = 짧게)."""
    if stac:
        hit(s, "duru", "ClarinetStac", midi, beat, min(dur, 0.6), vel=vel, amp=amp, pan=pan, send=send, rel=0.1)
    else:
        band.inst(s, "duru", "ClarinetSus", midi, beat, dur * 0.94, vel=vel, amp=amp * 0.9, pan=pan, send=send + 0.05, human=0.0, rel=0.18, attack=0.02)


def phrase(s, bar, notes, who, amp=1.0, vel=None, beat0=0.0):
    """주제 리듬(TH)으로 한 마디. who = cur(피치카토) · duru(클라리넷) · oboe · tutti(호른+바이올린) · tine."""
    for (t, d), m in zip(TH, notes):
        b = B(bar, beat0 + t)
        if who == "cur":
            pz(s, m, b, vel=vel or 98, amp=amp, dur=d)
        elif who == "duru":
            cl(s, m, b, d, vel=vel or 84, amp=amp)
        elif who == "oboe":
            band.inst(s, "mel", "OboeSusVib", m, b, d * 0.95, vel=vel or 76, amp=amp * 2.0, pan=0.12, send=0.3, human=0.0, rel=0.25, attack=0.04)
        elif who == "tutti":
            band.inst(s, "mel", "FHornSus", m, b, d * 0.95, vel=100, amp=amp, pan=-0.1, send=0.25, human=0.0, rel=0.12, attack=0.01)
            band.inst(s, "mel", "ViolinEnsSusVib", m, b, d * 0.95, vel=96, amp=amp * 0.8, pan=0.15, send=0.28, human=0.0, rel=0.12, attack=0.01)
        elif who == "tine":
            add_at(s, "mel", tine(band.m2f(m), 1.2 + d, amp), b, lead=0.0, pan=0.1, send=0.35)


def knock(s, beat, inside=False, amp=1.0):
    """노크 — 클라베. 6막 두루의 노크는 같은 소리를 유리 안쪽에서(저역통과 + 조금 작게)."""
    sf = band.sfz("GM-StylePerc")
    r = [x for x in sf["regions"] if x["lokey"] <= 75 <= x["hikey"]][0]
    y = band.wav(os.path.join(sf["base"], sf["dpath"], r["sample"]))[: int(0.5 * SR)].copy() * 10 ** (r["volume"] / 20)
    if inside:
        y = sosfilt(band.sos(1500, "lowpass", 2), y) * 1.25
    add_at(s, "fx", y, beat, gain=amp * (0.8 if inside else 1.0), pan=0.3 if not inside else -0.1, send=0.3 if not inside else 0.12)


def drums(s, bar, lv, g=1.0, upto=16):
    """쿵 짝 쿵 짝. lv 1 = 킥만(「짝」은 화음이 맡는다) · 2 = + 스네어 탭(2·4박) · 3 = 스네어 타격(합주). 탬버린 없음."""
    if lv <= 0:
        return
    for k in range(upto):
        b = B(bar, k * S16)
        if k in KICK:
            add_at(s, "kick", soft_kick(1.0 if k == 0 else (0.8 if k == 8 else 0.6)), b, gain=g, lead=0.0)
        if k in SNARE:
            if lv >= 2:
                band.perc(s, 38 if lv >= 3 else 37, b, amp=(0.55 if lv >= 3 else 0.6) * g, pan=0.1, vel=96 if lv >= 3 else 84, send=0.1, dur=0.5, human=0.0, bus="snare")
        # 탬버린(흔드는 소리) 없음 — 사용자 2026-11-09 「잔잔하게 깔리는 잘그락 소리가 박자를 해치는 것 같아」: 흔드는 소리는 시작점이 뭉개져 박을 흐린다


def bass(s, bar, lv, g=1.0, upto=4):
    """저음 = 콘트라베이스 피치카토. lv 1 = 1박 근음 · 2 = 1박 근음 + 3박 5음."""
    if lv <= 0:
        return
    sym = CH[bar]
    r = bass_note(sym, 33, 45)
    f5 = bass_note(sym.split("/")[0], 33, 47, "fifth")
    for beat, m, v in (((0, r, 98), (2, f5, 84)) if lv >= 2 else ((0, r, 90),)):
        if beat < upto:
            band.inst(s, "bass", "ContrabassPizz", m, B(bar, beat), 1.6, vel=v, amp=g, pan=0.0, send=0.06, human=0.0, rel=0.3)


def comp(s, bar, lv, g=1.0, prev=None, upto=4):
    """화음 = 비올라 피치카토, 2·4박(짝)."""
    if lv <= 0:
        return prev
    v = voice(CH[bar].split("/")[0], 55, 71, prev, n=3)
    for beat in (1, 3):
        if beat < upto:
            for m in v:
                band.inst(s, "chord", CHORD_INST, m, B(bar, beat), 0.5, vel=74 if lv == 1 else 80, amp=g * (0.75 if lv == 1 else 0.9), pan=-0.05, send=0.14, human=0.004, rel=0.15)
    return v


def pad(s, bar, g=1.0, prev=None, dur=3.9, lo=50, hi=69):
    """조용한 현 지속음(비올라 합주 + 첼로 근음)."""
    v = voice(CH[bar].split("/")[0], lo, hi, prev, n=3)
    for m in v:
        band.inst(s, "pad", "ViolaEnsSusVib-Quiet", m, B(bar), dur, vel=70, amp=g, pan=0.08, send=0.3, human=0.0, rel=0.4, attack=0.12)
    band.inst(s, "pad", "CelloEnsSusVib-Quiet", bass_note(CH[bar], 38, 50), B(bar), dur, vel=70, amp=g * 0.9, pan=-0.08, send=0.25, human=0.0, rel=0.4, attack=0.12)
    return v


def drag_notes(s, t, hi=False):
    """끌어오기 = 커서 피치카토 세 음: 집는 음 · 한 박 뒤 · 내려놓는 음(도착 박). 달리기 음형 없음."""
    b0, b1 = t["b0"], t["b1"]
    c0, c1 = CH[bar_of(b0)], CH[bar_of(b1)] if bar_of(b1) in CH else CH[bar_of(b0)]
    n0, n1 = call_notes(c0, 62), call_notes(c1, 62)
    pz(s, n0[1], b0, vel=92, amp=0.85)
    pz(s, n0[2], b0 + 1, vel=86, amp=0.75)
    pz(s, n1[1] if not hi else n1[0] + 12, b1, vel=100, amp=0.95)


def main():
    s = Song(f"poke_long_{TAG}", "건드리면 반응하는 두루 — 롱폼", bpm=M["bpm"], bar=BPB, bars=BARS, swing=0.5, tail=0.0, lufs=-14.0)
    s.N = BARS * BAR_N
    for a in TL["acts"]:
        s.section(a["name"], a["bar0"], a["bar1"] - a["bar0"])
    touches = TL["touch"]

    # ════ 0막 노크 — 거의 침묵 ═══════════════════════════════════════════════
    for t in touches:
        if t["kind"] == "knock":
            knock(s, t["b"], amp=0.9)
    band.inst(s, "bass", "ContrabassPizz", 38, C["peek"], 1.5, vel=70, amp=0.8, send=0.2, human=0.0, rel=0.4)      # 빼꼼 — 뜯는 소리 한 음(D)
    pz(s, 65, C["peek"] + 2, vel=70, amp=0.3)                                                                       # …? (F — 단조 3음)
    pz(s, 62, C["hide"], vel=76, amp=0.3)                                                                           # 쏙

    # ════ 1막 낯가림 — 단조 · 살금살금 바탕(저음 1·3박 · 화음 2·4박 작게) ═════
    pv = None
    for bar in range(4, 16):
        quiet = bar in (13, 14)                                        # 볼 빵빵 두 마디는 저음만
        bass(s, bar, 1 if (quiet or bar < 6) else 2, g=0.85)
        if bar >= 6 and not quiet:
            pv = comp(s, bar, 1, g=0.7, prev=pv)
    pz(s, 69, C["tap_edge"], vel=92)                                   # 톡
    n = call_notes("Dm", 50)                                           # 다시 빼꼼 — 클라리넷이 낮게 동기 앞 두 음(경계)
    cl(s, n[0], C["peek2"] + 3, 1.0, vel=62, amp=0.7)
    cl(s, n[1], C["peek2"] + 4, 2.0, vel=62, amp=0.7)
    cl(s, 62, C["come_out"], 0.5, vel=80, amp=0.8, stac=True)          # 톡 튀어나옴
    # 콕 1 → 깜짝: 커서 = 동기 앞 두 음(미–솔) · 두루 = 위로 튀는 두 음
    n1 = call_notes("Dm", 62)
    pz(s, n1[0], C["poke1"], vel=104)
    pz(s, n1[1], C["poke1"] + 1, vel=92, amp=0.85)
    cl(s, 69, C["poke1"] + 2, 0.4, vel=96, stac=True)
    cl(s, 74, C["poke1"] + 2.5, 0.5, vel=100, stac=True)
    # 콕 2 → 싫어: 커서 같은 두 음 · 두루 = 낮게 떨어지는 두 음(NO–PE)
    n2 = call_notes("Eb", 62)
    pz(s, n2[0], C["poke2"], vel=104)
    pz(s, n2[1], C["poke2"] + 1, vel=92, amp=0.85)
    cl(s, 58, C["poke2"] + 2, 0.9, vel=110, amp=1.0)                   # B♭3
    cl(s, 51, C["poke2"] + 3, 1.6, vel=110, amp=1.0)                   # E♭3
    # 망설임 → 콕 3 → 볼 빵빵: 낮은 음이 커지며 버팀 → 툴툴 네 번 → 한숨 두 음
    for t in touches:
        if t["kind"] == "wiggle":
            pz(s, 76 if t["b0"] < B(20) else 78, t["b0"], vel=66, amp=0.55, dur=0.3)
            pz(s, 74 if t["b0"] < B(20) else 81, t["b0"] + 0.5, vel=62, amp=0.5, dur=0.3)
    n3 = call_notes("Gm", 62)
    pz(s, n3[0], C["poke3"], vel=108)
    pz(s, n3[1], C["poke3"] + 0.5, vel=96, amp=0.85)
    hold_b = C["puff_max"] + 2 - (C["poke3"] + 1)
    y = band.sample_note("ClarinetSus", 55, hold_b * s.beat, vel=96, rr=1, release=0.15)                # G3 — 볼이 부푸는 동안 점점 커짐
    y *= np.linspace(0.3, 1.0, len(y))
    s.add("duru", y * 0.8, s.pos(C["poke3"] + 1), pan=-0.18, send=0.2)
    for i in range(4):                                                  # 툴툴(손 휘젓기) — 낮은 두 음 번갈아
        cl(s, 51 if i % 2 == 0 else 50, C["puff_max"] + 2 + i * 0.5, 0.4, vel=92, amp=0.8, stac=True)
    cl(s, 62, C["puff_out"], 1.0, vel=66, amp=0.7)                     # 푸우 — 내려가는 한숨
    cl(s, 57, C["puff_out"] + 1, 1.4, vel=60, amp=0.65)
    pz(s, 76, C["back3"], vel=72, amp=0.6)                             # 커서 물러남 — 두 음 내려감(A7)
    pz(s, 73, C["back3"] + 1, vel=66, amp=0.55)
    # 서로 사과: 커서 꾸벅 = 두 음 한숨 ×2 · 두루 = 긴 두 음 · 현이 떠오름(해 뜸)
    for i, b in enumerate((C["bow"], C["bow"] + 2)):
        pz(s, 70 if i == 0 else 69, b, vel=80, amp=0.8)
        pz(s, 67 if i == 0 else 65, b + 0.5, vel=68, amp=0.65)
    cl(s, 65, C["sorry"], 2.0, vel=70)
    cl(s, 64, C["sorry"] + 2, 2.0, vel=64)
    pv = None
    for bar, g in ((16, 0.5), (17, 0.6), (18, 0.75), (19, 0.9)):
        pv = pad(s, bar, g=g, prev=pv)
        bass(s, bar, 1, g=0.8)
    cl(s, 62, B(18), 2.0, vel=66, amp=0.7)                              # 4→3 해결(D → C#)
    cl(s, 61, B(19), 2.8, vel=70, amp=0.75)

    # ════ 2막 선물 공세 — 같은 으뜸음 장조 · 바탕이 계속 깔리고 두루가 처음 대답한다 ════
    pv = pp = None
    for bar in range(20, 36):
        g = 0.85 if bar < 24 else 0.95
        drums(s, bar, 1, g=g)
        bass(s, bar, 2, g=g)
        pv = comp(s, bar, 1, g=g, prev=pv)
        pp = pad(s, bar, g=0.55, prev=pp, dur=4.0)                       # 조용한 현이 밑에서 이어 줌(저음·화음이 한 박씩 따로 드러나지 않게)
    for t in touches:
        if t["kind"] == "drag" and t["item"] in ("cup", "bun"):
            drag_notes(s, t)
    cl(s, 69, C["coffee"], 2.0, vel=64, amp=0.8)                        # 후— 한 모금(5 → 3)
    cl(s, 66, C["coffee"] + 2, 2.0, vel=60, amp=0.75)
    phrase(s, 24, resp_notes(CH[24]), "duru", amp=0.9, vel=72)          # ★두루의 첫 대답
    phrase(s, 25, call_notes(CH[25]), "cur")                            # 표정이 풀리는 마디 — 커서가 처음 동기를 끝까지 부른다
    rn = resp_notes("D", 62)                                            # 냠냠 — 짧게 네 음
    for j, bb in enumerate((0, 0.5, 1.5, 2)):
        cl(s, rn[j % 2], C["eat"] + bb, 0.4, vel=84, amp=0.85, stac=True)
    phrase(s, 28, call_notes(CH[28]), "cur")                            # 주제: 커서 두 마디 부르고
    phrase(s, 29, call_notes(CH[29]), "cur")
    phrase(s, 30, resp_notes(CH[30]), "duru", amp=0.7, vel=64)          # 두루 두 마디 받는다(수줍은 마디는 작게)
    phrase(s, 31, resp_notes(CH[31]), "duru", amp=0.95)
    phrase(s, 32, call_notes(CH[32]), "cur")                            # 고마워 — 한 마디씩 주고받기
    phrase(s, 33, resp_notes(CH[33]), "duru", amp=1.0, vel=90)
    phrase(s, 34, call_notes(CH[34]), "cur")
    for i, (m, m2) in enumerate(((66, 62), (69, 66), (71, 67), (74, 71))):   # 3막으로 — 둘이 같이 올라가는 네 음(3도)
        pz(s, m, B(35, i), vel=94, amp=0.9)
        cl(s, m2, B(35, i), 0.9, vel=86, amp=0.9)

    # ════ 3막 같이 놀기 — 북이 들어오고 둘이 나란히 부른다 ════════════════════
    pv = None
    for bar in range(36, 56):
        melt = 40 <= bar < 43
        air = bar == 49
        fall = bar == 50
        if melt:
            bass(s, bar, 1, g=0.8)
            continue
        if air or fall:
            continue
        lv = 1 if bar in (43, 47, 51, 54, 55) else 2
        g = 0.85 if bar >= 54 else 1.0
        drums(s, bar, lv, g=g)
        bass(s, bar, 2, g=g)
        pv = comp(s, bar, lv, g=g, prev=pv)
    for t in touches:                                                    # 쓰담: 쓸 때마다(1박) 커서 피치카토가 화음의 1–3–5–3음
        if t["kind"] == "pat":
            b, i = t["b0"], 0
            while b < t["b1"] - 1e-6:
                bar = bar_of(b)
                r, q = root_of(CH[bar], 62)
                m = (r, r + q[1], r + 7, r + q[1])[i % 4]
                soft = 40 <= bar < 43
                pz(s, m, b, vel=84 if not soft else 70, amp=0.8 if not soft else 0.55)
                b += t["every"]
                i += 1
    phrase(s, 37, call_notes(CH[37]), "duru", amp=0.95, vel=84)           # 쓰담 위에서 두루가 부르고 받는다(커서와 3도로 어울림)
    phrase(s, 38, resp_notes(CH[38]), "duru", amp=0.95, vel=84)
    phrase(s, 39, call_notes(CH[39]), "duru", amp=0.95, vel=84)
    pvv = None                                                            # 녹아내림: 조용한 현 위로 클라리넷이 길게 미끄러져 내려감(이 곡에서 미끄러지는 소리는 여기와 들기뿐)
    for bar in (40, 41, 42):
        pvv = pad(s, bar, g=0.5, prev=pvv)
    y = band.glide_note("ClarinetSus", 74, 62, 4.2 * s.beat, 0.4 * s.beat, 3.6 * s.beat, vel=72, release=0.35)
    s.add("duru", y * 0.42, s.pos(C["melt_max"] - 1), pan=-0.15, send=0.28)
    cl(s, 62, C["melt_max"] + 3.5, 3.0, vel=60, amp=0.7)
    for i, m in enumerate((62, 66, 69, 74)):                              # 돌아옴 — 올라가는 네 음
        cl(s, m, C["melt_end"] - 2 + i * 0.5, 0.4, vel=80, amp=0.8, stac=True)
    for t in touches:                                                     # 간지럼: 문지를 때마다(반박) 커서가 근음·5음을 번갈아 · 두루는 1박마다 깔깔(부르는 동기)
        if t["kind"] == "tickle":
            b, i = t["b0"], 0
            while b < t["b1"] - 1e-6:
                bar = bar_of(b)
                r, q = root_of(CH[bar], 62)
                pz(s, r + 12 if i % 2 == 0 else r + 7, b, vel=88, amp=0.75, dur=0.4)
                if i % 2 == 0:
                    cl(s, call_notes(CH[bar], 62)[(i // 2) % 4], b, 0.5, vel=90, amp=0.9, stac=True)
                b += t["every"]
                i += 1
    cl(s, 69, C["tickle1"], 0.5, vel=84, stac=True)                       # 숨 고르기 — 하, 하
    cl(s, 66, C["tickle1"] + 1, 0.5, vel=76, amp=0.8, stac=True)
    pz(s, 71, C["grab"], vel=104)                                         # 들기: 잡는 순간 톡 · 들리는 동안 클라리넷이 미끄러져 올라감
    liftb = C["lift_top"] - C["grab"]
    y = band.glide_note("ClarinetSus", 59, 71, (liftb + 1.5) * s.beat, 0.0, liftb * s.beat, vel=84, release=0.2)
    s.add("duru", y * 0.8, s.pos(C["grab"]), pan=-0.15, send=0.2)
    for i in range(8):                                                    # 공중 = 바탕이 사라지고 두루만 두 음을 번갈아(버둥)
        cl(s, 71 if i % 2 == 0 else 68, B(49, i * 0.5), 0.4, vel=80, amp=0.8, stac=True)
    pz(s, 79, C["drop"], vel=100)                                         # 놓음 — 떨어지는 두 음
    pz(s, 74, C["drop"] + 0.5, vel=96, amp=0.9)
    band.perc(s, 36, C["land"], amp=1.0, vel=110, send=0.12, dur=1.4, human=0.0, bus="fx")                 # 털썩 — 큰북 + 팀파니
    add_at(s, "fx", band.sample_note("Timpani", 43, 1.4, vel=112, rr=2, release=0.3), C["land"], gain=0.9, send=0.15)
    cl(s, 62, C["land"] + 2, 0.5, vel=70, amp=0.75, stac=True)            # 머쓱 — 두 음
    cl(s, 59, C["land"] + 3, 0.8, vel=64, amp=0.7)
    for bar, fn_c, fn_u in ((52, call_notes, under_call), (53, call_notes, under_call), (54, resp_notes, under_resp), (55, resp_notes, under_resp)):
        a = 1.0 if bar < 54 else 0.85                                     # 또 해 줘 · 하트: 주제를 둘이 3도로 같이(커서 위 · 두루 아래)
        phrase(s, bar, fn_c(CH[bar]), "cur", amp=a)
        phrase(s, bar, fn_u(CH[bar]), "duru", amp=a, vel=88)

    # ════ 4막 돌봐 주기 — 쉼. 북 없음 · 조용한 현 + 오보에 ════════════════════
    pv = None
    for bar in range(56, 68):
        g = 0.45 if bar < 64 else (0.55 if bar < 66 else 0.7)
        pv = pad(s, bar, g=g, prev=pv)
        bass(s, bar, 1, g=0.7)
    cl(s, 69, C["hot"], 2.0, vel=60, amp=0.7)                             # 더워 — 축 처진 두 음
    cl(s, 66, C["hot"] + 2, 3.5, vel=58, amp=0.7)
    for t in touches:
        if t["kind"] == "drag" and t["item"] in ("fan", "blanket"):
            drag_notes(s, t)
        if t["kind"] == "fan":                                            # 부채 한 번마다 바람
            b, i = t["b0"], 0
            while b < t["b1"] - 1e-6:
                add_at(s, "fx", swish(amp=0.8, seed=30 + i), b, lead=0.0, pan=-0.3 if i % 2 == 0 else 0.1, send=0.1)
                b += t["every"]
                i += 1
    phrase(s, 59, call_notes(CH[59]), "oboe", amp=0.85, vel=68)           # 시원 — 오보에가 주제를 부르고 받는다
    phrase(s, 60, resp_notes(CH[60]), "oboe", amp=0.85, vel=66)
    cl(s, 61, C["cold"] + 0.5, 1.5, vel=58, amp=0.6)                      # 추워 — 낮게 두 음
    cl(s, 59, C["cold"] + 2.5, 3.0, vel=56, amp=0.6)
    phrase(s, 64, call_notes(CH[64]), "oboe", vel=76)                     # 포근 — 오보에가 부르고
    phrase(s, 65, resp_notes(CH[65], 61), "duru", amp=0.9, vel=72)        # 클라리넷이 받는다
    for (t_, d), m in zip(((0, 1), (1, 1), (2, 4)), (67, 71, 74)):         # 포옹 — 둘이 같은 음으로 올라가 머문다
        band.inst(s, "mel", "OboeSusVib", m, C["hug"] + t_, d * 0.95, vel=82, amp=2.0, pan=0.12, send=0.3, human=0.0, rel=0.3, attack=0.04)
        cl(s, m - 12, C["hug"] + t_, d, vel=78)

    # ════ 5막 정점 — 기다림 → 박수 빌드(선율 없이 손끝만 올라감) → 숨 → 합주 → 발굽 ════
    pv = None
    for bar in (68, 69):
        pv = pad(s, bar, g=0.7, prev=pv)
    hb = C["hold0"]
    while hb < C["clap"] - 1e-6:                                           # 꾹 — 심장 뛰듯 킥이 매 박
        add_at(s, "kick", soft_kick(0.7), hb, lead=0.0)
        hb += 1.0
    pz(s, 67, C["hold0"], vel=92)
    deg = [d + 12 * o for o in (0, 1, 2) for d in (57, 59, 61, 62, 64, 66, 67)]        # A3 부터 라장조 음계
    for t in touches:
        if t["kind"] == "tap" and "build" in t:
            i = t["build"]
            m = deg[min(len(deg) - 1, i // 2)]
            if CH[bar_of(t["b"])].startswith("G#dim") and m % 12 == 7:
                m += 1                                                     # G#°7 마디는 G → G#
            pz(s, m, t["b"], vel=84 + min(30, i), amp=0.45 + 0.012 * i, dur=0.3)
    for bar in range(70, 74):                                              # 빌드: 저음 페달(8분) + 팀파니 굴림이 커짐 — 그 위에 손끝 소리만
        r = bass_note(CH[bar], 33, 45)
        for k in range(8 if bar < 73 else 4):
            band.inst(s, "bass", "ContrabassPizz", r, B(bar, k * 0.5), 0.45, vel=80 + 6 * (bar - 70), amp=0.6 + 0.12 * (bar - 70), send=0.06, human=0.0, rel=0.1)
    y = band.sample_note("TimpaniRolls", 45, (C["breath"] - C["clap"]) * s.beat, vel=100, rr=0, release=0.03)
    y *= np.linspace(0.08, 1.0, len(y)) ** 1.6
    s.add("fx", y * 0.8, s.pos(C["clap"]), send=0.12)
    # (숨 멈춤 C["breath"]~C["slam"] = 마스터 뒤에서 완전 무음으로 자른다)
    pv = None                                                              # 합주 4마디: 역할당 한 명 — 선율(호른+바이올린) · 저음 · 화음 · 북
    for bar in range(74, 78):
        last = bar == 77
        up = 8 if last else 16                                             # 끝 마디는 2박까지만(다가가는 숨죽임으로 넘어감)
        drums(s, bar, 3, g=1.0, upto=up)
        bass(s, bar, 2, g=1.0, upto=2 if last else 4)
        pv = comp(s, bar, 2, g=1.0, prev=pv, upto=2 if last else 4)
    phrase(s, 74, call_notes(CH[74]), "tutti")
    phrase(s, 75, call_notes(CH[75]), "tutti")
    phrase(s, 76, resp_notes(CH[76]), "tutti")
    for t_, d, m in ((0, 0.5, 66), (0.5, 0.5, 69), (1, 1.0, 74)):          # 끝 마디: 3–5–8(으뜸음으로 올라가 닿음)
        band.inst(s, "mel", "FHornSus", m, B(77, t_), d * 0.95, vel=100, amp=1.0, pan=-0.1, send=0.25, human=0.0, rel=0.12, attack=0.01)
        band.inst(s, "mel", "ViolinEnsSusVib", m, B(77, t_), d * 0.95, vel=96, amp=0.8, pan=0.15, send=0.28, human=0.0, rel=0.12, attack=0.01)
    add_at(s, "fx", band.sample_note("Timpani", 50, 1.6, vel=120, rr=1, release=0.3), C["slam"], gain=1.0, send=0.15)
    band.perc(s, 49, C["slam"], amp=0.55, pan=0.0, vel=100, send=0.2, dur=3.0, human=0.0, bus="fx")
    pz(s, 74, C["slam"], vel=110)
    band.inst(s, "pad", "ViolaEnsSusVib-Quiet", 69, B(77, 2), 1.9, vel=60, amp=0.6, send=0.3, human=0.0, rel=0.3, attack=0.1)     # 다가감 — 숨죽인 한 음
    # 발굽 맞대기: 커서와 두루가 **같은 음**(F#)을 같이 낸다 + 종 한 음. 화음 IV → I(조용한 마침)
    add_at(s, "fx", band.sample_note("TubularBells", 74, 3.0, vel=104, rr=1, release=0.8), C["hoof_touch"], gain=0.8, send=0.3)
    pz(s, 78, C["hoof_touch"], vel=104)
    cl(s, 66, C["hoof_touch"], 3.0, vel=72, amp=0.55)
    pv = pad(s, 78, g=0.8, prev=None)
    pad(s, 79, g=0.7, prev=pv)

    # ════ 6막 이번엔 두루가 — 자리 바꿈 · 빗살 자장가 ════════════════════════
    pv = None
    for bar in (80, 81, 82, 83):
        pv = pad(s, bar, g=0.5, prev=pv)
    cl(s, 57, C["look"], 0.5, vel=60, amp=0.7, stac=True)                  # 두리번 — 음? (올라가는 두 음)
    cl(s, 62, C["look"] + 1, 1.0, vel=64, amp=0.7)
    for b in TL["d_knocks"]:
        knock(s, b, inside=True, amp=0.9)                                  # ★두루의 노크(0막과 같은 소리 · 같은 박 모양 · 안쪽에서)
    pz(s, 69, C["startle"], vel=104)                                       # 커서가 움찔 — 1막 두루의 깜짝과 같은 몸짓을 커서의 목소리로
    pz(s, 74, C["startle"] + 0.5, vel=108)
    phrase(s, 84, call_notes(CH[84]), "duru", vel=84)                      # 자리 바꿈: 두루(클라리넷)가 부르고
    phrase(s, 85, resp_notes(CH[85]), "cur", vel=92)                       # 커서(피치카토)가 받는다
    for bar in (84, 85):
        pad(s, bar, g=0.45)
        bass(s, bar, 1, g=0.7)
    y = band.glide_note("ClarinetSus", 74, 69, 3.4 * s.beat, 0.6 * s.beat, 2.8 * s.beat, vel=60, release=0.4)                       # 하품 — 길게 내려감
    s.add("duru", y * 0.6, s.pos(C["sleepy"] + 1.5), pan=-0.15, send=0.3)
    for bar in (86, 87):
        pad(s, bar, g=0.4)
    add_at(s, "mel", tine(band.m2f(69), 2.4, 0.7), B(87), lead=0.0, pan=0.1, send=0.35)       # 빗살이 두 음으로 들어옴
    add_at(s, "mel", tine(band.m2f(66), 2.4, 0.7), B(87, 2), lead=0.0, pan=0.1, send=0.35)
    for bar in (88, 89, 90, 91):                                           # 자장가 = 주제를 빗살로(부르고 · 부르고 · 받고 · 맺음)
        a = 0.85 if bar < 90 else (0.6 if bar == 90 else 0.5)
        if bar == 91:
            for i, m in enumerate((66, 69, 71, 74)):
                add_at(s, "mel", tine(band.m2f(m), 2.6 if i == 3 else 1.8, a), B(bar, i), lead=0.0, pan=0.1, send=0.35)
        else:
            phrase(s, bar, (call_notes if bar < 90 else resp_notes)(CH[bar]), "tine", amp=a)
        add_at(s, "mel", tine(band.m2f(bass_note(CH[bar], 50, 61)), 3.0, a * 0.7), B(bar), lead=0.0, pan=0.1, send=0.35)
        if bar < 90:
            pad(s, bar, g=0.32)
    add_at(s, "fx", click(1.0), C["lamp_off"], lead=0.0, pan=-0.4, send=0.1)            # 스탠드 딸깍

    # ── 믹스 ─────────────────────────────────────────────────────────────────
    # 막별 페이더(모든 버스에 같은 곡선 · 막 경계 앞뒤 0.2초 코사인 넘김) — 이야기의 크기 순서를 값으로 정한다
    env = np.ones(s.N)
    edges = [(a["bar0"], ACT_GAIN[a["name"]]) for a in TL["acts"]]
    w = int(0.2 * SR)
    ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, 2 * w))
    for i, (b0, g) in enumerate(edges):
        a_ = b0 * BAR_N
        b_ = edges[i + 1][0] * BAR_N if i + 1 < len(edges) else s.N
        env[a_:b_] = g
    for i in range(1, len(edges)):
        c_ = edges[i][0] * BAR_N
        env[c_ - w:c_ + w] = edges[i - 1][1] + (edges[i][1] - edges[i - 1][1]) * ramp
    for k_ in list(s.bus):
        s.bus[k_][0] *= env
        s.bus[k_][1] *= env
    gains = {"cur": {"Marimba": 5.6, "SViolinPizz": 1.9}[CUR_INST], "duru": 1.6, "bass": 1.6, "chord": {"ViolaEnsPizz": 0.5, "VSUpright1": 0.32}[CHORD_INST],   # 악기를 바꾸면 샘플 크기가 달라진다(마림바 = 피치카토보다 약 9dB 작음 — 버스 표 실측)
              "pad": 0.42, "mel": 0.8, "kick": 0.7, "snare": 1.6, "tamb": 1.5, "fx": 0.8}   # 선율(커서·두루)이 바탕(화음)보다 위
    out = HERE / "out" / TAG
    rep = band.master(s, gains, rev_rt=1.5, rev_wet=0.24, out_dir=out, fade_out=0.6, tp_target=-1.5)
    # 숨 멈춤 = 완전 무음(잔향까지 자름) — 슬램이 빈 자리에서 터지게. 앞 15ms 로 닫고 슬램 샘플에서 바로 연다.
    sr, x = wavfile.read(out / "mix.wav")
    x = x.astype(np.float64)
    a, b_ = int(round(s.pos(C["breath"]) * SR)), int(round(s.pos(C["slam"]) * SR))
    k = int(0.015 * SR)
    x[a - k:a] *= np.linspace(1, 0, k)[:, None]
    x[a:b_] = 0
    wavfile.write(out / "mix.wav", SR, x.astype(np.int16))
    info = {"tag": TAG, "bars": BARS, "samples": len(x), "frames_30fps": len(x) / SR * 30, "bpm": M["bpm"], "lufs_before_breath_cut": rep.get("lufs"), "tp": rep.get("true_peak_db"),
            "section_lufs": rep.get("section_lufs"), "layers_mean": rep.get("layers_mean"), "layers_max": rep.get("layers_max"), "bus_section_lufs": rep.get("bus_section_lufs"),
            "max_resample_semitones": rep.get("max_resample_semitones"), "gains": gains, "breath_samples": [a, b_], "slam_sample": b_,
            "fingerprint": {"HOME": [2, 3, -5], "SHY": [5, -4, 6, 5], "PLAY": [5, 3, -5, -3], "CARE": [4, -2, 3, -5], "BUILD-bass": [1, 1, 0, 5], "SORRY-bridge": [-5, -5, 0, 5], "kick": list(KICK), "grid": "STEP8"}, "cursor_inst": CUR_INST, "chord_inst": CHORD_INST}
    (out / "report.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "stem_peaks.json").write_text(json.dumps({k_: float(max(np.abs(s.bus[k_][0]).max(), np.abs(s.bus[k_][1]).max())) for k_ in gains if k_ in s.bus}), encoding="utf-8")
    print(json.dumps({k_: info[k_] for k_ in ("bars", "samples", "frames_30fps", "tp", "section_lufs", "layers_mean", "layers_max")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
