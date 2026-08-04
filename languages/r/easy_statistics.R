# R — Easy Example: Statistical Summary & Visualization Pipeline
# What: Data loading, summary statistics, and ggplot2-style base R plotting.
# Where: Biostatistics, data science, clinical trial analysis, research.
# When: Exploratory data analysis, statistical modeling, academic research.
# Why: R is the gold standard for statistical computing with 20,000+ CRAN packages.
# How: Vectorized operations on data frames with built-in statistical functions.

generate_sample_data <- function(n = 1000) {
  data.frame(
    id = seq_len(n),
    age = round(rnorm(n, mean = 35, sd = 12)),
    income = round(rlnorm(n, meanlog = 10.5, sdlog = 0.8)),
    score = round(rbeta(n, shape1 = 2, shape2 = 5) * 100, 1),
    group = sample(c("A", "B", "C"), n, replace = TRUE,
                   prob = c(0.3, 0.5, 0.2))
  )
}

summarize_data <- function(df) {
  cat("=== Dataset Summary ===\n")
  cat(sprintf("  Rows: %d, Columns: %d\n", nrow(df), ncol(df)))
  cat(sprintf("  Age: mean=%.1f, sd=%.1f, range=[%d, %d]\n",
              mean(df$age), sd(df$age), min(df$age), max(df$age)))
  cat(sprintf("  Income: median=$%s, IQR=$%s\n",
              format(median(df$income), big.mark = ","),
              format(IQR(df$income), big.mark = ",")))
  cat(sprintf("  Score: mean=%.1f, sd=%.1f\n",
              mean(df$score), sd(df$score)))

  # Group-wise summary
  cat("\n=== By Group ===\n")
  agg <- aggregate(cbind(age, income, score) ~ group, data = df, FUN = mean)
  print(agg)

  # Correlation matrix
  cat("\n=== Correlations ===\n")
  nums <- df[, c("age", "income", "score")]
  print(round(cor(nums), 3))
}

main <- function() {
  set.seed(42)
  df <- generate_sample_data(1000)
  summarize_data(df)

  # Shapiro-Wilk normality test on score
  sw <- shapiro.test(head(df$score, 100))
  cat(sprintf("\nShapiro-Wilk on score: W=%.4f, p=%.6f\n", sw$statistic, sw$p.value))

  # T-test: group A vs group B scores
  a_scores <- df$score[df$group == "A"]
  b_scores <- df$score[df$group == "B"]
  tt <- t.test(a_scores, b_scores)
  cat(sprintf("T-test A vs B: t=%.3f, p=%.4f, CI=[%.2f, %.2f]\n",
              tt$statistic, tt$p.value, tt$conf.int[1], tt$conf.int[2]))
}

main()
