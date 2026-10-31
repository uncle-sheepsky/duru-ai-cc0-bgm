"""T15 「달팽이 행진」 — A단조 4/4 ♩=64 · DEEP 구간(아주 느리고 진지한 척하는 달팽이).

지문: 축1 MINDESC — i–♭VI–iv–V (Am–F–Dm–E) `[−4,−3,+2,+5]` (heist i–VI–VII–V [−4,+2,−3,+5] 와 순서·벡터 상이 · 대장 미사용)
      B = 나란한조 C장조(꽃을 본 달팽이)
      축3 DIRGE — 큰북 {0} 하나 + 스네어 러프(꾸밈 16분 두 개 → 3박) + 팀파니 마디 첫박(A3) · 저음현 지속 (대장 킥세트 단독 {0} 전무)
음색: 리드 = 튜바(달팽이) → 튜바+바순 → 플루트(B) → 튜바+트롬본 3도 / 반짝 = 글로켄 / 저음 = 첼로 지속.
구성: 인트로4 · A16 · A16 · B8 · A16 · B8 · 아웃트로4 = 72마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t15_snail", "달팽이 행진"
A_CH = ["Am", "F", "Dm", "E", "Am", "F", "Dm", "E7", "Am", "F", "Dm", "E", "F", "Dm", "E", "Am"]
B_CH = ["C", "G", "Am", "Em", "F", "C", "Dm", "E"]
A_MEL = line("A3:1.5 B3:.5 C4:2 | A3:1.5 G3:.5 F3:2 | D3:1 F3:1 A3:1 D4:1 | B3:3 r:1 | C4:1.5 B3:.5 A3:1 E3:1 | F3:1.5 G3:.5 A3:2 | "
             "D4:1 C4:1 B3:1 A3:1 | G#3:3 r:1 | A3:.5 A3:.5 C4:1 E4:2 | F4:1.5 E4:.5 C4:2 | D4:.5 E4:.5 F4:.5 E4:.5 D4:1 A3:1 | "
             "G#3:1 B3:1 E4:2 | A3:1 C4:1 F4:1 E4:1 | D4:1 F4:1 A3:2 | B3:1 G#3:1 E3:2 | A3:3 r:1", bar=4)
B_MEL = line("E5:2 G5:2 | D5:3 B4:1 | C5:2 E5:1 A5:1 | G5:3 r:1 | A5:2 F5:1 C5:1 | E5:2 G5:2 | F5:1.5 E5:.5 D5:2 | B4:3 r:1", bar=4)
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 8), ("A3", 16), ("B2", 8), ("outro", 4)]


def third_below(notes):
    """A 화성단음계(G#)에서 온음계 3도 아래 — 트롬본 평행 3도. 음계 밖 음은 단3도 아래."""
    pcs = [9, 11, 0, 2, 4, 5, 8]
    out = []
    for b, d, m in notes:
        if m % 12 in pcs:
            tgt = pcs[(pcs.index(m % 12) - 2) % 7]
            n = m - 1
            while n % 12 != tgt:
                n -= 1
        else:
            n = m - 3
        out.append((b, d, n))
    return out


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=64, bar=4, bars=bars, swing=0.5, tail=4.0, lufs=-16.0)
    s.meta = {"fingerprint": "MINDESC×DIRGE", "key": "Am", "stage": "DEEP"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["Am", "Am", "Dm", "E"]
        elif name == "outro":
            chords += ["F", "Dm", "E", "Am"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar == len(chords) - 1
        light = name[0] == "B"
        inst(s, "bass", "CelloEnsSusVib-Quiet", B.bass_note(sym, 36, 52), b, 3.8 if not last else 6, vel=64, amp=0.55, pan=-0.1, send=0.25, rel=0.5, attack=0.08)
        if not light:
            perc(s, 36, b, amp=0.14, send=0.08, dur=1.4)
            perc(s, 37, b + 2 - 0.12, amp=0.05, pan=0.12, vel=50)
            perc(s, 37, b + 2 - 0.06, amp=0.06, pan=0.12, vel=55)
            perc(s, 38, b + 2, amp=0.09, pan=0.12, vel=80)
            if name in ("A3", "intro"):
                inst(s, "perc", "Timpani", B.bass_note(sym, 40, 52), b, 1.5, vel=90, amp=0.6, send=0.15)
        else:
            v = B.voice(sym, 57, 74)
            for i, m in enumerate(v + [v[1] + 12] + v[::-1]):
                inst(s, "chord", "Harp", m, b + i * 0.5, 1.0, vel=64, amp=0.85, pan=0.25, send=0.3, rel=0.5)
    play(s, "lead", "TubaSus", A_MEL, at=s.B(st["A1"]), amp=1.0, pan=-0.05, send=0.2, stac=0.92, rel=0.12, vel=90)
    play(s, "lead", "TubaSus", A_MEL, at=s.B(st["A2"]), amp=0.85, pan=-0.12, send=0.2, stac=0.92, rel=0.12, vel=90)
    play(s, "lead", "BassoonSus", A_MEL, at=s.B(st["A2"]), semis=12, amp=0.6, pan=0.12, send=0.2, stac=0.92, rel=0.12, vel=80)
    for b, d, m in A_MEL:
        if d >= 3:                                             # 쉬는 마디 끝 — 달팽이 끈적 반짝
            inst(s, "color", "Glockenspiel", m + 36, s.B(st["A2"]) + b + 3, 0.6, vel=70, amp=3.2, pan=0.35, send=0.35, rel=0.8)
    play(s, "lead", "FluteSusVib", B_MEL, at=s.B(st["B1"]), amp=1.0, pan=-0.05, send=0.3, stac=0.96, rel=0.25, vel=70)
    play(s, "lead", "TubaSus", A_MEL, at=s.B(st["A3"]), amp=1.0, pan=-0.08, send=0.2, stac=0.92, rel=0.12, vel=96)
    play(s, "resp", "TromboneSus", third_below(A_MEL), at=s.B(st["A3"]), semis=12, amp=0.45, pan=0.2, send=0.2, stac=0.92, rel=0.12, vel=80)
    play(s, "lead", "ClarinetSus", B_MEL, at=s.B(st["B2"]), semis=-12, amp=0.45, pan=-0.05, send=0.3, stac=0.96, rel=0.25, vel=70)
    for b, d, m in B_MEL:
        if b % 8 == 0:
            inst(s, "color", "Glockenspiel", m + 12, s.B(st["B2"]) + b, 0.8, vel=70, amp=3.2, pan=0.3, send=0.35, rel=0.8)
    # 아웃트로: 달팽이가 멈춰 잠듦 — 튜바 미끄러져 내려앉고 '퐁'
    ob = s.B(st["outro"])
    play(s, "lead", "TubaSus", line("A3:2 C4:2 | D4:2 F3:2 | E3:4 | r:4", bar=4), at=ob, amp=1.0, stac=0.95, rel=0.2, vel=90)
    y = B.glide_note("TubaSus", 45, 38, 3.0 * s.beat, 0.6, 2.6, vel=90)
    s.add("lead", y * 1.0, s.pos(ob + 12), pan=-0.05, send=0.25)
    s.add("sfx", B.sfx_pop() * 0.4, s.pos(ob + 15.5), pan=0.3)
    gains = {"bass": 1.0, "perc": 0.85, "chord": 0.85, "lead": 1.0, "resp": 0.9, "color": 0.8, "sfx": 0.5}
    return B.master(s, gains, rev_rt=1.8, rev_wet=0.32)


if __name__ == "__main__":
    build()
