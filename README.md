# Graduate Job Match Assistant

A web app that helps graduates from any field and any country check how well their CV matches a job description before applying.

## Problem

Many graduates apply for jobs without knowing if they actually qualify.  
This leads to rejections and wasted time.

## Solution

This app allows users to:
- Upload their CV
- Paste a job description
- Get a match score
- See missing keywords
- Generate a simple cover note

This helps graduates apply smarter and improve their chances.

## Features

- CV upload (PDF, DOCX, TXT)
- Job match score using text analysis
- Missing keyword detection
- Simple cover note generator
- Works for all fields (IT, Business, HR, Engineering, etc.)
- Works globally (any country)

## Tools Used

- Python
- Streamlit
- Scikit-learn (TF-IDF + Cosine Similarity)
- PyPDF2
- python-docx

## How to Run the App

1. Install requirements:
   ```bash
   pip install -r requirements.txt