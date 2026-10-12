import csv
import math
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "latihan1.csv"

st.set_page_config(page_title="Student Performance Dashboard", page_icon="◼", layout="wide", initial_sidebar_state="expanded")

# ---------- Data ----------
@st.cache_data
def load_data():
    with open(DATA_FILE, newline="", encoding="utf-8-sig") as f:
        parsed = [row for row in csv.reader(f) if row]
    rows = []
    for row in parsed:
        if len(row) == 1 and "," in row[0]:
            rows.append([x.strip() for x in row[0].split(",")])
        else:
            rows.append([x.strip() for x in row])
    df = pd.DataFrame(rows[1:], columns=rows[0])
    numeric = ["Student_ID", "Age", "Study_Hours", "Sleep_Hours", "Attendance", "Exam_Score", "Monthly_Spending", "Screen_Hours", "Satisfaction"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Exam_Score"]).reset_index(drop=True)


df = load_data()

# ---------- Helpers ----------
def relationship(r):
    a = abs(r)
    if a >= 0.70:
        return "Strong Relationship"
    if a >= 0.40:
        return "Moderate Relationship"
    if a >= 0.20:
        return "Weak Relationship"
    return "Very Weak Relationship"


def corr(col, data):
    if data[col].nunique() < 2 or data["Exam_Score"].nunique() < 2:
        return 0.0
    return float(data[col].corr(data["Exam_Score"]))


# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Manrope:wght@400;500;600&display=swap');
:root { --bg:#0d0d10; --card:#17171c; --card2:#1d1d23; --text:#f7f4f6; --muted:#aaa4aa; --pink:#e7a6bc; --pink2:#f3c8d6; --line:#2a2930; }
.stApp { background:var(--bg); color:var(--text); font-family:'Manrope',sans-serif; }
[data-testid="stHeader"] { background:rgba(13,13,16,.92); }
[data-testid="stSidebar"] { background:#111116; border-right:1px solid var(--line); }
.block-container { max-width:1450px; padding-top:2.2rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Sora',sans-serif !important; letter-spacing:-.02em; }
h1 { font-size:2.35rem !important; margin-bottom:.25rem !important; }
.hero-sub { color:var(--muted); font-size:1rem; margin-bottom:1.6rem; }
.section-title { font-family:'Sora'; font-size:1.15rem; font-weight:600; margin:1.35rem 0 .7rem; }
.metric-card { background:linear-gradient(145deg,#19191f,#141419); border:1px solid var(--line); border-radius:18px; padding:18px 20px; min-height:112px; box-shadow:0 8px 28px rgba(0,0,0,.16); }
.metric-label { color:var(--muted); font-size:.82rem; margin-bottom:8px; }
.metric-value { font-family:'Sora'; font-size:1.65rem; font-weight:700; color:var(--text); }
.metric-note { color:var(--pink); font-size:.76rem; margin-top:5px; }
.analysis-card { background:#17171c; border:1px solid var(--line); border-radius:18px; padding:18px 20px; line-height:1.65; color:#ddd8dc; }
.analysis-card b { color:var(--pink2); }
.corr-card { background:#17171c; border:1px solid var(--line); border-radius:16px; padding:15px 17px; margin-bottom:10px; }
.corr-top { display:flex; justify-content:space-between; align-items:center; }
.corr-name { font-weight:600; } .corr-value { color:var(--pink2); font-family:'Sora'; }
.corr-status { color:var(--muted); font-size:.78rem; margin-top:4px; }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
.stButton button, .stDownloadButton button { border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("### Dashboard Controls")
gender_options = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
selected_gender = st.sidebar.selectbox("Gender Filter", gender_options)
score_range = st.sidebar.slider("Exam Score Range", 0, 100, (0, 100))
filtered = df.copy()
if selected_gender != "All":
    filtered = filtered[filtered["Gender"] == selected_gender]
filtered = filtered[filtered["Exam_Score"].between(score_range[0], score_range[1])]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered)} of {len(df)} records")

# ---------- Header ----------
st.title("Student Performance Dashboard")
st.markdown('<div class="hero-sub">Descriptive statistics and performance patterns from the student dataset.</div>', unsafe_allow_html=True)

# ---------- Metrics ----------
scores = filtered["Exam_Score"]
mean_score = scores.mean() if len(scores) else 0
median_score = scores.median() if len(scores) else 0
std_score = scores.std(ddof=1) if len(scores) > 1 else 0
min_score = scores.min() if len(scores) else 0
max_score = scores.max() if len(scores) else 0
at_risk = int((scores < 60).sum())

metrics = [
    ("Total Records", f"{len(filtered):,}", "Filtered dataset"),
    ("Average Score", f"{mean_score:.2f}", "Exam score mean"),
    ("Median Score", f"{median_score:.2f}", "Middle score"),
    ("Standard Deviation", f"{std_score:.2f}", "Score variation"),
    ("Minimum Score", f"{min_score:.0f}", "Lowest result"),
    ("At-Risk Records", f"{at_risk}", "Score below 60"),
]
cols = st.columns(6)
for c, (label, value, note) in zip(cols, metrics):
    c.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

# ---------- Charts ----------
st.markdown('<div class="section-title">Score Distribution</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1.15, 1])
with col1:
    fig = px.histogram(filtered, x="Exam_Score", nbins=10, title="Exam Score Distribution", labels={"Exam_Score":"Exam Score", "count":"Records"})
    fig.update_traces(marker_line_width=0)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ddd8dc", margin=dict(l=10,r=10,t=55,b=10), height=340)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with col2:
    bands = pd.cut(filtered["Exam_Score"], bins=[-1,59,69,79,89,101], labels=["Below 60","60–69","70–79","80–89","90–100"])
    band_df = bands.value_counts().reindex(["Below 60","60–69","70–79","80–89","90–100"], fill_value=0).reset_index()
    band_df.columns = ["Score Band", "Count"]
    fig2 = px.bar(band_df, x="Score Band", y="Count", title="Score Bands")
    fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ddd8dc", margin=dict(l=10,r=10,t=55,b=10), height=340)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ---------- Relationships ----------
st.markdown('<div class="section-title">Performance Relationships</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1.25, .75])
with col1:
    scatter = px.scatter(filtered, x="Study_Hours", y="Exam_Score", color="Gender" if filtered["Gender"].nunique() > 1 else None, hover_data=["Student_ID", "Attendance", "Sleep_Hours"], title="Study Hours vs Exam Score", labels={"Study_Hours":"Study Hours", "Exam_Score":"Exam Score"})
    scatter.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ddd8dc", margin=dict(l=10,r=10,t=55,b=10), height=360)
    st.plotly_chart(scatter, use_container_width=True, config={"displayModeBar": False})
with col2:
    st.markdown("**Correlation Overview**")
    for col, label in [("Study_Hours","Study Hours"),("Attendance","Attendance"),("Screen_Hours","Screen Time"),("Sleep_Hours","Sleep Hours"),("Satisfaction","Satisfaction")]:
        r = corr(col, filtered)
        st.markdown(f'<div class="corr-card"><div class="corr-top"><span class="corr-name">{label}</span><span class="corr-value">r = {r:.3f}</span></div><div class="corr-status">{relationship(r)}</div></div>', unsafe_allow_html=True)

# ---------- Gender comparison ----------
st.markdown('<div class="section-title">Gender Comparison</div>', unsafe_allow_html=True)
g = filtered.groupby("Gender").agg(Records=("Student_ID","count"), Average_Score=("Exam_Score","mean"), Average_Attendance=("Attendance","mean"), Average_Study_Hours=("Study_Hours","mean"), Average_Satisfaction=("Satisfaction","mean")).reset_index()
g["Average_Score"] = g["Average_Score"].round(2)
g["Average_Attendance"] = g["Average_Attendance"].round(2)
g["Average_Study_Hours"] = g["Average_Study_Hours"].round(2)
g["Average_Satisfaction"] = g["Average_Satisfaction"].round(2)
st.dataframe(g, use_container_width=True, hide_index=True)

# ---------- Analysis ----------
st.markdown('<div class="section-title">Descriptive Analysis</div>', unsafe_allow_html=True)
if len(filtered):
    avg_att = filtered["Attendance"].mean()
    avg_study = filtered["Study_Hours"].mean()
    avg_screen = filtered["Screen_Hours"].mean()
    top_gender = g.loc[g["Average_Score"].idxmax(), "Gender"] if len(g) else "-"
    top_score = g["Average_Score"].max() if len(g) else 0
    r_study = corr("Study_Hours", filtered)
    r_att = corr("Attendance", filtered)
    st.markdown(f'''<div class="analysis-card">
    <b>Overall:</b> The filtered dataset contains <b>{len(filtered)}</b> records with an average exam score of <b>{mean_score:.2f}</b>. The median is <b>{median_score:.2f}</b>, while the standard deviation is <b>{std_score:.2f}</b>, showing how spread out the scores are around the average.<br><br>
    <b>Study pattern:</b> Average study time is <b>{avg_study:.2f} hours</b>. Study Hours has a <b>{relationship(r_study).lower()}</b> with Exam Score (r = {r_study:.3f}).<br><br>
    <b>Attendance pattern:</b> Average attendance is <b>{avg_att:.2f}%</b>. Attendance has a <b>{relationship(r_att).lower()}</b> with Exam Score (r = {r_att:.3f}).<br><br>
    <b>Screen time:</b> Average screen time is <b>{avg_screen:.2f} hours</b>. This can be compared with exam results to see whether higher screen time tends to appear alongside lower or higher scores.<br><br>
    <b>Gender comparison:</b> Based on the filtered data, <b>{top_gender}</b> has the higher average exam score at <b>{top_score:.2f}</b>. This is a descriptive comparison, not a conclusion that gender causes the difference.
    </div>''', unsafe_allow_html=True)

# ---------- Decision ----------
st.markdown('<div class="section-title">Data-Based Decision</div>', unsafe_allow_html=True)
recommendations = []
if mean_score < 70:
    recommendations.append("Focus support on improving overall exam performance because the average score is below 70.")
else:
    recommendations.append("Maintain the current learning pattern while targeting students whose scores are below the group average.")
if at_risk > 0:
    recommendations.append(f"Prioritize follow-up for the {at_risk} record(s) with scores below 60.")
if corr("Attendance", filtered) >= 0.4:
    recommendations.append("Attendance is a useful indicator to monitor because it shows a moderate-to-strong relationship with exam scores.")
if corr("Study_Hours", filtered) >= 0.4:
    recommendations.append("Study time is worth monitoring because higher study hours tend to appear with higher exam scores in this dataset.")
if not recommendations:
    recommendations.append("Use the dashboard filters to identify smaller groups that need closer review.")
for item in recommendations:
    st.markdown(f"- {item}")

# ---------- Data ----------
st.markdown('<div class="section-title">Data Preview</div>', unsafe_allow_html=True)
search_id = st.text_input("Search Student ID", placeholder="Type an ID, for example 12")
preview = filtered.copy()
if search_id.strip():
    preview = preview[preview["Student_ID"].astype(str).str.contains(search_id.strip(), case=False, na=False)]
st.dataframe(preview, use_container_width=True, hide_index=True)

st.caption("Dashboard built with Streamlit, Pandas, and Plotly.")
