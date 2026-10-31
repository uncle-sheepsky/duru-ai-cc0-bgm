"""T04 「베개 왈츠」 — E♭ 3/4 ♩=96 · DEEP 구간(느리고 멍한 자장가).

지문: 축1 STEP-UP I–ii–iii–IV + iv 차용 (E♭–Fm–Gm–A♭ … A♭m) `[+2,+2,+1,−5]` 이불 속으로 한 칸씩 기어오르다 하품(대장 미사용)
      축3 WALTZ3 — 3/4 · 첼로 피치카토 {1박} · 하프 {2·3박} '쿵짝짝' · 타악 없음 (대장에 3/4 박자 없음)
음색: 리드 = 오르골(합성) → 플루트(B) → 클라리넷(B2) / 화음 = 하프 / 저음 = 첼로 피치카토 / 개그 = 바순 하품 글라이드.
구성: 인트로4 · A16 · A16 · B16 · A16 · B16 · A16 · A16(잠듦) · 아웃트로8 = 124마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, play  # noqa: E402

TAG, TITLE = "t04_waltz", "베개 왈츠"
A_CH = ["Eb", "Fm", "Gm", "Ab", "Eb", "Abm", "Eb", "Bb7", "Eb", "Fm", "Gm", "Ab", "Ab", "Abm", "Eb", "Eb"]
B_CH = ["Cm", "G7", "Cm", "Cm", "Fm", "Bb7", "Eb", "Eb", "Ab", "Abm", "Eb", "C7", "Fm", "Bb7", "Eb", "Bb7"]
A_MEL = line("G5:2 Bb5:1 | Ab5:2 C6:1 | Bb5:2 D6:1 | C6:3 | Bb5:1 G5:1 Eb5:1 | Cb6:2 Ab5:1 | G5:1 F5:1 Eb5:1 | F5:2 r:1 | "
             "G5:2 Bb5:1 | Ab5:2 C6:1 | D6:1.5 C6:.5 Bb5:1 | Eb6:3 | C6:1 Ab5:1 F5:1 | Eb5:1 Cb5:1 Ab4:1 | G4:1.5 Ab4:.5 Bb4:1 | Eb5:3", bar=3)
B_MEL = line("Eb5:1 D5:1 C5:1 | B4:2 D5:1 | G5:2 Eb5:1 | C5:3 | Ab5:1 G5:1 F5:1 | D5:2 F5:1 | Eb5:3 | r:1 Bb4:1 Eb5:1 | "
             "C6:2 Ab5:1 | Cb6:2 Ab5:1 | G5:1 Bb5:1 G5:1 | E5:2 G5:1 | F5:1 Ab5:1 C6:1 | D6:1 C6:1 Ab5:1 | G5:3 | F5:2 r:1", bar=3)
SECS = [("intro", 4), ("A1", 16), ("A2", 16), ("B1", 16), ("A3", 16), ("B2", 16), ("A4", 16), ("A5", 16), ("outro", 8)]


def mbox(s, notes, at, amp=0.36, semis=0, pan=-0.05, send=0.35):
    for b, d, m in notes:
        y = B.music_box(B.m2f(m + semis), dur=max(1.2, d * s.beat + 0.8), amp=amp * (0.92 + 0.08 * B.h01(b, m)))
        s.add("lead", y, s.pos(at + b), pan=pan, send=send)


def build():
    bars = sum(n for _, n in SECS)
    s = Song(TAG, TITLE, bpm=96, bar=3, bars=bars, swing=0.5, tail=4.0, lufs=-16.0)   # DEEP = −16 (깊은 잠 구간은 한 단계 작게)
    s.meta = {"fingerprint": "STEPUP×WALTZ3", "key": "Eb", "stage": "DEEP"}
    plan, b0 = [], 0
    for name, n in SECS:
        s.section(name, b0, n)
        plan.append((name, b0, n))
        b0 += n
    st = {nm: x for nm, x, n in plan}
    chords = []
    for name, x, n in plan:
        if name == "intro":
            chords += ["Eb", "Ab", "Eb", "Bb7"]
        elif name == "outro":
            chords += ["Eb", "Ab", "Abm", "Eb", "Eb", "Abm", "Eb", "Eb"]
        else:
            chords += B_CH if name[0] == "B" else A_CH
    prev = None
    arp_secs = ("A3",)
    for bar, sym in enumerate(chords):
        name = next(nm for nm, x, n in plan if x <= bar < x + n)
        b = s.B(bar)
        end = bar >= len(chords) - 2
        quiet = name in ("A5", "outro")
        inst(s, "bass", "CelloEnsPizz", B.bass_note(sym, 36, 52), b, 1.2, vel=90, amp=0.9 * (0.8 if quiet else 1.0), pan=-0.1, send=0.2)
        v = B.voice(sym, 58, 72, prev=prev, n=3)
        prev = v
        if end:
            continue
        if name in arp_secs:                                     # 하프 분산(8분 6개) — 쿵짝짝 대신 물결
            seq = [v[0], v[1], v[2], v[1] + 12, v[2], v[1]]
            for i, m in enumerate(seq):
                inst(s, "chord", "Harp", m, b + i * 0.5, 0.9, vel=72, amp=0.42, pan=0.2 - 0.06 * i, send=0.3, rel=0.5)
        else:
            for q in (1, 2):
                for i, m in enumerate(v):
                    inst(s, "chord", "Harp", m, b + q + 0.02 * i, 0.6, vel=70 if quiet else 78, amp=0.38 * (0.75 if quiet else 1.0),
                         pan=0.22, send=0.3, rel=0.35)
    mbox(s, A_MEL, s.B(st["A1"]), amp=0.36)
    mbox(s, line("Bb5:3 | G5:3 | Eb5:3 | F5:3", bar=3), s.B(st["intro"]), amp=0.3)
    play(s, "lead", "FluteSusVib", A_MEL, at=s.B(st["A2"]), semis=-12, amp=1.25, pan=-0.05, send=0.3, stac=0.95, rel=0.25, vel=70)
    mbox(s, [n for n in A_MEL if n[0] % 3 == 0], s.B(st["A2"]), amp=0.35, pan=0.3)
    play(s, "lead", "FluteSusVib", B_MEL, at=s.B(st["B1"]), semis=-12, amp=1.3, pan=-0.05, send=0.3, stac=0.95, rel=0.25, vel=70)
    mbox(s, [n for n in B_MEL if n[1] >= 2], s.B(st["B1"]), amp=0.32, semis=12, pan=0.3)
    mbox(s, A_MEL, s.B(st["A3"]), amp=0.36)
    play(s, "lead", "ClarinetSus", B_MEL, at=s.B(st["B2"]), semis=-12, amp=0.45, pan=-0.05, send=0.3, stac=0.95, rel=0.25, vel=64)
    mbox(s, [n for n in B_MEL if n[0] % 3 == 0], s.B(st["B2"]), amp=0.3, semis=12, pan=0.3)
    mbox(s, A_MEL, s.B(st["A4"]), amp=0.36)
    play(s, "resp", "CelloEnsSusVib-Quiet", [(b, d, m) for b, d, m in A_MEL if b % 6 == 0], at=s.B(st["A4"]), semis=-24, amp=0.4, pan=0.15, send=0.3, rel=0.4, vel=60)
    mbox(s, [n for n in A_MEL if n[0] < 24], s.B(st["A5"]), amp=0.3)                  # 잠듦: 앞 8마디만, 뒤는 비움
    mbox(s, [(b * 2, d * 2, m) for b, d, m in A_MEL if b < 12], s.B(st["outro"]), amp=0.28)   # 반 템포로 늘어지는 기억
    # 바순 하품 — B 끝마다·아웃트로
    for bb, m0 in ((s.B(st["B1"] + 15), 55), (s.B(st["B2"] + 15), 53), (s.B(st["outro"] + 5), 51)):
        y = B.glide_note("BassoonSus", m0, m0 - 7, 1.9 * s.beat * 1.6, 0.35, 2.2, vel=70)
        s.add("resp", y * 0.55, s.pos(bb), pan=0.2, send=0.3)
    end = s.B(st["outro"] + 7)
    for m in B.voice("Eb", 58, 75):
        inst(s, "chord", "Harp", m, end, 3.0, vel=70, amp=0.4, send=0.35, rel=1.5)
    s.add("lead", B.music_box(B.m2f(87), 2.4, 0.55), s.pos(end + 0.5), pan=0.2, send=0.4)
    gains = {"bass": 1.0, "chord": 0.85, "lead": 1.0, "resp": 0.9, "color": 0.8, "sfx": 0.5}
    return B.master(s, gains, rev_rt=1.8, rev_wet=0.34)


if __name__ == "__main__":
    build()
