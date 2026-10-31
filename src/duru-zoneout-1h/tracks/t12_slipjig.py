"""T12 「깡총 슬립지그」 — D 믹솔리디안 9/8 ♩.=116 · LIGHT 구간(깨나서 깡총깡총).

지문: 축1 MIXFOLK — I–♭VII–I–V (D–C–D–A) `[−2,+2,−5,+5]` 믹솔리디안 ♭7 왕복 후 V로 (대장 미사용 · channelsurf2 I–V–♭VII–IV 와 순서·벡터 상이)
      축3 SLIPJIG98 — 9/8(점4분 ×3) · 툼바 강박 {0} + 콩가 탭 8분 셋잇단 · 기타 점4분 스트럼 (대장에 9박 계열 없음)
음색: 리드 = 플루트(아이리시) → 바이올린 스피카토 → 하프 선율 → 플루트+바이올린 / 화음 = 나일론 기타(합성) / 저음 = 콘트라베이스.
구성: 인트로4 · (A8 A8 B8 B8) ×5 · 아웃트로4 = 168마디.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import band as B  # noqa: E402
from band import Song, inst, line, perc, play  # noqa: E402

TAG, TITLE = "t12_slipjig", "깡총 슬립지그"
A_CH = ["D", "C", "D", "A", "D", "C", "A", "D"]
B_CH = ["G", "D", "G", "A", "G", "D", "C", "D"]
A1 = "A5:1/3 F#5:1/3 A5:1/3 D6:2/3 A5:1/3 F#5:1/3 E5:1/3 D5:1/3 | G5:1/3 E5:1/3 G5:1/3 C6:2/3 G5:1/3 E5:1/3 D5:1/3 C5:1/3 | "
A_MEL = line(A1 + "A5:1/3 F#5:1/3 A5:1/3 D6:1/3 E6:1/3 F#6:1/3 E6:1/3 D6:1/3 B5:1/3 | A5:2/3 G5:1/3 F#5:1/3 E5:1/3 D5:1/3 E5:1 | "
             + A1 + "E5:1/3 F#5:1/3 G5:1/3 A5:2/3 C#6:1/3 E6:1/3 C#6:1/3 A5:1/3 | D6:1 A5:1/3 F#5:1/3 D5:1 r:1/3", bar=3)
B1 = "B5:1/3 D6:1/3 B5:1/3 G5:2/3 B5:1/3 D6:1/3 G6:1/3 D6:1/3 | A5:1/3 D6:1/3 A5:1/3 F#5:2/3 A5:1/3 D6:1/3 F#6:1/3 D6:1/3 | "
B_MEL = line(B1 + "B5:1/3 D6:1/3 B5:1/3 G5:1/3 A5:1/3 B5:1/3 C6:1/3 B5:1/3 A5:1/3 | E6:2/3 C#6:1/3 A5:2/3 E5:1/3 A5:1 | "
             + B1 + "G6:1/3 E6:1/3 C6:1/3 G5:1/3 E5:1/3 G5:1/3 C6:2/3 B5:1/3 | A5:1 F#5:1/3 E5:1/3 D5:1 r:1/3", bar=3)
TUNE = A_MEL + B.shift(A_MEL, 24) + B.shift(B_MEL, 48) + B.shift(B_MEL, 72)       # A A B B = 32마디 = 96박
TUNE_CH = A_CH + A_CH + B_CH + B_CH
LEADS = ["flute", "fiddle", "harp", "both", "fiddle_then_all"]


def gtr(s, m, b, amp, pan):
    y = B.ks_pluck(m, 0.6, bright=0.5, decay=0.993)
    s.add("chord", y * amp, s.pos(b) + (B.h01(b, m, 17) - 0.5) * 0.006, pan=pan, send=0.12)


def build():
    bars = 4 + 32 * len(LEADS) + 4
    s = Song(TAG, TITLE, bpm=116, bar=3, bars=bars, swing=0.5, tail=3.0)
    s.meta = {"fingerprint": "MIXFOLK×SLIPJIG98", "key": "D mixolydian", "stage": "LIGHT"}
    s.section("intro", 0, 4)
    for i, ld in enumerate(LEADS):
        s.section(f"T{i + 1}", 4 + 32 * i, 32)
    s.section("outro", 4 + 32 * len(LEADS), 4)
    chords = ["D", "C", "A", "A"] + TUNE_CH * len(LEADS) + ["D", "C", "D", "D"]
    prev = None
    for bar, sym in enumerate(chords):
        b = s.B(bar)
        last = bar >= len(chords) - 2
        r = B.bass_note(sym, 33, 48)
        inst(s, "bass", "ContrabassPizz", r, b, 0.9, vel=96, amp=1.55, pan=-0.05, send=0.08)
        if not last:
            inst(s, "bass", "ContrabassPizz", B.bass_note(sym, 33, 48, "fifth"), b + 2, 0.9, vel=90, amp=1.25, pan=-0.05, send=0.08)
        v = B.voice(sym, 50, 66, prev=prev, n=3)
        prev = v
        if last:
            continue
        for q in range(3):                                   # 점4분마다 스트럼(아래로) + 셋째 8분 가벼운 위로
            for i, m in enumerate(v):
                gtr(s, m, b + q + 0.01 * i, 0.16, 0.2)
            for i, m in enumerate(reversed(v[1:])):
                gtr(s, m, b + q + 2 / 3 + 0.01 * i, 0.08, 0.25)
        if bar >= 2:
            perc(s, 65, b, amp=0.6, pan=-0.15, vel=90)
            for k in range(1, 9):
                perc(s, 62, b + k / 3, amp=0.34 if k % 3 == 0 else 0.2, pan=-0.2, vel=70, dur=0.3)
    for i, ld in enumerate(LEADS):
        at = s.B(4 + 32 * i)
        if ld == "flute":
            play(s, "lead", "FluteSusNV", TUNE, at=at, amp=1.0, pan=-0.05, send=0.2, stac=0.9, rel=0.06)
        elif ld == "fiddle":
            play(s, "lead", "SViolinSpic", TUNE, at=at, amp=1.3, pan=-0.05, send=0.2)
        elif ld == "harp":
            play(s, "lead", "Harp", TUNE, at=at, amp=1.7, pan=-0.05, send=0.25, rel=0.3)
            play(s, "resp", "SViolinVib-Quiet", [(b, d, m) for b, d, m in TUNE if d >= 1], at=at, semis=-12, amp=1.05, pan=0.25, send=0.3, rel=0.2)
        elif ld == "both":
            play(s, "lead", "FluteSusNV", TUNE, at=at, amp=0.85, pan=-0.15, send=0.2, stac=0.9, rel=0.06)
            play(s, "lead", "SViolinSpic", TUNE, at=at, semis=-12, amp=0.85, pan=0.15, send=0.2)
        else:
            play(s, "lead", "SViolinSpic", [n for n in TUNE if n[0] < 48], at=at, amp=1.0, pan=-0.05, send=0.2)
            play(s, "lead", "FluteSusNV", [n for n in TUNE if n[0] >= 48], at=at, amp=0.85, pan=-0.15, send=0.2, stac=0.9, rel=0.06)
            play(s, "lead", "SViolinSpic", [n for n in TUNE if n[0] >= 48], at=at, semis=-12, amp=0.85, pan=0.15, send=0.2)
            play(s, "resp", "PiccoloStac", [n for n in TUNE if n[0] >= 72 and n[1] >= 2 / 3], at=at, amp=0.5, pan=0.35, send=0.2)
    ob = s.B(4 + 32 * len(LEADS))
    for m in B.voice("D", 50, 74):
        gtr(s, m, ob + 6, 0.3, 0.1)
    inst(s, "lead", "FluteSusNV", 74, ob + 6, 2.0, amp=0.9, rel=0.4)
    perc(s, 65, ob + 6, amp=1.0)
    s.add("sfx", B.boing(0.5) * 0.45, s.pos(ob + 9), pan=0.3)
    gains = {"bass": 1.0, "perc": 0.85, "chord": 0.85, "lead": 1.0, "resp": 0.9, "sfx": 0.5}
    return B.master(s, gains, rev_rt=1.2, rev_wet=0.26)


if __name__ == "__main__":
    build()
