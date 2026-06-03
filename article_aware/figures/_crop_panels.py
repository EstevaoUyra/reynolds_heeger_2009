"""One-shot helper: crop each paper figure JPG into per-panel JPGs.

Bounding boxes are fractional (left, top, right, bottom) of the full image,
estimated by eye from the paper figure images (article_aware/figures/figure_<N>.jpg).
Approximate crops are fine — they exist so each reproduced panel has its paper
counterpart as an isolated comparison unit (WORKFLOW.md §3). Re-runnable.

Run:  python article_aware/figures/_crop_panels.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent

# Fractional boxes (l, t, r, b) per figure, per panel id.
PANELS: dict[int, dict[str, tuple[float, float, float, float]]] = {
    2: {
        "A": (0.00, 0.00, 0.50, 0.70),
        "B": (0.50, 0.00, 1.00, 0.70),
        "legend": (0.00, 0.70, 1.00, 1.00),
    },
    3: {
        "A": (0.00, 0.00, 0.27, 0.42),
        "B": (0.27, 0.00, 0.66, 0.42),
        "C": (0.66, 0.00, 1.00, 0.42),
        "D": (0.00, 0.42, 0.27, 0.85),
        "E": (0.27, 0.42, 0.66, 0.85),
        "F": (0.66, 0.42, 1.00, 0.85),
        "legend": (0.00, 0.85, 1.00, 1.00),
    },
    4: {
        "A": (0.00, 0.00, 0.33, 0.40),
        "B": (0.33, 0.00, 0.66, 0.40),
        "C": (0.66, 0.00, 1.00, 0.40),
        "D": (0.00, 0.40, 0.33, 0.83),
        "E": (0.66, 0.40, 1.00, 0.83),
        "legend": (0.00, 0.83, 1.00, 1.00),
    },
    5: {
        "A": (0.00, 0.00, 0.18, 0.78),
        "B": (0.18, 0.00, 0.60, 0.78),
        "C": (0.60, 0.00, 1.00, 0.78),
        "legend": (0.00, 0.78, 1.00, 1.00),
    },
    6: {
        "A": (0.00, 0.00, 0.18, 0.78),
        "B": (0.18, 0.00, 0.60, 0.78),
        "C": (0.60, 0.00, 1.00, 0.78),
        "legend": (0.00, 0.78, 1.00, 1.00),
    },
    7: {
        "A": (0.00, 0.00, 0.18, 0.78),
        "B": (0.18, 0.00, 0.60, 0.78),
        "C": (0.60, 0.00, 1.00, 0.78),
        "legend": (0.00, 0.78, 1.00, 1.00),
    },
}


def main() -> None:
    for fig_n, panels in PANELS.items():
        src = HERE / f"figure_{fig_n}.jpg"
        img = Image.open(src)
        w, h = img.size
        out_dir = HERE / f"figure_{fig_n}"
        out_dir.mkdir(exist_ok=True)
        for pid, (l, t, r, b) in panels.items():
            box = (int(l * w), int(t * h), int(r * w), int(b * h))
            img.crop(box).save(out_dir / f"panel_{pid}.jpg", quality=90)
            print(f"figure_{fig_n}/panel_{pid}.jpg  {box}")


if __name__ == "__main__":
    main()
