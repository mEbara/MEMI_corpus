# MEMI_corpus

This repository provides a corpus designed to evaluate the **ethical decision-making of large language models (LLMs)** in clinical contexts.


## 🚀 Features 
- Evaluate the ethical reasoning of **LLMs and human respondents** in simulated clinical scenarios  
- The default configuration allows the execution of **human responses, GPT models via API, and LLaMA-based models**  
- Estimate **latent ethicality scores** using **Item Response Theory (IRT)**–based scoring

## 📂 Directory structure
```
┗ data/              # Core dataset of the corpus
  ┣ annotation/        # ethical lapse annotation labels for each option
  ┣ scenario/          # Clinical scenarios (in both Japanese and English)
  ┗ tree/              # Graph structures defining scenario flows
┗ config.json        # Configuration file managing model settings
┗ play.py            # Main script to execute scenario simulations
┗ models/            # Model loading and generation modules
┗ util.py            # Text preprocessing utilities and helper functions
```

---

## ⚙️ Installation

Clone this repository and install the required dependencies:

```
git clone https://github.com/mEbara/MEMI_corpus.git
cd corpus
pip install -r requirements.txt
```
