# House style — *Reinforcement Learning for Real Robots*

The contract that produced edition 2 (209 pages), after edition 1 (59 pages) was rejected as too dense.
Any new chapter, revision, or spin-off book for Lucas follows this. Nothing here is decoration —
each rule fixes a specific way edition 1 failed its reader.

## The reader

A strong software engineer retraining into robotics RL. Working calculus and probability (reads an
expectation, a gradient, a Gaussian without looking them up; no measure theory). Real hands-on RL:
PPO/SB3, custom Gymnasium envs, MuJoCo, domain randomization, a real SO-101 running HIL-SERL.
**Never touched generative models, transformers, or VLAs.** Wants intuition first, then the math,
then the bridge to his own hardware. Density is his enemy, not difficulty.

## The seven pedagogy rules

1. **Never state a solution before the reader feels the problem.** Every idea arrives as: (a) what we
   want, (b) the obvious thing to try, (c) exactly how and why it fails — with a concrete instance,
   (d) the fix, (e) why the fix works. Edition 1 jumped to (d); that is what made it unreadable. The
   fix alone is a fact to memorize; the sequence is understanding.
2. **Every key equation gets an "In plain words" box** naming *every* symbol and saying what the
   formula does. 2–5 per chapter. Never assume a symbol is self-evident.
3. **Define jargon inline at first use**, plus one "Words you will hear" box per chapter covering
   3–6 terms he will meet in papers and codebases — including terms the book does not otherwise use,
   so papers stop being opaque.
4. **At least two analogies per chapter, each with its limit stated immediately.** A good analogy
   with a stated limit teaches; an unlimited one misleads. ("Chess captures delayed evaluative
   feedback exactly, and hidden state and stochastic dynamics not at all.")
5. **At least one worked example per chapter with every arithmetic step shown.** Never jump from
   setup to answer. The best ones make an abstract claim physical — e.g. hand-computing three
   denoising steps and watching the sample land on a *mode* rather than the average.
6. **End every chapter with a Checkpoint box**: 4–6 bullets of what the reader should now be able to
   explain or do, phrased so a false bullet tells him which section to re-read. Then a short
   "Where to go deeper" paragraph naming papers.
7. **No compression.** Three ideas in a sentence become three sentences. A paragraph needing a
   re-read gets split. Concrete instance before abstraction. Long is fine; dense is not.

## Boxes (CSS classes in `build/build.py`)

| Class | Title | Job |
|---|---|---|
| `box plain` | In plain words | Unpack the preceding equation, every symbol named |
| `box jargon` | Words you will hear | Vocabulary for reading papers and code |
| `box lehome` | In the LeHome solution | Where the idea appears in the running example, with real numbers |
| `box rig` | On your rig | Connection to rl-rover / hil-serl / the SO-101 |
| `box pitfall` | Pitfalls | Mistakes that cost weeks, including ones he has hit |
| `box checkpoint` | Checkpoint | What you can now explain (chapter end) |

Boxes run up to ~120 words. Every chapter carries lehome (unless the whole chapter is LeHome),
at least one pitfall, and a checkpoint; rig where natural.

## Tone and language

Warm, direct, patient, precise. Address the reader as "you". American English. No hype, no filler,
no cheerleading. Explain, don't impress. Saying "this is genuinely hard" or "everyone finds this
confusing at first" is good when true. Chapter openers may name the difficulty outright — *"You will
find diffusion strange for about ten minutes and then obvious. Everyone does."*

## Structure

- Parts group chapters; each part gets a divider page with a one-sentence blurb.
- One `<h1>` per file, `<h2>` as `N.1`, numbered `<h3>` as `N.1.1` (book-wide, so subsections can be cited).
- Chapters are HTML fragments: a single `<section class="chapter" id="chNN">`, no `<style>`/`<script>`.
- Word budgets 4,200–5,000 per chapter. **Under-writing is the failure mode to guard against.**
- A chapter that would need to teach four new concepts is really four chapters. Edition 1's Chapter 5
  became edition 2's Chapters 5–9.

## Math

MathJax TeX; `\(...\)` inline, `\[...\]` display; `\lt`/`\gt` never raw angle brackets; no Unicode
math glyphs inside TeX. The 2–4 central equations per chapter go in `<div class="key-eq">`, each
followed by its plain-words box. Notation is fixed in one table in the front matter and never drifts;
flag every collision explicitly (flow time `u` vs. env timestep `t`, diffusion index `k`,
`ρ_GV` vs. `ρ_t`, schedule `β_k` vs. AWR temperature `β`).

## Figures

Hand-authored inline SVG, `viewBox="0 0 W H"`, W ≤ 700, H ≤ 320. `font-family="Noto Sans"`, sizes
10–13. Palette: blue `#4878a8`/`#eaf1f8`, orange `#b0703a`/`#f8efe8`, green `#4a8a5c`/`#ecf5ee`,
text `#333`, red accent `#b04a4a`, gray `#666`, `rx=6`. **Every marker/gradient id prefixed by
chapter and figure** (`ch06f2arr`) — collisions across files break rendering silently. Leave padding:
~7px per character at size 12.

**Captions teach.** 2–3 sentences saying what to notice, never a five-word label:
*"Notice where the cost is: the dashed feedback arrow is traversed once per denoising step…"*

## Facts

Every claim about LeHome, Pi0.5/Pi*0.6, or the papers must trace to `textbook/research/*.md`
(digests fetched from primary sources). Invented numbers and invented method details are critical
defects. Where the book simplifies for teaching, say so and name the fuller version.
