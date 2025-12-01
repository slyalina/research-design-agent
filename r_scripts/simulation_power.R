#' Simulation-Based Power Analysis Script
#' 
#' This script performs simulation-based power analysis for complex study designs.
#' It supports mixed effects models, non-normal distributions, and custom designs.
#'
#' Usage:
#' Rscript simulation_power.R --design <type> --effect_size <value> --n <value> --n_sims <value> --alpha <value>

library(argparser)

# Create a parser
p <- arg_parser("Perform Simulation-Based Power Analysis")

# Add command line arguments
p <- add_argument(p, "--design", help="Study design type (mixed_effects, clustered, poisson, survival, custom)", default="mixed_effects")
p <- add_argument(p, "--effect_size", help="Effect size", type="numeric", default=0.5)
p <- add_argument(p, "--n", help="Sample size (subjects or clusters)", type="numeric", default=50)
p <- add_argument(p, "--n_sims", help="Number of simulations", type="numeric", default=1000)
p <- add_argument(p, "--alpha", help="Significance level", type="numeric", default=0.05)
p <- add_argument(p, "--n_timepoints", help="Number of timepoints (for repeated measures)", type="numeric", default=3)
p <- add_argument(p, "--cluster_size", help="Cluster size (for clustered designs)", type="numeric", default=20)
p <- add_argument(p, "--icc", help="Intra-cluster correlation", type="numeric", default=0.05)
p <- add_argument(p, "--seed", help="Random seed for reproducibility", type="numeric", default=12345)

# Parse the command line arguments
argv <- parse_args(p)

# Set seed for reproducibility
set.seed(argv$seed)

# Load required packages based on design
if (argv$design %in% c("mixed_effects", "clustered")) {
  suppressPackageStartupMessages(library(lme4))
} else if (argv$design == "survival") {
  suppressPackageStartupMessages(library(survival))
}

# Use parallel processing for faster simulations
library(parallel)
n_cores <- max(1, detectCores() - 1)

cat(sprintf("Running %d simulations using %d cores...\n", argv$n_sims, n_cores))

# Simulation function for mixed effects (repeated measures)
simulate_mixed_effects <- function(n, effect_size, n_timepoints, alpha) {
  # Generate data
  subject_id <- rep(1:n, each = n_timepoints)
  time <- rep(0:(n_timepoints-1), n)
  treatment <- rep(rbinom(n, 1, 0.5), each = n_timepoints)
  
  # Random intercept for each subject
  subject_effect <- rep(rnorm(n, 0, 1), each = n_timepoints)
  
  # Generate outcome with treatment effect
  y <- subject_effect + effect_size * treatment * time + rnorm(n * n_timepoints, 0, 1)
  
  # Fit mixed effects model
  data <- data.frame(y = y, time = time, treatment = treatment, subject_id = factor(subject_id))
  
  tryCatch({
    model <- lmer(y ~ time * treatment + (1 | subject_id), data = data)
    p_value <- summary(model)$coefficients["time:treatment", "Pr(>|t|)"]
    return(p_value < alpha)
  }, error = function(e) {
    return(NA)
  })
}

# Simulation function for clustered data
simulate_clustered <- function(n_clusters, cluster_size, effect_size, icc, alpha) {
  # Generate cluster-level random effects
  cluster_effect <- rnorm(n_clusters, 0, sqrt(icc))
  
  # Generate individual-level data
  treatment <- rep(rbinom(n_clusters, 1, 0.5), each = cluster_size)
  cluster_id <- rep(1:n_clusters, each = cluster_size)
  
  # Outcome with cluster effect and treatment effect
  individual_effect <- rnorm(n_clusters * cluster_size, 0, sqrt(1 - icc))
  y <- rep(cluster_effect, each = cluster_size) + effect_size * treatment + individual_effect
  
  # Fit model accounting for clustering
  data <- data.frame(y = y, treatment = treatment, cluster_id = factor(cluster_id))
  
  tryCatch({
    model <- lmer(y ~ treatment + (1 | cluster_id), data = data)
    p_value <- summary(model)$coefficients["treatment", "Pr(>|t|)"]
    return(p_value < alpha)
  }, error = function(e) {
    return(NA)
  })
}

# Simulation function for Poisson (count data)
simulate_poisson <- function(n, effect_size, alpha) {
  # effect_size is rate ratio here
  treatment <- rbinom(n, 1, 0.5)
  
  # Generate count data
  lambda <- exp(log(5) + log(effect_size) * treatment)  # baseline rate = 5
  y <- rpois(n, lambda)
  
  # Fit Poisson regression
  data <- data.frame(y = y, treatment = treatment)
  
  tryCatch({
    model <- glm(y ~ treatment, data = data, family = poisson())
    p_value <- summary(model)$coefficients["treatment", "Pr(>|z|)"]
    return(p_value < alpha)
  }, error = function(e) {
    return(NA)
  })
}

# Simulation function for survival analysis
simulate_survival <- function(n, effect_size, alpha) {
  # effect_size is hazard ratio here
  treatment <- rbinom(n, 1, 0.5)
  
  # Generate survival times (exponential distribution)
  lambda <- exp(log(0.1) + log(effect_size) * treatment)  # baseline hazard = 0.1
  time <- rexp(n, lambda)
  
  # Add censoring (30% censored)
  censor_time <- rexp(n, 0.05)
  observed_time <- pmin(time, censor_time)
  event <- as.numeric(time <= censor_time)
  
  # Fit Cox proportional hazards model
  data <- data.frame(time = observed_time, event = event, treatment = treatment)
  
  tryCatch({
    model <- coxph(Surv(time, event) ~ treatment, data = data)
    p_value <- summary(model)$coefficients["treatment", "Pr(>|z|)"]
    return(p_value < alpha)
  }, error = function(e) {
    return(NA)
  })
}

# Run simulations based on design type
cat("Starting simulations...\n")

if (argv$design == "mixed_effects") {
  results <- mclapply(1:argv$n_sims, function(i) {
    if (i %% 100 == 0) cat(sprintf("  Simulation %d/%d\n", i, argv$n_sims))
    simulate_mixed_effects(argv$n, argv$effect_size, argv$n_timepoints, argv$alpha)
  }, mc.cores = n_cores)
  
} else if (argv$design == "clustered") {
  results <- mclapply(1:argv$n_sims, function(i) {
    if (i %% 100 == 0) cat(sprintf("  Simulation %d/%d\n", i, argv$n_sims))
    simulate_clustered(argv$n, argv$cluster_size, argv$effect_size, argv$icc, argv$alpha)
  }, mc.cores = n_cores)
  
} else if (argv$design == "poisson") {
  results <- mclapply(1:argv$n_sims, function(i) {
    if (i %% 100 == 0) cat(sprintf("  Simulation %d/%d\n", i, argv$n_sims))
    simulate_poisson(argv$n, argv$effect_size, argv$alpha)
  }, mc.cores = n_cores)
  
} else if (argv$design == "survival") {
  results <- mclapply(1:argv$n_sims, function(i) {
    if (i %% 100 == 0) cat(sprintf("  Simulation %d/%d\n", i, argv$n_sims))
    simulate_survival(argv$n, argv$effect_size, argv$alpha)
  }, mc.cores = n_cores)
  
} else {
  stop(paste("Unknown design type:", argv$design))
}

# Calculate power
results <- unlist(results)
results <- results[!is.na(results)]  # Remove failed simulations
power <- mean(results)

# Output results
cat("\n")
cat("=== Simulation-Based Power Analysis Results ===\n")
cat(sprintf("Design: %s\n", argv$design))
cat(sprintf("Sample size: %d\n", argv$n))
if (argv$design == "mixed_effects") {
  cat(sprintf("Time points: %d\n", argv$n_timepoints))
} else if (argv$design == "clustered") {
  cat(sprintf("Cluster size: %d\n", argv$cluster_size))
  cat(sprintf("ICC: %.3f\n", argv$icc))
}
cat(sprintf("Effect size: %.3f\n", argv$effect_size))
cat(sprintf("Alpha: %.3f\n", argv$alpha))
cat(sprintf("Number of simulations: %d\n", argv$n_sims))
cat(sprintf("Successful simulations: %d\n", length(results)))
cat(sprintf("\nEstimated Power: %.3f (%.1f%%)\n", power, power * 100))
cat("===============================================\n")
