import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="Winter Teleconnection Dashboard", layout="wide")

st.title("🌎 Real-Time Winter Pattern Dashboard")
st.markdown("Track key atmospheric indices that influence the Northeast U.S. winter pattern.")

# ---- Helper Function ----
def fetch_cpc_data(url, index_name):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lines = [
            line.strip().split()
            for line in response.text.splitlines()
            if len(line.strip().split()) == 4
        ]
        df = pd.DataFrame(lines, columns=["Year", "Month", "Day", index_name])
        df[["Year", "Month", "Day"]] = df[["Year", "Month", "Day"]].astype(int)
        df[index_name] = df[index_name].astype(float)
        df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]])
        return df
    except Exception as e:
        st.error(f"Failed to fetch {index_name}: {e}")
        return pd.DataFrame()


# ---- Data Sources ----

index_urls = {
    "AO": "https://www.cpc.ncep.noaa.gov/data/teledoc/ao_index.timser",
    "NAO": "https://www.cpc.ncep.noaa.gov/data/teledoc/nao_index.timser",
    "PNA": "https://www.cpc.ncep.noaa.gov/data/teledoc/pna_index.timser",
}

# ---- Fetch Data ----
index_data = {}
for name, url in index_urls.items():
    df = fetch_cpc_data(url, name)
    if not df.empty:
        index_data[name] = df.tail(90)

# ---- Plot Teleconnection Indices ----
st.header("📈 Teleconnection Indices (AO, NAO, PNA)")
cols = st.columns(3)

for i, (name, df) in enumerate(index_data.items()):
    with cols[i]:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df[name], mode="lines+markers", name=name))
        fig.update_layout(title=f"{name} Index (Last 90 Days)", xaxis_title="Date", yaxis_title="Index Value", height=300)
        st.plotly_chart(fig, use_container_width=True)

# ---- ENSO & MJO (Manual Links for Now) ----
st.header("🌊 ENSO & MJO Monitoring")
st.markdown("""
- **ENSO (Niño 3.4)**: [CPC ENSO Dashboard](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php)
- **MJO Phase Diagram:** [CPC MJO Monitoring](https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/mjo.shtml)
- **Stratospheric Polar Vortex Status:** [ECMWF 10hPa Analysis](https://www.ecmwf.int/en/forecasts/charts)
""")

st.header("🧊 Quick Interpretation Guide")

st.markdown("""
| Indicator | Negative Phase | Positive Phase | Cold Signal for Northeast? |
|------------|----------------|----------------|-----------------------------|
| **AO** | Arctic air intrusion | Arctic contained | ✅ When Negative |
| **NAO** | Greenland block (trough in East) | Zonal flow (mild East) | ✅ When Negative |
| **PNA** | West trough / East ridge | West ridge / East trough | ✅ When Positive |
| **ENSO (La Niña)** | Variable jet, favors cold North | Warm bias South/East | ✅ When Central-Pacific Based |
| **MJO (Phases 7–8)** | Pacific blocking | Warm Pacific jet | ✅ When in 7–8 |
""")

st.success("✅ Tip: Check this dashboard daily in winter to anticipate 7–10 day cold patterns in the Northeast.")
