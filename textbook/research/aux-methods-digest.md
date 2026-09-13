# Research Digest: Grounding Facts for Textbook

## 1. HIL-SERL (arXiv 2410.21845) — VERIFIED (abstract + numbers), details FROM-KNOWLEDGE

Luo, Xu, Wu, Levine (Berkeley): "Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning." Pipeline: (1) a small set of teleoperated offline demos seeds a prior-data buffer; (2) a binary reward classifier trained on human-labeled success/failure images provides the sparse reward; (3) during online training a human can intervene via SpaceMouse teleoperation, and intervention transitions are stored (in the demo buffer) as corrections; (4) the learner is RLPD — an off-policy SAC-style actor–critic with **symmetric sampling** (each batch is 50% offline/intervention data, 50% online replay), high update-to-data ratio, critic ensembling, and layer norm. Update target:

$$y = r + \gamma\, \mathbb{E}_{a'\sim\pi}\big[\min_{i} Q_{\bar\theta_i}(s',a')\big], \qquad \mathcal{B} = \tfrac{1}{2}\mathcal{B}_{\text{demo+interv}} + \tfrac{1}{2}\mathcal{B}_{\text{online}}$$

Verified results: near-perfect (≈100%) success rates on nearly all tasks within **1–2.5 hours** of real-world training per task, an average **2× success-rate improvement** and **1.8× faster execution (cycle time)** than imitation-learning baselines. Tasks span three families: dynamic manipulation (e.g., object flipping in a pan, Jenga whipping), precision assembly (RAM/SSD insertion, timing-belt assembly, IC-chip insertion, dashboard assembly), and dual-arm coordination. Interventions taper off as the policy improves — the human effectively hard-mines failure states early in training.

## 2. Real-Time Chunking (arXiv 2506.07339) — VERIFIED

Black, Galliker, Levine: "Real-Time Execution of Action Chunking Flow Policies." Problem: a VLA emits chunks of $H$ actions, but inference latency $\delta$ means either the robot pauses between chunks (synchronous) or, if the next chunk is generated asynchronously from a stale observation, the new chunk disagrees with actions already being executed, causing jerky discontinuities at chunk boundaries. RTC is an inference-time, no-retraining fix that frames next-chunk generation as **inpainting**: while chunk $k$ executes, generate chunk $k{+}1$; the first $d$ actions (those guaranteed to execute before generation finishes) are **frozen** to the corresponding tail of chunk $k$, and the remaining overlap region is softly encouraged to stay close to the old chunk via a decaying mask $W$, with the post-overlap actions generated freely. Mechanically this is guidance during flow-ODE integration (diffusion-inpainting style): the velocity field is corrected toward consistency with the frozen prefix,

$$A^{\text{new}}_{1:d} \leftarrow A^{\text{prev}}_{d':d'+d}, \qquad v'(A^\tau) = v_\theta(A^\tau) + \beta\, W \odot \big(\text{correction toward } A^{\text{prev}}\big)$$

so continuity is guaranteed where actions are committed and blended where they are not. Results: on 12 Kinetix simulated tasks and 6 real bimanual tasks, RTC preserves high success rates and task throughput even under large injected inference delays, including precision tasks like lighting a match; baselines (naive async swap, temporal ensembling) degrade.

## 3. Difficulty-Targeted Data Selection (arXiv 2506.05316) — VERIFIED

Sun et al., "Improving Data Efficiency for LLM Reinforcement Fine-tuning Through Difficulty-targeted Online Data Selection and Rollout Replay" (NeurIPS 2025). Core idea: in GRPO-style RL, a question whose rollouts are all correct or all wrong yields zero advantage and zero gradient; the learning signal is maximal at **moderate difficulty** (success probability near 0.5). Define adaptive difficulty from current-policy rollouts,

$$d(q) = 1 - \tfrac{1}{G}\sum_{i=1}^{G} \mathbb{1}[o_i \text{ correct}],$$

and preferentially select questions with $d(q)$ near the middle. To avoid rolling out on everything, they roll out only a small reference set and estimate other questions' difficulty with an attention/similarity-based predictor; a **rollout replay** buffer reuses recent rollouts to cut per-step compute. Verified result: 23–62% reduction in RL fine-tuning time to reach the same performance as vanilla GRPO across six model–dataset combinations. For a robotics textbook, this is the principled version of hard mining for rollout selection: spend rollouts and gradient steps on tasks/states where the policy succeeds sometimes, not on solved or hopeless ones.

## 4. BEHAVIOR Challenge Winner (arXiv 2512.06951) — VERIFIED

Larchenko, Zarin, Karnatak: "Task adaptation of Vision-Language-Action model: 1st Place Solution for the 2025 BEHAVIOR Challenge" — 50 long-horizon household tasks in photorealistic simulation (bimanual manipulation + navigation), won with **26% q-score** on public and private leaderboards. Architecture: π0.5 (Pi0.5) base with learnable mixed-layer attention and a "System 2" stage tracker — a linear classifier on VLM features (~99% train accuracy) with a sliding-window voting rule (advance on 2-of-3 votes, skip a stage on 3-of-3 for stage+2, roll back only on unanimity). Training uses **multi-sample flow matching**: 15 flow predictions per VLM forward pass with different noise/time samples, amortizing the expensive VLM pass and reducing gradient variance, plus correlated noise. The chunk post-processing (the part relevant to LeHome — note the paper itself doesn't mention LeHome; that link is your project's): (a) **action compression** — cubic-spline resampling of a predicted 26-action chunk down to 20 executed steps at 30 Hz (1.3× speedup), scaling base velocity dimensions by 1.3× while leaving joint targets to the controller, and **disabling compression whenever gripper state changes significantly** so grasps execute at full resolution; (b) **correction rules** — the big one is gripper recovery: if the gripper is closed at a task stage where it was never closed in training data, treat it as a failed grasp and fully open it; this alone roughly doubled success on some tasks. One task-specific rollback rule existed (radio task); the authors flag such rules as non-scalable.

## 5. HG-DAgger (arXiv 1810.02890) — FROM-KNOWLEDGE

Kelly, Sidrane, Driggs-Campbell, Kochenderfer: "HG-DAgger: Interactive Imitation Learning with Human Experts." Vanilla DAgger (Ross, Gordon & Bagnell, arXiv 1011.0686) executes a stochastic mixture $\pi_i = \beta_i \pi^* + (1-\beta_i)\hat\pi_i$, has the expert relabel **every** visited state, aggregates $\mathcal{D} \leftarrow \mathcal{D} \cup \{(s, \pi^*(s))\}$, and retrains — giving no-regret guarantees, but the mixture is unsafe/confusing with human experts, and dense relabeling is burdensome. HG-DAgger replaces the mixing coefficient with a **human gate**: the novice runs autonomously until the human judges it necessary to intervene, at which point the human takes full control:

$$\pi_{\text{HG}}(s) = \begin{cases} \pi_H(s) & \text{human engaged} \\ \pi_N(s) & \text{otherwise} \end{cases}$$

and **only the states/actions from intervention segments** are added to the training set (no relabeling of autonomous states). This naturally concentrates labels on the failure boundary of the current policy, and the intervention statistics also yield a learned risk/"doubt" metric for gauging policy safety. It is exactly the labeling rule HIL-SERL's intervention buffer inherits in spirit.

## 6. Potential-Based Reward Shaping (Ng, Harada & Russell, 1999) — FROM-KNOWLEDGE

"Policy Invariance Under Reward Transformations" (ICML 1999). Theorem: adding a shaping reward $F$ to an MDP preserves the set of optimal policies (in fact, near-optimal policies too) **if and only if** (necessity holding when dynamics/reward are otherwise arbitrary) $F$ is potential-based:

$$F(s, a, s') = \gamma\, \Phi(s') - \Phi(s)$$

for some potential function $\Phi : S \to \mathbb{R}$. The shaped and original value functions relate by $Q'^*(s,a) = Q^*(s,a) - \Phi(s)$ and $V'^*(s) = V^*(s) - \Phi(s)$, so the argmax over actions is unchanged in every state. Intuition: along any trajectory the shaping terms telescope, contributing $\gamma^T\Phi(s_T) - \Phi(s_0)$, which is policy-independent (in expectation/limit). Choosing $\Phi \approx V^*$ gives dense guidance without changing what "optimal" means; non-potential shaping (e.g., raw progress bonuses) can create reward-cycling exploits — the paper's famous bicycle example rides in circles.

## 7. CUPED (Deng, Xu, Kohavi & Walker, 2013) — FROM-KNOWLEDGE

"Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data" (WSDM 2013). A control-variates estimator: for metric $Y$ and a covariate $X$ unaffected by treatment (canonically, the same metric measured pre-experiment), define

$$Y^{\text{cv}}_i = Y_i - \theta\,(X_i - \bar{X}), \qquad \theta^* = \frac{\operatorname{Cov}(Y, X)}{\operatorname{Var}(X)}$$

The adjusted mean $\bar{Y}^{\text{cv}}$ is unbiased for $\mathbb{E}[Y]$ (since $\mathbb{E}[X]$ cancels or is known/estimated pooled), and at $\theta^*$ its variance is

$$\operatorname{Var}(\bar{Y}^{\text{cv}}) = \operatorname{Var}(\bar{Y})\,(1 - \rho^2), \quad \rho = \operatorname{corr}(Y, X)$$

so a covariate correlated at $\rho = 0.7$ halves the variance. The treatment effect is estimated as the difference of adjusted means across arms; because randomization makes $X$ independent of assignment, the adjustment cannot bias the effect. This is equivalent to one-step regression adjustment and transfers directly to robot evaluation: use a pre-treatment covariate (e.g., a baseline policy's success on the same initial condition) to shrink A/B eval variance.

## 8. GRPO (DeepSeekMath, arXiv 2402.03300) — FROM-KNOWLEDGE

Shao et al. Group Relative Policy Optimization removes PPO's learned value function: for each prompt $q$, sample a group of $G$ responses $\{o_i\}$ from the old policy, score them $\{r_i\}$, and compute the **group-relative advantage** by within-group standardization:

$$\hat{A}_i = \frac{r_i - \operatorname{mean}(\{r_1,\dots,r_G\})}{\operatorname{std}(\{r_1,\dots,r_G\})}$$

with every token of $o_i$ receiving the same $\hat{A}_i$ under outcome supervision (process supervision assigns per-step normalized rewards summed over subsequent steps). The objective is the PPO clipped surrogate with this advantage, plus a KL penalty to a reference policy using the unbiased nonnegative estimator $\mathbb{D}_{KL} \approx \tfrac{\pi_{\text{ref}}}{\pi_\theta} - \log\tfrac{\pi_{\text{ref}}}{\pi_\theta} - 1$ added directly to the loss rather than folded into the reward. The group mean acts as a Monte Carlo baseline — which is why all-identical-reward groups contribute zero gradient (the hook for §3's difficulty targeting).

## 9. AWR (1910.00177) & AWAC (2006.09359) — FROM-KNOWLEDGE

**AWR** (Peng, Kumar, Zhang, Levine). Derivation sketch: maximize expected improvement $\mathbb{E}_{s,a\sim\pi}[A^{\pi_{\text{old}}}(s,a)]$ subject to $D_{KL}(\pi \,\|\, \pi_{\text{old}}) \le \epsilon$. The Lagrangian yields the closed-form nonparametric solution

$$\pi^*(a|s) \propto \pi_{\text{old}}(a|s)\, \exp\!\big(A(s,a)/\beta\big)$$

and projecting $\pi^*$ onto a parametric class by minimizing forward KL gives a weighted maximum-likelihood ("advantage-weighted regression") update:

$$\theta \leftarrow \arg\max_\theta\, \mathbb{E}_{(s,a)\sim\mathcal{D}}\big[\log \pi_\theta(a|s)\, \exp(A(s,a)/\beta)\big]$$

AWR estimates $A$ with a Monte-Carlo/TD($\lambda$) **state-value baseline** $V(s)$ fit by regression on the replay buffer. **AWAC** (Nair, Gupta, Dalal, Levine, "Accelerating Online RL with Offline Datasets") keeps the identical actor update but computes $A(s,a) = Q(s,a) - \mathbb{E}_{a'\sim\pi}Q(s,a')$ from an off-policy **Q-function trained by TD bootstrapping**, and enforces the KL constraint implicitly against the replay-buffer distribution without fitting an explicit behavior model. That combination makes it well-suited to offline pretraining on demonstrations followed by sample-efficient **online fine-tuning**, avoiding both the over-conservatism of offline-RL penalties and the forgetting/collapse of naive BC-then-RL.

## 10. Flow Matching (Lipman et al., arXiv 2210.02747) — FROM-KNOWLEDGE

Flow matching trains a velocity field $v_\theta(x, t)$ whose ODE transports noise to data. The intractable marginal-velocity regression is replaced by **conditional flow matching**, which has identical gradients: condition on a data point $x_1$, define a simple probability path, and regress onto its known conditional velocity. With the linear (optimal-transport / rectified-flow) interpolant $x_t = (1-t)\,x_0 + t\,x_1$, $x_0 \sim \mathcal{N}(0, I)$, the target velocity is constant in $t$ and the loss is

$$\mathcal{L}_{\text{CFM}} = \mathbb{E}_{t \sim \mathcal{U}[0,1],\, x_1 \sim p_{\text{data}},\, x_0 \sim \mathcal{N}(0,I)} \big\|\, v_\theta(x_t, t) - (x_1 - x_0) \,\big\|^2$$

(Lipman et al.'s exact OT-Gaussian path uses $\mu_t = t x_1$, $\sigma_t = 1-(1-\sigma_{\min})t$ with $u_t(x|x_1) = \frac{x_1 - (1-\sigma_{\min})x}{1-(1-\sigma_{\min})t}$; the simple form above is the $\sigma_{\min}\!\to\!0$ version used by π0-style policies.) Sampling integrates the learned ODE $\frac{dx}{dt} = v_\theta(x, t)$ from $t=0$ (noise) to $t=1$ (data), typically with a handful of Euler steps ($x \leftarrow x + \Delta t\, v_\theta$) — e.g., 10 steps in π0 — because straight-ish OT paths make coarse integration accurate. Deterministic, simulation-free training and few-step deterministic sampling are why VLAs prefer it over DDPM-style diffusion.

## 11. Classifier-Free Guidance (Ho & Salimans, arXiv 2207.12598) — FROM-KNOWLEDGE

Train a single conditional denoiser $\epsilon_\theta(x_t, c)$ while randomly **dropping the condition** (replacing $c$ with a null token $\varnothing$) with probability $p_{\text{uncond}}$ (typically 10–20%), so one network jointly learns conditional and unconditional score estimates. At sampling time, extrapolate away from the unconditional prediction with guidance scale $g$:

$$\tilde{\epsilon}(x_t, c) = \epsilon_\theta(x_t, \varnothing) + g\,\big(\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing)\big)$$

$g = 1$ recovers plain conditional sampling; $g > 1$ amplifies the condition, equivalent to sampling from a distribution $\propto p(x|c)\,\big(p(c|x)\big)^{\,g-1}$ — sharpening an implicit classifier without training one (the original motivation, replacing classifier guidance). The cost is a fidelity–diversity trade-off (higher $g$ → higher sample quality/adherence, lower diversity, eventual saturation artifacts) and two forward passes per denoising step. The same formula applies verbatim to flow-matching velocity fields ($\tilde{v} = v_\varnothing + g(v_c - v_\varnothing)$), which is how goal- or language-conditioned robot policies modulate conditioning strength.