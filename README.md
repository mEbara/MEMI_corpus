# Corpus of Medical Ethics for LLMs (MEMI Corpus)

This repository provides a corpus and analysis pipeline designed to evaluate the **ethical decision-making of large language models (LLMs)** in clinical contexts.  
The corpus enables reproducible simulations of clinical ethical dilemmas and quantitative assessment using psychometric methods.

---

## 🚀 Features

- Evaluate the **ethical reasoning** of both **LLMs and human respondents** in simulated clinical scenarios  
- Execute experiments with **human responses, GPT models (via API), and LLaMA-based models**  
- Estimate **latent ethicality scores** using **Item Response Theory (IRT)**–based scoring  
- Analyze **reliability, validity, and local independence** through integrated R scripts (e.g., CFA, ω, Q3)  

---

## 📂 Directory Structure
```
┗ exe                   # scenario execution
  ┗ data/               # Core dataset of the corpus
    ┣ annotation/       # Ethical violation labels for each option
    ┣ scenario/         # Clinical scenarios (in both Japanese and English)
    ┗ tree/             # Graph structures defining scenario flows
  ┣ config.json         # Configuration file managing model settings
  ┣ play.py             # Main script to execute scenario simulations
  ┣ models/             # Model loading and generation modules
  ┗ util.py             # Utilities and helper functions  

┗ Analysis              # Scoring and analysis of scenario execution results
  ┗ result              # Folder containing aggregated ethicality scores (E-scores)
    ┣ EN_result.csv     # English version results (excluding physician data)
    ┗ JP_result.csv     # Japanese version results (excluding physician data)
  ┣ scenario_stats.json # Maximum violation counts for all scenarios
  ┣ aggregate.py        # Aggregates ethicality scores from all executions
  ┣ corpus_assess.r     # R script for reliability and model fit evaluation
  ┗ estimate_theta.r    # R script for θ estimation and visualization

```

---

## ⚙️ Installation

Clone this repository and install the required dependencies:

```
git clone https://github.com/mEbara/MEMI_corpus.git
pip install -r requirements.txt
```

## ▶️ Scenario Execution
Navigate to the execution directory:
```
cd exe
```

```
unzip data.zip
```

List all available scenarios:
```
python play.py --play_mode Listup
```

Run a specific scenario manually (e.g., Q1):
```
python play.py --play_mode Interaction -- scenarioID Q1
```
After execution, the outputs are automatically saved in outputs/ directory.


## 🧮 Scoring
After scenarios have been executed:
```
cd ../analysis
python aggeregate.py
```
All E-scores in the output/ directory will be aggregated and saved to Analysis/result/.


## 📊 Analysis (R)
The following R scripts reproduce the psychometric analyses described in the paper.

1️⃣ Reliability & Model Fit Assessment
```
source("corpus_assess.r")

print(omega_result)   # Cronbach's α, McDonald's ω
print(cfa_result)     # CFA fit indices (CFI, TLI, RMSEA, SRMR)
print(q3_result)      # Q3 local dependence summary
print(TIC)            # Test Information Curve (TIC)
print(coef_result)    # Discrimination (a) and Difficulty (b) parameters
```

2️⃣ θ Estimation and Group Comparison
```
source("estimate_theta.r") # The KDE plot of θ distributions is automatically saved as PDF.

print(result)         # Mean and SD of θ for each group
```