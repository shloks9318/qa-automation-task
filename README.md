# QA Automation Assignment - ElPais Article Scraper

---

## 1️⃣ Project Overview
This project automates the scraping of the **Opinion section** of [ElPais](https://elpais.com/opinion/).  
It extracts article titles, authors, dates, previews, and images, translates titles to English, and performs basic word frequency analysis.  

The solution is fully tested across multiple browsers and devices using **BrowserStack** with parallel execution.

---

## 2️⃣ Tools Used
- Python  
- Selenium  
- BrowserStack  
- Deep Translator  

---

## 3️⃣ Features
- Scrapes 5 opinion articles  
- Translates titles to English  
- Downloads article images locally  
- Performs word frequency analysis on translated titles  
- Executes in parallel across 5 browser/device combinations  

---

## 4️⃣ How to Run Locally

Open terminal in the project folder and run:

```bash
pip install -r requirements.txt
python el_pais.py
```

## 5️⃣ How to Run on BrowserStack
```bash
browserstack-sdk python el_pais.py
```
