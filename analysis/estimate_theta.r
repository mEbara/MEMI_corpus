# ===================================
# IRT Scoring and Visualization Script
# ===================================
# This script fits an IRT model (GRM/2PL), estimates ability (θ),
# aggregates mean and SD by group, and visualizes θ distributions.

# ---- Install required packages ----
install.packages(c("mirt", "dplyr", "ggplot2", "ggrepel"))

# ---- Load libraries ----
library(mirt)
library(dplyr)
library(ggplot2)
library(ggrepel)


# ---- Load response data (wide format) ----
# Each row: subject / Each column: item responses
df <- read.csv("analysis/result/EN_result.csv",
               row.names = 1,
               stringsAsFactors = FALSE)

# ---- Prepare response matrix ----
response_matrix <- as.matrix(df) # Convert dataframe to numeric matrix

# Detect item type by number of unique categories per item
max_per_item <- apply(response_matrix, 2, max, na.rm=TRUE) # If max == 1, binary
item_types <- ifelse(max_per_item == 1, "2PL", "graded") # 2PL for binary / GRM for ordinal

# ---- Fit IRT model ----
mod_grm <- mirt(
  data     = response_matrix,  # Numeric response matrix
  model    = 1,                # Unidimensional IRT model
  itemtype = item_types
)

# ---- Estimate ability (θ) for each respondent ----
theta_df <- data.frame(
  SubjectID = rownames(response_matrix),
  Theta     = fscores(mod_grm, method = "EAP")[ , 1] # EAP estimation
  ) 

# ---- Derive group labels from SubjectID ----
# Automatically extracts prefix (e.g., LLAMA, GPT, Human)
theta_df <- theta_df %>% 
  mutate(Group = sub("([A-Za-z0-9]+).*", "\\1", SubjectID))

# ---- Compute summary statistics (mean, SD) by group ----
result <- aggregate(Theta ~ Group, data = theta_df, 
                    FUN = function(x) c(mean=mean(x), sd=sd(x)))

# ---- Plot θ distribution by group ----
theta_plot <- ggplot(theta_df, aes(x = Theta, fill = Group)) +
                     geom_density(alpha = 0.4) +
                     labs(x = expression(theta), y = "Density") +
                     theme_minimal()

ggsave("analysis/theta_plot.pdf", plot = theta_plot, width = 8, height = 8, dpi = 500)