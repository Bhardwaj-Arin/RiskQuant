---
generator: pandoc
title: "-"
viewport: width=device-width, initial-scale=1.0, user-scalable=yes
---

# UBS QRM Interview Preparation

## 30-second project explanation

> RiskForge-QRM is a quantitative market-risk modelling and validation
> framework. I built a hypothetical multi-factor portfolio and
> implemented historical, parametric and EWMA-based VaR models, Expected
> Shortfall, statistical backtesting, stress testing, reverse stress
> testing and risk attribution. The main objective was not just to
> calculate risk, but to validate whether the models behaved reliably
> out of sample and understand when and why they failed.

## 60-second explanation

Explain: 1. problem; 2. data; 3. portfolio; 4. three models; 5.
validation; 6. stress/reverse stress; 7. key learning.

## Questions you must master

### What is VaR?

A quantile-based loss threshold at a chosen confidence level.

### What is Expected Shortfall?

The average loss conditional on being beyond the VaR threshold.

### Why compare models?

Different assumptions produce different risk estimates. Comparison
reveals robustness and model risk.

### Why historical simulation?

It avoids imposing a parametric distribution and uses empirical
outcomes.

### Why parametric VaR?

It is transparent and computationally efficient.

### Why EWMA?

Volatility is time-varying, so recent observations can be weighted more
heavily.

### Why backtest?

A risk model should be compared with realized outcomes.

### What is a VaR exception?

A realized loss larger than the model's VaR threshold.

### Why can exception clustering matter?

It may indicate that the model fails to capture changing
volatility/regime dependence.

### What is stress testing?

Evaluating losses under adverse predefined scenarios.

### What is reverse stress testing?

Starting with a target adverse outcome and finding plausible shocks that
could cause it.

### Why is reverse stress useful?

It reveals vulnerabilities and combinations of shocks that may not be
obvious from one-factor stress tests.

### What is look-ahead bias?

Using information that would not have been available at the forecast
time.

### Why is it dangerous?

It makes out-of-sample performance unrealistically good.

### Why might normal VaR fail?

Financial returns can have heavy tails, skewness and time-varying
volatility.

### What is model risk?

The risk that a model is wrong, poorly specified, poorly implemented or
misused.

### Why not just use the model with the lowest VaR?

Lower VaR does not mean lower true risk. The model must be evaluated for
coverage, independence, tail behaviour and plausibility.

## Deeper questions

Prepare for: - Why 250-day rolling window? - Why 95%, 99% or 97.5%? -
How does correlation affect portfolio risk? - What happens when
correlations increase during crises? - Why can historical VaR
underestimate unseen events? - How would you extend the model to
nonlinear options? - How would you handle missing risk factors? - How
would you monitor model drift? - How would you validate a model
independently? - What would you change for production?

## Production-extension answer

If asked how to make it production-ready: - reliable market-data feed; -
automated data-quality checks; - independent validation; - model
versioning; - monitoring; - alerting; - audit logging; - access
control; - high-availability database; - performance optimization; -
regulatory review; - documented governance.

## What not to say

Avoid: - "My model predicts the market." - "99% confidence means the
loss cannot exceed VaR." - "The model is accurate because AUC is
high." - "This is Basel compliant." - "Reverse stress gives the true
worst case." - "Normality is realistic for all financial returns."

## Best interview story

The strongest story is not a perfect model.

It is: \> I built a transparent baseline, tested it, found where
assumptions broke down, compared alternative models, and used
stress/reverse-stress analysis to understand the weaknesses.
