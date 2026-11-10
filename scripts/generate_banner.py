"""Generate the README hero banner (dist/banner.svg).

A dark navy-to-teal panel with the name and positioning on the left and a
clinical-data motif on the right: Kaplan-Meier step curves that draw
themselves on load, censor ticks, and a DNA double helix made of data points.

Usage:
    python scripts/generate_banner.py [--out dist/banner.svg]
"""

from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

W, H = 1200, 300
SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SEED = 7  # deterministic curves, so regenerating gives the same banner


def km_path(rng: random.Random, x0: float, x1: float, y0: float, y1: float,
            hazard: float, steps: int) -> tuple[str, list[tuple[float, float]]]:
    """Build a Kaplan-Meier style step path plus censor-tick positions."""
    x, surv = x0, 1.0
    pts = [f"M{x0:.1f},{y0:.1f}"]
    ticks = []
    dx = (x1 - x0) / steps
    for _ in range(steps):
        x += dx * rng.uniform(0.6, 1.4)
        if x > x1:
            break
        y = y0 + (1 - surv) * (y1 - y0)
        pts.append(f"H{x:.1f}")
        if rng.random() < 0.55:
            surv *= 1 - hazard * rng.uniform(0.4, 1.6)
            pts.append(f"V{y0 + (1 - surv) * (y1 - y0):.1f}")
        elif rng.random() < 0.5:
            ticks.append((x, y))
    pts.append(f"H{x1:.1f}")
    return "".join(pts), ticks


def helix(x0: float, x1: float, cy: float, amp: float, n: int) -> list[str]:
    """Two phase-shifted sine strands of dots joined by faint rungs."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + t * (x1 - x0)
        a = t * math.tau * 2.2
        ya, yb = cy + amp * math.sin(a), cy + amp * math.sin(a + math.pi)
        depth = (math.cos(a) + 1) / 2  # fake 3D: front dots larger/brighter
        if i % 3 == 0:
            out.append(f'<line x1="{x:.1f}" y1="{ya:.1f}" x2="{x:.1f}" y2="{yb:.1f}" '
                       f'stroke="#5eead4" stroke-opacity="0.12"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{ya:.1f}" r="{1.6 + 1.6 * depth:.1f}" '
                   f'fill="#5eead4" fill-opacity="{0.25 + 0.55 * depth:.2f}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{yb:.1f}" r="{1.6 + 1.6 * (1 - depth):.1f}" '
                   f'fill="#a78bfa" fill-opacity="{0.25 + 0.55 * (1 - depth):.2f}"/>')
    return out


def dot_grid() -> str:
    return ('<pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse">'
            '<circle cx="2" cy="2" r="1" fill="#ffffff" fill-opacity="0.06"/></pattern>')


def build() -> str:
    rng = random.Random(SEED)
    px0, px1, py0, py1 = 640, 1150, 60, 250  # plot area
    arm_a, ticks_a = km_path(rng, px0, px1, py0, py1, 0.05, 26)
    arm_b, ticks_b = km_path(rng, px0, px1, py0, py1, 0.11, 26)

    def ticks(pts, colour):
        return "".join(f'<path d="M{x:.1f},{y - 5:.1f}v10" stroke="{colour}" stroke-width="1.6" '
                       f'class="fade"/>' for x, y in pts)

    axis = (f'<path d="M{px0},{py0 - 10}V{py1}H{px1}" fill="none" stroke="#94a3b8" '
            f'stroke-opacity="0.35" stroke-width="1"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Jaime Yan, PhD. Clinical data science, statistical programming and GxP-ready AI.">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#0b1220"/><stop offset="0.55" stop-color="#0f2740"/><stop offset="1" stop-color="#0b3b40"/>
</linearGradient>
<radialGradient id="glow" cx="0.8" cy="0.2" r="0.6"><stop offset="0" stop-color="#14b8a6" stop-opacity="0.22"/><stop offset="1" stop-color="#14b8a6" stop-opacity="0"/></radialGradient>
{dot_grid()}
</defs>
<style>
.draw{{stroke-dasharray:1400;stroke-dashoffset:1400;animation:d 2.6s ease-out forwards}}
.b{{animation-delay:.5s}}
.fade{{opacity:0;animation:f .8s ease-out 2.4s forwards}}
@keyframes d{{to{{stroke-dashoffset:0}}}}
@keyframes f{{to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.draw{{animation:none;stroke-dashoffset:0}}.fade{{animation:none;opacity:1}}}}
</style>
<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>
<rect width="{W}" height="{H}" rx="12" fill="url(#g)"/>
<rect width="{W}" height="{H}" rx="12" fill="url(#glow)"/>
<g opacity="0.9">{''.join(helix(600, 1180, 268, 14, 64))}</g>
{axis}
<path d="{arm_a}" fill="none" stroke="#2dd4bf" stroke-width="2.6" class="draw"/>
<path d="{arm_b}" fill="none" stroke="#a78bfa" stroke-width="2.6" class="draw b"/>
{ticks(ticks_a, '#2dd4bf')}{ticks(ticks_b, '#a78bfa')}
<g font-family="{MONO}" font-size="14" fill="#94a3b8" class="fade">
<text x="{px1 - 190}" y="{py0 + 4}"><tspan fill="#2dd4bf">━</tspan> Treatment  <tspan fill="#a78bfa">━</tspan> Control</text>
</g>
<g font-family="{SANS}">
<text x="56" y="112" font-size="50" font-weight="700" fill="#f8fafc">Jaime Yan, PhD</text>
<text x="58" y="150" font-size="20" fill="#cbd5e1">Clinical Data Science · Statistical Programming Leader</text>
<text x="58" y="184" font-size="18" fill="#a5b4c8">Reproducible, compliant, AI-assisted analytics.</text>
</g>
<g font-family="{MONO}" font-size="16">
<rect x="56" y="208" width="560" height="38" rx="8" fill="#0b1220" fill-opacity="0.55" stroke="#2dd4bf" stroke-opacity="0.35"/>
<text x="74" y="233" fill="#5eead4">R · Python · CDISC · GxP · LLM/RAG</text>
<text x="440" y="233" fill="#94a3b8">// jaimeyan.com</text>
</g>
</svg>
"""


def build_footer() -> str:
    """Thin wave strip that closes the README in the banner's colours."""
    w, h = W, 90
    waves = []
    for i, (amp, phase, op) in enumerate(((14, 0.0, 0.55), (10, 1.3, 0.35), (7, 2.4, 0.25))):
        pts = " ".join(
            f"{x},{h * 0.45 + amp * math.sin(x / w * math.tau * 1.5 + phase):.1f}" for x in range(0, w + 1, 20)
        )
        waves.append(f'<polygon points="0,{h} {pts} {w},{h}" fill="url(#fw)" fill-opacity="{op}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">
<defs><linearGradient id="fw" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#14b8a6" stop-opacity="0"/><stop offset="0.6" stop-color="#14b8a6"/><stop offset="1" stop-color="#a78bfa"/>
</linearGradient></defs>
{''.join(waves)}
</svg>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="dist/banner.svg")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    footer = out.with_name("footer.svg")
    footer.write_text(build_footer(), encoding="utf-8")
    print(f"wrote {footer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
