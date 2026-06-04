import streamlit as st
import pandas as pd

from containers import CONTAINERS

st.set_page_config(
    page_title="Container Fit Analyzer",
    layout="wide"
)

st.title("🚢 Container Fit Analyzer")

st.markdown("""
### How it works

1. Download the template
2. Fill in your cargo information
3. Upload the completed file
4. Analyze container fit
""")

# ==========================
# TEMPLATE DOWNLOAD
# ==========================

template_df = pd.DataFrame({
    "Length": [48],
    "Width": [40],
    "Height": [83],
    "Weight": [370],
    "DoubleStack": ["No"]
})

template_csv = template_df.to_csv(index=False)

st.download_button(
    label="📥 Download Template",
    data=template_csv,
    file_name="container_template.csv",
    mime="text/csv"
)

st.divider()

# ==========================
# FILE UPLOAD
# ==========================

uploaded_file = st.file_uploader(
    "Upload Completed Template",
    type=["csv", "xlsx"]
)

if uploaded_file:

    try:

        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

    except Exception as e:

        st.error(f"Error reading file: {e}")
        st.stop()

    required_columns = [
        "Length",
        "Width",
        "Height",
        "Weight",
        "DoubleStack"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            "Invalid file format. Please use the official template."
        )

        st.stop()

    # Convert numeric fields
    numeric_columns = [
        "Length",
        "Width",
        "Height",
        "Weight"
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=numeric_columns
    )

    st.subheader("Uploaded Cargo")

    st.dataframe(
        df,
        use_container_width=True
    )

    total_weight = df["Weight"].sum()

    total_pallets = len(df)

    total_volume_in3 = (
        df["Length"] *
        df["Width"] *
        df["Height"]
    ).sum()

    total_volume_ft3 = (
        total_volume_in3 / 1728
    )

    st.subheader("Cargo Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Pallets",
        total_pallets
    )

    col2.metric(
        "Total Weight (kg)",
        f"{total_weight:,.0f}"
    )

    col3.metric(
        "Volume (ft³)",
        f"{total_volume_ft3:,.1f}"
    )

    results = []

    for container_name, container in CONTAINERS.items():

        pallets_per_row = int(
            container["width"] // 40
        )

        rows = int(
            container["length"] // 48
        )

        max_pallets = (
            pallets_per_row * rows
        )

        weight_ok = (
            total_weight <=
            container["payload"]
        )

        pallet_ok = (
            total_pallets <=
            max_pallets
        )

        fit = (
            weight_ok and
            pallet_ok
        )

        utilization = (
            total_pallets /
            max_pallets
        ) * 100

        results.append({
            "Container": container_name,
            "Max Pallets": max_pallets,
            "Payload Limit (kg)": container["payload"],
            "Weight OK": "YES" if weight_ok else "NO",
            "Fits": "YES" if fit else "NO",
            "Utilization %": round(utilization, 1)
        })

    st.subheader("Container Analysis")

    results_df = pd.DataFrame(results)

    st.dataframe(
        results_df,
        use_container_width=True
    )

    fit_options = results_df[
        results_df["Fits"] == "YES"
    ]

    if len(fit_options) > 0:

        recommended = fit_options.iloc[0]

        st.success(
            f"Recommended Container: "
            f"{recommended['Container']}"
        )

    else:

        st.error(
            "Cargo does not fit in any available container."
        )
