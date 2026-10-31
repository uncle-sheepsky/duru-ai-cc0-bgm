"""T13 「부스러기 찰스턴」 — A♭ 4/4 ♩=168 · LIGHT 구간(과자 부스러기 흘리며 우다다).

지문: 축1 MAJAUG-iv — I–I+–IV–ivm (A♭–A♭+–D♭–D♭m) `[0,+5,0,−5]` 5음이 반음 올라 IV로 끌려갔다 단조로 시드는 머리 4마디 (대장 미사용)
      축3 CHARL — 튜바+밴조 찰스턴 리듬 {0,6}(1박·2박 뒷8분) + 밴조 2·4박 '처크' + 우드블록 (대장 킥세트 {0,6} 단독 전무)
      C = 스톱타임(1박 일격 후 클라리넷 혼자 채움)
음색: 리드 = 클라리넷(딕시) / B = 밴조 선율(카플러스-스트롱 밝게) / 응답 = 트롬본 '테일게이트' 글라이드 / 저음 = 튜바.
구성: 인트로4 · A16 · A16 · B16 · A16 · C16 · B16 · A16 · A16 · 아웃트로4 = 148마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t13_charleston", "부스러기 찰스턴"
A4 = ["Ab", "Ab+", "Db", "Dbm"]
A_CH = A4 + ["Ab", "F7", "Bb7", "Eb7"] + A4 + ["Ab", "Eb7", "Ab", "Ab"]
B_CH = ["Db", "Db", "Ab", "Ab", "Bb7", "Bb7", "Eb7", "Eb7", "Db", "Dbm", "Ab", "F7", "Bb7", "Eb7", "Ab", "Eb7"]
AH = "Eb5:1.5 C5:.5 Ab4:1 C5:1 | E5:1.5 C5:.5 Ab4:1 E5:1 | F5:1.5 Db5:.5 Ab4:1 F5:1 | Fb5:1.5 Db5:.5 Ab4:2 | "
A_MEL = line(AH + "Eb5:.5 F5:.5 Eb5:.5 C5:.5 Ab4:1 C5:1 | A4:.5 C5:.5 Eb5:.5 F5:.5 A5:1 F5:1 | Ab5:1.5 F5:.5 D5:1 Bb4:1 | "
             "G4:.5 Bb4:.5 Db5:.5 Eb5:.5 G5:2 | " + AH + "C6:1.5 Ab5:.5 Eb5:1 C5:1 | Db5:.5 C5:.5 Bb4:.5 G4:.5 Eb4:2 | "
             "Ab4:.5 C5:.5 Eb5:.5 Ab5:.5 C6:1 r:1 | Ab5:.5 r:.5 Eb5:.5 r:.5 Ab4:1 r:1", bar=4)
B_MEL = line("F5:1 Ab5:1 F5:1 Db5:1 | Ab4:.5 Bb4:.5 C5:.5 Db5:.5 F5:2 | Eb5:1 C5:1 Ab4:1 C5:1 | Eb5:3 r:1 | D5:1 F5:1 Ab5:1 F5:1 | "
             "D5:.5 Eb5:.5 F5:.5 Ab5:.5 Bb5:2 | G5:1 Eb5:1 Db5:1 Bb4:1 | G4:3 r:1 | F5:1 Ab5:1 Db6:1 Ab5:1 | Fb5:1 Ab5:1 Db6:2 | "
             "C6:1 Ab5:1 Eb5:1 C5:1 | Eb5:1 C5:1 A4:2 | Bb4:.5 D5:.5 F5:.5 Ab5:.5 Bb5:2 | G5:.5 F5:.5 Eb5:.5 Db5:.5 Bb4:2 | "
             "Ab4:1 C5:1 Eb5:1 Ab5:1 | G5:2 Eb5:2", bar=4)
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 16), ("A3", 16), ("C1", 16), ("B2", 16), ("A4", 16), ("A5", 16), ("outro", 4)]


def banjo(s, m, b, dur_b, amp, pan, bus="chord"):
    y = B.ks_pluck(m, max(0.3, dur_b * s.beat + 0.15), bright=0.95, decay=0.990, body=False)
    y = B.sosfilt(B.sos(500, "highpass"), y)
    s.add(bus, y * amp, s.pos(b) + (B.h01(b, m, 19) - 0.5) * 0.005, pan=pan, send=0.12)


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=168, bar=4, bars=bars, swing=0.5, tail=3.0)
    s.meta = {"fingerprint": "MAJAUGiv×CHARL", "key": "Ab", "stage": "LIGHT"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["Ab", "F7", "Bb7", "Eb7"]
        elif name == "outro":
            chords += ["Ab", "Eb7", "Ab", "Ab"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    fills = []
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        last = bar >= len(chords) - 2
        stop = name == "C1"
        tb = B.bass_note(sym, 32, 47)
        v = B.voice(sym, 55, 70, prev=prev, n=3)
        prev = v
        if stop:                                            # 스톱타임: 1박 일격만
            inst(s, "bass", "TubaStac", tb, b, 0.6, vel=110, amp=2.6, send=0.08)
            for m in v:
                banjo(s, m + 12, b, 0.4, 0.35, 0.2)
            perc(s, 76, b, amp=0.5, pan=0.3)
            # 클라리넷 채움: 2박부터 화음음 8분 상행 → 4박에서 꺾임
            tones = sorted(set(v + [x + 12 for x in v]))
            seq = tones[:5] + [tones[3]]
            fills += [(b + 1 + 0.5 * i, 0.45, m + 12) for i, m in enumerate(seq)]
            continue
        if last:
            if bar == len(chords) - 1:
                continue
            inst(s, "bass", "TubaStac", tb, b, 1.0, vel=110, amp=2.6, send=0.08)
            continue
        for q, m in ((0, tb), (1.5, B.bass_note(sym, 32, 47, "fifth"))):
            inst(s, "bass", "TubaStac", m, b + q, 0.6, vel=100, amp=2.3, send=0.06)
        for q in (0, 1.5):
            for m in v:
                banjo(s, m + 12, b + q, 0.3, 0.3, 0.22)
        for q in (1, 3):
            for m in v:
                banjo(s, m + 12, b + q, 0.2, 0.19, 0.28)
        if name != "intro":
            for q in (0, 1, 2, 3):
                perc(s, 76 if q % 2 else 77, b + q, amp=0.3 if q % 2 else 0.22, pan=0.3)
    for sec in ("A1", "A3", "A4"):
        play(s, "lead", "ClarinetStac", A_MEL, at=s.B(st[sec]), amp=0.95, pan=-0.08, send=0.18)
    play(s, "lead", "ClarinetStac", A_MEL, at=s.B(st["A2"]), amp=0.95, pan=-0.08, send=0.18)
    play(s, "lead", "ClarinetStac", A_MEL, at=s.B(st["A5"]), amp=0.95, pan=-0.12, send=0.18)
    play(s, "resp", "TrumpetStac", A_MEL, at=s.B(st["A5"]), amp=0.55, pan=0.15, send=0.18)
    for sec in ("B1", "B2"):
        for b, d, m in B_MEL:
            banjo(s, m, s.B(st[sec]) + b, d, 0.75, -0.08, bus="lead")
    play(s, "lead", "ClarinetStac", fills, at=0.0, amp=0.6, pan=-0.05, send=0.18)
    # 트롬본 테일게이트 — A 4·8·12마디 끝에서 '와앙' 미끄러져 내려감
    for sec in ("A1", "A2", "A3", "A4", "A5"):
        for k, (m0, m1) in ((3, (56, 51)), (7, (55, 50)), (11, (56, 51))):
            y = B.glide_note("TromboneSus", m0, m1, 1.4 * s.beat, 0.15, 0.95, vel=95)
            s.add("resp", y * 1.3, s.pos(s.B(st[sec] + k, 2.0)), pan=0.25, send=0.2)
    ob = s.B(st["outro"])
    for m in B.voice("Ab", 56, 75):
        banjo(s, m, ob + 8, 1.0, 0.4, 0.1)
    inst(s, "lead", "ClarinetStac", 80, ob + 8, 0.8, amp=1.0)
    inst(s, "bass", "TubaStac", 44, ob + 8, 0.8, amp=2.6)
    perc(s, 81, ob + 8.5, amp=0.6, dur=1.5)
    gains = {"bass": 1.0, "perc": 0.85, "chord": 0.85, "lead": 1.0, "resp": 0.9}
    return B.master(s, gains, rev_rt=1.0, rev_wet=0.24)


if __name__ == "__main__":
    build()
