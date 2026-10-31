"""T02 「콧방울 폴카」 — B♭ 2/4 ♩=120 · LIGHT 구간.

지문: 축1 CHROM-CLIMB I–#I°7–ii–V7 (B♭–B°7–Cm–F7) `[+1,+1,+5,+5]` — 근음이 반음씩 기어오르다 5도로 떨어짐(대장 미사용)
      축3 POLKA24 — 2/4 · 튜바 {1박 근음, 2박 5음} · 아코디언풍 리드 화음 {1&, 2&} · 스트레이트8 (대장에 2/4 박자 없음)
음색: 리드 = 피콜로 → 실로폰 → 클라리넷(B) → 플루트(트리오) / 화음 = 리드 합성 '아코디언' / 저음 = 튜바.
구성: 인트로4 · A16 · A16 · B16 · 트리오(E♭)16×2 · A16 · B16 · A16 · 코다4 = 152마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t02_polka", "콧방울 폴카"

A_CH = ["Bb", "Bb", "Bdim7", "Bdim7", "Cm", "Cm", "F7", "F7", "Bb", "Bb", "Bdim7", "Bdim7", "Cm", "F7", "Bb", "Bb"]
B_CH = ["Gm", "Gm", "Cm", "Cm", "F7", "F7", "Bb", "Bb", "Gm", "Gm", "Cm", "Cm", "F7", "F7", "Bb", "F7"]
C_CH = ["Eb", "Eb", "Bb7", "Bb7", "Bb7", "Bb7", "Eb", "Eb", "Eb", "Eb7", "Ab", "Abm", "Eb", "Bb7", "Eb", "F7"]
A_MEL = line("F5:.5 D5:.5 F5:.5 D5:.5 | Bb5:1 r:.5 F5:.5 | F5:.5 D5:.5 F5:.5 Ab5:.5 | G5:1 r:.5 F5:.5 | "
             "Eb5:.5 C5:.5 Eb5:.5 G5:.5 | F5:.5 Eb5:.5 D5:.5 C5:.5 | A4:.5 C5:.5 Eb5:.5 F5:.5 | D5:1 r:1 | "
             "F5:.5 D5:.5 F5:.5 D5:.5 | Bb5:1 r:.5 Bb5:.5 | B5:.5 Ab5:.5 F5:.5 D5:.5 | Eb5:1 r:.5 C5:.5 | "
             "Eb5:.5 G5:.5 C6:.5 G5:.5 | A5:.5 F5:.5 Eb5:.5 A4:.5 | Bb4:.5 D5:.5 F5:.5 Bb5:.5 | Bb5:.5 r:.5 Bb4:.5 r:.5", bar=2)
# 리스폰스(바순) — A 의 쉼표 자리만 채운다
A_RESP = line("r:2 | r:1.5 D3:.25 Eb3:.25 | r:2 | r:1.5 Eb3:.25 E3:.25 | r:2 | r:2 | r:2 | r:1 F3:.5 C3:.5 | "
              "r:2 | r:1.5 D3:.5 | r:2 | r:1.5 G3:.5 | r:2 | r:2 | r:2 | r:2", bar=2)
B_MEL = line("D5:.75 C5:.25 Bb4:.5 A4:.5 | G4:1 D5:1 | Eb5:.75 D5:.25 C5:.5 Bb4:.5 | G4:1 Eb5:1 | "
             "F5:.5 Eb5:.5 D5:.5 C5:.5 | A4:.5 Bb4:.5 C5:1 | D5:.5 F5:.5 Bb5:.5 F5:.5 | D5:1.5 r:.5 | "
             "D5:.75 C5:.25 Bb4:.5 A4:.5 | G4:1 D5:1 | Eb5:.75 D5:.25 C5:.5 Bb4:.5 | G4:1 G5:1 | "
             "F5:.5 A5:.5 C6:.5 A5:.5 | Eb5:.5 F5:.5 G5:.5 A5:.5 | Bb5:1 F5:.5 D5:.5 | C5:.5 D5:.5 Eb5:.5 E5:.5", bar=2)
C_MEL = line("G5:1.5 F5:.5 | Eb5:1 Bb4:1 | Ab5:1.5 G5:.5 | F5:2 | F5:.5 G5:.5 Ab5:.5 F5:.5 | D5:1 Bb4:1 | "
             "Eb5:.5 F5:.5 G5:.5 Eb5:.5 | Bb5:2 | G5:1.5 Ab5:.5 | G5:1 Db5:1 | C5:1.5 Eb5:.5 | Cb5:2 | "
             "Bb4:.5 Eb5:.5 G5:.5 Bb5:.5 | Ab5:1 F5:1 | Eb5:1.5 r:.5 | r:1 F4:.25 G4:.25 A4:.5", bar=2)

SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 16), ("C1", 16), ("C2", 16), ("A3", 16), ("B2", 16), ("A4", 16), ("coda", 4)]


def accordion(s, sym, b, dur_b, amp, prev):
    v = B.voice(sym, 58, 72, prev=prev)
    for i, m in enumerate(v):
        y = B.reed(B.m2f(m), dur_b * s.beat, amp=amp, vib=0.0035, bright=3000)
        s.add("chord", y, s.pos(b) + 0.002 * i, pan=0.22, send=0.12)
    return v


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=120, bar=2, bars=bars, swing=0.5)
    s.meta = {"fingerprint": "CHROM×POLKA24", "key": "Bb", "stage": "LIGHT"}
    plan = []
    b0 = 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    chords = []
    for name, st, n in plan:
        src = {"A": A_CH, "B": B_CH, "C": C_CH}.get(name[0], None)
        if name == "intro":
            chords += ["Bb", "F7", "Bb", "F7"]
        elif name == "coda":
            chords += ["Bb", "F7", "Bb", "Bb"]
        else:
            chords += src
    prev = None
    for bar, sym in enumerate(chords):
        name = next(nm for nm, st, n in plan if st <= bar < st + n)
        b = s.B(bar)
        last = bar == len(chords) - 1
        # 튜바: 1박 근음 · 2박 5음(트리오는 부드럽게)
        amp_t = {"intro": 0.9, "C1": 0.75, "C2": 0.85, "A4": 1.1}.get(name, 1.0) * 2.4
        inst(s, "bass", "TubaStac", B.bass_note(sym, 31, 46), b, 0.7, vel=100, amp=amp_t, send=0.05, rel=0.05)
        if not last:
            inst(s, "bass", "TubaStac", B.bass_note(sym, 31, 46, "fifth"), b + 1, 0.6, vel=92, amp=amp_t * 0.85, send=0.05, rel=0.05)
        # 아코디언 화음: 1& · 2&
        if name != "intro" or bar >= 2:
            if not last:
                for off in (0.5, 1.5):
                    prev = accordion(s, sym, b + off, 0.32, 0.55 if name[0] != "C" else 0.5, prev)
        # 타악: 로그드럼 고 '탁' 2박 · 트라이앵글 프레이즈 끝
        if name not in ("intro",) and not last:
            perc(s, 76, b + 1, amp=0.32, pan=0.25)
            if name[0] in "AB":
                perc(s, 77, b, amp=0.22, pan=-0.2)
        if name[0] in "AB" and bar % 8 == 7:
            perc(s, 81, b + 1.5, amp=0.35, pan=0.4, dur=1.5)
    # 선율
    st = {nm: st for nm, st, n in plan}
    play(s, "lead", "PiccoloStac", A_MEL, at=s.B(st["A1"]), semis=0, amp=0.8, pan=-0.05, send=0.15)
    play(s, "resp", "BassoonStac", A_RESP, at=s.B(st["A1"]), amp=0.75, pan=0.2)
    play(s, "lead", "Xylophone", A_MEL, at=s.B(st["A2"]), semis=0, amp=0.42, pan=-0.05, send=0.2, rel=0.3)
    play(s, "resp", "BassoonStac", A_RESP, at=s.B(st["A2"]), amp=0.75, pan=0.2)
    for sec in ("B1", "B2"):
        play(s, "lead", "ClarinetStac", B_MEL, at=s.B(st[sec]), amp=0.95, pan=-0.08, send=0.18)
    for b, d, m in B_MEL:                                   # B 콜에 실로폰 반짝(마디 첫 음만)
        if b % 2 == 0:
            for sec in ("B1", "B2"):
                inst(s, "color", "Glockenspiel", m + 12, s.B(st[sec]) + b, 0.5, vel=80, amp=0.35, pan=0.35, send=0.25, rel=0.4)
    play(s, "lead", "FluteSusNV", C_MEL, at=s.B(st["C1"]), amp=0.95, pan=-0.05, send=0.25, stac=0.92, rel=0.12)
    play(s, "lead", "ClarinetStac", C_MEL, at=s.B(st["C2"]), semis=-12, amp=0.9, pan=-0.1, send=0.2)
    play(s, "resp", "FluteSusNV", C_MEL, at=s.B(st["C2"]), amp=0.55, pan=0.15, send=0.25, stac=0.92, rel=0.12)
    play(s, "lead", "PiccoloStac", A_MEL[:len(A_MEL) // 2], at=s.B(st["A3"]), amp=0.8, pan=-0.05)
    play(s, "lead", "Xylophone", [n for n in A_MEL if n[0] >= 16], at=s.B(st["A3"]), amp=0.42, pan=0.05, rel=0.3)
    play(s, "resp", "BassoonStac", A_RESP, at=s.B(st["A3"]), amp=0.75, pan=0.2)
    play(s, "lead", "PiccoloStac", A_MEL, at=s.B(st["A4"]), amp=0.85, pan=-0.05)
    play(s, "resp", "ClarinetStac", A_MEL, at=s.B(st["A4"]), semis=-12, amp=0.55, pan=0.2)
    # 코다: B♭ 화음 탁 · 미끄럼 휘슬 내려가며 '퐁'
    cb = s.B(st["coda"])
    for m in B.voice("Bb", 58, 74):
        inst(s, "chord", "UprightPiano", m, cb + 4, 1.5, vel=96, amp=0.7, send=0.2, rel=0.4)
    inst(s, "color", "Glockenspiel", 82, cb + 4, 1.5, vel=90, amp=0.45, pan=0.3, send=0.3, rel=1.0)
    s.add("sfx", B.slide_whistle(72, 91, 0.7, seed=1) * 0.5, s.pos(s.B(3, 1.0)) - 0.1, pan=-0.2)
    s.add("sfx", B.slide_whistle(86, 67, 0.9, seed=2) * 0.45, s.pos(cb + 5), pan=0.3)
    s.add("sfx", B.sfx_pop() * 0.5, s.pos(cb + 6.5), pan=-0.2)
    for sec in ("A1", "A3"):                               # 8마디째 쉼표에 코풍선 '퐁'
        s.add("sfx", B.sfx_pop() * 0.35, s.pos(s.B(st[sec] + 7, 1.0)), pan=0.3)
    gains = {"bass": 1.0, "perc": 0.9, "chord": 0.85, "lead": 1.0, "resp": 0.95, "color": 0.8, "sfx": 0.55}
    return B.master(s, gains, rev_rt=1.0, rev_wet=0.28)


if __name__ == "__main__":
    build()
