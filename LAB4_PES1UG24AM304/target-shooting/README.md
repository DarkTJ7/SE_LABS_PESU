# Target Shooting

A Pygame target-shooting game with circular hit detection, moving targets,
combo scoring, and timed 30-second rounds.

## Setup and run

Requires Python 3.10+.

```bash
python -m pip install -r requirements.txt
python main.py
```

## How to play

- Left-click to shoot. A hit must land inside the visible circle.
- Targets move at different speeds and bounce within the play area.
- Hits score 10 points times the current consecutive-hit combo. A miss resets it.
- The round ends after 30 seconds and displays the final score.
- Press **R** on the results screen to start a new round.
