import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"  # Update with your backend URL

st.title("🚩 Red Flag Tender System")

if st.button("🚀 Import Tenders"):
    resp = requests.post(f"{API_URL}/import-file")
    st.success(resp.json().get("message", "Done!"))
if st.button("📊 Refresh Data"):
    tenders = requests.get(f"{API_URL}/notices").json()
    print(tenders)
    if tenders:
        df = pd.DataFrame(tenders)

        # Safely drop columns only if they exist in the dataframe
        to_drop = ["raw_json", "red_flags"]
        existing_to_drop = [c for c in to_drop if c in df.columns]

        st.subheader("Tenders Overview")
        st.dataframe(df.drop(columns=existing_to_drop))

        st.divider()
        # Create a dictionary for easy lookup
        tender_map = {str(t["id"]): t for t in tenders}
        selected_id = st.selectbox("Select Tender ID to inspect flags:", list(tender_map.keys()))

        selected_data = tender_map[selected_id]
        flags = selected_data.get("red_flags", [])

        if flags:
            st.warning(f"🚨 Found {len(flags)} Red Flags")
            st.table(flags)  # Prettier than raw JSON
        else:
            st.success("✅ No red flags detected.")
    else:
        st.info("Database is empty.")
