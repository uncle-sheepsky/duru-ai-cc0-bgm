"""T03 「짝짝이 양말 행진곡」 — G 4/4 ♩=100 · LIGHT 구간.

지문: 축1 VofV — I–II7–V7–I (G–A7–D7–G) `[+2,+5,+5]` 2차 도미넌트(V의 V) 짧은 사슬 · 트리오 같은 골격 C로 + iv 차용(C–Cm)
      축3 MARCH-BB16 — 큰북 {0,8,10}(1박·3박·3박 뒷16분 '쿵 쿵쿵') + 스네어 탭 16분 러디먼트 + 호른 엇박{4,12} (대장 킥세트 전무)
음색: 리드 = 트럼펫 스타카토 → 약음기 트럼펫(트리오) / 엇박 = 호른 / 저음 = 튜바 / 쉬는 구간 = 휘파람.
구성: 인트로4 · A16 · A16 · 트리오16×2 · 쉬는 8 · A16 · 코다4 = 96마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t03_march", "짝짝이 양말 행진곡"
A_CH = ["G", "G", "A7", "A7", "D7", "D7", "G", "G", "G", "G7", "C", "Cm", "G", "A7", "D7", "G"]
T_CH = ["C", "C", "D7", "D7", "G7", "G7", "C", "C", "C", "C7", "F", "Fm", "C", "D7", "G7", "C"]
A_MEL = line("D5:.75 D5:.25 G5:1 B5:1 G5:1 | D5:.75 D5:.25 B4:1 G4:2 | E5:.75 E5:.25 A5:1 C#6:1 A5:1 | G5:1.5 F#5:.5 E5:1 r:1 | "
             "F#5:.75 F#5:.25 A5:1 C6:1 A5:1 | F#5:1 D5:1 A4:1 C5:1 | B4:.75 C5:.25 D5:1 G5:1 D5:1 | G5:1 r:1 G4:.5 A4:.5 B4:.5 C5:.5 | "
             "D5:.75 D5:.25 G5:1 B5:1 G5:1 | F5:.75 F5:.25 G5:1 B5:1 F5:1 | E5:1.5 G5:.5 C6:2 | Eb5:1.5 G5:.5 C6:2 | "
             "D5:.75 B4:.25 G4:1 D5:.75 B4:.25 G4:1 | C#5:.75 E5:.25 A5:1 G5:1 E5:1 | F#5:1 A5:1 C6:1 F#5:1 | G5:1 D5:.5 B4:.5 G4:1 r:1", bar=4)
T_MEL = line("E5:2 G5:2 | C6:3 r:1 | A5:2 F#5:1 D5:1 | C6:3 r:1 | B5:2 G5:1 F5:1 | D5:2 B4:2 | C5:1 E5:1 G5:1 C6:1 | E5:3 r:1 | "
             "E5:2 G5:2 | C6:2 B5:1 A5:1 | A5:2 C6:2 | Ab5:3 r:1 | G5:1 E5:1 C5:1 E5:1 | F#5:2 A5:2 | G5:1 F5:1 D5:1 B4:1 | C5:2 r:2", bar=4)
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("T1", 16), ("T2", 16), ("rest", 8), ("A3", 16), ("coda", 4)]


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=100, bar=4, bars=bars, swing=0.5)
    s.meta = {"fingerprint": "VofV×MARCH-BB16", "key": "G", "stage": "LIGHT"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["G", "G", "D7", "D7"]
        elif name == "rest":
            chords += ["G", "C", "G", "D7"] * 2
        elif name == "coda":
            chords += ["G", "D7", "G", "G"]
        elif name == "T2":
            chords += T_CH[:-1] + ["D7"]
        else:
            chords += T_CH if name[0] == "T" else A_CH
    prev = None
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar >= len(chords) - 2
        trio = name[0] == "T"
        # 큰북 {0, 8, 10} · 스네어 러디먼트(16분) · 섹션 첫 마디 심벌
        if not (name == "coda" and bar == len(chords) - 1):
            for q, a in ((0, 0.55), (8, 0.5), (10, 0.38)):
                perc(s, 36, b + q / 4, amp=a * (0.8 if trio else 1.0), pan=0.0, send=0.04, dur=0.9)
            if name != "intro" or bar >= 1:
                for q in (4, 12):
                    perc(s, 38, b + q / 4, amp=0.32 * (0.7 if name == "rest" else 1), pan=0.12, vel=80)
                for q in (6, 7, 13, 14, 15):
                    perc(s, 37, b + q / 4, amp=0.16, pan=0.12, vel=60)
        if (bar - 4) % 16 == 0 and name not in ("intro", "rest") and bar < len(chords) - 4:
            perc(s, 49, b, amp=0.3, pan=-0.3, dur=2.5, send=0.1)
        # 튜바 1·3박 근음/5음 · 4박 뒤 걷는 음
        tb = B.bass_note(sym, 31, 47)
        inst(s, "bass", "TubaStac", tb, b, 0.8, vel=100, amp=2.3, send=0.05, rel=0.05)
        if not last:
            inst(s, "bass", "TubaStac", B.bass_note(sym, 31, 47, "fifth"), b + 2, 0.8, vel=96, amp=2.1, send=0.05, rel=0.05)
        # 호른 엇박 2·4박
        if name not in ("intro", "rest") and not last:
            v = B.voice(sym, 55, 69, prev=prev, n=3)
            prev = v
            for q in (1, 3):
                for m in v:
                    inst(s, "chord", "FHornStac", m, b + q, 0.45, vel=88, amp=0.5, pan=0.25, send=0.15)
    # 선율
    play(s, "lead", "TrumpetStac", A_MEL, at=s.B(st["A1"]), amp=0.75, pan=-0.08, send=0.18)
    play(s, "lead", "TrumpetStac", A_MEL, at=s.B(st["A2"]), amp=0.7, pan=-0.08, send=0.18)
    play(s, "resp", "PiccoloStac", [n for n in A_MEL if n[1] <= 1.0 and (n[0] % 4) >= 2], at=s.B(st["A2"]), semis=12, amp=0.42, pan=0.35)
    # A2 마지막: 트롬본 미끄럼 하강(짝짝이 양말 개그)
    y = B.glide_note("TromboneSus", 55, 43, 1.6 * s.beat * 2, 0.1, 1.2, vel=90)
    s.add("resp", y * 0.6, s.pos(s.B(st["A2"] + 15, 2.0)), pan=0.2, send=0.2)
    for sec in ("T1", "T2"):
        mel = T_MEL if sec == "T1" else T_MEL[:-1] + [(60, 2, 69)]
        play(s, "lead", "TrumpetStraightMuteSus", mel, at=s.B(st[sec]), amp=0.48, pan=-0.05, send=0.22, rel=0.12)
    for b, d, m in T_MEL:
        if b % 8 == 0:
            inst(s, "color", "Glockenspiel", m + 12, s.B(st["T2"]) + b, 0.8, vel=84, amp=0.45, pan=0.3, send=0.3, rel=0.6)
    # 쉬는 8마디 — 휘파람이 A 첫 두 마디를 느슨하게
    wb = s.B(st["rest"])
    frag = [(s.pos(wb + b), d * s.beat * 0.95, m - 12) for b, d, m in A_MEL if b < 8] + \
           [(s.pos(wb + 16 + b), d * s.beat * 0.95, m - 12) for b, d, m in A_MEL if b < 8]
    s.add("lead", B.whistle_phrase(frag, seed=3) * 0.3, 0.0, pan=-0.1, send=0.25)
    play(s, "lead", "TrumpetStac", A_MEL, at=s.B(st["A3"]), amp=1.0, pan=-0.08, send=0.18)
    play(s, "resp", "TromboneStac", A_MEL, at=s.B(st["A3"]), semis=-12, amp=0.75, pan=0.2, send=0.15)
    cb = s.B(st["coda"])
    for m in B.voice("G", 55, 74):
        inst(s, "chord", "FHornStac", m, cb + 8, 1.0, vel=100, amp=0.7, send=0.2)
        inst(s, "chord", "TrumpetStac", m + 12, cb + 8, 0.8, vel=100, amp=0.5, send=0.2)
    inst(s, "bass", "TubaStac", 31, cb + 8, 1.0, vel=110, amp=2.6)
    perc(s, 49, cb + 8, amp=0.4, dur=3.0, send=0.15)
    s.add("sfx", B.boing(0.6) * 0.5, s.pos(cb + 10), pan=0.3, send=0.1)
    gains = {"bass": 1.0, "perc": 0.85, "chord": 0.8, "lead": 1.0, "resp": 0.9, "color": 0.8, "sfx": 0.55}
    return B.master(s, gains, rev_rt=1.3, rev_wet=0.3)


if __name__ == "__main__":
    build()
