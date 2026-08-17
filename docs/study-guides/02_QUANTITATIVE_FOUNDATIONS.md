---
generator: pandoc
title: "-"
viewport: width=device-width, initial-scale=1.0, user-scalable=yes
---

# Quantitative Foundations Study Guide

## 1. Returns

Simple return: R_t = P_t/P\_(t-1) - 1

Log return: r_t = ln(P_t/P\_(t-1))

Know: - difference between price and return; - why returns are
modelled; - when simple/log returns are convenient.

## 2. Mean

mu = (1/n) sum r_i

Interpretation: average observed return over the sample.

## 3. Variance and volatility

sigma\^2 = Var(R) sigma = sqrt(Var(R))

Know: - variance measures dispersion; - volatility is standard
deviation; - volatility is not the same as risk in every context.

## 4. Covariance

Cov(X,Y) = E\[(X-mu_X)(Y-mu_Y)\]

Positive covariance: assets tend to move together.

Negative covariance: they tend to move in opposite directions.

## 5. Correlation

rho_XY = Cov(X,Y)/(sigma_X sigma_Y)

Correlation is standardized covariance.

## 6. Portfolio variance

For weights w and covariance matrix Sigma: sigma_p\^2 = w' Sigma w

This is one of the most important formulas in the project.

Be able to explain: - diagonal terms = individual variances; -
off-diagonal terms = co-movement; - diversification depends on
correlations.

## 7. Quantiles

The alpha quantile is a threshold below which a chosen proportion of
observations fall.

For a loss convention, VaR is based on a lower-tail quantile of returns.

## 8. Normal distribution

Know: - mean; - variance; - z-score; - tails; - why the normal
assumption can underestimate extreme financial events.

Do not claim financial returns are normally distributed.

## 9. Heavy tails

Financial returns can exhibit: - skewness; - kurtosis; - fat tails; -
volatility clustering.

These motivate comparing historical and time-varying models.

## 10. Rolling windows

A rolling model at time t must use information available up to t only.

Example: 20-day rolling volatility at t uses observations t-19,...,t.

The future observation t+1 must never influence the t forecast.

## 11. Statistical hypothesis testing

Know: - null hypothesis; - alternative hypothesis; - test statistic; -
p-value; - significance level; - Type I error.

For risk models, understand that statistical tests are evidence, not
absolute proof.

## 12. Optimization

Reverse stress testing uses constrained optimization.

Generic form: minimize f(x) subject to g(x) \>= 0 and lower \<= x \<=
upper

Interpretation: find the smallest/plausible shock that produces a target
loss.

## 13. Matrix basics

Know: - vector; - matrix; - transpose; - covariance matrix; - positive
semidefinite idea; - matrix multiplication.

No advanced linear algebra is required beyond what is used in the
project.

## Interview checklist

You must be able to answer: - What is volatility? - Why covariance
matters? - Why portfolio risk is not the weighted average of individual
risks? - What is a quantile? - Why rolling windows? - What is look-ahead
bias? - Why can correlation change portfolio risk? - Why are fat tails
important? - Why does model validation matter?
