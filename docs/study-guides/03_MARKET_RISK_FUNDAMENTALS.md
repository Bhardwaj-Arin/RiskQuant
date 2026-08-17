---
generator: pandoc
title: "-"
viewport: width=device-width, initial-scale=1.0, user-scalable=yes
---

# Market Risk Fundamentals

## What is market risk?

Market risk is the risk of loss caused by adverse movements in market
variables such as: - equity prices; - interest rates; - FX rates; -
commodity prices; - credit spreads.

For this project, focus on a simplified linear portfolio of market risk
factors.

## Risk factors vs assets

A risk factor is a market variable that drives portfolio value.

Examples: - EUR/USD; - 10Y yield; - crude oil price; - equity index
return.

## P&L

For the prototype: P&L_t = portfolio value \* portfolio return_t

Keep the sign convention explicit.

Recommended convention: - positive P&L = gain; - negative P&L = loss.

Then VaR is reported as a positive loss threshold.

## Risk horizon

Use one trading day initially.

Do not scale to multiple days automatically unless the assumptions are
explained.

## Confidence level

For learning: - 95% - 99%

The Basel market-risk internal-model framework uses Expected Shortfall
at a 97.5% one-tailed confidence level for regulatory market-risk
capital calculations. This project may study 97.5% as an educational
reference but must not claim to implement the Basel regulatory
framework.

## Historical simulation

Historical simulation uses observed historical portfolio returns
directly.

Advantages: - few distributional assumptions; - intuitive; - captures
empirical tails.

Limitations: - depends heavily on historical sample; - regime changes; -
limited data for extreme events.

## Parametric model

A parametric model summarizes returns using estimated parameters and a
distributional assumption.

Prototype: normal distribution.

Advantages: - simple; - computationally efficient; - easy to explain.

Limitations: - normal tails may be too thin; - parameters can be
unstable; - dependence structure can change.

## EWMA

EWMA gives more weight to recent observations.

Use it to demonstrate: - volatility clustering; - responsiveness to
changing conditions.

## Expected Shortfall

Expected Shortfall answers: \> If we are already in the worst alpha% of
outcomes, how large is the average loss?

This makes it a tail-severity measure rather than only a threshold.

## Stress testing

Stress testing evaluates losses under adverse scenarios.

A scenario can be: - historical; - hypothetical; - sensitivity-based; -
multi-factor.

## Reverse stress testing

Reverse stress starts with a predefined adverse outcome and works
backward to identify scenarios that could produce it.

BIS guidance published in 2026 describes reverse stress testing in this
way and identifies stress testing as a core risk-management tool.

## Risk attribution

Risk attribution asks: \> Which exposures/risk factors are responsible
for the portfolio's risk?

This turns a risk number into an actionable explanation.

## Important distinction

This project is about market-risk measurement and model validation. It
is not: - a credit default model; - a counterparty exposure simulator; -
a derivatives pricing engine; - a full regulatory capital engine.
