"""T14 「하품 미뉴에트」 — G 3/4 ♩=104 · DEEP 구간(점잖은 척하다 하품하는 궁정 춤).

지문: 축1 DIA-CIRCLE — I–IV–vii°–iii–vi–ii–V7–I (G–C–F#°–Bm–Em–Am–D7–G) `[+5,+6,+5,+5,+5,+5,+5]` 온음계 5도권(삼온 한 칸 포함)
      (데모의 2차 도미넌트 래그 [+5,+5,+5,+5] 와 벡터·품질 상이) · 트리오 C장조
      축3 MINUET3 — 3/4 · 첼로 스피카토 매 박 {0,1,2}(바로크 걷는 베이스) + 하프 8분 분산 · 타악 없음 (WALTZ3 쿵짝짝과 상이)
음색: 리드 = 오보에 → 클라리넷(트리오) → 바순(D) / 응답 = 플루트 / 저음 = 첼로 스피카토 / 개그 = 늘어지는 트릴·바순 하품.
구성: 인트로4 · 미뉴에트(A A B A' B A')48 · 트리오(C C D C' D C')48 · 다카포 48 · 코다4 = 152마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, play  # noqa: E402

TAG, TITLE = "t14_minuet", "하품 미뉴에트"
CH = {
    "A": ["G", "C", "F#dim", "Bm", "Em", "Am", "D7", "G"],
    "B": ["Em", "B7", "Em", "C", "Am", "D7", "G", "D7"],
    "C": ["C", "G7", "C", "F", "C", "G7", "C", "C"],
    "D": ["Am", "E7", "Am", "Dm", "G7", "C", "F", "G7"],
}
MEL = {
    "A": line("B4:1 D5:.5 G5:.5 F#5:.5 G5:.5 | E5:1 C5:1 G5:1 | A5:.5 F#5:.5 C6:.5 A5:.5 F#5:1 | B5:1 F#5:1 D5:1 | "
              "E5:.5 G5:.5 B5:.5 G5:.5 E5:1 | C6:1 A5:.5 G5:.5 F#5:.5 E5:.5 | F#5:1 A5:.5 G5:.5 F#5:.5 E5:.5 | G5:2 r:1", bar=3),
    "B": line("B5:1 G5:1 E5:1 | D#5:1 F#5:1 A5:1 | G5:.5 F#5:.5 E5:.5 G5:.5 B5:1 | E6:1.5 D6:.5 C6:1 | "
              "C6:.5 B5:.5 A5:.5 C6:.5 E5:1 | F#5:1 D5:1 C6:1 | B5:.5 A5:.5 G5:.5 D5:.5 B4:1 | A4:1 D5:1 F#5:1", bar=3),
    "C": line("E5:1.5 F5:.5 G5:1 | F5:1 D5:1 B4:1 | C5:1 E5:1 G5:1 | A5:2 F5:1 | G5:1.5 A5:.5 G5:1 | F5:.5 E5:.5 D5:1 G4:1 | "
              "C5:1 E5:1 G5:1 | C6:2 r:1", bar=3),
    "D": line("A5:1 E5:1 C5:1 | B4:1 D5:1 G#5:1 | A5:1.5 B5:.5 C6:1 | D6:2 A5:1 | B5:1 G5:1 F5:1 | E5:1 G5:1 C6:1 | "
              "A5:1 F5:1 A5:1 | G5:2 r:1", bar=3),
}
MINUET = [("A", "oboe"), ("A", "oboe+flute"), ("B", "oboe"), ("A", "oboe"), ("B", "oboe+bsn"), ("A", "oboe+flute")]
TRIO = [("C", "clar"), ("C", "flute"), ("D", "bsn"), ("C", "clar"), ("D", "bsn+flute"), ("C", "clar+flute")]
FORM = [("intro", None)] + MINUET + TRIO + MINUET + [("coda", None)]


def build():
    bars = 4 + 8 * (len(FORM) - 2) + 4
    s = Song(TAG, TITLE, bpm=104, bar=3, bars=bars, swing=0.5, tail=4.0, lufs=-16.0)
    s.meta = {"fingerprint": "DIACIRCLE×MINUET3", "key": "G", "stage": "DEEP"}
    s.section("intro", 0, 4)
    s.section("minuet", 4, 48)
    s.section("trio", 52, 48)
    s.section("dacapo", 100, 48)
    s.section("coda", 148, 4)
    chords, bar0 = ["G", "D7", "G", "D7"], 4
    starts = []
    for part, who in FORM[1:-1]:
        starts.append((bar0, part, who))
        chords += CH[part]
        bar0 += 8
    chords += ["C", "D7", "G", "G"]
    prev = None
    for bar, sym in enumerate(chords):
        b = s.B(bar)
        last = bar >= len(chords) - 1
        r = B.bass_note(sym, 36, 52)
        walk = [r, r + 12 if (bar % 2) else r + 7, r + 4 if "m" not in sym.replace("dim", "") else r + 3]
        for i, m in enumerate(walk if not last else walk[:1]):
            inst(s, "bass", "CelloEnsSpic", m, b + i, 0.6, vel=88, amp=1.35 * (1.15 if i == 0 else 0.85), pan=-0.1, send=0.15)
        if last:
            continue
        v = B.voice(sym, 57, 72, prev=prev, n=3)
        prev = v
        for i, m in enumerate([v[0], v[1], v[2], v[1], v[2], v[1]]):
            inst(s, "chord", "Harp", m, b + i * 0.5, 0.6, vel=62, amp=0.66, pan=0.22, send=0.25, rel=0.3)
    for bar0, part, who in starts:
        at = s.B(bar0)
        mel = MEL[part]
        if "oboe" in who:
            play(s, "lead", "OboeStac", mel, at=at, amp=1.0, pan=-0.05, send=0.22)
        if "clar" in who:
            play(s, "lead", "ClarinetStac", mel, at=at, semis=-12, amp=1.3, pan=-0.05, send=0.22)
        if who == "flute":
            play(s, "lead", "FluteSusNV", mel, at=at, amp=0.95, pan=-0.05, send=0.25, stac=0.9, rel=0.1)
        elif "flute" in who:
            play(s, "resp", "FluteSusNV", mel, at=at, semis=12 if part in "AB" else 0, amp=0.2, pan=0.25, send=0.25, stac=0.9, rel=0.1)
        if who.startswith("bsn"):
            play(s, "lead", "BassoonStac", mel, at=at, semis=-12, amp=1.0, pan=-0.05, send=0.2)
        if who.endswith("+bsn"):
            play(s, "resp", "BassoonStac", [n for n in mel if n[1] >= 1], at=at, semis=-24, amp=0.4, pan=0.25, send=0.2)
        # 하품: 각 B·D 끝 마디에서 오보에/플루트가 늘어지는 트릴 대신 바순이 반음씩 미끄러져 하품
        if part in "BD":
            y = B.glide_note("BassoonSus", 50, 43, 2.2 * s.beat, 0.25, 1.8, vel=72)
            s.add("resp", y * 0.6, s.pos(at + 7 * 3), pan=0.3, send=0.3)
    cb = s.B(148)
    play(s, "lead", "OboeStac", line("B4:1 D5:1 G5:1 | F#5:1.5 E5:.5 F#5:1 | G5:3", bar=3), at=cb, amp=1.0, send=0.25)
    gains = {"bass": 1.0, "chord": 0.85, "lead": 1.0, "resp": 0.9}
    return B.master(s, gains, rev_rt=1.6, rev_wet=0.3)


if __name__ == "__main__":
    build()
