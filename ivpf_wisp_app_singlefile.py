
import streamlit as st
import pandas as pd
import numpy as np

# IVPFN class
class IVPFN:
    def __init__(self, mu_low, mu_high, nu_low, nu_high):
        self.mu = [mu_low, mu_high]
        self.nu = [nu_low, nu_high]

    def score(self):
        mu_sq = (self.mu[0]**2 + self.mu[1]**2) / 2
        nu_sq = (self.nu[0]**2 + self.nu[1]**2) / 2
        return 0.5 * ((mu_sq - nu_sq) + 1)

# App layout
st.title("🚦 IVPF-WISP Ranking App")
st.subheader("Rank University Commuting Alternatives Using Fuzzy Logic")

uploaded_file = st.file_uploader("📤 Upload the Excel file (must include both 'IVPF karar matrisi' and 'Weights')", type="xlsx")

if uploaded_file:
    try:
        ivpf_df = pd.read_excel(uploaded_file, sheet_name="IVPF karar matrisi", index_col=0)
        weights_df = pd.read_excel(uploaded_file, sheet_name="Weights", index_col=0)

        ivpf_df = ivpf_df.dropna(axis=1, how='all')
        weights_df = weights_df.dropna()
        ivpf_df = ivpf_df.reset_index(drop=True)
        weights_df = weights_df.reset_index()

        num_alts = 6
        num_criteria = 14
        matrix = []

        for i in range(num_alts):
            row = []
            for j in range(num_criteria):
                base = j * 4
                mu_high = ivpf_df.iloc[i, base]
                mu_low = ivpf_df.iloc[i, base+1]
                nu_low = ivpf_df.iloc[i, base+2]
                nu_high = ivpf_df.iloc[i, base+3]
                row.append(IVPFN(mu_low, mu_high, nu_low, nu_high))
            matrix.append(row)

        weights = []
        for i in range(num_criteria):
            mu_high = weights_df.iloc[i, 1]
            mu_low = weights_df.iloc[i, 2]
            nu_low = weights_df.iloc[i, 3]
            nu_high = weights_df.iloc[i, 4]
            weight_score = IVPFN(mu_low, mu_high, nu_low, nu_high).score()
            weights.append(weight_score)
        weights = np.array(weights)
        weights = weights / weights.sum()

        def wisp_scores(matrix, weights):
            scores = []
            for alt in matrix:
                s = sum(weights[i] * alt[i].score() for i in range(len(weights)))
                p = np.prod([alt[i].score() ** weights[i] for i in range(len(weights))])
                final_score = 0.5 * (s + p)
                scores.append(final_score)
            return scores

        alternatives = ["Public Transport", "Walking", "Private Car", "Ride-Sharing", "University Shuttle", "Bicycle/E-scooter"]
        scores = wisp_scores(matrix, weights)
        result_df = pd.DataFrame({"Alternative": alternatives, "Score": scores})
        result_df = result_df.sort_values(by="Score", ascending=False).reset_index(drop=True)

        st.success("🎉 Ranking completed! Here's the final result:")
        st.dataframe(result_df)

        top_choice = result_df.iloc[0]["Alternative"]
        if "Bus" in top_choice or "Public" in top_choice:
            msg = "🚌 Bus on top — smooth and cheap, a chill ride while prices sleep!"
        elif "Walk" in top_choice:
            msg = "🚶 Walkin’ wins — no fare to pay, but better leave by light of day!"
        elif "Car" in top_choice:
            msg = "🚗 Car takes gold, but let’s be real — that fuel receipt? A painful deal!"
        elif "Ride" in top_choice:
            msg = "🚙 Sharing is caring — and apparently winning too!"
        elif "Shuttle" in top_choice:
            msg = "🚍 The shuttle wins — comfy, free, and always near!"
        elif "Bicycle" in top_choice or "scooter" in top_choice:
            msg = "🚲 Biking’s boss — you’re lean, you’re fast, just hope that morning coffee lasts!"
        else:
            msg = "🌟 Interesting result! Looks like there's a new favorite."

        st.markdown(f"### 🥇 {msg}")

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
