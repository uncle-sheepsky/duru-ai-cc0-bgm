# duru-reacts — composer code (CC0)

Music for *반응하는 두루 / Duru Reacts* (https://youtu.be/Ab87XWl7h4Y), a 2:27 touch-reaction animation.
♩150 · 4/4 · 92 bars · D minor → D major. Marimba (the cursor's voice) and clarinet (Duru's voice)
trade a 3–5–6–5 motif and its mirror 5–3–2–3; strings / contrabass pizzicato underneath, oboe in the
"taking care" act, horn + violins at the climax, a small code-synthesized thumb-piano for the lullaby.

- `timeline.py` → `timeline.json` — the single value file the picture and the music both read (cue beats, acts, gestures).
- `build_music.py --tag v4a --chord pizz` — the track as released. Needs the shared sampler/mixer `band.py` + `sfz_sampler.py`
  from [`../duru-zoneout-1h/`](../duru-zoneout-1h/) (point `sys.path` at that folder) and the **VSCO 2 Community Edition** SFZ
  samples (CC0) at the path `band.py` expects (`VSCO_SFZ_DIR`).
- `gate_music.py --tag v4a` — the measurement gates we ran (loudness, true peak, onset-per-gesture, spectral register, timbre churn).

Instrument samples: VSCO 2 Community Edition (CC0). Everything else is code. License: CC0 1.0, same as the rest of this repo.
