"""T16 「별똥별 휘파람」 — C 12/8 ♩.=52 · DREAM 구간(마지막 곡 — 휘파람 자장가).

지문: 축1 DRIFT — I–vi–iii–IV (C–Am–Em–F) `[−3,−5,+1,−5]` 3도씩 가라앉다가 IV로 살짝 떠오름 (대장 미사용 · Axis I–V–vi–IV 와 음집합·순서 상이)
      축3 ROCK12 — 12/8 · 타악 없음 · 콘트라베이스 지속 {0,2}(점4분 1·3박) + 하프 셋잇단 분산 12개 (대장 전무)
음색: 리드 = 휘파람(합성) / B = 글로켄슈필 / 화음 = 하프 + 현 지속(조용) / 끝 = 미끄럼 휘슬 별똥별.
구성: 인트로2 · A16 · B8 · A16 · B8 · A8(잦아듦) · 아웃트로2 = 60마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, play  # noqa: E402

TAG, TITLE = "t16_whistle", "별똥별 휘파람"
A_CH = ["C", "Am", "Em", "F", "C", "Am", "Dm", "G7", "C", "Am", "Em", "F", "Dm", "G7", "C", "C"]
B_CH = ["F", "G", "Em", "Am", "F", "G", "C", "G7"]
AH = "E5:1 G5:2/3 E5:1/3 C5:2 | C5:1 E5:2/3 C5:1/3 A4:2 | B4:1 E5:2/3 G5:1/3 B5:2 | A5:2 G5:2/3 F5:1/3 E5:1 | "
A_MEL = line(AH + "E5:1 G5:2/3 C6:1/3 E6:2 | C6:1 B5:2/3 A5:1/3 E5:2 | F5:1 E5:2/3 D5:1/3 A5:2 | G5:3 r:1 | " + AH +
             "F5:1 A5:2/3 D6:1/3 C6:1 A5:1 | B5:1 D6:2/3 B5:1/3 G5:2 | C6:4 | r:4", bar=4)
B_MEL = line("A5:1 C6:1 F6:2 | G5:1 B5:1 D6:2 | E6:1 D6:2/3 B5:1/3 G5:2 | A5:2 E5:2 | F5:1 A5:1 C6:1 F6:1 | D6:2 B5:2 | "
             "C6:1 G5:1 E5:2 | D5:2 F5:1 B5:1", bar=4)
SECS = [("intro", 2), ("A1", 16), ("B1", 8), ("A2", 16), ("B2", 8), ("A3", 8), ("outro", 2)]


def whistle(s, notes, at, amp, semis=0, pan=-0.05, seed=0):
    ph = [(s.pos(at + b), d * s.beat * 0.97, m + semis) for b, d, m in notes]
    s.add("lead", B.whistle_phrase(ph, seed=seed) * amp, 0.0, pan=pan, send=0.35)


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=52, bar=4, bars=bars, swing=0.5, tail=6.0, lufs=-16.5)
    s.meta = {"fingerprint": "DRIFT×ROCK12", "key": "C", "stage": "DREAM"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["C", "G7"]
        elif name == "outro":
            chords += ["F", "Cadd9"]
        elif name == "A3":
            chords += A_CH[:6] + ["F", "C"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    for bar, sym in enumerate(chords):
        b = s.B(bar)
        last = bar == len(chords) - 1
        r = B.bass_note(sym, 33, 48)
        for q in ((0, 2) if not last else (0,)):
            inst(s, "bass", "ContrabassSusNV", r, b + q, 1.9 if not last else 5.0, vel=60, amp=0.6, pan=-0.05, send=0.3, rel=0.6, attack=0.06)
        v = B.voice(sym, 55, 72, prev=prev)
        prev = v
        inst(s, "chord", "ViolinEnsSusVib-Quiet", v[-1], b, 3.9 if not last else 5.5, vel=56, amp=0.35, pan=0.3, send=0.35, rel=0.8, attack=0.4)
        tones = v + [v[0] + 12]
        seq = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1] if not last else [0, 1, 2, 3, 4 % len(tones)]
        for i, k in enumerate(seq):
            inst(s, "chord", "Harp", tones[k % len(tones)], b + i / 3, 1.1, vel=60, amp=0.5 * (1.15 if i % 3 == 0 else 1.0), pan=0.2 - 0.03 * (i % 6), send=0.38, rel=0.6)
    whistle(s, A_MEL, s.B(st["A1"]), 0.25, seed=1)
    play(s, "lead", "Glockenspiel", B_MEL, at=s.B(st["B1"]), semis=-12, amp=5.0, pan=-0.05, send=0.4, rel=1.0, vel=90)
    whistle(s, A_MEL, s.B(st["A2"]), 0.25, seed=2)
    play(s, "resp", "FluteSusNV", [(b, d, m) for b, d, m in A_MEL if d >= 2], at=s.B(st["A2"]), semis=-12, amp=0.78, pan=0.25, send=0.35, rel=0.4, vel=60)
    play(s, "lead", "Glockenspiel", B_MEL, at=s.B(st["B2"]), semis=-12, amp=5.0, pan=-0.05, send=0.4, rel=1.0, vel=90)
    whistle(s, [n for n in A_MEL if n[0] < 24], s.B(st["A3"]), 0.21, seed=3)
    ob = s.B(st["outro"])
    inst(s, "color", "Glockenspiel", 96, ob + 4.5, 2.5, vel=64, amp=3.6, pan=0.35, send=0.5, rel=2.0)
    s.add("sfx", B.slide_whistle(91, 70, 1.6, seed=9) * 0.22, s.pos(ob + 5.2), pan=0.4, send=0.4)
    for sec in ("B1", "B2"):
        s.add("sfx", B.slide_whistle(93, 76, 1.2, seed=11) * 0.18, s.pos(s.B(st[sec]) - 1.2), pan=-0.4, send=0.4)
    gains = {"bass": 1.0, "chord": 0.9, "lead": 1.0, "resp": 0.9, "color": 0.8, "sfx": 0.5}
    return B.master(s, gains, rev_rt=2.4, rev_wet=0.38)


if __name__ == "__main__":
    build()
