"""T10 「구름 위 5박자」 — A 5/4 ♩=104 · DREAM 구간(한 박 모자란 듯 절뚝이는 몽롱함).

지문: 축1 DIA-PLANE — IVmaj7–iiim7–iim7–Imaj7 (Dmaj7–C#m7–Bm7–Amaj7) `[−1,−2,−2,+5]` 7화음이 계단처럼 미끄러져 내려와 앉음
      (chatlove 하행다이아 [−2,−1,−2,+5] 와 순환 회전 비교 — 불일치) · B는 vim7 축
      축3 FIVE4 — 5/4 · 3+2 묶음 · 첼로 지속 {0} + 하프 8분 분산 10개 · 트라이앵글 {0} 만 (대장에 5박자 없음)
음색: 리드 = 첼레스타(합성) / 응답 = 클라리넷 저음 지속 / 화음 = 하프 분산 / 저음 = 첼로 지속(조용).
구성: 인트로4 · A16 · A16 · B8 · A16 · B8 · A16 · 아웃트로4 = 88마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t10_five", "구름 위 5박자"
A_CH = ["Dmaj7", "C#m7", "Bm7", "Amaj7"] * 3 + ["Dmaj7", "C#m7", "E7sus4", "Amaj7"]
B_CH = ["F#m7", "F#m7", "Dmaj7", "Dmaj7", "Bm7", "C#m7", "Dmaj7", "E7sus4"]
A_MEL = line("F#5:1.5 E5:.5 C#5:1 A5:1 E5:1 | E5:1.5 G#5:.5 B5:1 G#5:1 E5:1 | D5:1.5 F#5:.5 A5:1 C#6:1 A5:1 | G#5:3 E5:2 | "
             "F#5:1.5 A5:.5 C#6:1 E6:1 C#6:1 | B5:1.5 G#5:.5 E5:1 G#5:1 B5:1 | A5:1.5 F#5:.5 D5:1 C#5:1 B4:1 | C#5:5 | "
             "F#5:1.5 E5:.5 C#5:1 A5:1 E5:1 | E5:1.5 G#5:.5 B5:1 G#5:1 E5:1 | D5:1.5 F#5:.5 A5:1 C#6:1 A5:1 | G#5:2 A5:1 B5:1 C#6:1 | "
             "D6:1.5 C#6:.5 A5:1 F#5:1 A5:1 | C#6:1.5 B5:.5 G#5:1 E5:1 G#5:1 | B5:1.5 A5:.5 F#5:1 D5:1 E5:1 | A5:5", bar=5)
B_MEL = line("C#6:2 A5:1 E5:2 | F#5:3 r:2 | A5:2 F#5:1 C#5:2 | E5:3 r:2 | D6:1.5 C#6:.5 B5:1 A5:1 F#5:1 | G#5:1.5 E5:.5 C#5:3 | "
             "F#5:1.5 A5:.5 D6:3 | E5:2 D5:1 B4:2", bar=5)
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 8), ("A3", 16), ("B2", 8), ("A4", 16), ("outro", 4)]


def cel(s, notes, at, amp, semis=0, pan=-0.05, bus="lead"):
    for b, d, m in notes:
        s.add(bus, B.celesta(B.m2f(m + semis), dur=max(1.4, d * s.beat + 1.0), amp=amp * (0.93 + 0.07 * B.h01(b, m))), s.pos(at + b), pan=pan, send=0.4)


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=104, bar=5, bars=bars, swing=0.5, tail=5.0, lufs=-16.5)
    s.meta = {"fingerprint": "DIAPLANE×FIVE4", "key": "A", "stage": "DREAM"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["Dmaj7", "C#m7", "Bm7", "Amaj7"]
        elif name == "outro":
            chords += ["Dmaj7", "C#m7", "Bm7", "Amaj9"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar == len(chords) - 1
        inst(s, "bass", "CelloEnsSusVib-Quiet", B.bass_note(sym, 33, 48) + 12, b, 4.6, vel=60, amp=0.38, pan=-0.1, send=0.3, rel=0.4, attack=0.15)
        v = B.voice(sym, 57, 74, prev=prev)
        prev = v
        notes = v + [v[0] + 12]
        seq = [0, 1, 2, 3, 4, 3, 2, 1, 2, 3] if not last else [0, 1, 2, 3, 4]
        for i, k in enumerate(seq):
            inst(s, "chord", "Harp", notes[k % len(notes)], b + i * 0.5, 1.4, vel=66, amp=0.6 * (1.0 if i not in (0, 6) else 1.25), pan=0.25 - 0.05 * (i % 5), send=0.35, rel=0.7)
        if name not in ("intro",) and not last:
            perc(s, 81, b, amp=0.6, pan=0.4, vel=60, dur=1.6, send=0.2)
    cel(s, A_MEL, s.B(st["A1"]), 0.31)
    cel(s, A_MEL, s.B(st["A2"]), 0.31)
    play(s, "resp", "ClarinetSus", [(b, d, m) for b, d, m in A_MEL if d >= 3], at=s.B(st["A2"]), semis=-12, amp=0.2, pan=0.25, send=0.35, rel=0.3, vel=60)
    play(s, "lead", "FluteSusNV", B_MEL, at=s.B(st["B1"]), semis=-12, amp=1.8, pan=-0.05, send=0.35, stac=0.95, rel=0.3, vel=64)
    cel(s, A_MEL, s.B(st["A3"]), 0.31)
    play(s, "resp", "FluteSusNV", [(b, d, m) for b, d, m in A_MEL if d >= 1.5], at=s.B(st["A3"]), semis=-12, amp=1.1, pan=0.3, send=0.35, rel=0.3, vel=60)
    cel(s, B_MEL, s.B(st["B2"]), 0.31)
    cel(s, A_MEL[:len(A_MEL) * 3 // 4], s.B(st["A4"]), 0.27)
    s.add("sfx", B.slide_whistle(76, 88, 0.9, seed=7) * 0.3, s.pos(s.B(st["B1"]) - 1.0), pan=0.3, send=0.3)
    ob = s.B(st["outro"])
    cel(s, line("C#6:5 | B5:5 | A5:5 | E6:5", bar=5), ob, 0.24)
    gains = {"bass": 1.0, "perc": 0.8, "chord": 0.9, "lead": 1.0, "resp": 0.9, "sfx": 0.5}
    return B.master(s, gains, rev_rt=2.2, rev_wet=0.36)


if __name__ == "__main__":
    build()
