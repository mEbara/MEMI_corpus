# ===============================
# Corpus Ethics Analysis Pipeline
# ===============================
# This script loads item responses, checks reliability, fits CFA and IRT models,
# evaluates local independence and overall/model fit, and aggregates key metrics.
# All comments are short, clear English for public release.

# ---- Install required packages ----
install.packages(c("polycor", "psych", "lavaan", "mirt"))

# ---- Load libraries ----
library(polycor) 
library(psych)
library(lavaan)
library(mirt)


# ---- Load response data (wide format) ----
# Each row: subject / Each column: item responses
data <- read.csv("result/EN_result.csv",
                 row.names = 1,
                 stringsAsFactors = FALSE)

# ---- Polychoric correlation matrix (for reporting/reliability) ----
# Note: lavaan can compute polychorics internally; we keep this for transparency.
hetcor_result <- hetcor(data)
comat <- hetcor_result$correlations

# ---- Internal consistency (alpha, omega) ----
omega_result <- omega(comat, nfactors = 1)


# ---- Unidimensionality Check (One-factor CFA) ----
# Tip: You may perform an Exploratory Factor Analysis (EFA) before the CFA
Scree <- VSS.scree(comat)

# Tip: Passing raw data + ordered=... lets lavaan compute polychorics internally.
item_names <- colnames(data) # Identify ordinal items (2–10 unique numeric categories)
ordinal_items <- item_names[sapply(data[, item_names], function(x) {
  ux <- na.omit(unique(x))       
  is.numeric(x) && length(ux) >= 2 && length(ux) <= 10
})]

model <- '
F1 =~ Q1 + Q2 + Q3 + Q4 + Q5 + Q6 + Q7 + Q8 + Q9 + Q10 + Q11 + Q12 + Q13 + Q14 + Q15 + Q16 + Q17 + Q18 + Q19 + Q20 + Q21 + Q22 + Q23 + Q24 + Q25 + Q26 + Q27 + Q28 + Q29 + Q30 + Q31 + Q32 + Q33 + Q34 + Q35 + Q36 + Q37 + Q38 + Q39 + Q40 + Q41 + Q42 + Q43 + Q44 + Q45 + Q46 + Q47 + Q48 + Q49 + Q50
'
cfa_fit <- cfa(model, data = comat, std.lv = TRUE, estimator="WLSMV", ordered=ordinal_items)
cfa_result <- fitMeasures(cfa_fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))



# ---- IRT: 2PL (binary) and GRM (polytomous) by item ----
response_matrix <- as.matrix(data) # Convert to matrix

# If max == 1 → binary score (2PLM), else → graded response model (GRM)
max_per_item <- apply(response_matrix, 2, max, na.rm=TRUE) # If max == 1, binary
item_types <- ifelse(max_per_item == 1, "2PL", "graded")   # 2PL for binary / GRM for ordinal

# ---- Fit IRT model ----
mod_grm <- mirt(data = response_matrix, model = 1, itemtype = item_types)

# ---- Local independence (Yen’s Q3) ----
q3 <- residuals(mod_grm, type = "Q3", as.matrix = TRUE)
q3_result <- summary(q3[upper.tri(q3)])

# ---- Test information (overall measurement precision) ----
# TIC is plotted; you may save the plot object if needed.
TIC <- plot(mod_grm, type = "info")

# ---- Item parameters (for scenario-specific precision if needed) ----
coef_result <- coef(mod_grm, simplify=TRUE, IRTpars = TRUE)

# ---- Model fit (overall + item-level) ----
m2_fit <- M2(mod_grm, type="C2") # Overall fit (M2 family)
item_fit <- itemfit(mod_grm, na.rm=TRUE) # Item-level fit
model_fit <- item_fit %>%        # aggregate numeric columns by mean (handles NA)
  summarise(across(where(is.numeric), ~ mean(.x, na.rm = TRUE)))


# ---- (Optional) Print key summaries ----
print(cfa_result)      # CFA fit indices
print(q3_result)      # Q3 summary statistics
print(m2_fit)          # M2-based overall fit
print(model_fit)       # Mean of item-level fit indices