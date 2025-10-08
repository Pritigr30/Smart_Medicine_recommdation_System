import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import requests

# =============================
# STEP 1: Load dataset
# =============================
@st.cache_data
def load_data():
    data = pd.read_csv("medicine_dataset.csv")
    return data

data = load_data()

# =============================
# STEP 2: Page setup
# =============================
st.set_page_config(page_title="Smart Medicine Recommender", page_icon="💊", layout="centered")
st.title("💊 AI-Powered Medicine Recommendation System")
st.write("Enter a disease or condition to get the best medicine recommendation and alternatives.")

# =============================
# STEP 3: User Input
# =============================
disease = st.text_input("Enter Disease Name (e.g., Pain, Infection, Flu):")

# =============================
# STEP 4: Fallback function (external lookup)
# =============================
def get_external_recommendation(disease_name):
    """
    Use OpenFDA API to fetch common medicines for unknown diseases.
    This version handles missing brand_name properly.
    """
    try:
        # Query OpenFDA for drugs mentioning the disease
        url = f"https://api.fda.gov/drug/label.json?search=indications_and_usage:{disease_name}&limit=5"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                meds = []
                for entry in data["results"]:
                    openfda = entry.get("openfda", {})

                    # Try multiple sources for medicine name
                    med_name = (
                        openfda.get("brand_name", [None])[0]
                        or openfda.get("generic_name", [None])[0]
                        or openfda.get("substance_name", [None])[0]
                        or "Unknown Medicine"
                    )

                    purpose = entry.get("indications_and_usage", ["Information not available"])[0]
                    meds.append((med_name, purpose))
                return meds
    except Exception as e:
        print("External fetch error:", e)
        return None
    return None

# =============================
# STEP 5: Recommendation Logic
# =============================
if disease:
    results = data[data['Indication'].str.contains(disease, case=False, na=False)]

    # If not found, try fuzzy match
    if results.empty:
        indications = data['Indication'].unique()
        match, score, _ = process.extractOne(disease, indications, scorer=fuzz.token_sort_ratio)
        if score > 65:
            st.warning(f"No exact match for '{disease}', showing results for similar condition: **{match}**")
            results = data[data['Indication'].str.contains(match, case=False, na=False)]
        else:
            # External knowledge fallback
            st.info(f"🧠 '{disease}' not found in dataset — fetching verified medical data...")
            meds = get_external_recommendation(disease)
            if meds:
                st.subheader("🌍 External Medicine Recommendations (via OpenFDA)")
                for med_name, purpose in meds:
                    st.markdown(f"**💊 {med_name}**  \n📄 {purpose[:400]}...")
            else:
                st.error("No external data found either. Try a more common disease term.")
            st.stop()

    # If we have dataset results, score them
    def score_medicine(row):
        score = 0
        if "Prescription" in row["Classification"]:
            score += 3
        else:
            score += 1
        top_brands = ["Pfizer", "Roche", "Johnson", "Novartis", "GSK", "AbbVie", "Teva"]
        if any(brand.lower() in row["Manufacturer"].lower() for brand in top_brands):
            score += 2
        if any(cat.lower() in row["Category"].lower() for cat in ["antibiotic", "antiviral", "antifungal", "antidiabetic"]):
            score += 1
        return score

    results["Score"] = results.apply(score_medicine, axis=1)
    results = results.sort_values(by="Score", ascending=False).reset_index(drop=True)

    # Show best recommendation
    best = results.iloc[0]
    st.subheader("🌟 Best Recommended Medicine")
    st.markdown(f"""
    **Name:** {best['Name']}  
    **Category:** {best['Category']}  
    **Dosage Form:** {best['Dosage Form']}  
    **Strength:** {best['Strength']}  
    **Manufacturer:** {best['Manufacturer']}  
    **Classification:** {best['Classification']}
    """)
    st.divider()

    # Show other medicines
    st.subheader("💡 Other Available Medicines")
    st.dataframe(results[['Name', 'Category', 'Dosage Form', 'Strength', 'Manufacturer', 'Classification']].iloc[1:])
else:
    st.info("Please enter a disease name above to get recommendations.")

# =============================
# STEP 6: Footer
# =============================
st.markdown("---")

