#' Power Analysis Script
#' 
#' This script performs power analysis for various statistical tests.
#' It uses the `pwr` package.
#'
#' Usage:
#' Rscript power_analysis.R --test_type <type> --effect_size <value> --alpha <value> --power <value> --n <value> --alternative <type>
#' 
#' Note: One of effect_size, power, n, or alpha must be NULL (or omitted) to be calculated.

library(pwr)
library(argparser)

# Create a parser
p <- arg_parser("Perform Power Analysis")

# Add command line arguments
p <- add_argument(p, "--test_type", help="Type of test (t.test, anova, correlation, chisq, proportion)", default="t.test")
p <- add_argument(p, "--effect_size", help="Effect size (Cohen's d, f, r, w, h)", type="numeric", default=NULL)
p <- add_argument(p, "--n", help="Sample size", type="numeric", default=NULL)
p <- add_argument(p, "--alpha", help="Significance level", type="numeric", default=0.05)
p <- add_argument(p, "--power", help="Power of the test", type="numeric", default=NULL)
p <- add_argument(p, "--alternative", help="Alternative hypothesis (two.sided, less, greater)", default="two.sided")
p <- add_argument(p, "--type", help="Type of t-test (two.sample, one.sample, paired)", default="two.sample")

# Parse the command line arguments
argv <- parse_args(p)

# Function to handle NULLs properly for pwr functions
# pwr functions expect NULL for the value to be calculated
prepare_arg <- function(x) {
  if (is.na(x)) return(NULL)
  return(x)
}

# Perform the power analysis based on test type
result <- NULL

tryCatch({
  if (argv$test_type == "t.test") {
    result <- pwr.t.test(n = prepare_arg(argv$n), 
                         d = prepare_arg(argv$effect_size), 
                         sig.level = prepare_arg(argv$alpha), 
                         power = prepare_arg(argv$power), 
                         type = argv$type,
                         alternative = argv$alternative)
  } else if (argv$test_type == "anova") {
    # For ANOVA, k is number of groups. We might need to add k as an arg if we support it fully.
    # Assuming one-way ANOVA for now.
    # pwr.anova.test(k = NULL, n = NULL, f = NULL, sig.level = 0.05, power = NULL)
    # We need 'k' (number of groups) for ANOVA. Let's assume it's passed via a generic arg or we add it.
    # For simplicity in this template, let's stick to simple tests or add 'k' if needed.
    stop("ANOVA support requires number of groups (k). Not fully implemented in this simple template yet.")
  } else if (argv$test_type == "correlation") {
    result <- pwr.r.test(n = prepare_arg(argv$n), 
                         r = prepare_arg(argv$effect_size), 
                         sig.level = prepare_arg(argv$alpha), 
                         power = prepare_arg(argv$power), 
                         alternative = argv$alternative)
  } else if (argv$test_type == "proportion") {
      result <- pwr.p.test(h = prepare_arg(argv$effect_size),
                           n = prepare_arg(argv$n),
                           sig.level = prepare_arg(argv$alpha),
                           power = prepare_arg(argv$power),
                           alternative = argv$alternative)
  } else {
    stop(paste("Unknown test type:", argv$test_type))
  }

  # Output the result
  if (!is.null(result)) {
    print(result)
  }

}, error = function(e) {
  cat("Error:", e$message, "\n")
  quit(status = 1)
})
