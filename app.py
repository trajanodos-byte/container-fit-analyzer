import streamlit as st
import pandas as pd

from containers import CONTAINERS

st.set_page_config(
    page_title="Container Fit Analyzer",
    layout="wide"
)

st.title("🚢 Container Fit Analyzer")

st.info("""
Accepted formats:

• CSV (.csv)
• Excel (.xlsx)

Required information:

• Length
• Width
• Height
• Weight
""")

uploaded_file = st.file_uploader(
    "Upload Cargo File",
    type=["xlsx", "csv"]
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

    # Normalize column names
    df.columns = [str(col).strip() for col in df.columns]

    column_mapping = {
        "length": "Length",
        "length (in)": "Length",
        "len": "Length",
        "l": "Length",

        "width": "Width",
        "width (in)": "Width",
        "w": "Width",

        "height": "Height",
        "height (in)": "Height",
        "h": "Height",

        "weight": "Weight",
        "weight (kg)": "Weight",
        "kg": "Weight",
        "kgs": "Weight",
        "gross weight": "Weight"
    }

    normalized_columns = {}

    for col in df.columns:
        key = col.lower().strip()

        if key in column_mapping:
            normalized_columns[col] = column_mapping[key]

    df = df.rename(columns=normalized_columns)

    required_columns = [
        "Length",
        "Width",
        "Height",
        "Weight"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

        st.stop()

    # Convert numeric columns
    for col in required_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=required_columns
    )

    st.subheader("Uploaded Data")

    st.dataframe(
        df,
        use_container_width=True
    )

    total_weight = df["Weight"].sum()

    total_pallets = len(df)

    st.subheader("Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Pallets",
            total_pallets
        )

    with col2:
        st.metric(
            "Total Weight (kg)",
            f"{total_weight:,.2f}"
        )

    results = []

    for name, c in CONTAINERS.items():

        pallets_per_row = int(
            c["width"] // 40
        )

        rows = int(
            c["length"] // 48
        )

        max_pallets = (
            pallets_per_row *
            rows
        )

        weight_ok = (
            total_weight <=
            c["payload"]
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
            "Container": name,
            "Max Pallets": max_pallets,
            "Payload Limit (kg)": c["payload"],
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
            f"Recommended Container: {recommended['Container']}"
        )

    else:

        st.error(
            "Cargo does not fit in any available container."
        )
