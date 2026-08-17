---
generator: pandoc
title: "-"
viewport: width=device-width, initial-scale=1.0, user-scalable=yes
---

# Backtesting and Model Validation

## Why validation is central

A quantitative risk model is useful only if its outputs are credible
under out-of-sample evaluation.

The project must separate: 1. model development; 2. model validation; 3.
reporting.

## Backtesting data structure

For each forecast date: - forecast_date - model_name - VaR -
realized_PnL - realized_loss - exception_flag

Exception: realized_loss \> VaR

under a positive-loss convention.

## Exception rate

exception_rate = exceptions / number_of_forecasts

Compare this with the expected tail probability.

## Kupiec Proportion-of-Failures test

Purpose: test whether the observed exception frequency is consistent
with the expected frequency.

Know conceptually: - null: exception probability equals target; -
alternative: exception probability differs.

Do not memorize code without understanding the likelihood-ratio idea.

## Christoffersen independence test

Purpose: test whether exceptions are independent over time.

Why it matters: a model may have the right overall number of exceptions
but cluster them during volatile periods.

## Combined conditional-coverage idea

A model should have: - appropriate exception frequency; - reasonably
independent exceptions.

## Model risk

A model can fail because: - assumptions are wrong; - data are poor; -
parameters are unstable; - regime changes occur; - implementation
contains errors; - risk factors are incomplete.

## Validation layers

### Conceptual validation

Does the model make sense?

### Data validation

Are the inputs correct and timely?

### Implementation validation

Does code implement the mathematical formula correctly?

### Statistical validation

Do out-of-sample results behave as expected?

### Stress validation

Does the model produce plausible behaviour under severe scenarios?

### Sensitivity analysis

Do results change excessively when reasonable assumptions change?

## Independent implementation checks

For critical calculations: - compare a vectorized implementation with a
small hand-computed example; - compare a formula implementation with a
trusted library only as a secondary check; - use synthetic data where
the expected result is known.

## Basel context

Basel market-risk materials emphasize backtesting and comparison of risk
estimates with actual gains/losses. The project uses this as conceptual
guidance but does not claim regulatory compliance.

## Model validation report

Include: 1. model objective; 2. data; 3. assumptions; 4. implementation;
5. test design; 6. results; 7. failures/exceptions; 8. limitations; 9.
conclusion; 10. recommended next steps.

## Golden rule

Never hide a model failure.

A failed model can be more valuable in an interview if you can
explain: - why it failed; - how you detected it; - what you changed; -
what limitation remains.
