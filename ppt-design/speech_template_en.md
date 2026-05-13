# English Speech Template

## Slide 1 Title

Good morning. My presentation is about a replication project for dynamic pricing with demand learning and reference-price effects. The project has three parts: reproducing the main numerical experiments, comparing the published benchmark with my independent simulation, and adding a robust calibration extension.

## Slide 2 One-Sentence Problem

The central problem can be summarized in one sentence: today's price affects not only today's demand, but also the price that customers regard as reasonable tomorrow. The feedback diagram shows that price enters current demand and regret, but it also updates the reference price and therefore changes future demand states.

## Slide 3 Background and Motivation

In many markets, customers remember historical prices. A current price below the reference point can feel like a gain, while a current price above it can feel like a loss. Therefore, a pricing experiment is not a neutral data collection device; it can reshape the future demand environment.

## Slide 4 Operations Research Perspective

From an operations research perspective, this is not only a statistical estimation problem and not only a static revenue-maximization problem. The seller must jointly manage learning, earning, and state control. Aggressive exploration may generate information, but it can also distort the reference-price state.

## Slide 5 Demand Model

The demand model combines base demand, the direct price effect, asymmetric reference effects, and a random shock. The reference effect is written with gain and loss components, so price decreases and price increases can have different impacts on demand. This is the behavioral channel that a standard linear learning model misses.

## Slide 6 Reference Price and Regret

The reference price follows exponential smoothing, so it gradually moves toward historical posted prices. Regret measures cumulative revenue loss relative to a full-information benchmark. In my implementation, expected demand is used for regret evaluation, while realized demand is used only to update the estimator.

## Slide 7 Theoretical Intuition

The key theoretical intuition is that if a price is held for a sufficiently long period, the reference price converges toward that price. Therefore, if price changes are smooth enough, a policy can learn demand parameters while limiting disturbances to the reference-price state.

## Slide 8 Policy Comparison

The paper contrasts two policy families. Deterministic testing uses fixed test prices to collect information quickly, but it creates large price jumps. Slow-moving pricing uses longer episodes and smaller two-sided perturbations, so exploration is smoother and more compatible with markets that have price memory.

## Slide 9 Replication Terminology and Pipeline

For rigor, I call the converted numerical result from the published study the Published Study Benchmark, or PSB. I call my independently implemented simulation the Independent Replication Experiment, or IRE. The pipeline diagram emphasizes that PSB and IRE are kept separate in data generation and are merged only when producing shared-axis comparison figures and summary tables.

## Slide 10 Experimental Setup

The replication uses a price interval from 0.5 to 1.5, a horizon of 10000 periods, and 10 simulation replications. The two main scenarios are no-reference and reference-effect. This setup lets us test whether the same learning policy behaves differently after reference-price effects are introduced.

## Slide 11 Figure 2: Regret Under Deterministic Testing

Figure 2 shows regret under deterministic testing. Without reference effects, regret remains low. With reference effects, regret increases sharply. The PSB, IRE, and overlay views all support the same conclusion: a standard testing policy can fail when the market has reference-price memory.

## Slide 12 Figure 3: Bias in Estimated Optimal Price

Figure 3 explains where this failure comes from. In the reference-effect scenario, the estimated optimal price stays below the full-information target region. The estimator does not explicitly model the hidden reference state, so it absorbs the state effect into the demand parameters.

## Slide 13 Figure 4: State Paths Under Slow-Moving Pricing

Figure 4 shows the state paths under slow-moving pricing. The estimated price and the reference price do not jump violently; instead, they gradually move back toward a stable region. This shows that slow-moving pricing is not only learning parameters, but also controlling the reference-price state.

## Slide 14 Figure 5: Regret Under Slow-Moving Pricing

Figure 5 shows the regret performance. Compared with deterministic testing, slow-moving pricing keeps regret low in both the no-reference and reference-effect scenarios. This supports the paper's main claim: in reference-price environments, exploration must be smooth enough.

## Slide 15 Mechanism Summary

The mechanism diagram summarizes the difference between the two policies. The left side shows how deterministic testing creates large price jumps and disturbs the reference state. The right side shows how slow-moving pricing uses local perturbations and longer episodes to stabilize the state. The main lesson is that exploration is not only sampling; it is also an intervention.

## Slide 16 RARC Extension Design

Based on the replication, I add a Reference-Aware Robust Calibration experiment, or RARC. The workflow starts from a behavioral uncertainty set, combines it with candidate slow-moving schedules, runs IRE simulations, and evaluates average and worst-case regret. This moves the project from single-parameter replication to robust policy calibration.

## Slide 17 RARC Extension Results

The RARC numerical results show that the replication setting remains robust, but within the tested uncertainty set, `c0 = 0.05` and `decay = 0.20` achieve lower average final regret and lower worst-case regret. The heatmaps and frontier plot point to the same message: when reference effects are uncertain, more local and gentler exploration can be more robust.

## Slide 18 Conclusion and Outlook

The main conclusion is that learning and state control must be designed together in dynamic pricing with reference effects. The method is strong because it is interpretable and explains why a standard learning policy fails. Its limitations are that the experiments use synthetic linear demand, while real markets may include inventory, competition, and customer communication. Future work can study richer reference-price processes, adaptive perturbation schedules, and applications in promotion and subscription pricing. Thank you.
