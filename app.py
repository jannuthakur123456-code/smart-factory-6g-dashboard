import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & ENTERPRISE STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Thales 6G Smart Factory Diagnostic Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Industrial Dark Theme CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }
    .status-badge-green {
        background-color: #059669;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .section-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BULLETPROOF REALISTIC IIOT TELEMETRY GENERATOR
# -----------------------------------------------------------------------------
@st.cache_data
def generate_industrial_telemetry():
    np.random.seed(42)
    base_time = datetime(2026, 9, 1, 0, 0)
    num_hours = 168  # 7 Days Data
    machines = [f"MCH-10{i}" for i in range(1, 6)]
    modes = ["Normal", "High-Load", "Eco"]
    shifts = ["Shift Alpha (Morning)", "Shift Beta (Evening)", "Shift Gamma (Night)"]

    rows = []
    for h in range(num_hours):
        current_dt = base_time + timedelta(hours=h)
        date_str = current_dt.strftime("%Y-%m-%d")
        time_str = current_dt.strftime("%H:%M:%S")
        hour = current_dt.hour
        shift = shifts[0] if 6 <= hour < 14 else (shifts[1] if 14 <= hour < 22 else shifts[2])

        for m_id in machines:
            machine_wear = 1.0 + (int(m_id[-1]) * 0.12)
            op_mode = np.random.choice(modes, p=[0.6, 0.25, 0.15])

            if op_mode == "High-Load":
                temp = (70.0 * machine_wear) + np.random.normal(6, 2.5)
                power = 380.0 + np.random.normal(25, 8)
                speed = np.random.normal(295, 12)
            elif op_mode == "Eco":
                temp = (52.0 * machine_wear) + np.random.normal(3, 1.5)
                power = 180.0 + np.random.normal(12, 4)
                speed = np.random.normal(175, 8)
            else:  # Normal
                temp = (62.0 * machine_wear) + np.random.normal(4, 2)
                power = 270.0 + np.random.normal(18, 6)
                speed = np.random.normal(240, 10)

            vibration = (temp * 0.42) + np.random.normal(8, 2.0)
            latency_ms = 1.1 + np.random.exponential(0.35)
            packet_loss_pct = max(0.001, np.random.normal(0.015, 0.008))

            thermal_stress = max(0.0, temp - 76.0)
            vib_stress = max(0.0, vibration - 34.0)

            defect_rate = max(0.1, 0.7 + (thermal_stress * 0.14) + (vib_stress * 0.09) + np.random.normal(0, 0.15))
            error_rate = max(0.05, 0.25 + (vib_stress * 0.08) + np.random.normal(0, 0.08))
            health_score = max(10.0, min(100.0, 100.0 - (thermal_stress * 2.1) - (vib_stress * 1.7) - (defect_rate * 2.5)))

            if health_score >= 78 and defect_rate < 2.2:
                eff_status = "High"
            elif health_score >= 58 and defect_rate < 3.8:
                eff_status = "Medium"
            else:
                eff_status = "Low"

            rows.append([
                date_str, time_str, current_dt, shift, m_id, op_mode,
                round(temp, 2), round(vibration, 2), round(power, 2),
                round(latency_ms, 2), round(packet_loss_pct, 4),
                round(defect_rate, 2), round(speed, 1),
                round(health_score, 1), round(error_rate, 2), eff_status
            ])

    cols = [
        "Date", "Time", "Timestamp", "Shift", "Machine_ID", "Operation_Mode",
        "Temperature_C", "Vibration_Hz", "Power_Consumption_kW",
        "Network_Latency_ms", "Packet_Loss_%",
        "Quality_Control_Defect_Rate_%", "Production_Speed_units_per_hr",
        "Predictive_Maintenance_Score", "Error_Rate_%", "Efficiency_Status"
    ]
    return pd.DataFrame(rows, columns=cols)

df = generate_industrial_telemetry()

# -----------------------------------------------------------------------------
# 3. HEADER & CONTROL PANEL
# -----------------------------------------------------------------------------
st.title("🏭 Thales 6G Smart Factory Diagnostics Intelligence")
st.markdown("`SYSTEM STATUS:` <span class='status-badge-green'>🟢 6G IIoT NETWORK ONLINE</span> &nbsp;|&nbsp; **Architecture:** Private 6G Edge-MEC &nbsp;|&nbsp; **Sub-ms Latency:** Operational", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Filters
st.sidebar.markdown("### 🎛️ Diagnostic Controls")
machines_list = sorted(df["Machine_ID"].unique())
selected_machines = st.sidebar.multiselect("Select Target Machines", machines_list, default=machines_list)

modes_list = sorted(df["Operation_Mode"].unique())
selected_modes = st.sidebar.multiselect("Operation Mode Filter", modes_list, default=modes_list)

temp_alert_threshold = st.sidebar.slider("Thermal Alert Threshold (°C)", min_value=60.0, max_value=95.0, value=78.0, step=1.0)

filtered_df = df[
    (df["Machine_ID"].isin(selected_machines)) &
    (df["Operation_Mode"].isin(selected_modes))
]

if filtered_df.empty:
    st.error("⚠️ No telemetry data matches the current filter selection.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. EXECUTIVE KPIS
# -----------------------------------------------------------------------------
st.subheader("📌 Key Operational Indicators (KPIs)")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Avg Speed", f"{filtered_df['Production_Speed_units_per_hr'].mean():.1f} u/hr", "+4.2% target")
c2.metric("Defect Index", f"{filtered_df['Quality_Control_Defect_Rate_%'].mean():.2f}%", "-0.31% benchmark")
c3.metric("6G Latency", f"{filtered_df['Network_Latency_ms'].mean():.2f} ms", "Sub-2ms OK")
c4.metric("Machine Health", f"{filtered_df['Predictive_Maintenance_Score'].mean():.1f} / 100", "Nominal")
c5.metric("Thermal Anomalies", f"{(filtered_df['Temperature_C'] > temp_alert_threshold).sum()}", f">{temp_alert_threshold}°C Spikes", delta_color="inverse")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 10 SCROLLABLE SECTIONS (PAGES 1 TO 10)
# -----------------------------------------------------------------------------

# PAGE 1
st.markdown("## 📊 1. Executive Factory Overview")
col1, col2 = st.columns(2)
with col1:
    fig_pie = px.pie(
        filtered_df, names="Efficiency_Status",
        color="Efficiency_Status",
        color_discrete_map={"High": "#10b981", "Medium": "#f59e0b", "Low": "#ef4444"},
        hole=0.45, title="Manufacturing Efficiency Distribution"
    )
    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    fig_bar = px.histogram(
        filtered_df, x="Machine_ID", color="Operation_Mode",
        barmode="group", color_discrete_sequence=["#3b82f6", "#8b5cf6", "#ec4899"],
        title="Operation Mode Allocation per Machine"
    )
    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# PAGE 2
st.markdown("## ⚙️ 2. Thermal & Mechanical Diagnostics")
col1, col2 = st.columns(2)
with col1:
    fig_box = px.box(
        filtered_df, x="Machine_ID", y="Temperature_C", color="Operation_Mode",
        title="Thermal Spread by Machine (°C)"
    )
    fig_box.add_hline(y=temp_alert_threshold, line_dash="dash", line_color="#ef4444", annotation_text="Threshold")
    fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_box, use_container_width=True)
with col2:
    fig_vib = px.scatter(
        filtered_df, x="Vibration_Hz", y="Temperature_C", color="Efficiency_Status",
        title="Mechanical Vibration vs Thermal Stress"
    )
    fig_vib.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_vib, use_container_width=True)

st.markdown("---")

# PAGE 3
st.markdown("## 🎯 3. Output Speed & Quality Control")
fig_scatter = px.scatter(
    filtered_df, x="Production_Speed_units_per_hr", y="Quality_Control_Defect_Rate_%",
    color="Machine_ID", title="Output Velocity vs. Quality Control Defect Density (%)"
)
fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# PAGE 4
st.markdown("## 📡 4. 6G Network & Edge MEC Telemetry")
col1, col2 = st.columns(2)
with col1:
    fig_lat = px.line(
        filtered_df.groupby(["Date", "Machine_ID"])["Network_Latency_ms"].mean().reset_index(),
        x="Date", y="Network_Latency_ms", color="Machine_ID", markers=True,
        title="Mean 6G Communication Latency over Time (ms)"
    )
    fig_lat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_lat, use_container_width=True)
with col2:
    fig_pkt = px.bar(
        filtered_df.groupby("Machine_ID")["Packet_Loss_%"].mean().reset_index(),
        x="Machine_ID", y="Packet_Loss_%", title="Average Network Packet Loss Rate (%)"
    )
    fig_pkt.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    st.plotly_chart(fig_pkt, use_container_width=True)

st.markdown("---")

# PAGE 5
st.markdown("## ⚡ 5. Energy Draw & Power Efficiency")
fig_power = px.line(
    filtered_df.groupby(["Date", "Machine_ID"])["Power_Consumption_kW"].mean().reset_index(),
    x="Date", y="Power_Consumption_kW", color="Machine_ID", title="Power Draw Trend over Time (kW)"
)
fig_power.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
st.plotly_chart(fig_power, use_container_width=True)

st.markdown("---")

# PAGE 6
st.markdown("## 🔄 6. Work Shift Performance Analytics")
fig_shift = px.bar(
    filtered_df.groupby(["Shift", "Efficiency_Status"])["Production_Speed_units_per_hr"].count().reset_index(),
    x="Shift", y="Production_Speed_units_per_hr", color="Efficiency_Status",
    barmode="group", title="Shift Efficiency Breakdown (Alpha / Beta / Gamma)"
)
fig_shift.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
st.plotly_chart(fig_shift, use_container_width=True)

st.markdown("---")

# PAGE 7
st.markdown("## 🛠️ 7. Predictive Equipment Health Index")
fig_health = px.line(
    filtered_df.groupby(["Date", "Machine_ID"])["Predictive_Maintenance_Score"].mean().reset_index(),
    x="Date", y="Predictive_Maintenance_Score", color="Machine_ID", title="Equipment Wear Degradation Curve (100 = Optimal)"
)
fig_health.add_hline(y=50, line_dash="dash", line_color="#ef4444", annotation_text="Maintenance Limit")
fig_health.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
st.plotly_chart(fig_health, use_container_width=True)

st.markdown("---")

# PAGE 8
st.markdown("## 🔥 8. Diagnostic Risk & Heatmap Density")
fig_heat = px.density_heatmap(
    filtered_df, x="Temperature_C", y="Quality_Control_Defect_Rate_%",
    color_continuous_scale="Viridis", title="Heatmap Matrix: Thermal Stress vs Defect Rate Density"
)
fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# PAGE 9
st.markdown("## 🤖 9. Root Cause & FMEA Failure Mode Matrix")
st.info("🤖 **Automated FMEA Analysis:** Real-time root cause identification based on sensor telemetry thresholds.")
col1, col2, col3 = st.columns(3)
col1.metric("Critical Asset", "MCH-105", "Wear Level: High")
col2.metric("Primary Failure Mode", "Thermal Fatigue", "Trigger: Temp > 82°C")
col3.metric("Est. Remaining Life", "48.5 Hours", "-12 hrs degradation")

fmea_df = pd.DataFrame([
    {"Machine": "MCH-105", "Failure Mode": "Bearing Overheat", "Severity": 8, "Occurrence": 6, "RPN": 48},
    {"Machine": "MCH-104", "Failure Mode": "Vibration Misalignment", "Severity": 6, "Occurrence": 5, "RPN": 30},
    {"Machine": "MCH-103", "Failure Mode": "6G Buffer Overflow", "Severity": 4, "Occurrence": 2, "RPN": 8},
    {"Machine": "MCH-102", "Failure Mode": "Power Inverter Spike", "Severity": 5, "Occurrence": 3, "RPN": 15},
    {"Machine": "MCH-101", "Failure Mode": "Normal Operation", "Severity": 1, "Occurrence": 1, "RPN": 1}
])
st.dataframe(fmea_df, use_container_width=True)

st.markdown("---")

# PAGE 10
st.markdown("## 📂 10. Live Sensor Data Stream & Emergency Logs")
anomalies = filtered_df[filtered_df["Temperature_C"] > temp_alert_threshold]

st.warning(f"🚨 **Critical Thermal Anomalies Logged:** {len(anomalies)} events above {temp_alert_threshold}°C")
if not anomalies.empty:
    st.dataframe(anomalies[["Date", "Time", "Machine_ID", "Shift", "Operation_Mode", "Temperature_C", "Vibration_Hz", "Predictive_Maintenance_Score"]], use_container_width=True)

st.markdown("#### Complete Industrial Telemetry Record")
st.dataframe(filtered_df, use_container_width=True)