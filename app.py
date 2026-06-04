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

# ==================================

# TEMPLATE DOWNLOAD

# ==================================

template_df = pd.DataFrame({
"Qty": [1],
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

# ==================================

# FILE UPLOAD

# ==================================

uploaded_file = st.file_uploader(
"Upload Completed Template",
type=["csv", "xlsx"]
)

if uploaded_file:

```
try:

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"Error reading file: {e}")
    st.stop()

required_columns = [
    "Qty",
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

numeric_columns = [
    "Qty",
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

total_pallets = df["Qty"].sum()

total_weight = (
    df["Qty"] *
    df["Weight"]
).sum()

total_volume_in3 = (
    df["Qty"] *
    df["Length"] *
    df["Width"] *
    df["Height"]
).sum()

total_volume_ft3 = (
    total_volume_in3 / 1728
)

df["FloorArea"] = (
    df["Qty"] *
    df["Length"] *
    df["Width"]
)

total_floor_area = (
    df["FloorArea"]
).sum()

st.subheader("Cargo Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Pallets",
    f"{int(total_pallets)}"
)

col2.metric(
    "Total Weight (kg)",
    f"{total_weight:,.0f}"
)

col3.metric(
    "Volume (ft³)",
    f"{total_volume_ft3:,.1f}"
)

col4.metric(
    "Floor Area (in²)",
    f"{total_floor_area:,.0f}"
)

def check_double_stack(
    row,
    container_height
):

    if (
        str(
            row["DoubleStack"]
        ).lower()
        != "yes"
    ):
        return True

    return (
        row["Height"] * 2
        <= container_height
    )

results = []

for container_name, container in CONTAINERS.items():

    weight_ok = (
        total_weight
        <= container["payload"]
    )

    height_ok = (
        df["Height"].max()
        <= container["height"]
    )

    container_area = (
        container["length"] *
        container["width"]
    )

    floor_ok = (
        total_floor_area
        <= container_area
    )

    stack_ok = all(
        check_double_stack(
            row,
            container["height"]
        )
        for _, row in df.iterrows()
    )

    fit = (
        weight_ok and
        height_ok and
        floor_ok and
        stack_ok
    )

    weight_utilization = (
        total_weight /
        container["payload"]
    ) * 100

    floor_utilization = (
        total_floor_area /
        container_area
    ) * 100

    reasons = []

    if not weight_ok:
        reasons.append(
            "Weight Exceeded"
        )

    if not height_ok:
        reasons.append(
            "Height Exceeded"
        )

    if not floor_ok:
        reasons.append(
            "Floor Space Exceeded"
        )

    if not stack_ok:
        reasons.append(
            "Double Stack Exceeded"
        )

    reason = (
        "OK"
        if len(reasons) == 0
        else ", ".join(reasons)
    )

    results.append({
        "Container": container_name,
        "Payload Limit (kg)": container["payload"],
        "Weight Util %": round(
            weight_utilization,
            1
        ),
        "Floor Util %": round(
            floor_utilization,
            1
        ),
        "Fits": (
            "YES"
            if fit
            else "NO"
        ),
        "Reason": reason
    })

st.subheader(
    "Container Analysis"
)

results_df = pd.DataFrame(
    results
)

st.dataframe(
    results_df,
    use_container_width=True
)

fit_options = results_df[
    results_df["Fits"]
    == "YES"
]

if len(fit_options) > 0:

    priority = {
        "20DC": 1,
        "40DC": 2,
        "40HC": 3
    }

    fit_options = (
        fit_options.copy()
    )

    fit_options["Priority"] = (
        fit_options["Container"]
        .map(priority)
    )

    recommended = (
        fit_options
        .sort_values(
            "Priority"
        )
        .iloc[0]
    )

    st.success(
        f"Recommended Container: "
        f"{recommended['Container']}"
    )

    st.subheader(
        "Executive Summary"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Container",
        recommended[
            "Container"
        ]
    )

    col2.metric(
        "Weight Util %",
        f"{recommended['Weight Util %']}%"
    )

    col3.metric(
        "Floor Util %",
        f"{recommended['Floor Util %']}%"
    )

else:

    st.error(
        "Cargo does not fit in any available container."
    )
```
