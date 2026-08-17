---
generator: pandoc
title: "-"
viewport: width=device-width, initial-scale=1.0, user-scalable=yes
---

# Risk Attribution Study Guide

## Goal

Turn a risk number into an explanation.

Question: \> Which risk factors drive the portfolio's VaR, volatility,
stress loss, or expected shortfall?

## Linear portfolio

Portfolio return: R_p = w'R

For variance: sigma_p\^2 = w'Sigma w

A transparent contribution analysis can use marginal and component
contributions.

## Marginal risk contribution

For volatility: MRC_i = partial sigma_p / partial w_i

Under standard deviation: MRC = Sigma w / sigma_p

Component contribution: CC_i = w_i \* MRC_i

Sum of component contributions should equal total portfolio volatility
under the consistent formulation.

## Interpretation

A large contribution can come from: - large exposure; - high
volatility; - strong covariance with the portfolio.

## Stress attribution

For a scenario: total P&L = sum_i contribution_i

This is especially easy to explain for a linear portfolio.

## VaR attribution

Keep the first implementation simple and transparent. If the project
later adds more advanced VaR attribution, document the method carefully.

## Dashboard output

Example: \| Risk Factor \| Weight \| Volatility \| Risk Contribution \|
\|---\|---:\|---:\|---:\| \| Equity \| 40% \| ... \| ... \| \| FX \| 20%
\| ... \| ... \| \| Gold \| 15% \| ... \| ... \| \| Oil \| 10% \| ... \|
... \| \| Rates \| 15% \| ... \| ... \|

## Interview questions

-   Why does the largest position not always have the largest risk
    contribution?
-   How does correlation affect contribution?
-   Can a negative-weight position reduce total risk?
-   Why should contribution methods sum to the total under the chosen
    formulation?
