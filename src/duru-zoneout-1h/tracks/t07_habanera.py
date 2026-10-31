"""T07 「이불 하바네라」 — D단조 2/4 ♩=66 · DEEP 구간(이불 속 느린 탱고).

지문: 축1 HAB — i–iv–♭VI–V7 (Dm–Gm–B♭–A7) `[+5,+3,−1,+5]` · B는 같은 으뜸의 장조로 밝아짐(D–G–A7) (대장 미사용)
      축3 HABANERA — 2/4 · 저음 하바네라 리듬 {0,3,4,6}(16분: 점8분·16분·8분·8분) + 피치카토 화음 {2,6} + 클라베 (대장 킥세트 전무)
음색: 리드 = 바순(능청) ↔ 오보에 / B = 오보에 / D = 바이올린 피치카토 솔로 / 저음 = 첼로+콘트라베이스 피치카토.
구성: 인트로4 · A16 · A16 · B16 · A16 · B16 · D16 · A16 · 코다4 = 120마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t07_habanera", "이불 하바네라"
A_CH = ["Dm", "Dm", "Gm", "Gm", "Bb", "Bb", "A7", "A7", "Dm", "Dm", "Gm", "Gm", "Bb", "A7", "Dm", "Dm"]
B_CH = ["D", "D", "G", "G", "A7", "A7", "D", "D", "D", "D7", "G", "Gm", "D", "A7", "D", "A7"]
A_MEL = line("A4:.75 Bb4:.25 A4:.5 G#4:.5 | A4:1.5 r:.5 | D5:.75 Eb5:.25 D5:.5 C#5:.5 | D5:1.5 r:.5 | "
             "F5:.5 E5:.5 D5:.5 C5:.5 | Bb4:1 D5:1 | C#5:.75 D5:.25 E5:.5 G5:.5 | F5:.5 E5:.5 C#5:1 | "
             "A4:.75 Bb4:.25 A4:.5 G#4:.5 | A4:.5 D5:.5 F5:.5 A5:.5 | G5:.75 F5:.25 E5:.5 D5:.5 | Bb5:1 G5:1 | "
             "F5:.75 G5:.25 F5:.5 D5:.5 | E5:.5 C#5:.5 A4:1 | D5:.75 E5:.25 F5:.5 A4:.5 | D5:1 r:1", bar=2)
B_MEL = line("F#5:1 A5:1 | F#5:.5 E5:.5 D5:1 | B5:1 D6:1 | B5:.5 A5:.5 G5:1 | A5:.75 G5:.25 F#5:.5 E5:.5 | C#5:1 E5:1 | "
             "D5:.5 F#5:.5 A5:.5 D6:.5 | A5:1.5 r:.5 | F#5:1 A5:1 | C6:1 A5:1 | B5:.75 A5:.25 G5:.5 D5:.5 | Bb5:1 G5:1 | "
             "A5:.5 F#5:.5 D5:1 | E5:.5 G5:.5 C#6:1 | D6:1 A5:1 | E5:1 r:1", bar=2)
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 16), ("A3", 16), ("B2", 16), ("D1", 16), ("A4", 16), ("coda", 4)]


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=66, bar=2, bars=bars, swing=0.5, tail=4.0, lufs=-16.0)
    s.meta = {"fingerprint": "HAB×HABANERA", "key": "Dm", "stage": "DEEP"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["Dm", "Dm", "A7", "A7"]
        elif name == "coda":
            chords += ["Dm", "A7", "Dm", "Dm"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar >= len(chords) - 2
        r = B.bass_note(sym, 31, 45)
        f5 = B.bass_note(sym, 31, 45, "fifth")
        if not last:
            for q, m, a in ((0, r, 1.0), (3, r, 0.55), (4, f5, 0.8), (6, r + 12, 0.6)):
                inst(s, "bass", "CelloEnsPizz", m + 12, b + q / 4, 0.5, vel=96, amp=0.9 * a, pan=-0.1, send=0.15, human=0.006)
                inst(s, "bass", "ContrabassPizz", m, b + q / 4, 0.5, vel=96, amp=1.25 * a, pan=-0.05, send=0.08, human=0.006)
            v = B.voice(sym, 55, 69, prev=prev, n=3)
            prev = v
            for q in (2, 6):
                for m in v:
                    inst(s, "chord", "ViolaEnsPizz", m, b + q / 4, 0.4, vel=88, amp=0.32, pan=0.25, send=0.2)
            if name != "intro":
                for q, a in ((0, 0.9), (3, 0.5), (4, 0.7), (6, 0.5)):
                    perc(s, 75, b + q / 4, amp=a * 1.5, pan=0.35, vel=70)
                if name[0] == "B":
                    perc(s, 54, b + 1, amp=1.0, pan=-0.35, vel=70)
    A = s.B(st["A1"])
    play(s, "lead", "BassoonStac", A_MEL, at=A, semis=-12, amp=1.0, pan=-0.05, send=0.2)
    play(s, "lead", "OboeStac", A_MEL, at=s.B(st["A2"]), amp=1.12, pan=-0.05, send=0.22)
    play(s, "resp", "BassoonStac", [n for n in A_MEL if n[1] >= 1], at=s.B(st["A2"]), semis=-12, amp=0.7, pan=0.25, send=0.2)
    play(s, "lead", "OboeSusNV", B_MEL, at=s.B(st["B1"]), amp=1.35, pan=-0.05, send=0.25, stac=0.92, rel=0.15, vel=80)
    play(s, "lead", "BassoonStac", A_MEL, at=s.B(st["A3"]), semis=-12, amp=1.0, pan=-0.1, send=0.2)
    play(s, "lead", "OboeStac", A_MEL, at=s.B(st["A3"]), amp=0.55, pan=0.1, send=0.2)
    play(s, "lead", "ClarinetSus", B_MEL, at=s.B(st["B2"]), semis=-12, amp=0.45, pan=-0.05, send=0.25, stac=0.92, rel=0.15, vel=72)
    play(s, "lead", "SViolinPizz", A_MEL, at=s.B(st["D1"]), semis=12, amp=1.7, pan=-0.05, send=0.25)
    play(s, "resp", "BassoonSus", [n for n in A_MEL if n[1] >= 1], at=s.B(st["D1"]), semis=-12, amp=0.38, pan=0.25, send=0.25, rel=0.2, vel=70)
    play(s, "lead", "BassoonStac", A_MEL, at=s.B(st["A4"]), semis=-12, amp=1.05, pan=-0.05, send=0.2)
    play(s, "resp", "OboeStac", [n for n in A_MEL if n[1] <= 0.5], at=s.B(st["A4"]), amp=0.5, pan=0.3, send=0.2)
    # 코다 — 탱고식 끝맺음 '둠… 둠!'(2박 앞박 → 2박 뒷8분)
    cb = s.B(st["coda"])
    for q, a in ((4.0, 0.7), (5.5, 1.0)):
        for m in B.voice("Dm", 50, 69):
            inst(s, "chord", "ViolaEnsPizz", m, cb + q, 0.5, vel=100, amp=0.8 * a, send=0.25)
        inst(s, "bass", "ContrabassPizz", 38, cb + q, 0.6, vel=110, amp=1.8 * a)
        inst(s, "lead", "BassoonStac", 38, cb + q, 0.5, vel=100, amp=1.0 * a)
    perc(s, 75, cb + 5.5, amp=0.8, pan=0.3)
    gains = {"bass": 1.0, "perc": 0.8, "chord": 0.85, "lead": 1.0, "resp": 0.9}
    return B.master(s, gains, rev_rt=1.4, rev_wet=0.3)


if __name__ == "__main__":
    build()
