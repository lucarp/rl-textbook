#!/usr/bin/env python3
"""Assemble textbook chapters into build/book.html and render textbook/rl-field-guide.pdf.

Usage: python3 build.py [--html-only]
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # textbook/

# (part title, part blurb) inserted before the chapter it is keyed to; None = no divider.
PARTS = {
    "ch01-rl-problem.html": ("Part I", "Foundations",
        "The problem every method in this book is trying to solve, and the classical "
        "machinery — policy gradients, PPO, advantage estimation — that solves it when "
        "samples are cheap."),
    "ch04-awr-awac.html": ("Part II", "Learning from data you already have",
        "Real robots make samples expensive. This part rebuilds RL as a weighted "
        "supervised problem — the form that survives everything that follows."),
    "ch05-why-gaussian-fails.html": ("Part III", "Generative policies: the new world",
        "Why a Gaussian stopped being enough, what a generative model actually is, and "
        "how diffusion, flow matching, and vision-language-action models changed what a "
        "policy is — with PPO and VLA-RL finally placed side by side."),
    "ch11-reward-advantage.html": ("Part IV", "Making it work",
        "The engineering that decides whether any of it trains: reward and advantage "
        "design, inference-time gains, the human in the loop, and the simulator."),
    "ch15-capstone.html": ("Part V", "Doing it",
        "Turning the whole book into one staged project on hardware you own."),
}

CHAPTERS = [
    "ch01-rl-problem.html",
    "ch02-policy-gradients.html",
    "ch03-ppo-gae.html",
    "ch04-awr-awac.html",
    "ch05-why-gaussian-fails.html",
    "ch06-diffusion.html",
    "ch07-flow-matching.html",
    "ch08-vla.html",
    "ch09-ppo-vs-vla.html",
    "ch10-recap.html",
    "ch11-reward-advantage.html",
    "ch12-inference-time.html",
    "ch13-imitation-hil.html",
    "ch14-sim2real-async.html",
    "ch15-capstone.html",
    "appA-reading-guide.html",
    "appB-experiments.html",
]


def part_divider(name: str) -> str:
    """HTML for the part-title page preceding a chapter, or '' if none."""
    entry = PARTS.get(name)
    if not entry:
        return ""
    num, title, blurb = entry
    return (
        f'\n<section class="part-divider">\n'
        f'  <div class="part-inner">\n'
        f'    <div class="part-num">{num}</div>\n'
        f'    <h2 class="part-title">{title}</h2>\n'
        f'    <p class="part-blurb">{blurb}</p>\n'
        f'  </div>\n</section>\n'
    )

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Reinforcement Learning for Real Robots</title>
<script>
window.PagedConfig = { auto: false };
window.MathJax = {
  tex: { inlineMath: [['\\\\(','\\\\)']], displayMath: [['\\\\[','\\\\]']] },
  svg: { fontCache: 'none' }
};
</script>
<script src="../assets/mathjax-tex-svg.js"></script>
<script src="../assets/paged.polyfill.js"></script>
<script>
window.addEventListener('load', () => {
  MathJax.startup.promise
    .then(() => window.PagedPolyfill.preview())
    .then(() => { window.__PAGED_DONE__ = true; })
    .catch(e => { console.error(e); window.__PAGED_DONE__ = true; });
});
</script>
<style>
/* ---------- page geometry ---------- */
@page {
  size: A4;
  margin: 21mm 19mm 23mm 19mm;
  @bottom-center { content: counter(page); font-family: "Noto Sans", sans-serif; font-size: 9pt; color: #777; }
  @top-left { content: string(chaptitle); font-family: "Noto Sans", sans-serif; font-size: 7.5pt; color: #999; letter-spacing: 0.07em; text-transform: uppercase; }
}
@page cover { margin: 0; @bottom-center { content: none; } @top-left { content: none; } }
@page frontmatter { @top-left { content: none; } }

/* ---------- base typography ---------- */
html { font-family: "Bitstream Charter", "Charter", "Liberation Serif", serif;
       font-size: 10.3pt; line-height: 1.42; color: #1a1a1a; }
p { margin: 0.45em 0; text-align: justify; hyphens: auto; orphans: 2; widows: 2; }
strong { color: #111; }
.mono { font-family: "Noto Mono", "DejaVu Sans Mono", monospace; font-size: 0.92em; }

h1 { font-family: "Noto Sans", sans-serif; font-size: 19pt; line-height: 1.15;
     string-set: chaptitle content(text); break-before: auto; margin: 0 0 0.7em 0;
     padding-bottom: 0.35em; border-bottom: 2.5px solid #4878a8; color: #17385c; }
h1.unnumbered, h1.toc-title { break-before: auto; }
h2 { font-family: "Noto Sans", sans-serif; font-size: 12.5pt; color: #17385c;
     margin: 1.25em 0 0.35em 0; break-after: avoid; }
h3 { font-family: "Noto Sans", sans-serif; font-size: 10.8pt; color: #333;
     margin: 1em 0 0.25em 0; break-after: avoid; }

/* ---------- cover ---------- */
section.chapter { break-before: page; }
section.cover { page: cover; height: 100vh; display: flex; align-items: center; justify-content: center;
                background: linear-gradient(160deg, #f7fafd 55%, #eaf1f8 100%); }
.cover-inner { padding: 0 22mm; text-align: left; }
.cover-title { font-family: "Noto Sans", sans-serif; font-size: 34pt; font-weight: 800; color: #17385c;
               border: none; margin: 14mm 0 6mm 0; break-before: auto; line-height: 1.1; }
.cover-subtitle { font-family: "Noto Sans", sans-serif; font-size: 13pt; color: #445; max-width: 150mm; text-align: left; }
.cover-byline { font-family: "Noto Sans", sans-serif; font-size: 10.5pt; color: #666; margin-top: 16mm; }
.cover-credit { font-size: 9.5pt; color: #778; max-width: 140mm; text-align: left; margin-top: 2mm; }

/* ---------- part dividers ---------- */
/* No break-after, and no vh height: the following h1 already carries
   break-before: page, and a vh-sized block overflows the page box and spills a
   blank page. Padding positions the block instead. */
section.part-divider { page: frontmatter; break-before: page; padding-top: 62mm; }
.part-inner { border-left: 5px solid #4878a8; padding-left: 12mm; max-width: 132mm; }
.part-num { font-family: "Noto Sans", sans-serif; font-size: 10pt; letter-spacing: 0.22em;
            text-transform: uppercase; color: #7d94ab; margin-bottom: 3mm; }
h2.part-title { font-family: "Noto Sans", sans-serif; font-size: 25pt; font-weight: 800;
                color: #17385c; margin: 0 0 5mm 0; line-height: 1.15; }
.part-blurb { font-size: 10.8pt; color: #46525e; text-align: left; }

/* ---------- toc ---------- */
section.toc-page { page: frontmatter; }
.toc-title { border-bottom: 2.5px solid #4878a8; }
ol.toc { list-style: none; padding: 0; margin: 1.2em 0; }
ol.toc li { margin: 0.55em 0; font-family: "Noto Sans", sans-serif; font-size: 11pt; }
ol.toc a { text-decoration: none; color: #1a1a1a; display: block; }
ol.toc a::after { content: target-counter(attr(href url), page);
                  float: right; font-size: 10pt; color: #555; }
.toc-num { display: inline-block; min-width: 2em; color: #4878a8; font-weight: 700; }
ol.toc li.toc-part { font-size: 8.6pt; letter-spacing: 0.13em; text-transform: uppercase;
                     color: #8497a8; margin: 1.15em 0 0.35em 0; font-weight: 600; }
ol.toc li.toc-part:first-child { margin-top: 0.4em; }

/* ---------- figures ---------- */
figure { margin: 0.9em auto; text-align: center; break-inside: avoid; }
figure svg { max-width: 100%; height: auto; }
figcaption { font-family: "Noto Sans", sans-serif; font-size: 8.4pt; color: #555;
             margin-top: 0.35em; text-align: center; }

/* ---------- boxes ---------- */
.box { border: 1px solid #c9d4e0; background: #f2f6fa; border-radius: 4px;
       padding: 7px 11px; margin: 0.9em 0; break-inside: avoid; font-size: 9.6pt; }
.box p { margin: 0.25em 0; }
.box .box-title { font-family: "Noto Sans", sans-serif; font-weight: 700; font-size: 8.6pt;
                  color: #23527c; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
.box.rig { border-color: #b7d2bf; background: #eef6f0; }
.box.rig .box-title { color: #2e6b40; }
.box.pitfall { border-color: #ddb9b9; background: #faf0f0; }
.box.pitfall .box-title { color: #8a3535; }
/* plain-words: the equation-unpacking box — quiet, sits right under the math */
.box.plain { border: none; border-left: 3px solid #b0703a; background: #fdf8f4;
             border-radius: 0 3px 3px 0; font-size: 9.7pt; }
.box.plain .box-title { color: #8a5426; }
/* jargon: vocabulary the reader will meet in papers and code */
.box.jargon { border-color: #cfc8dc; background: #f5f3f9; }
.box.jargon .box-title { color: #4c3f6b; }
.box.jargon dt, .box.jargon strong { color: #2f2745; }
/* checkpoint: what you should now be able to explain */
.box.checkpoint { border-color: #c3cdd6; background: #f4f7f9; border-left-width: 3px;
                  border-left-color: #4878a8; }
.box.checkpoint .box-title { color: #17385c; }
.box.checkpoint ul { margin: 0.25em 0 0.1em 1.1em; }
.box.checkpoint li { margin: 0.22em 0; }

/* ---------- equations & code ---------- */
.key-eq { border-left: 3px solid #4878a8; background: #f7fafd; padding: 2px 10px;
          margin: 0.8em 0; break-inside: avoid; }
mjx-container[display="true"] { margin: 0.55em 0 !important; }
pre.code { font-family: "Noto Mono", "DejaVu Sans Mono", monospace; font-size: 8.3pt; line-height: 1.35;
           background: #f6f6f2; border: 1px solid #ddd; border-radius: 4px;
           padding: 7px 10px; margin: 0.8em 0; white-space: pre-wrap; break-inside: avoid; }

/* ---------- tables ---------- */
table.tbl { border-collapse: collapse; margin: 0.9em auto; font-size: 9.3pt; break-inside: avoid; }
table.tbl th { font-family: "Noto Sans", sans-serif; font-size: 8.6pt; text-align: left;
               background: #eaf1f8; color: #17385c; padding: 4px 9px; border: 1px solid #c9d4e0; }
table.tbl td { padding: 3.5px 9px; border: 1px solid #d8dee5; vertical-align: top; }
table.notation td:first-child { white-space: nowrap; }

ul, ol { margin: 0.45em 0 0.45em 1.3em; padding: 0; }
li { margin: 0.18em 0; }
</style>
</head>
<body>
"""

FOOT = "</body>\n</html>\n"


def main() -> None:
    parts = [HEAD, (ROOT / "frontmatter.html").read_text()]
    missing = []
    for name in CHAPTERS:
        p = ROOT / "chapters" / name
        if p.exists():
            parts.append(part_divider(name))
            parts.append(f"\n<!-- ===== {name} ===== -->\n" + p.read_text())
        else:
            missing.append(name)
    parts.append(FOOT)
    out = ROOT / "build" / "book.html"
    out.write_text("\n".join(parts))
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    if missing:
        print("MISSING chapters:", ", ".join(missing))
    if "--html-only" in sys.argv:
        return
    pdf = ROOT / "rl-field-guide.pdf"
    # Chrome's --print-to-pdf fires before Paged.js finishes a ~50-page layout,
    # so render.js drives Chrome over CDP and prints only on the completion flag.
    subprocess.run(["node", str(ROOT / "build" / "render.js"), str(out), str(pdf)],
                   check=True, timeout=660)
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pages = [l for l in info.splitlines() if l.startswith("Pages")]
    print(f"rendered {pdf} — {pages[0] if pages else '?'}")


if __name__ == "__main__":
    main()
