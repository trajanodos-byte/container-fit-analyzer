import streamlit as st
import pandas as pd

from containers import CONTAINERS

st.set_page_config(
    page_title="Container Fit Analyzer",
    layout="wide"
)

st.title("🚢 Container Fit Analyzer")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df)

    total_weight = df["Weight (kg)"].sum()

    total_pallets = len(df)

    st.write(f"Total Pallets: {total_pallets}")
    st.write(f"Total Weight: {total_weight:,.2f} kg")

    results = []

    for name, c in CONTAINERS.items():

        pallets_per_row = int(c["width"] // 40)

        rows = int(c["length"] // 48)

        max_pallets = pallets_per_row * rows

        weight_ok = total_weight <= c["payload"]

        pallet_ok = total_pallets <= max_pallets

        fit = weight_ok and pallet_ok

        utilization = (
            total_pallets /
            max_pallets
        ) * 100

        results.append({
            "Container": name,
            "Max Pallets": max_pallets,
            "Utilization %": round(utilization,1),
            "Fits": "YES" if fit else "NO"
        })

    st.subheader("Results")

    st.dataframe(
        pd.DataFrame(results)
    )
