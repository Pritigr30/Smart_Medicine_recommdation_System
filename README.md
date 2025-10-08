# Smart_Medicine_recommdation_System
Smart AI-Powered Disease-to-Medicine Recommendation System A web application that recommends the best medicine for a given disease. It uses a local dataset, fuzzy search, and an external API (OpenFDA) as fallback for diseases not in the dataset. It also ranks medicines based on type, manufacturer, and category.

## Features
- Search medicines for a disease using a local dataset
- Intelligent ranking based on prescription, manufacturer, and category
- Fuzzy search to handle typos and partial names
- Fallback to OpenFDA API if the disease is not in the dataset
- Best medicine highlighted with alternatives listed
- Built with Python & Streamlit

## Tech Stack
- Python 3.x
- Streamlit (Web App)
- Pandas (Data Handling)
- RapidFuzz (Fuzzy Matching)
- Requests (API Calls)
- OpenFDA API

## Run Locally
```bash
git clone <repo_url>
cd <project_folder>
python -m venv venv
# Activate venv (Windows)
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
