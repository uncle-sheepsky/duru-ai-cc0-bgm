"""T05 「늘어진 양말 블루스」 — C 12/8 ♩.=60 · DEEP 구간(느릿느릿 셔플).

지문: 축1 BLUES12 — 12마디 블루스 I7–IV7–I7–I7 / IV7–IV7–I7–I7 / V7–IV7–I7–V7 (퀵체인지) (대장 미사용)
      축3 BLUES128 — 12/8 · 콘트라베이스 워킹 매 박 · 피아노 '처-커' {2박·4박 + 셋잇단 셋째} · 스네어 브러시 {2,4} · 셰이커 셋잇단 (12/8 백비트 대장 전무)
음색: 리드 = 하먼 약음기 트럼펫(와와) · 응답/솔로 = 클라리넷 저음(샬뤼모) · 피아노 코러스 / 저음 = 콘트라베이스 피치카토.
구성: 인트로4 · 헤드12 · 클라리넷12 · 피아노12 · 헤드12 · 엔딩4 = 56마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t05_blues", "늘어진 양말 블루스"
BL = ["C7", "F7", "C7", "C7", "F7", "F7", "C7", "C7", "G7", "F7", "C7", "G7"]
HEAD = line("G4:2/3 Bb4:1/3 C5:2 r:1 | Eb5:2/3 E5:1/3 C5:2 r:1 | G4:2/3 Bb4:1/3 C5:1 A4:2/3 G4:1/3 Eb4:1 | C4:2 r:2 | "
            "A4:2/3 C5:1/3 Eb5:2 r:1 | F5:2/3 Eb5:1/3 C5:1 A4:1 r:1 | G4:2/3 Bb4:1/3 C5:2 r:1 | E4:2/3 G4:1/3 Bb4:1 A4:1 r:1 | "
            "B4:2/3 D5:1/3 F5:2 D5:1 | Eb5:2/3 C5:1/3 A4:2 r:1 | G4:1 E4:1 C4:1 Eb4:2/3 E4:1/3 | G4:2 r:2", bar=4)
CLAR = line("C4:1 Eb4:2/3 E4:1/3 G4:1 Bb4:1 | A4:2/3 Ab4:1/3 G4:2 r:1 | C5:2/3 Bb4:1/3 G4:2/3 F4:1/3 Eb4:2/3 C4:1/3 r:1 | E4:3 r:1 | "
            "F4:2/3 A4:1/3 C5:2/3 Eb5:1/3 F5:2 | Eb5:2/3 C5:1/3 A4:2/3 F4:1/3 Ab4:2 | G4:1 E4:1 C4:2 | r:1 G3:2/3 Bb3:1/3 C4:2 | "
            "D4:2/3 F4:1/3 G4:2/3 B4:1/3 D5:2 | C5:2/3 A4:1/3 F4:2/3 Eb4:1/3 C4:2 | E4:1 G4:1 Bb4:1 A4:1 | G4:2 r:2", bar=4)
# 피아노 코러스 중 트럼펫 '와' 응답(마디 끝 셋잇단)
WAH = [(4 * k + 3, 2 / 3, m) for k, m in ((0, 70), (1, 69), (4, 75), (5, 72), (8, 74), (9, 72))]
SECS = [("intro", 4), ("H1", 12), ("S1", 12), ("P1", 12), ("H2", 12), ("end", 4)]


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=60, bar=4, bars=bars, swing=0.5, tail=4.0, lufs=-16.0)
    s.meta = {"fingerprint": "BLUES12×BLUES128", "key": "C", "stage": "DEEP"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = ["G7", "F7", "C7", "G7"] + BL * 4 + ["C7", "F7", "C7", "C9"]
    prev = None
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar == len(chords) - 1
        r = B.bass_note(sym, 28, 43)
        # 워킹: 근음 · 3음 · 5음 · 6음(마디 끝은 다음 근음 반음 위/아래로)
        nxt = B.bass_note(chords[bar + 1], 28, 43) if bar + 1 < len(chords) else r
        walk = [r, r + 4, r + 7, r + 9] if not last else [r]
        if bar + 1 < len(chords) and nxt != r:
            walk[3] = nxt + (1 if nxt < r + 9 else -1)
        for i, m in enumerate(walk):
            inst(s, "bass", "ContrabassPizz", m, b + i, 0.9, vel=95, amp=1.65, pan=-0.05, send=0.12, human=0.012)
        if last:
            continue
        v = B.voice(sym, 55, 70, prev=prev)
        prev = v
        for q in (1, 1 + 2 / 3, 3, 3 + 2 / 3):          # '처-커' — 2·4박 + 셋잇단 셋째
            a = 0.42 if q % 1 == 0 else 0.3
            for m in v:
                inst(s, "chord", "UprightPiano", m, b + q, 0.28, vel=80, amp=1.6 * a * (0.8 if name == "P1" else 1.0), pan=0.25, send=0.15, human=0.008)
        if name != "intro":
            for q in (1, 3):
                perc(s, 37, b + q, amp=0.9, pan=0.15, vel=90)
            for q in range(4):
                perc(s, 53, b + q + 2 / 3, amp=0.28, pan=0.4, vel=60, dur=0.25)
    play(s, "lead", "TrumpetHarmonMuteSus", HEAD, at=s.B(st["H1"]), amp=1.05, pan=-0.08, send=0.22, rel=0.14, human=0.015)
    play(s, "lead", "ClarinetSus", CLAR, at=s.B(st["S1"]), amp=0.48, pan=-0.05, send=0.22, rel=0.12, human=0.015, vel=80)
    play(s, "lead", "UprightPiano", HEAD, at=s.B(st["P1"]), semis=12, amp=5.0, vel=104, pan=-0.12, send=0.2, rel=0.2, human=0.01)
    play(s, "resp", "TrumpetHarmonMuteSus", WAH, at=s.B(st["P1"]), amp=0.75, pan=0.25, send=0.2, rel=0.1)
    play(s, "lead", "TrumpetHarmonMuteSus", HEAD, at=s.B(st["H2"]), amp=1.15, pan=-0.08, send=0.22, rel=0.14, human=0.015)
    play(s, "resp", "ClarinetSus", [n for n in HEAD if n[1] >= 1], at=s.B(st["H2"]), semis=-12, amp=0.2, pan=0.2, send=0.2, rel=0.2, vel=64)
    # 엔딩 — 약음기 트럼펫 '와 와 와 와아~' 반음 하강 + 피아노 C9 트레몰로
    eb = s.B(st["end"])
    for i, m in enumerate((67, 66, 65)):
        inst(s, "lead", "TrumpetHarmonMuteSus", m, eb + 4 + i * 1.0, 0.8, vel=90, amp=1.9, pan=-0.05, send=0.25, rel=0.1)
    y = B.glide_note("TrumpetHarmonMuteSus", 64, 63, 2.6 * s.beat, 0.6, 2.4, vel=90)
    s.add("lead", y * 1.9, s.pos(eb + 7), pan=-0.05, send=0.3)
    for k in range(9):
        for m in B.voice("C9", 55, 74):
            inst(s, "chord", "UprightPiano", m, eb + 12 + k / 3, 0.3, vel=70, amp=0.3 * (1 - k / 10), pan=0.2, send=0.25)
    inst(s, "bass", "ContrabassPizz", 36, eb + 12, 2.0, vel=100, amp=1.4)
    gains = {"bass": 1.0, "perc": 0.8, "chord": 0.8, "lead": 1.0, "resp": 0.9}
    return B.master(s, gains, rev_rt=1.4, rev_wet=0.3)


if __name__ == "__main__":
    build()
