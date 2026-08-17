---
generator: pandoc
title: "-"
viewport: width=device-width, initial-scale=1.0, user-scalable=yes
---

# VaR and Expected Shortfall Study Guide

## 1. Value at Risk

VaR at confidence alpha is a loss threshold such that losses exceed it
only with approximately 1-alpha probability under the model.

For returns R: VaR_alpha = -Q\_(1-alpha)(R)

when reporting VaR as a positive loss.

## 2. Historical VaR

Steps: 1. create historical portfolio returns; 2. choose rolling window;
3. calculate lower-tail empirical quantile; 4. convert to positive loss;
5. forecast next-day VaR; 6. compare with realized next-day loss.

## 3. Parametric VaR

For approximately normal returns: VaR_alpha = -(mu + z\_(1-alpha) sigma)

where z\_(1-alpha) is a negative lower-tail quantile.

Be extremely careful with signs.

## 4. EWMA VaR

First estimate time-varying volatility: sigma_t\^2 =
lambda*sigma\_(t-1)\^2 + (1-lambda)*r\_(t-1)\^2

Then use the estimated sigma in a parametric VaR calculation.

## 5. Expected Shortfall

Historical ES: ES_alpha = -mean(R \| R \<= q\_(1-alpha))

It summarizes average tail loss beyond the VaR threshold.

## 6. VaR vs ES

VaR: - threshold; - does not describe tail severity beyond threshold.

ES: - average tail loss; - more informative about tail severity.

## 7. Common mistakes

Do not: - use full-sample statistics to forecast past dates; - mix
return and loss sign conventions; - compare VaR numbers from different
horizons without adjustment; - claim a model is accurate from one
backtest; - use future volatility in a historical forecast.

## 8. Model comparison

Compare models using: - exception rate; - Kupiec test; - Christoffersen
test; - exceedance size; - stability; - stress behaviour; -
interpretability.

Do not choose solely on the lowest VaR.

## 9. Interview questions

Q: Why use more than one VaR model? A: Different models make different
assumptions. Comparing them helps evaluate robustness and model risk.

Q: Why Expected Shortfall? A: It measures the average loss in the tail
beyond the VaR threshold.

Q: Why historical VaR? A: It uses the empirical distribution and makes
fewer distributional assumptions.

Q: Why parametric VaR? A: It is transparent and computationally
efficient but depends more strongly on distributional assumptions.

Q: Why EWMA? A: It lets recent observations influence volatility more
strongly, helping capture changing volatility regimes.
