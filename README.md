# rl — theory hub and learning roadmap

The central place for RL + robotics theory and planning. The experiments live in sibling repos; this repo holds the map.

## Contents

- **`ROADMAP.md`** — the 5–6 month robot-learning study roadmap: how the four fronts (RL, robotics, ROS 2, simulation) fit together, phased milestones, and the LeHome replication capstone.
- **`textbook/rl-field-guide.pdf`** — *Reinforcement Learning for Real Robots* (2nd edition). **209 pages, 15 chapters in 5 parts + 2 appendices**, covering the full LeHome Challenge stack. Part I foundations (MDPs → policy gradients → PPO/GAE); Part II AWR/AWAC; **Part III the generative-policy arc** (why Gaussians fail → diffusion from zero → flow matching → VLAs → *PPO vs. VLA-RL side by side* → RECAP); Part IV reward/advantage engineering, inference-time optimization, DAgger/HIL-SERL, sim-to-real; Part V the staged replication capstone. Every key equation is followed by an "In plain words" box; every chapter has a jargon box, worked examples with all arithmetic shown, and an end-of-chapter checkpoint. Appendix A is a tiered reading guide; Appendix B is the experiment ladder (E1–E12).
- **`textbook/chapters-ed1/`** — the 59-page first edition's sources, kept for reference.
- **`textbook/research/`** — verified research digests (LeHome tech report, Pi0.5/Pi*0.6, auxiliary papers, diffusion) used to fact-check the book.
- **`textbook/chapters/`** — chapter sources (HTML fragments); **`textbook/frontmatter.html`** — cover/TOC/preface.
- **`textbook/STYLE.md`** — the house style contract (pedagogy rules, box types, figure palette, notation discipline). Read it before writing or revising any chapter; it is what makes the book readable.

## Rebuilding the PDF

```bash
cd textbook/build && python3 build.py     # assembles book.html, renders via headless Chrome
```

Requires `google-chrome`, `node` (for `build/render.js`, which drives Chrome over the DevTools protocol and prints only after Paged.js finishes pagination), and `poppler-utils`. MathJax, Paged.js, and `chrome-remote-interface` are vendored under `textbook/` — no network needed to rebuild.

## Sibling repos (the practice)

| Repo | What it is | Roadmap phase |
|---|---|---|
| `../rl-boarding` | Gymnasium fundamentals (gridworld, wrappers) | done — foundations |
| `../rl-rover` | Custom env → PPO → MuJoCo → domain randomization → real rover; v1 adds LIDAR + ROS 2 | Phases 0, 4 (ROS 2 track) |
| `../hil-serl` | HIL-SERL on the real SO-101 with LeRobot | Phases 1, 4 |
| `../lehome-replica` (future) | The capstone | Phases 2–4 |
