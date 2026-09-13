# Digest: π0.5 and π*0.6 / RECAP (Physical Intelligence)

Both papers were successfully fetched (arxiv abstract pages + full HTML). Claims are labeled **VERIFIED** (from fetched text, source noted) or **FROM-KNOWLEDGE** (prior knowledge, unverified in this session).

---

## Paper 1 — π0.5: a VLA with Open-World Generalization (arXiv:2504.16054)

**What it is.** VERIFIED (abstract): "a new model based on π0 that uses co-training on heterogeneous tasks to enable broad generalization... data from multiple robots, high-level semantic prediction, web data, and other sources." The headline demo: cleaning kitchens and bedrooms in entirely new homes never seen in training.

### Architecture

- **VLM backbone.** VERIFIED (html): weights are "initialized from a standard VLM trained on data from the web"; the paper's main text does not name it. FROM-KNOWLEDGE: as with π0, the backbone is PaliGemma (~3B parameters), and the action expert is ~300M parameters, giving a single mixture-of-experts-style transformer where the action expert is a smaller set of weights attending to the VLM's KV cache.
- **Action expert.** VERIFIED: "significantly smaller than the rest of the LLM backbone"; it is **initialized with random weights at post-training** (not pre-trained).
- **Dual action representation — discrete + continuous.** VERIFIED: Pre-training represents actions as **discrete tokens via the FAST tokenizer** ("simple, scalable, and efficient training"). Post-training adds the action expert producing **continuous action chunks via flow matching**; the model "trains on discretized actions but still allows for use of flow matching to produce continuous actions at inference time." The combined post-training loss is next-token prediction + α·(flow-matching loss) with **α = 10.0**.
- **Flow matching mechanics.** VERIFIED: action tokens "receive the partially denoised actions from the previous step of flow matching as input, and output the flow matching vector field." Inference integrates **10 denoising steps**, conditioned on text tokens, to produce an action chunk. FROM-KNOWLEDGE: chunk length H = 50 actions (1 s at 50 Hz), same as π0; the html extraction did not state H explicitly.
- **Hierarchical inference.** VERIFIED: two-stage inference in one model. First the model autoregressively predicts a **high-level subtask in text** — π_θ(ℓ̂ | o_t, ℓ), e.g. "pick up the plate" — then, conditioned on that subtask, the action expert predicts low-level actions π_θ(a_{t:t+H} | o_t, ℓ̂). High-level inference runs at lower frequency than low-level inference. High-level uses all four cameras (forward, backward, both wrists); low-level uses forward + wrist cameras.

### Training data recipe and co-training

VERIFIED (html), the co-training mixture:

1. **MM (Mobile Manipulator):** ~**400 hours** of mobile manipulators doing household tasks in ~**100 home environments**.
2. **ME (Multi-Environment):** static (non-mobile) arms in diverse homes.
3. **CE (Cross-Embodiment lab data):** lab tasks (table bussing, shirt folding) incl. the OXE dataset.
4. **HL (High-Level subtask prediction):** all robot data manually annotated with semantic subtask descriptions.
5. **WD (Web Data):** captioning (CapsFusion, COCO), VQA (Cambrian-7M, PixMo, VQAv2), object localization.
6. **VI (Verbal Instructions):** expert users giving "language demonstrations" (step-by-step spoken subtask commands), used in post-training.

Key statistic, VERIFIED: **97.6% of first-phase training examples are NOT mobile-manipulator household data** — generalization is driven by everything else.

**Two stages.** VERIFIED:
- **Pre-training, 280k gradient steps:** all sources (MM, ME, CE, HL, WD), discrete FAST tokens only (α=0), standard autoregressive training.
- **Post-training, 80k steps:** MM+ME filtered to successful, short-enough episodes; HL; VI; WD retained to preserve semantics; **CE dropped**; hybrid discrete + flow-matching objective (α=10); action expert added from scratch.

### Open-world generalization claims

VERIFIED: evaluated in **3 kitchens and 3 bedrooms in real homes not seen in training**; tasks like put items in drawer, dishes in sink, clothes in laundry basket, 10 trials per task/environment; multi-stage tasks of **2–5 minutes**, with full cleaning runs of **10–15 minutes**. **Scaling with environment count:** performance rises across 3 → 12 → 22 → 53 → 82 → 104 training locations; a control model trained *on the test homes* achieved similar performance — i.e., co-training closes the gap to in-domain training. Language-following on out-of-distribution objects rose from ~20% (3 locations) to ~60% (104 locations).

### Inference cost

VERIFIED: **10 flow-matching (denoising) steps** per chunk; control at **50 Hz** with action chunking; 18–19-dim action space (arm joints, grippers, base velocities, torso lift); high-level text inference at lower frequency than the action loop.

---

## Paper 2 — π*0.6: a VLA That Learns From Experience (arXiv:2511.14759)

**Acronym.** VERIFIED: **RECAP = "RL with Experience and Corrections via Advantage-conditioned Policies."**

**Abstract claims.** VERIFIED: RECAP pre-trains a generalist VLA with offline RL (yielding π*0.6), then specializes via on-robot data collection with demonstrations, on-policy rollouts, and expert teleoperated interventions. Result: folds laundry in real homes, reliably assembles boxes, makes espresso drinks on a professional espresso machine; "on some of the hardest tasks, RECAP more than doubles task throughput and roughly halves the task failure rate."

### Architecture (vs. π0.5)

VERIFIED (html): backbone upgraded to **Gemma 3 4B** VLM; **action expert enlarged to 860M parameters**; advantage-indicator **text-token conditioning** added to the input; pre-training data augmented with additional multi-robot-platform data; same **Knowledge Insulation (KI)** training recipe as before (FROM-KNOWLEDGE gloss: KI = training the backbone on discrete FAST tokens while gradients from the flow-matching action expert are stopped from flowing into the backbone, per the earlier π0.5+KI paper).

### The method, exactly

**Value function.** VERIFIED: a separate, smaller **670M-parameter Gemma 3 VLM** trained as a **distributional critic**: p_φ(V | o_t, ℓ) over **B = 201 discretized value bins**, trained with **cross-entropy** against the empirical return-to-go R_t(τ) = Σ r_t′ (Monte Carlo return to episode end, discretized). Loss: min_φ E_τ [Σ_t H(R_t^B(τ), p_φ(V|o_t, ℓ))].

**Advantage conditioning.** VERIFIED: the advantage enters the policy **as a literal text token in the VLA's input sequence** — "Advantage: positive" or "Advantage: negative." The conditioning signal is a **binary indicator** I_t = 1(A(o_t, a_t, ℓ) > ε_ℓ), with the per-task threshold **ε_ℓ set at the 30th percentile** of value-function outputs for that task. Policy objective (VERIFIED): min_θ E_D[−log π_θ(a_t|o_t,ℓ) − α log π_θ(a_t|I_t,o_t,ℓ)] — i.e., jointly train the unconditioned and advantage-conditioned policies.

**Three data sources.** VERIFIED:
1. **Demonstrations** — pre-train value function and policy; treated with I_t = True in fine-tuning.
2. **On-policy autonomous rollouts** — added to the dataset with advantage indicators computed from the critic.
3. **Expert teleoperated corrections** — interventions during autonomous execution; correction actions get **forced I_t = True** (the expert's fix is assumed advantageous).

All merged into one per-task dataset D_ℓ for iterative training.

**Pipeline stages.** VERIFIED:
1. **Offline-RL pre-training:** train value function on the multi-task demo corpus; estimate per-task thresholds ε_ℓ; train π*0.6 with advantage conditioning on all demos.
2. **Task-specific iterations (repeatable):** fine-tune the value function on task data → fine-tune π*0.6 from the pre-trained checkpoint → deploy the policy autonomously with an expert monitoring and providing corrections → fold new rollouts/corrections back in → repeat.

**Inference-time conditioning.** VERIFIED: at test time, sample from **π_θ(a | I = True, o, ℓ)** — condition on the positive-advantage token (β = 1). Optionally apply **classifier-free-guidance-style blending** (β > 1) between π_θ(·|I=True) and π_θ(·|I=False) to push harder toward high-advantage actions — "steering toward actions the model learned were improvements."

### Headline results

VERIFIED (html + abstract):
- **Throughput** (successful completions/hour): **>2×** on diverse laundry (hardest items) and espresso making; smaller but real gains on t-shirts/shorts; **2× throughput** on box assembly after iteration 2.
- **Failure rate:** roughly **halved** on the hardest tasks; final success rates in the **90%+ range** on most tasks; laundry with targeted failure removal reached **97%** under a strict collar-facing criterion.
- **Endurance:** espresso ran **13 hours straight** autonomously; diverse laundry in a new home ran **over two hours without interruption**; box assembly demonstrated in a factory-deployment scenario.
- FROM-KNOWLEDGE: the espresso task includes milk steaming and pouring latte art; the fetched text confirms "espresso drinks on a professional espresso machine" but the extraction did not explicitly surface the phrase "latte art."

---

## RECAP vs. AWR and classifier-free guidance (one paragraph)

FROM-KNOWLEDGE (analysis; the paper itself makes the CFG connection explicitly, VERIFIED via the β>1 mechanism above). Advantage-Weighted Regression (AWR) performs offline policy improvement by **re-weighting** the behavior-cloning loss with exp(A/λ): good actions get larger gradient weight, bad ones smaller, and the resulting policy directly imitates a reweighted distribution. RECAP instead performs improvement by **conditioning**: it trains on *all* data at equal weight but labels each action with a binarized advantage token, learning both π(a|I=True) and π(a|I=False); improvement is deferred to inference by sampling with I=True. This is the "upside-down RL"/decision-transformer-style trick (condition on outcome, then ask for the good outcome), which avoids AWR's weight truncation/variance issues and, crucially for flow-matching policies, avoids reweighting a regression loss whose samples are denoising targets. The β>1 mode is exactly **classifier-free guidance** transplanted from diffusion models: the conditional and unconditional (here, negatively-conditioned) score/velocity estimates are extrapolated, v = v(I=False) + β·[v(I=True) − v(I=False)], amplifying the direction that separates high-advantage behavior from the rest — an implicit classifier of "advantageous action" guiding generation, with β controlling the strength of policy improvement at test time.

---

**Sources:**
- [π0.5 abstract](https://arxiv.org/abs/2504.16054), [π0.5 full HTML](https://arxiv.org/html/2504.16054v1)
- [π*0.6 abstract](https://arxiv.org/abs/2511.14759), [π*0.6 full HTML](https://arxiv.org/html/2511.14759v1)