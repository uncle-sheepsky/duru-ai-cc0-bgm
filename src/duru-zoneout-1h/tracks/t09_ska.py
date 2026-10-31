"""T09 「뒤척뒤척 스카」 — F 4/4 ♩=152 · LIGHT 구간(엎치락뒤치락).

지문: 축1 ROCK-IVBACK — I–IV–V–IV (F–B♭–C–B♭) `[+5,+2,−2,−5]` V에서 해결 안 하고 IV로 되돌아가는 왕복 · B는 vi–IV–V (대장 미사용)
      축3 ONEDROP-SKANK — 큰북·림 3박만 {8}(원 드롭) + 오르간 엇박 스캥크 {2,6,10,14} + 탬버린 셰이크 8분 (대장 킥세트 전무)
음색: 리드 = 트럼펫+트롬본 유니즌(스카 혼) / B = 멜로디카(리드 합성) / 화음 = 오르간 / 저음 = 콘트라베이스.
구성: 인트로8 · A16 · A16 · B16 · A16 · 덥8 · B16 · A16 · A16 · 아웃트로8 = 136마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t09_ska", "뒤척뒤척 스카"
A_CH = ["F", "Bb", "C", "Bb", "F", "Bb", "C", "C", "F", "Bb", "C", "Bb", "F", "C", "F", "F"]
B_CH = ["Dm", "Dm", "Bb", "Bb", "C", "C", "F", "F", "Dm", "Dm", "Bb", "Gm", "C", "C", "Bb", "C"]
H1 = ("A5:.5 r:.5 A5:.5 C6:.5 r:.5 A5:.5 G5:1 | F5:1.5 D5:.5 r:1 F5:.5 G5:.5 | E5:.5 r:.5 E5:.5 G5:.5 r:.5 E5:.5 C5:1 | "
      "D5:2 r:1 C5:.5 D5:.5 | ")
A_MEL = line(H1 + "F5:.5 r:.5 F5:.5 A5:.5 r:.5 C6:.5 Bb5:.5 A5:.5 | G5:1.5 F5:.5 D5:2 | E5:.5 G5:.5 C6:.5 G5:.5 E5:.5 G5:.5 Bb5:1 | A5:2 r:2 | "
             + H1 + "A5:.5 r:.5 A5:.5 C6:.5 r:.5 A5:.5 G5:1 | E5:1 G5:1 C6:1 Bb5:1 | A5:1.5 G5:.5 F5:2 | r:4", bar=4)
B_MEL = line("D6:2 A5:1 F5:1 | E5:1 F5:1 A5:2 | Bb5:2 F5:1 D5:1 | C5:1 D5:1 F5:2 | G5:2 E5:1 C5:1 | D5:1 E5:1 G5:2 | A5:3 G5:1 | F5:4 | "
             "D6:2 A5:1 F5:1 | E5:1 F5:1 A5:2 | Bb5:2 D6:2 | G5:2 Bb5:2 | C6:2 G5:1 E5:1 | G5:4 | F5:2 D5:2 | E5:2 G5:2", bar=4)
SECS = [("intro", 8), ("A1", 16), ("A2", 16), ("B1", 16), ("A3", 16), ("dub", 8), ("B2", 16), ("A4", 16), ("A5", 16), ("outro", 8)]


def melodica(s, notes, at, amp, semis=0, pan=-0.05):
    for b, d, m in notes:
        y = B.reed(B.m2f(m + semis), d * s.beat * 0.97 + 0.05, amp=amp, vib=0.007, bright=2400)
        s.add("lead", y, s.pos(at + b), pan=pan, send=0.25)


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=152, bar=4, bars=bars, swing=0.5, tail=3.0)
    s.meta = {"fingerprint": "ROCKIVBACK×ONEDROP-SKANK", "key": "F", "stage": "LIGHT"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name in ("intro", "dub", "outro"):
            chords += ["F", "Bb", "C", "Bb"] * 2
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar == len(chords) - 1
        dub = name == "dub"
        r = B.bass_note(sym, 29, 44)
        line_b = [(0, r, 1.0), (1, r + 7, 0.6), (1.5, r + 12, 0.5), (2, r, 0.9), (3, r + 7, 0.6), (3.5, r + 4, 0.5)]
        if last:
            line_b = [(0, r, 1.0)]
        for q, m, a in line_b:
            inst(s, "bass", "ContrabassPizz", m, b + q, 0.45, vel=100, amp=2.0 * a, pan=-0.05, send=0.06)
        if last:
            continue
        v = B.voice(sym, 57, 72, prev=prev, n=3)
        prev = v
        for q in (0.5, 1.5, 2.5, 3.5):
            if dub and q in (1.5, 3.5):
                continue
            for m in v:
                inst(s, "chord", "OrganQuiet", m, b + q, 0.22, vel=90, amp=4.6, pan=0.25, send=0.12 if not dub else 0.45, rel=0.03)
        if name != "intro" or bar >= 4:
            perc(s, 36, b + 2, amp=0.11, send=0.04, dur=0.8)
            perc(s, 37 if dub else 38, b + 2, amp=0.12, pan=0.1, vel=85)
            for q in range(8):
                perc(s, 53, b + q * 0.5, amp=0.3 if q % 2 else 0.18, pan=-0.3, vel=60, dur=0.15)
    for sec in ("A1", "A2", "A4", "A5"):
        play(s, "lead", "TrumpetStac", A_MEL, at=s.B(st[sec]), amp=0.63, pan=-0.12, send=0.18)
        play(s, "lead", "TromboneStac", A_MEL, at=s.B(st[sec]), semis=-12, amp=0.63, pan=0.12, send=0.18)
    melodica(s, B_MEL, s.B(st["B1"]), 1.0)
    play(s, "lead", "TromboneStac", A_MEL, at=s.B(st["A3"]), semis=-12, amp=1.2, pan=0.0, send=0.2)       # 트롬본 혼자
    play(s, "resp", "PiccoloStac", [n for n in A_MEL if n[1] == 0.5], at=s.B(st["A3"]), amp=0.45, pan=0.35, send=0.2)
    melodica(s, B_MEL, s.B(st["B2"]), 1.0)
    play(s, "resp", "PiccoloStac", A_MEL, at=s.B(st["A5"]), semis=12, amp=0.35, pan=0.35, send=0.2)
    # 덥: 혼 조각이 메아리처럼(지연 3/4박 · 2번)
    db = s.B(st["dub"])
    for k, g in ((0, 1.0), (0.75, 0.5), (1.5, 0.25)):
        play(s, "resp", "TrumpetStac", [n for n in A_MEL if n[0] < 4], at=db + k, amp=0.4 * g, pan=0.4 * (-1) ** int(k * 4 / 3), send=0.4)
        play(s, "resp", "TrumpetStac", [n for n in A_MEL if n[0] < 4], at=db + 16 + k, amp=0.4 * g, pan=0.4 * (-1) ** int(k * 4 / 3), send=0.4)
    s.add("sfx", B.slide_whistle(70, 89, 0.5, seed=5) * 0.45, s.pos(s.B(st["A1"]) - 0.75), pan=-0.3)
    ob = s.B(st["outro"])
    for m in B.voice("F", 53, 72):
        inst(s, "chord", "OrganQuiet", m, ob + 28, 2.5, vel=100, amp=4.0, send=0.3)
    inst(s, "lead", "TrumpetStac", 77, ob + 28, 1.0, amp=0.9)
    inst(s, "lead", "TromboneStac", 53, ob + 28, 1.0, amp=0.9)
    gains = {"bass": 1.0, "perc": 0.85, "chord": 0.85, "lead": 1.0, "resp": 0.9, "sfx": 0.5}
    return B.master(s, gains, rev_rt=1.0, rev_wet=0.28)


if __name__ == "__main__":
    build()
