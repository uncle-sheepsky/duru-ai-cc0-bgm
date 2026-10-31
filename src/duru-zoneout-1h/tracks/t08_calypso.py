"""T08 「꼬르륵 칼립소」 — C 4/4 ♩=104 · LIGHT 구간(뒤척인 뒤 배꼽시계).

지문: 축1 CALY — I–I7–IV–iv6–I–V7 (C–C7–F–Fm6–C–G7) 같은 근음 위 7음·장→단 색만 바꾸며 도는 칼립소 순환 (대장 미사용)
      축3 TRES16 — 베이스 트레실로 {0,6,12}(3+3+2) + 우쿨렐레 엇박 스트럼 {2,6,10,14} + 카우벨 {4,12} + 셰이커 16분 (대장 킥세트 전무)
음색: 리드 = 스틸팬(합성) / 응답·B = 트롬본 / A3 = 우쿨렐레 선율(카플러스-스트롱) / 화음 = 우쿨렐레 스트럼 / 저음 = 콘트라베이스.
구성: 인트로4 · A16 · A16 · B8 · A16 · B8 · A16 · B8 · A16 · 아웃트로4 = 112마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t08_calypso", "꼬르륵 칼립소"
A8 = ["C", "C7", "F", "Fm6", "C", "G7", "C", "G7"]
A_CH = A8 + A8[:6] + ["C", "C"]
B_CH = ["F", "F", "C", "C", "G7", "G7", "C", "G7"]
A_HEAD = ("E5:.5 G5:.5 r:.5 E5:.5 G5:1 E5:1 | Bb5:.5 G5:.5 r:.5 E5:.5 G5:2 | A5:.5 C6:.5 r:.5 A5:.5 C6:1 A5:1 | "
          "Ab5:.5 F5:.5 r:.5 D5:.5 F5:2 | E5:.75 F5:.25 G5:.5 E5:.5 C5:1 E5:1 | D5:.5 F5:.5 r:.5 B4:.5 D5:2 | ")
A_MEL = line(A_HEAD + "C5:.5 E5:.5 G5:.5 C6:.5 E6:1 C6:1 | B5:.5 A5:.5 G5:.5 F5:.5 D5:1 r:1 | " + A_HEAD +
             "C5:.5 E5:.5 G5:.5 C6:.5 G5:1 E5:1 | C5:2 r:2", bar=4)
B_MEL = line("C6:1.5 A5:.5 F5:2 | G5:.5 A5:.5 Bb5:.5 A5:.5 G5:2 | E5:1.5 G5:.5 C6:2 | r:1 E5:.5 F5:.5 G5:2 | "
             "F5:1.5 D5:.5 B4:2 | r:.5 B4:.5 D5:.5 F5:.5 A5:2 | G5:1 E5:1 C5:2 | D5:.5 E5:.5 F5:.5 G5:.5 B5:2", bar=4)
RESP = [(4 * k + 2.5, 0.5, m) for k, m in ((0, 55), (1, 58), (2, 57), (3, 56), (5, 53), (7, 55), (8, 55), (9, 58), (10, 57), (11, 56), (13, 53))]
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 8), ("A3", 16), ("B2", 8), ("A4", 16), ("B3", 8), ("A5", 16), ("outro", 4)]


def pan_line(s, notes, at, amp, semis=0, pan=-0.05, bus="lead"):
    for b, d, m in notes:
        s.add(bus, B.steelpan(B.m2f(m + semis), dur=max(0.8, d * s.beat + 0.5), amp=amp), s.pos(at + b), pan=pan, send=0.22)


def uke(s, m, b, dur_b, amp, pan, bus="chord", bright=0.7):
    y = B.ks_pluck(m, max(0.35, dur_b * s.beat + 0.2), bright=bright, decay=0.994)
    s.add(bus, y * amp, s.pos(b) + (B.h01(b, m, 13) - 0.5) * 0.006, pan=pan, send=0.15)


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=104, bar=4, bars=bars, swing=0.5, tail=3.5)
    s.meta = {"fingerprint": "CALY×TRES16", "key": "C", "stage": "LIGHT"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["C", "F", "G7", "G7"]
        elif name == "outro":
            chords += ["C", "G7", "C", "C"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar >= len(chords) - 2
        r = B.bass_note(sym, 33, 48)
        f5 = B.bass_note(sym, 33, 48, "fifth")
        hits = ((0, r, 1.0), (1.5, r, 0.7), (3.0, f5, 0.85)) if not last else ((0, r, 1.0),)
        for q, m, a in hits:
            inst(s, "bass", "ContrabassPizz", m, b + q, 1.2 if q < 3 else 0.9, vel=96, amp=1.6 * a, pan=-0.05, send=0.08)
        if last:
            continue
        v = B.voice(sym, 57, 72)                       # 우쿨렐레 자리(높은 밀집)
        for q in (0.5, 1.5, 2.5, 3.5):
            for i, m in enumerate(v):
                uke(s, m, b + q + 0.012 * i, 0.4, 0.2, 0.2 + 0.04 * i)
        if name != "intro":
            for q in (1, 3):
                perc(s, 56, b + q, amp=0.35, pan=0.35, vel=70)
        for q in range(16):
            perc(s, 53, b + q * 0.25, amp=0.42 if q % 2 == 0 else 0.26, pan=-0.35, vel=60, dur=0.18)
    pan_line(s, A_MEL, s.B(st["A1"]), 0.36)
    pan_line(s, A_MEL, s.B(st["A2"]), 0.36)
    play(s, "resp", "TromboneStac", RESP, at=s.B(st["A2"]), amp=1.35, pan=0.25, send=0.18)
    play(s, "lead", "TromboneStac", B_MEL, at=s.B(st["B1"]), semis=-12, amp=1.6, pan=-0.05, send=0.2)
    for b, d, m in A_MEL:
        uke(s, m, s.B(st["A3"]) + b, d, 0.75, -0.08, bus="lead", bright=0.8)
    pan_line(s, RESP, s.B(st["A3"]), 0.33, semis=12, pan=0.3, bus="resp")
    pan_line(s, B_MEL, s.B(st["B2"]), 0.36)
    pan_line(s, A_MEL, s.B(st["A4"]), 0.36)
    play(s, "resp", "TromboneStac", A_MEL, at=s.B(st["A4"]), semis=-12, amp=0.9, pan=0.25, send=0.18)
    for b, d, m in B_MEL:
        uke(s, m, s.B(st["B3"]) + b, d, 0.75, -0.08, bus="lead", bright=0.8)
    pan_line(s, A_MEL, s.B(st["A5"]), 0.36)
    play(s, "resp", "TromboneStac", RESP, at=s.B(st["A5"]), amp=1.35, pan=0.25, send=0.18)
    ob = s.B(st["outro"])
    pan_line(s, line("C6:1 G5:1 E5:1 C5:1 | r:4 | C6:4", bar=4), ob, 0.36)
    s.add("sfx", B.boing(0.55) * 0.45, s.pos(ob + 6), pan=0.3)
    s.add("sfx", B.sfx_pop() * 0.4, s.pos(ob + 3.5), pan=-0.3)
    gains = {"bass": 1.0, "perc": 0.8, "chord": 0.85, "lead": 1.0, "resp": 0.9, "sfx": 0.55}
    return B.master(s, gains, rev_rt=1.1, rev_wet=0.26, tp_target=-2.5)   # 스틸팬 어택이 AAC 후 +1.2dB 튐(실측)


if __name__ == "__main__":
    build()
