# Interview notes -- honest positioning

Keep this alongside the pack's own `11_INTERVIEW_PREPARATION.md`. A few
project-specific notes worth adding once you've actually run this code:

## The EWMA-model finding is a feature, not a bug to hide
In the reference synthetic run, the EWMA VaR model's exceptions clustered
enough that the Christoffersen independence test rejected at 5%
(overall_pass=False), while Historical and Parametric VaR passed both
tests. That is exactly the kind of "a model can have the right exception
count but still fail if exceptions cluster in volatile periods" scenario
the pack's backtesting guide describes. Good answer if asked "tell me
about a model that didn't validate": explain what failed, how you
detected it (Christoffersen test), and what you'd try next (shorter EWMA
half-life, conditional-vol regime check, GARCH comparison) -- without
overclaiming you fixed it if you haven't yet.

## Be upfront about scope vs the actual JD
This is a market-risk project. UBS QRM-Mumbai's posting is about credit
exposure measures for the banking/trading book. If asked, say so plainly:
this project demonstrates the shared skill set (statistical modelling,
validation, Python, SQL, clear reporting) rather than claiming to be a
credit-risk/PFE project.

## Reverse stress -- the one-sentence version
"Normal stress testing asks 'what happens if X falls 20%?'. Reverse stress
starts from an unacceptable loss and solves backward for the smallest
combination of market shocks that could cause it -- here, minimum L2-norm
shock vector subject to bound constraints, solved with SLSQP and
independently re-verified."

## Numbers change on re-run
Every number quoted here comes from one synthetic run (see
`results/reports/model_validation_report.md` for the exact run's
metadata: git commit, execution timestamp, data period). Re-running with
a different seed, date range, or real data will change specific figures
-- don't memorize numbers, memorize the methodology.
