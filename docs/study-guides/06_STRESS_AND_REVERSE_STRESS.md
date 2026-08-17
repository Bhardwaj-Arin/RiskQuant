---
generator: pandoc
title: "-"
viewport: width=device-width, initial-scale=1.0, user-scalable=yes
---

# Stress Testing and Reverse Stress Testing

## 1. Stress testing objective

Estimate portfolio losses under adverse but plausible market scenarios.

## 2. Scenario categories

### Historical

Replay observed changes from a historical stress period.

### Hypothetical

Define shocks manually.

Example: - equity -20% - EUR/USD -5% - oil -15% - rates +100 bps - gold
+10%

### Sensitivity

Change one risk factor while holding others fixed.

### Multi-factor

Shock several risk factors simultaneously.

## 3. Scenario engine

Inputs: - baseline risk factors; - shock vector; - portfolio weights; -
mapping from risk factor to portfolio return.

Output: - shocked P&L; - percentage loss; - factor contributions.

## 4. Historical stress

Do not simply label the worst day as a "crisis scenario" without
documenting the date and reason.

## 5. Reverse stress testing

Start with an unacceptable outcome.

Example: Target loss = 10% of portfolio.

Find the smallest plausible shock vector that reaches the target.

Optimization: minimize \|\|Delta x\|\|\_2 subject to: Loss(Delta x) \>=
TargetLoss LowerBound \<= Delta x \<= UpperBound

Interpretation: What is the minimum-sized combination of shocks that can
make the portfolio breach the loss threshold?

## 6. Why reverse stress is useful

It helps identify vulnerabilities that ordinary scenario testing may
miss.

Example: A portfolio may tolerate a 15% equity decline alone but breach
its threshold when a smaller equity shock combines with a rate and FX
shock.

## 7. Constraints

Constraints make reverse stress more realistic.

Examples: - equity shock between -30% and 0%; - rates shock between 0
and +300 bps; - FX shock between -15% and +15%; - commodity shock
between -25% and +25%.

These are modelling assumptions for the project, not regulatory limits.

## 8. Plausibility

A mathematically valid stress is not automatically economically
plausible.

Report: - constraints; - magnitude; - sign; - interpretation; - whether
the scenario resembles historical conditions.

## 9. Interview explanation

Normal stress: \> I define a scenario and measure the resulting loss.

Reverse stress: \> I define the unacceptable loss first and solve
backward for the market-factor shock that can produce it.

## 10. Validation

After solving: - verify the target loss is actually reached; - verify
constraints; - rerun from the same configuration; - test alternative
starting points if the solver is non-convex; - report whether the
solution is unique or simply one feasible solution.

## 11. Avoid overclaiming

Do not say: "this finds the true worst-case market scenario."

Say: "this finds a minimum-norm scenario under the project's specified
portfolio model and constraints."
