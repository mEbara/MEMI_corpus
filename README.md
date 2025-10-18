# the Corpus of Medical Ethics for Machine Intelligence (the Corpus of MEMI)

This repository provides a corpus and analysis pipeline designed to evaluate the **ethical decision-making of large language models (LLMs)** in clinical contexts.  
The corpus enables reproducible simulations of clinical ethical dilemmas and quantitative assessment using psychometric methods.

---

## 🚀 Features

- Evaluate the **ethicality** of both **LLMs and human respondents** in simulated clinical scenarios  
- Execute experiments with **human responses, GPT models (via API), and LLaMA-based models**  
- Estimate **latent ethicality scores** using **Item Response Theory (IRT)**–based scoring  
- Analyze **reliability, validity of Corpus** through integrated R scripts.

---

## 📂 Directory Structure
```
┗ exe                   # Scenario execution
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


## ⚙️ Installation


💡 Note:  
All steps up to the **Scoring** stage can be easily demonstrated on [🔗Google Colaboratory](https://colab.research.google.com/drive/1SgInxctJICtfod3RY7lUwwvCNVWKM8mR?usp=sharing). 
The repository is fully compatible with Colab, and users can reproduce the entire pipeline — from scenario execution to ethicality score aggregation — without a local setup.


Clone this repository and install the required dependencies:

```
git clone https://github.com/mEbara/MEMI_corpus.git
pip install -r requirements.txt
```

## ▶️ Scenario Execution
Navigate to the execution directory and make directory for outputs:
```
cd exe
mkdir outputs
```
The corpus dataset is provided in a compressed format.  
Please unzip it before executing any scripts:
```
unzip data.zip
```

List all available clinical scenarios:
```
python play.py --play_mode Listup
```

Run a specific scenario manually (e.g., Q1):
```
python play.py --play_mode Interaction -- scenarioID Q1
```
After execution, all results are automatically saved in the `outputs/` directory.


## 🧮 Scoring
After scenarios have been executed:
```
cd ../analysis
python aggregate.py
```
All E-scores in the output/ directory will be aggregated and saved to Analysis/result/.


## 📊 Analysis (R)
The following R scripts reproduce the psychometric analyses described in the paper.

1️⃣ Reliability & Model Fit Assessment
```
source("corpus_assess.r")

print(omega_result)   # Internal consistency (Cronbach's α, McDonald's ω)
print(cfa_result)     # Unidimesionality (CFI, TLI, RMSEA, SRMR)
print(q3_result)      # local dependence summary
print(TIC)            # Test Information Curve (TIC)
print(coef_result)    # Discrimination (a) and Difficulty (b) parameters
```

2️⃣ θ Estimation and Group Comparison
```
source("estimate_theta.r") # The KDE plot of θ distributions is automatically saved as PDF.

print(result)              # Mean and SD of θ for each group
```


# 📜 License

This work is licensed under a **Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.  
You are free to share and adapt the material under the following terms:

- **Attribution (BY):** You must give appropriate credit.  
- **NonCommercial (NC):** You may not use the material for commercial purposes.  
- **ShareAlike (SA):** If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

For more details, see the full license text:  
🔗 [https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/)
