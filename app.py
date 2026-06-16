import streamlit as st
import pandas as pd
import plotly.express as px

from modules.parser import (
    load_csv,
    get_max_dose,
    get_min_dose,
    get_max_let
)
st.set_page_config(
    page_title="CubeSat Radiation Analysis Platform",
    layout="wide"
)

st.title("🛰️ CubeSat Radiation Analysis Platform")
st.write("PHITS-based Radiation Dose and LET Analysis for CubeSat Shielding Study")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Dashboard", "Dose Analysis", "LET Analysis", "Shielding Efficiency", "Report"]
)

st.sidebar.header("Input Parameters")

proton_energy = st.sidebar.selectbox(
    "Proton Energy (MeV)",
    [30, 50, 100]
)

al_thickness = st.sidebar.slider(
    "Selected Aluminum Thickness (mm)",
    0.0, 10.0, 1.0, 0.5
)

uploaded_file = st.file_uploader(
    "Upload PHITS Result CSV",
    type=["csv"]
)


def classify_risk(dose):
    if dose < 2.0e-9:
        return "LOW RISK"
    elif dose <= 4.0e-9:
        return "MEDIUM RISK"
    else:
        return "HIGH RISK"


if uploaded_file is not None:
    df = load_csv(uploaded_file)

    required_columns = ["Thickness_mm", "Dose_Gy", "LET_keV_um"]

    if not all(col in df.columns for col in required_columns):
        st.error("CSV file must contain: Thickness_mm, Dose_Gy, LET_keV_um")
        st.stop()

    df = df.sort_values("Thickness_mm").reset_index(drop=True)

    dose0 = df.loc[df["Thickness_mm"] == 0, "Dose_Gy"]

    if len(dose0) > 0:
        reference_dose = dose0.iloc[0]
    else:
        reference_dose = df["Dose_Gy"].iloc[0]

    df["Shielding_Efficiency_%"] = (
        (reference_dose - df["Dose_Gy"]) / reference_dose
    ) * 100

    df["Risk_Level"] = df["Dose_Gy"].apply(classify_risk)

    max_dose = get_max_dose(df)
    min_dose = get_min_dose(df)
    avg_dose = df["Dose_Gy"].mean()
    max_let = get_max_let(df)

    optimal_row = df.loc[df["Dose_Gy"].idxmin()]
    optimal_thickness = optimal_row["Thickness_mm"]
    optimal_dose = optimal_row["Dose_Gy"]
    optimal_efficiency = optimal_row["Shielding_Efficiency_%"]
    optimal_risk = optimal_row["Risk_Level"]

    selected_row = df.iloc[
        (df["Thickness_mm"] - al_thickness).abs().argsort()[:1]
    ].iloc[0]

    selected_dose = selected_row["Dose_Gy"]
    selected_let = selected_row["LET_keV_um"]
    selected_efficiency = selected_row["Shielding_Efficiency_%"]
    selected_risk = selected_row["Risk_Level"]

    if page == "Dashboard":
        st.subheader("Radiation Summary")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Max Dose", f"{max_dose:.2E} Gy")
        c2.metric("Min Dose", f"{min_dose:.2E} Gy")
        c3.metric("Avg Dose", f"{avg_dose:.2E} Gy")
        c4.metric("Max LET", f"{max_let:.2f} keV/µm")

        st.subheader("Selected Thickness Result")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Selected Thickness", f"{selected_row['Thickness_mm']} mm")
        c6.metric("Selected Dose", f"{selected_dose:.2E} Gy")
        c7.metric("Efficiency", f"{selected_efficiency:.2f} %")
        c8.metric("Risk Level", selected_risk)

        st.subheader("Optimal Shielding Recommendation")
        st.success(
            f"Recommended Aluminum Thickness: {optimal_thickness} mm | "
            f"Minimum Dose: {optimal_dose:.2E} Gy | "
            f"Efficiency: {optimal_efficiency:.2f}% | "
            f"Risk: {optimal_risk}"
        )

        st.subheader("Uploaded Data")
        st.dataframe(df, use_container_width=True)

    elif page == "Dose Analysis":
        st.subheader("Dose vs Aluminum Thickness")

        fig = px.line(
            df,
            x="Thickness_mm",
            y="Dose_Gy",
            markers=True,
            title="Dose vs Aluminum Thickness"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "Dose may initially increase because of secondary particle production, "
            "proton slowing down, and Bragg peak shift."
        )

    elif page == "LET Analysis":
        st.subheader("LET vs Aluminum Thickness")

        fig2 = px.line(
            df,
            x="Thickness_mm",
            y="LET_keV_um",
            markers=True,
            title="LET vs Aluminum Thickness"
        )
        st.plotly_chart(fig2, use_container_width=True)

    elif page == "Shielding Efficiency":
        st.subheader("Shielding Efficiency Analysis")

        fig3 = px.bar(
            df,
            x="Thickness_mm",
            y="Shielding_Efficiency_%",
            title="Shielding Efficiency vs Aluminum Thickness"
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Efficiency Table")
        st.dataframe(
            df[["Thickness_mm", "Dose_Gy", "Shielding_Efficiency_%", "Risk_Level"]],
            use_container_width=True
        )

        st.warning(
            "Negative efficiency means dose increased compared with 0 mm shielding."
        )

    elif page == "Report":
        st.subheader("Automatic Radiation Analysis Report")

        st.write(f"Selected Proton Energy: **{proton_energy} MeV**")
        st.write(f"Selected Aluminum Thickness: **{al_thickness} mm**")
        st.write(f"Nearest Available Thickness: **{selected_row['Thickness_mm']} mm**")
        st.write(f"Selected Dose: **{selected_dose:.2E} Gy**")
        st.write(f"Selected LET: **{selected_let:.2f} keV/µm**")
        st.write(f"Selected Shielding Efficiency: **{selected_efficiency:.2f}%**")
        st.write(f"Selected Risk Level: **{selected_risk}**")

        st.markdown("---")

        st.write(f"Maximum Dose: **{max_dose:.2E} Gy**")
        st.write(f"Minimum Dose: **{min_dose:.2E} Gy**")
        st.write(f"Average Dose: **{avg_dose:.2E} Gy**")
        st.write(f"Maximum LET: **{max_let:.2f} keV/µm**")

        st.markdown("---")

        st.success(
            f"Recommended Thickness: **{optimal_thickness} mm** "
            f"with Minimum Dose: **{optimal_dose:.2E} Gy**"
        )

else:
    st.info("Please upload a PHITS result CSV file.")