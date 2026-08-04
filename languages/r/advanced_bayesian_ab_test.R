# R — Advanced Example: Exact Beta-Binomial Decision Engine
#
# What: Computes exact conjugate posteriors for two conversion rates and uses
# deterministic posterior Monte Carlo only for derived lift and loss quantities.
# Where: Product experiments, clinical decision support, and risk-aware rollout gates.
# When: Decisions need probabilities, practical-equivalence bounds, and expected loss.
# Why: R provides transparent statistical primitives and vectorized posterior analysis.
# How: Validated Beta-Binomial updates, seeded independent draws, HDIs, ROPE,
# minimum-effect probability, expected loss, and explicit decision thresholds.
# Claim boundary: This is not MCMC and does not report an invalid point-null Bayes factor.

validate_arm <- function(successes, trials, label) {
  if (length(successes) != 1 || length(trials) != 1 ||
      !is.finite(successes) || !is.finite(trials) ||
      successes < 0 || trials <= 0 || successes > trials ||
      successes != floor(successes) || trials != floor(trials)) {
    stop(sprintf("%s counts must be finite integers with 0 <= successes <= trials", label))
  }
}

posterior <- function(successes, trials, alpha = 1, beta = 1) {
  if (!is.finite(alpha) || !is.finite(beta) || alpha <= 0 || beta <= 0) {
    stop("Beta prior parameters must be positive")
  }
  list(alpha = alpha + successes, beta = beta + trials - successes)
}

hdi <- function(draws, mass = 0.95) {
  if (length(draws) < 2 || mass <= 0 || mass >= 1) stop("invalid HDI request")
  ordered <- sort(draws)
  width <- floor(mass * length(ordered))
  starts <- seq_len(length(ordered) - width)
  spans <- ordered[starts + width] - ordered[starts]
  index <- starts[which.min(spans)]
  c(lower = ordered[index], upper = ordered[index + width])
}

analyze_experiment <- function(
    control_successes, control_trials,
    treatment_successes, treatment_trials,
    prior_alpha = 1, prior_beta = 1,
    draws = 100000, seed = 42,
    rope = 0.005, minimum_effect = 0.005,
    ship_probability = 0.95, max_expected_loss = 0.001) {
  validate_arm(control_successes, control_trials, "control")
  validate_arm(treatment_successes, treatment_trials, "treatment")
  if (draws < 1000 || rope < 0 || minimum_effect < 0) stop("invalid decision bounds")

  control <- posterior(control_successes, control_trials, prior_alpha, prior_beta)
  treatment <- posterior(treatment_successes, treatment_trials, prior_alpha, prior_beta)
  set.seed(seed)
  control_draws <- rbeta(draws, control$alpha, control$beta)
  treatment_draws <- rbeta(draws, treatment$alpha, treatment$beta)
  lift <- treatment_draws - control_draws
  relative_lift <- lift / pmax(control_draws, .Machine$double.eps)

  probability_better <- mean(lift > 0)
  probability_meaningful <- mean(lift > minimum_effect)
  probability_rope <- mean(abs(lift) <= rope)
  expected_loss_treatment <- mean(pmax(-lift, 0))
  expected_loss_control <- mean(pmax(lift, 0))
  decision <- if (probability_meaningful >= ship_probability &&
                  expected_loss_treatment <= max_expected_loss) {
    "SHIP_TREATMENT"
  } else if (probability_rope >= ship_probability) {
    "PRACTICALLY_EQUIVALENT"
  } else {
    "CONTINUE_TESTING"
  }

  list(
    control_mean = control$alpha / (control$alpha + control$beta),
    treatment_mean = treatment$alpha / (treatment$alpha + treatment$beta),
    absolute_lift_mean = mean(lift),
    absolute_lift_hdi_95 = hdi(lift),
    relative_lift_hdi_95 = hdi(relative_lift),
    probability_treatment_better = probability_better,
    probability_meaningful = probability_meaningful,
    probability_in_rope = probability_rope,
    expected_loss_treatment = expected_loss_treatment,
    expected_loss_control = expected_loss_control,
    decision = decision
  )
}

main <- function() {
  result <- analyze_experiment(1200, 10000, 1350, 10000)
  repeated <- analyze_experiment(1200, 10000, 1350, 10000)
  stopifnot(identical(result, repeated))
  stopifnot(result$probability_treatment_better > 0.99)
  stopifnot(result$absolute_lift_hdi_95[1] < result$absolute_lift_hdi_95[2])
  invalid_rejected <- tryCatch({ analyze_experiment(2, 1, 1, 2); FALSE }, error = function(e) TRUE)
  stopifnot(invalid_rejected)
  cat(sprintf(
    '{"status":"VERIFIED","method":"exact-beta-posterior-plus-monte-carlo-derived-lift","control_mean":%.6f,"treatment_mean":%.6f,"probability_better":%.6f,"expected_loss_treatment":%.8f,"decision":"%s"}\n',
    result$control_mean, result$treatment_mean,
    result$probability_treatment_better, result$expected_loss_treatment,
    result$decision
  ))
}

main()
