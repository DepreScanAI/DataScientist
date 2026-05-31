import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# PAGE CONFIG
st.set_page_config(
    page_title="Dashboard Kesehatan Mental NHANES",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# SESSION STATE
if "dark" not in st.session_state:
    st.session_state.dark = True
if "page" not in st.session_state:
    st.session_state.page = "overview"

# Tema
def get_theme():
    if st.session_state.dark:
        return {
            "bg":             "#0f1117",
            "card":           "#1a1d27",
            "card2":          "#22263a",
            "text":           "#e2e8f0",
            "text2":          "#94a3b8",
            "text3":          "#64748b",
            "border":         "#2d3748",
            "accent":         "#3b82f6",
            "plot_bg":        "#1a1d27",
            "paper_bg":       "#1a1d27",
            "grid":           "#2d3748",
            "font_color":     "#e2e8f0",
            "insight_bg":     "#1e2a3a",
            "insight_border": "#3b82f6",
        }
    else:
        return {
            "bg":             "#f0f4ff",
            "card":           "#ffffff",
            "card2":          "#e8eeff",
            "text":           "#1e293b",
            "text2":          "#475569",
            "text3":          "#94a3b8",
            "border":         "#dde5ff",
            "accent":         "#3b82f6",
            "plot_bg":        "#ffffff",
            "paper_bg":       "#f0f4ff",
            "grid":           "#e2e8f0",
            "font_color":     "#1e293b",
            "insight_bg":     "#eff6ff",
            "insight_border": "#3b82f6",
        }

# Konstans
DEP_COLORS = {
    "Minimal":           "#10b981",
    "Mild":              "#3b82f6",
    "Moderate":          "#f59e0b",
    "Moderately Severe": "#f97316",
    "Severe":            "#ef4444",
}
DEP_ORDER = ["Minimal", "Mild", "Moderate", "Moderately Severe", "Severe"]
DEP_LABEL = {
    "Minimal":           "Minimal",
    "Mild":              "Ringan",
    "Moderate":          "Sedang",
    "Moderately Severe": "Agak Berat",
    "Severe":            "Berat",
}
GENDER_COLORS = {"Perempuan": "#ec4899", "Laki-laki": "#3b82f6"}
PALETTE = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#06b6d4"]

RACE_MAP = {
    1.0: "Mexican American",
    2.0: "Other Hispanic",
    3.0: "Non-Hispanic White",
    4.0: "Non-Hispanic Black",
    6.0: "Non-Hispanic Asian",
    7.0: "Other/Multi",
}
EDU_MAP = {
    1.0: "< SMP",
    2.0: "SMP-SMA awal",
    3.0: "SMA/GED",
    4.0: "D3/Kuliah sebagian",
    5.0: "Sarjana ke atas",
}
EDU_ORDER_VAL = [1.0, 2.0, 3.0, 4.0, 5.0]
EDU_ORDER_LABEL = [EDU_MAP[v] for v in EDU_ORDER_VAL]

MARITAL_MAP = {
    1.0: "Menikah",
    2.0: "Janda/Duda",
    3.0: "Berpisah",
    4.0: "Bercerai",
    5.0: "Tidak Menikah",
    6.0: "Hidup Bersama",
}

AGE_ORDER = ["18-29", "30-44", "45-59", "60-74", "75+"]

PA_COLORS = {
    "Active":                "#10b981",
    "Insufficiently Active": "#f59e0b",
    "Inactive":              "#ef4444",
}
PA_LABEL = {
    "Active":                "Aktif",
    "Insufficiently Active": "Kurang Aktif",
    "Inactive":              "Tidak Aktif",
}
PA_ORDER = ["Active", "Insufficiently Active", "Inactive"]

EXCLUDED_FEATURES = {"PHQ9_SCORE", "SEQN", "PHQ9_LABEL", "PHQ9_BINARY", "PHQ9_SEVERITY"}

# Data
@st.cache_data
def load_data():
    df = pd.read_csv("Final_Data.csv")
    # Gender label
    df["gender_label"] = df["GENDER"].map({1.0: "Laki-laki", 2.0: "Perempuan"})
    # Education label
    df["edu_label"] = df["EDUCATION"].map(EDU_MAP)
    # Race label
    df["race_label"] = df["RACE"].map(RACE_MAP)
    # Marital label
    df["marital_label"] = df["MARITAL"].map(MARITAL_MAP)
    # PA label ID
    df["pa_label"] = df["PA_CATEGORY"].map(PA_LABEL)
    return df

def plo(th, title="", height=380):
    return dict(
        title=dict(text=f"<b>{title}</b>" if title else "",
                   font=dict(size=14, color=th["font_color"]), x=0.01),
        paper_bgcolor=th["paper_bg"],
        plot_bgcolor=th["plot_bg"],
        font=dict(color=th["font_color"], size=12),
        height=height,
        margin=dict(l=40, r=24, t=52, b=44),
        xaxis=dict(gridcolor=th["grid"], showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=th["grid"], showgrid=True, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )

def insight(th, text: str):
    st.markdown(
        f"""<div style="background:{th['insight_bg']};border-left:4px solid {th['insight_border']};
        border-radius:0 8px 8px 0;padding:14px 18px;margin-top:10px;margin-bottom:32px;
        font-size:13px;color:{th['text2']};line-height:1.8;">
        💡 <b>Insight:</b> {text}</div>""",
        unsafe_allow_html=True,
    )

def chart_title(th, text: str):
    st.markdown(
        f"<div style='font-size:13px;font-weight:600;color:{th['text']};margin-bottom:8px;margin-top:6px;'>{text}</div>",
        unsafe_allow_html=True,
    )

def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f"<div style='font-size:24px;font-weight:700;letter-spacing:-0.5px;margin-bottom:2px;'>{title}</div>",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f"<div style='font-size:13px;color:#94a3b8;margin-bottom:24px;'>{subtitle}</div>",
            unsafe_allow_html=True,
        )

def spacer(px: int = 16):
    st.markdown(f"<div style='margin-top:{px}px;'></div>", unsafe_allow_html=True)

def divider_section(th):
    st.markdown(
        f"<hr style='border:none;border-top:1px solid {th['border']};margin:32px 0 28px 0;'>",
        unsafe_allow_html=True,
    )

# CSS
def inject_css(th):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
    .stApp {{ background-color:{th["bg"]}; color:{th["text"]}; }}

    section[data-testid="stSidebar"] {{
        background-color:{th["card"]};
        border-right:1px solid {th["border"]};
    }}
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSlider label {{
        color:{th["text2"]} !important; font-size:13px;
    }}
    div[data-testid="metric-container"] {{
        background:{th["card"]}; border:1px solid {th["border"]};
        border-radius:14px; padding:18px 22px;
    }}
    div[data-testid="metric-container"] label {{
        color:{th["text2"]} !important; font-size:11px !important;
        font-weight:600 !important; text-transform:uppercase; letter-spacing:0.8px;
    }}
    div[data-testid="metric-container"] [data-testid="metric-value"] {{
        color:{th["text"]} !important; font-size:28px !important; font-weight:700 !important;
    }}
    .stPlotlyChart {{
        background:{th["card"]}; border-radius:14px;
        border:1px solid {th["border"]}; overflow:hidden;
        margin-bottom:8px;
    }}
    .stButton > button {{
        border-radius:10px; font-weight:500; font-size:13px; transition:all 0.2s;
    }}
    .stButton > button[kind="primary"] {{
        background:linear-gradient(135deg,#3b82f6,#6366f1);
        color:white; border:none;
        box-shadow:0 2px 12px rgba(59,130,246,0.35);
    }}
    .stButton > button[kind="secondary"] {{
        background:{th["card2"]}; color:{th["text2"]};
        border:1px solid {th["border"]};
    }}
    .stButton > button:hover {{ transform:translateY(-1px); }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: {th["card2"]};
        border-radius: 14px;
        padding: 6px 8px;
        margin-bottom: 24px;
        border: 1px solid {th["border"]};
        width: fit-content;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        color: {th["text2"]};
        font-weight: 500;
        font-size: 13px;
        padding: 8px 20px;
        border: none;
        transition: background 0.2s, color 0.2s;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background: {th["border"]};
        color: {th["text"]};
    }}
    .stTabs [aria-selected="true"] {{
        background: {th["accent"]} !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(59,130,246,0.35);
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 14px;
    }}
    hr {{ border-color:{th["border"]}; margin:16px 0; }}
    [data-testid="column"] > div:first-child {{
        padding-left: 2px;
        padding-right: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR
def render_sidebar(df):
    th = get_theme()
    with st.sidebar:
        st.markdown(f"""
        <div style="margin-bottom:6px;">
          <div style="font-size:22px;font-weight:800;color:{th['accent']};letter-spacing:-1px;">🧠 DepreScan</div>
          <div style="font-size:11px;color:{th['text3']};margin-top:2px;text-transform:uppercase;letter-spacing:1px;">
            NHANES Kesehatan Mental
          </div>
          <div style="margin-top:8px;padding:8px 10px;background:{th['card2']};border-radius:8px;border:1px solid {th['border']};">
            <div style="font-size:11px;font-weight:700;color:{th['text2']};">Capstone Coding Camp 2026</div>
            <div style="font-size:11px;color:{th['text3']};margin-top:2px;">ID Tim: CC26-PSU066</div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.divider()

        pages = [
            ("overview",    "📊 Ringkasan Utama"),
            ("demography",  "👥 Demografi"),
            ("depression",  "🧠 Analisis Depresi"),
            ("lifestyle",   "🏃 Gaya Hidup & Risiko"),
            ("business",    "💼 Pertanyaan Bisnis"),
        ]
        for key, label in pages:
            active = st.session_state.page == key
            if st.button(label, key=f"nav_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.divider()

        st.markdown(
            f"<div style='font-size:11px;font-weight:700;color:{th['text3']};"
            f"text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;'>"
            f"🎛️ Filter Data</div>",
            unsafe_allow_html=True,
        )

        gender_opts = ["Semua"] + sorted(df["gender_label"].dropna().unique().tolist())
        sel_gender  = st.selectbox("Jenis Kelamin", gender_opts)

        sel_dep = st.multiselect(
            "Tingkat Depresi",
            options=DEP_ORDER,
            default=DEP_ORDER,
            format_func=lambda x: DEP_LABEL.get(x, x),
        )

        age_min = int(df["AGE"].min())
        age_max = int(df["AGE"].max())
        sel_age = st.slider("Rentang Usia", age_min, age_max, (age_min, age_max))

        st.divider()

        st.markdown(
            f"<div style='font-size:11px;font-weight:700;color:{th['text3']};"
            f"text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;'>"
            f"⚙️ Tampilan</div>",
            unsafe_allow_html=True,
        )
        dark_val = st.toggle("🌙 Mode Gelap", value=st.session_state.dark)
        if dark_val != st.session_state.dark:
            st.session_state.dark = dark_val
            st.rerun()

    return sel_gender, sel_dep if sel_dep else DEP_ORDER, sel_age

def apply_filters(df, sel_gender, sel_dep, sel_age):
    dff = df.copy()
    if sel_gender != "Semua":
        dff = dff[dff["gender_label"] == sel_gender]
    if sel_dep:
        dff = dff[dff["PHQ9_SEVERITY"].isin(sel_dep)]
    dff = dff[(dff["AGE"] >= sel_age[0]) & (dff["AGE"] <= sel_age[1])]
    return dff

# TOP 10 HEATMAP
def render_top10_heatmap(dff, th):
    divider_section(th)
    st.markdown(
        f"<div style='font-size:18px;font-weight:700;color:{th['text']};margin-bottom:4px;'>"
        f"🔥 Top 10 Fitur Paling Berpengaruh terhadap PHQ-9</div>"
        f"<div style='font-size:13px;color:{th['text3']};margin-bottom:20px;'>"
        f"Heatmap korelasi nilai rata-rata fitur di setiap tingkat depresi, dinormalisasi per baris</div>",
        unsafe_allow_html=True,
    )

    num_cols     = dff.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in num_cols if c not in EXCLUDED_FEATURES]

    if not feature_cols:
        st.info("Tidak ada fitur numerik yang tersedia.")
        return

    corr_with_phq = (
        dff[feature_cols + ["PHQ9_SCORE"]]
        .dropna()
        .corr()["PHQ9_SCORE"]
        .drop("PHQ9_SCORE")
    )
    top10_cols  = corr_with_phq.abs().sort_values(ascending=False).head(10).index.tolist()
    top10_named = top10_cols 

    dep_label_order = [DEP_LABEL[d] for d in DEP_ORDER]

    hm_data = []
    for col, name in zip(top10_cols, top10_named):
        row = {"Fitur": name}
        for lvl in DEP_ORDER:
            sub = dff[dff["PHQ9_SEVERITY"] == lvl]
            row[DEP_LABEL[lvl]] = round(sub[col].mean(), 3) if len(sub) > 0 else np.nan
        hm_data.append(row)

    hm_df   = pd.DataFrame(hm_data).set_index("Fitur")[dep_label_order]
    hm_norm = hm_df.apply(lambda r: (r - r.min()) / (r.max() - r.min() + 1e-9), axis=1)

    annotations = []
    for i, fitur in enumerate(top10_named):
        for j, dep in enumerate(dep_label_order):
            val = hm_df.loc[fitur, dep]
            annotations.append(dict(
                x=dep, y=fitur,
                text=f"{val:.2f}" if not np.isnan(val) else "",
                showarrow=False,
                font=dict(size=11, color="white"),
                xref="x", yref="y",
            ))

    fig_hm = px.imshow(
        hm_norm,
        labels=dict(x="Tingkat Depresi", y="Fitur", color="Intensitas"),
        x=dep_label_order,
        y=top10_named,
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        zmin=0, zmax=1,
    )
    fig_hm.update_layout(
        paper_bgcolor=th["paper_bg"],
        plot_bgcolor=th["plot_bg"],
        font=dict(color=th["font_color"], size=12),
        height=430,
        margin=dict(l=200, r=50, t=40, b=60),
        coloraxis_colorbar=dict(
            title="Intensitas",
            tickvals=[0, 0.5, 1],
            ticktext=["Rendah", "Sedang", "Tinggi"],
            thickness=14, len=0.8,
        ),
        xaxis=dict(side="bottom", tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        annotations=annotations,
    )
    st.plotly_chart(fig_hm, use_container_width=True)
    spacer(12)

    corr_table = corr_with_phq.loc[top10_cols].reset_index()
    corr_table.columns = ["Kolom", "Korelasi"]
    corr_table["Korelasi"] = corr_table["Korelasi"].round(3)
    corr_table["Arah"]     = corr_table["Korelasi"].apply(
        lambda v: "🔴 Positif" if v > 0 else "🟢 Negatif")
    corr_table["| r |"]    = corr_table["Korelasi"].abs().round(3)
    corr_table["Kekuatan"] = corr_table["| r |"].apply(
        lambda v: "Sangat Kuat" if v >= 0.7 else
                  "Kuat"        if v >= 0.4 else
                  "Sedang"      if v >= 0.2 else "Lemah")
    st.dataframe(
        corr_table[["Kolom", "Korelasi", "Arah", "Kekuatan"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    top_name = top10_named[0]
    top_r    = corr_with_phq.abs().sort_values(ascending=False).values[0]
    insight(th,
        f"Heatmap dinormalisasi per baris sehingga gradasi warna menunjukkan <b>pola perubahan</b> "
        f"tiap fitur seiring meningkatnya tingkat depresi. "
        f"Fitur <b>{top_name}</b> memiliki korelasi tertinggi (|r| = {top_r:.3f}) "
        f"dengan skor PHQ-9. "
        f"Warna <b>merah = nilai tinggi</b>, <b>hijau = nilai rendah</b> (relatif per baris).")

# PAGE 1: RINGKASAN UTAMA
def page_overview(df, dff, th):
    section_header("📊 Ringkasan Utama",
                   "Gambaran besar data kesehatan mental responden NHANES")

    n_total = len(df)
    n_filt  = len(dff)
    pct_min = (dff["PHQ9_SEVERITY"] == "Minimal").mean() * 100
    pct_sev = dff["PHQ9_SEVERITY"].isin(["Moderately Severe", "Severe"]).mean() * 100
    pct_dep = (dff["PHQ9_BINARY"] == 1).mean() * 100

    st.markdown(
        f"<div style='background:{th['card2']};border:1px solid {th['border']};border-radius:10px;"
        f"padding:10px 16px;font-size:13px;color:{th['text2']};margin-bottom:20px;'>"
        f"📌 Menampilkan <b style='color:{th['text']};'>{n_filt:,}</b> dari "
        f"<b style='color:{th['text']};'>{n_total:,}</b> total responden sesuai filter.</div>",
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("👥 Total Responden",  f"{n_filt:,}")
    k2.metric("🎂 Rata-rata Usia",   f"{dff['AGE'].mean():.0f} thn")
    k3.metric("📋 Rata-rata PHQ-9",  f"{dff['PHQ9_SCORE'].mean():.1f} / 27")
    k4.metric("✅ Kondisi Minimal",  f"{pct_min:.1f}%")
    k5.metric("🚨 Depresi Berat+",   f"{pct_sev:.1f}%")

    spacer(24)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        chart_title(th, "Komposisi tingkat depresi seluruh responden")
        dep_cnt = dff["PHQ9_SEVERITY"].value_counts().reindex(DEP_ORDER).dropna()
        labels_id = [DEP_LABEL[l] for l in dep_cnt.index]
        fig = go.Figure(go.Pie(
            labels=labels_id,
            values=dep_cnt.values.tolist(),
            hole=0.6,
            marker_colors=[DEP_COLORS[l] for l in dep_cnt.index],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Jumlah: %{value:,}<br>%{percent}<extra></extra>",
        ))
        fig.update_layout(**plo(th, "", 340))
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        insight(th,
            f"Sebagian besar responden (<b>{pct_min:.0f}%</b>) berada di kategori <b>Minimal</b>. "
            f"Hanya <b>{pct_sev:.1f}%</b> yang mengalami depresi Agak Berat hingga Berat. "
            f"Responden dengan PHQ9_BINARY = 1 (butuh perhatian) sebesar <b>{pct_dep:.1f}%</b>.")

    with c2:
        chart_title(th, "Perbandingan jumlah responden laki-laki vs perempuan")
        gender_cnt = dff["gender_label"].value_counts()
        f_n = gender_cnt.get("Perempuan", 0)
        m_n = gender_cnt.get("Laki-laki", 0)
        f_pct = f_n / n_filt * 100 if n_filt > 0 else 0
        m_pct = m_n / n_filt * 100 if n_filt > 0 else 0
        fig2 = go.Figure(go.Pie(
            labels=["Perempuan", "Laki-laki"],
            values=[f_n, m_n],
            hole=0.6,
            marker_colors=["#ec4899", "#3b82f6"],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value:,} orang<br>%{percent}<extra></extra>",
        ))
        fig2.update_layout(**plo(th, "", 340))
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        insight(th,
            f"Data cukup seimbang: <b>Perempuan {f_pct:.0f}%</b> dan "
            f"<b>Laki-laki {m_pct:.0f}%</b>. "
            f"Keseimbangan ini memungkinkan perbandingan antar gender dilakukan secara valid.")

    spacer(8)

    c3, c4 = st.columns(2, gap="large")

    with c3:
        chart_title(th, "Sebaran kelompok usia responden")
        age_cnt = (dff["AGE_GROUP"].value_counts()
                   .reindex(AGE_ORDER).dropna().reset_index())
        age_cnt.columns = ["Usia", "Jumlah"]
        fig3 = px.bar(
            age_cnt, x="Usia", y="Jumlah",
            color="Jumlah",
            color_continuous_scale=["#1e3a5f", "#3b82f6", "#93c5fd"],
            text="Jumlah",
        )
        fig3.update_layout(**plo(th, "", 340))
        fig3.update_traces(textposition="outside", marker_line_width=0)
        fig3.update_layout(coloraxis_showscale=False,
                           xaxis_title="Kelompok Usia", yaxis_title="Jumlah Orang")
        st.plotly_chart(fig3, use_container_width=True)
        top_age = age_cnt.loc[age_cnt["Jumlah"].idxmax(), "Usia"]
        insight(th,
            f"Kelompok usia <b>{top_age} tahun</b> adalah yang paling banyak. "
            f"Dataset ini mencakup responden dewasa dari 5 kelompok usia.")

    with c4:
        chart_title(th, "Rata-rata skor PHQ-9 per tingkat depresi")
        phq_mean = (dff.groupby("PHQ9_SEVERITY")["PHQ9_SCORE"]
                      .mean().reindex(DEP_ORDER).dropna().reset_index())
        phq_mean.columns = ["Tingkat", "Skor"]
        phq_mean["Label"] = phq_mean["Tingkat"].map(DEP_LABEL)
        phq_mean["Skor"]  = phq_mean["Skor"].round(1)
        fig4 = px.bar(
            phq_mean, x="Label", y="Skor",
            color="Tingkat",
            color_discrete_map=DEP_COLORS,
            text="Skor",
            category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
        )
        fig4.update_layout(**plo(th, "", 340))
        fig4.update_traces(textposition="outside")
        fig4.update_layout(showlegend=False,
                           xaxis_title="Tingkat Depresi", yaxis_title="Rata-rata Skor PHQ-9")
        st.plotly_chart(fig4, use_container_width=True)
        sev_row  = phq_mean[phq_mean["Tingkat"] == "Severe"]
        sev_skor = sev_row["Skor"].values[0] if len(sev_row) else "?"
        insight(th,
            f"Setiap tingkat depresi memiliki kisaran skor PHQ-9 yang khas. "
            f"Kategori <b>Berat</b> rata-rata skornya <b>{sev_skor}</b> "
            f"jauh di atas Minimal yang hanya sekitar 1-2 poin.")

    spacer(8)

    chart_title(th, "Jumlah responden berdasarkan tingkat pendidikan")
    edu_cnt = (dff.dropna(subset=["edu_label"])["edu_label"]
                  .value_counts().reindex(EDU_ORDER_LABEL).dropna().reset_index())
    edu_cnt.columns = ["Pendidikan", "Jumlah"]
    edu_cnt["Persen"] = (edu_cnt["Jumlah"] / edu_cnt["Jumlah"].sum() * 100).round(1)
    edu_cnt["Teks"]   = edu_cnt.apply(lambda r: f"{r['Jumlah']:,}  ({r['Persen']}%)", axis=1)
    fig5 = px.bar(
        edu_cnt, x="Jumlah", y="Pendidikan",
        orientation="h",
        color="Jumlah",
        color_continuous_scale=["#1e3a5f", "#3b82f6", "#93c5fd"],
        text="Teks",
        category_orders={"Pendidikan": EDU_ORDER_LABEL},
    )
    fig5.update_layout(**plo(th, "", 280))
    fig5.update_traces(textposition="outside")
    fig5.update_layout(coloraxis_showscale=False,
                       yaxis_title="", xaxis_title="Jumlah Responden")
    st.plotly_chart(fig5, use_container_width=True)
    top_edu_row = edu_cnt.loc[edu_cnt["Jumlah"].idxmax()]
    insight(th,
        f"Kelompok pendidikan terbesar adalah <b>{top_edu_row['Pendidikan']}</b> "
        f"dengan {top_edu_row['Jumlah']:,} responden ({top_edu_row['Persen']}%). "
        f"Keragaman latar pendidikan memungkinkan analisis hubungannya dengan tingkat depresi.")

    render_top10_heatmap(dff, th)

# PAGE 2: DEMOGRAFI
def page_demography(dff, th):
    section_header("👥 Analisis Demografi",
                   "Pola depresi berdasarkan jenis kelamin, pendidikan, usia, dan ras")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["  👫 Jenis Kelamin  ", "  🎓 Pendidikan  ", "  🎂 Kelompok Usia  ", "  🌍 Ras & Status  "])

    # TAB GENDER
    with tab1:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Rata-rata skor depresi: perempuan vs laki-laki")
            phq_g = dff.groupby("gender_label")["PHQ9_SCORE"].mean().reset_index()
            phq_g["Skor"] = phq_g["PHQ9_SCORE"].round(2)
            fig = px.bar(
                phq_g, x="gender_label", y="Skor",
                color="gender_label",
                color_discrete_map=GENDER_COLORS,
                text="Skor",
            )
            fig.update_layout(**plo(th, "", 340))
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False,
                              xaxis_title="", yaxis_title="Rata-rata Skor PHQ-9")
            st.plotly_chart(fig, use_container_width=True)
            f_sc = phq_g.loc[phq_g["gender_label"] == "Perempuan", "Skor"]
            m_sc = phq_g.loc[phq_g["gender_label"] == "Laki-laki", "Skor"]
            f_v  = f_sc.values[0] if len(f_sc) else 0
            m_v  = m_sc.values[0] if len(m_sc) else 0
            insight(th,
                f"Perempuan memiliki rata-rata skor <b>{f_v:.2f}</b> dan laki-laki <b>{m_v:.2f}</b>. "
                f"Selisih sekitar <b>{abs(f_v - m_v):.2f} poin</b> pola ini umum ditemukan "
                f"di berbagai penelitian kesehatan mental.")

        with c2:
            chart_title(th, "Komposisi tingkat depresi: perempuan vs laki-laki (%)")
            dep_g = dff.groupby(["gender_label", "PHQ9_SEVERITY"]).size().reset_index(name="n")
            tot_g = dep_g.groupby("gender_label")["n"].transform("sum")
            dep_g["pct"]  = (dep_g["n"] / tot_g * 100).round(1)
            dep_g["Teks"] = dep_g["pct"].astype(str) + "%"
            fig2 = px.bar(
                dep_g, x="gender_label", y="pct",
                color="PHQ9_SEVERITY",
                color_discrete_map=DEP_COLORS,
                text="Teks",
                category_orders={"PHQ9_SEVERITY": DEP_ORDER},
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_traces(textposition="inside", textfont_size=10)
            fig2.update_layout(yaxis_title="Persentase (%)",
                               xaxis_title="", legend_title="Tingkat Depresi")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Setiap batang mewakili 100% dari masing-masing jenis kelamin. "
                f"Perhatikan proporsi warna kuning-merah untuk membandingkan "
                f"beban depresi antar gender.")

        divider_section(th)
        chart_title(th, "Jumlah orang per tingkat depresi, dipisah jenis kelamin")
        dep_g2 = dff.groupby(["PHQ9_SEVERITY", "gender_label"]).size().reset_index(name="n")
        dep_g2["Tingkat"] = dep_g2["PHQ9_SEVERITY"].map(DEP_LABEL)
        fig3 = px.bar(
            dep_g2, y="Tingkat", x="n",
            color="gender_label",
            barmode="group",
            orientation="h",
            color_discrete_map=GENDER_COLORS,
            text="n",
            category_orders={"Tingkat": [DEP_LABEL[d] for d in DEP_ORDER]},
        )
        fig3.update_layout(**plo(th, "", 380))
        fig3.update_traces(textposition="outside")
        fig3.update_layout(xaxis_title="Jumlah Orang", yaxis_title="",
                           legend_title="Jenis Kelamin")
        st.plotly_chart(fig3, use_container_width=True)
        insight(th, "Batang horizontal ini memperlihatkan jumlah absolut di tiap kategori depresi per gender.")
        spacer(16)

    # TAB PENDIDIKAN
    with tab2:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Rata-rata skor depresi per tingkat pendidikan")
            phq_e = (dff.groupby("edu_label")["PHQ9_SCORE"]
                       .mean().reindex(EDU_ORDER_LABEL).dropna().reset_index())
            phq_e.columns = ["edu", "Skor"]
            phq_e["Skor"]  = phq_e["Skor"].round(2)
            fig = px.bar(
                phq_e, y="edu", x="Skor",
                orientation="h",
                color="Skor",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                text="Skor",
                category_orders={"edu": EDU_ORDER_LABEL},
            )
            fig.update_layout(**plo(th, "", 340))
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False,
                              xaxis_title="Rata-rata Skor PHQ-9", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
            low_edu  = phq_e.loc[phq_e["Skor"].idxmax(), "edu"] if len(phq_e) else "?"
            high_edu = phq_e.loc[phq_e["Skor"].idxmin(), "edu"] if len(phq_e) else "?"
            insight(th,
                f"Pendidikan <b>{low_edu}</b> memiliki skor depresi rata-rata tertinggi, "
                f"sedangkan <b>{high_edu}</b> terendah. "
                f"Pendidikan lebih tinggi berkaitan dengan kondisi mental yang lebih baik.")

        with c2:
            chart_title(th, "% depresi sedang-berat (Moderate ke atas) per pendidikan")
            heavy   = dff[dff["PHQ9_SEVERITY"].isin(["Moderate", "Moderately Severe", "Severe"])]
            tot_edu = dff.groupby("edu_label").size().reindex(EDU_ORDER_LABEL).dropna()
            hvy_edu = heavy.groupby("edu_label").size().reindex(EDU_ORDER_LABEL).fillna(0)
            pct_hvy = (hvy_edu / tot_edu * 100).round(1).reset_index()
            pct_hvy.columns = ["edu", "pct"]
            pct_hvy["Teks"]  = pct_hvy["pct"].astype(str) + "%"
            fig2 = px.bar(
                pct_hvy, y="edu", x="pct",
                orientation="h",
                color="pct",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                text="Teks",
                category_orders={"edu": EDU_ORDER_LABEL},
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(coloraxis_showscale=False,
                               xaxis_title="% Depresi Sedang-Berat", yaxis_title="")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Semakin rendah pendidikan, persentase depresi sedang-berat cenderung lebih tinggi.")

        divider_section(th)
        chart_title(th, "Komposisi tingkat depresi di setiap jenjang pendidikan (%)")
        dep_e = dff.groupby(["edu_label", "PHQ9_SEVERITY"]).size().reset_index(name="n")
        tot_e = dep_e.groupby("edu_label")["n"].transform("sum")
        dep_e["pct"]  = (dep_e["n"] / tot_e * 100).round(1)
        dep_e["Teks"] = dep_e["pct"].astype(str) + "%"
        fig3 = px.bar(
            dep_e, x="edu_label", y="pct",
            color="PHQ9_SEVERITY",
            color_discrete_map=DEP_COLORS,
            text="Teks",
            category_orders={
                "PHQ9_SEVERITY": DEP_ORDER,
                "edu_label": EDU_ORDER_LABEL,
            },
        )
        fig3.update_layout(**plo(th, "", 400))
        fig3.update_traces(textposition="inside", textfont_size=10)
        fig3.update_layout(yaxis_title="Persentase (%)", xaxis_title="",
                           legend_title="Tingkat Depresi", xaxis_tickangle=-15)
        st.plotly_chart(fig3, use_container_width=True)
        insight(th,
            f"Setiap batang = 100% responden di jenjang itu. "
            f"Jenjang pendidikan rendah cenderung punya lebih banyak warna kuning dan merah.")
        spacer(16)

    # TAB USIA
    with tab3:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Rata-rata skor depresi per kelompok usia")
            age_phq = (dff.groupby("AGE_GROUP")["PHQ9_SCORE"]
                         .mean().reindex(AGE_ORDER).dropna().reset_index())
            age_phq.columns = ["Usia", "Skor"]
            age_phq["Skor"] = age_phq["Skor"].round(2)
            fig = px.line(
                age_phq, x="Usia", y="Skor",
                markers=True,
                color_discrete_sequence=[th["accent"]],
                text="Skor",
            )
            fig.update_traces(line_width=3, marker_size=10,
                              textposition="top center", textfont_size=11)
            fig.update_layout(**plo(th, "", 340))
            fig.update_layout(xaxis_title="Kelompok Usia",
                              yaxis_title="Rata-rata Skor PHQ-9")
            st.plotly_chart(fig, use_container_width=True)
            insight(th,
                f"Garis ini menunjukkan tren skor depresi di setiap kelompok usia. "
                f"Usia muda (18-29) sering memiliki skor lebih tinggi karena tekanan "
                f"hidup yang cukup besar di masa itu.")

        with c2:
            chart_title(th, "% depresi sedang-berat di tiap kelompok usia")
            heavy_age = dff[dff["PHQ9_SEVERITY"].isin(["Moderate", "Moderately Severe", "Severe"])]
            tot_age   = dff.groupby("AGE_GROUP").size().reindex(AGE_ORDER).dropna()
            hvy_age2  = heavy_age.groupby("AGE_GROUP").size().reindex(AGE_ORDER).fillna(0)
            pct_age   = (hvy_age2 / tot_age * 100).round(1).reset_index()
            pct_age.columns = ["Usia", "pct"]
            pct_age["Teks"] = pct_age["pct"].astype(str) + "%"
            fig2 = px.bar(
                pct_age, x="Usia", y="pct",
                color="pct",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                text="Teks",
                category_orders={"Usia": AGE_ORDER},
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(coloraxis_showscale=False,
                               xaxis_title="Kelompok Usia",
                               yaxis_title="% Depresi Sedang-Berat")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Batang yang lebih tinggi = kelompok usia dengan lebih banyak kasus depresi. "
                f"Ini bisa jadi prioritas intervensi program kesehatan jiwa.")

        divider_section(th)
        chart_title(th, "Komposisi lengkap tingkat depresi di setiap kelompok usia")
        dep_age = dff.groupby(["AGE_GROUP", "PHQ9_SEVERITY"]).size().reset_index(name="n")
        tot_a   = dep_age.groupby("AGE_GROUP")["n"].transform("sum")
        dep_age["pct"]  = (dep_age["n"] / tot_a * 100).round(1)
        dep_age["Teks"] = dep_age["pct"].astype(str) + "%"
        fig3 = px.bar(
            dep_age, x="AGE_GROUP", y="pct",
            color="PHQ9_SEVERITY",
            color_discrete_map=DEP_COLORS,
            text="Teks",
            category_orders={"PHQ9_SEVERITY": DEP_ORDER, "AGE_GROUP": AGE_ORDER},
        )
        fig3.update_layout(**plo(th, "", 400))
        fig3.update_traces(textposition="inside", textfont_size=10)
        fig3.update_layout(yaxis_title="Persentase (%)",
                           xaxis_title="Kelompok Usia",
                           legend_title="Tingkat Depresi")
        st.plotly_chart(fig3, use_container_width=True)
        insight(th,
            f"Setiap batang = 100% responden di kelompok usia itu. "
            f"Lihat proporsi warna hangat untuk menilai kelompok usia paling rentan.")
        spacer(16)

    # TAB RAS & STATUS
    with tab4:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Rata-rata skor PHQ-9 per kelompok ras/etnis")
            race_phq = (dff.groupby("race_label")["PHQ9_SCORE"]
                          .mean().dropna().sort_values(ascending=True).reset_index())
            race_phq.columns = ["Ras", "Skor"]
            race_phq["Skor"] = race_phq["Skor"].round(2)
            fig = px.bar(
                race_phq, y="Ras", x="Skor",
                orientation="h",
                color="Skor",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                text="Skor",
            )
            fig.update_layout(**plo(th, "", 360))
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False,
                              xaxis_title="Rata-rata Skor PHQ-9", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
            insight(th,
                f"Perbedaan skor antar kelompok ras mencerminkan faktor sosial-ekonomi "
                f"dan akses layanan kesehatan yang berbeda.")

        with c2:
            chart_title(th, "Distribusi status pernikahan dan rata-rata PHQ-9")
            mar_phq = (dff.groupby("marital_label")["PHQ9_SCORE"]
                         .mean().dropna().sort_values(ascending=True).reset_index())
            mar_phq.columns = ["Status", "Skor"]
            mar_phq["Skor"] = mar_phq["Skor"].round(2)
            fig2 = px.bar(
                mar_phq, y="Status", x="Skor",
                orientation="h",
                color="Skor",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                text="Skor",
            )
            fig2.update_layout(**plo(th, "", 360))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(coloraxis_showscale=False,
                               xaxis_title="Rata-rata Skor PHQ-9", yaxis_title="")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Status pernikahan berhubungan erat dengan kesehatan mental. "
                f"Dukungan sosial dari pasangan dapat menjadi faktor protektif terhadap depresi.")

        divider_section(th)
        chart_title(th, "Proporsi responden hidup sendirian vs bersama orang lain")
        alone_cnt = dff["LIVING_ALONE"].value_counts().reset_index()
        alone_cnt.columns = ["Nilai", "Jumlah"]
        alone_cnt["Label"] = alone_cnt["Nilai"].map({0: "Tidak Tinggal Sendiri", 1: "Tinggal Sendiri"})
        alone_cnt["Persen"] = (alone_cnt["Jumlah"] / alone_cnt["Jumlah"].sum() * 100).round(1)
        fig3 = go.Figure(go.Pie(
            labels=alone_cnt["Label"],
            values=alone_cnt["Jumlah"],
            hole=0.55,
            marker_colors=["#3b82f6", "#ef4444"],
            textinfo="percent+label",
        ))
        fig3.update_layout(**plo(th, "", 320))
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
        alone_pct_v = alone_cnt.loc[alone_cnt["Nilai"] == 1, "Persen"]
        ap = alone_pct_v.values[0] if len(alone_pct_v) else "?"
        alone_score = dff.groupby("LIVING_ALONE")["PHQ9_SCORE"].mean()
        s_alone = alone_score.get(1, 0)
        s_not   = alone_score.get(0, 0)
        insight(th,
            f"Sekitar <b>{ap}%</b> responden tinggal sendirian. "
            f"Rata-rata PHQ-9 yang tinggal sendiri: <b>{s_alone:.2f}</b> vs "
            f"yang tidak sendiri: <b>{s_not:.2f}</b>. "
            f"Isolasi sosial berkaitan dengan risiko depresi yang lebih tinggi.")
        spacer(16)

# PAGE 3: ANALISIS DEPRESI
def page_depression(dff, th):
    section_header("🧠 Analisis Depresi",
                   "Memahami pola PHQ-9, distribusi skor, dan hubungan antar variabel")

    tab1, tab2, tab3 = st.tabs(
        ["  📊 Distribusi Skor  ", "  🔢 Item PHQ-9  ", "  🔗 Hubungan Variabel  "])

    # TAB DISTRIBUSI SKOR
    with tab1:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Berapa banyak orang di setiap kisaran skor PHQ-9?")
            fig = px.histogram(
                dff, x="PHQ9_SCORE", nbins=20,
                color_discrete_sequence=[th["accent"]],
            )
            fig.update_layout(**plo(th, "", 340))
            fig.update_traces(marker_line_width=0.5, marker_line_color="white")
            fig.update_layout(
                xaxis_title="Skor PHQ-9 (0 = Sehat   27 = Sangat Berat)",
                yaxis_title="Jumlah Orang", bargap=0.05,
            )
            st.plotly_chart(fig, use_container_width=True)
            insight(th,
                f"Mayoritas orang berkumpul di skor rendah (0-5). "
                f"Semakin ke kanan (skor makin tinggi), makin sedikit orangnya "
                f"depresi berat memang lebih jarang terjadi.")

        with c2:
            chart_title(th, "Skor PHQ-9 dipisah warna per tingkat depresi")
            fig2 = px.histogram(
                dff, x="PHQ9_SCORE",
                color="PHQ9_SEVERITY",
                barmode="overlay", nbins=20, opacity=0.75,
                color_discrete_map=DEP_COLORS,
                category_orders={"PHQ9_SEVERITY": DEP_ORDER},
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_layout(
                xaxis_title="Skor PHQ-9",
                yaxis_title="Jumlah Orang",
                legend_title="Tingkat", bargap=0.05,
            )
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Hijau (Minimal) mendominasi skor rendah, merah (Berat) hanya muncul di skor tinggi. "
                f"Klasifikasi depresi berdasarkan skor PHQ-9 sangat konsisten.")

        divider_section(th)
        chart_title(th, "Piramida depresi dari terbanyak hingga paling sedikit")
        dep_cnt = (dff["PHQ9_SEVERITY"].value_counts()
                     .reindex(DEP_ORDER).dropna().reset_index())
        dep_cnt.columns = ["Tingkat", "Jumlah"]
        dep_cnt["Label"]  = dep_cnt["Tingkat"].map(DEP_LABEL)
        dep_cnt["Persen"] = (dep_cnt["Jumlah"] / dep_cnt["Jumlah"].sum() * 100).round(1)
        dep_cnt["Teks"]   = dep_cnt.apply(
            lambda r: f"{r['Label']}   {r['Jumlah']:,} orang ({r['Persen']}%)", axis=1)
        fig3 = go.Figure(go.Funnel(
            y=dep_cnt["Teks"],
            x=dep_cnt["Jumlah"],
            marker_color=[DEP_COLORS[d] for d in dep_cnt["Tingkat"]],
            textinfo="value+percent initial",
        ))
        fig3.update_layout(
            paper_bgcolor=th["paper_bg"],
            plot_bgcolor=th["plot_bg"],
            font=dict(color=th["font_color"], size=12),
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig3, use_container_width=True)
        insight(th,
            f"Grafik corong: paling banyak di Minimal, makin ke bawah makin sedikit. "
            f"Depresi berat masih merupakan minoritas dalam populasi ini.")
        spacer(16)

    # TAB ITEM PHQ-9 (menggunakan N_SEVERE_ITEMS dan DPQ100)
    with tab2:
        spacer(12)

        chart_title(th, "Distribusi jumlah item parah (N_SEVERE_ITEMS) per responden")
        nsev_cnt = dff["N_SEVERE_ITEMS"].value_counts().sort_index().reset_index()
        nsev_cnt.columns = ["Jumlah Item Parah", "Frekuensi"]
        fig = px.bar(
            nsev_cnt, x="Jumlah Item Parah", y="Frekuensi",
            color="Frekuensi",
            color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            text="Frekuensi",
        )
        fig.update_layout(**plo(th, "", 340))
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False,
                          xaxis_title="Jumlah Item PHQ-9 yang Parah (skor ≥ 2)",
                          yaxis_title="Jumlah Responden")
        st.plotly_chart(fig, use_container_width=True)
        insight(th,
            f"N_SEVERE_ITEMS menghitung berapa item PHQ-9 yang dijawab dengan skor ≥ 2 (sering/hampir selalu). "
            f"Semakin banyak item parah, semakin besar kemungkinan depresi klinis.")

        divider_section(th)

        c1, c2 = st.columns(2, gap="large")
        with c1:
            chart_title(th, "Rata-rata N_SEVERE_ITEMS per tingkat depresi")
            nsev_dep = (dff.groupby("PHQ9_SEVERITY")["N_SEVERE_ITEMS"]
                          .mean().reindex(DEP_ORDER).dropna().reset_index())
            nsev_dep.columns = ["Tingkat", "Rata-rata"]
            nsev_dep["Label"] = nsev_dep["Tingkat"].map(DEP_LABEL)
            nsev_dep["Rata-rata"] = nsev_dep["Rata-rata"].round(2)
            fig2 = px.bar(
                nsev_dep, x="Label", y="Rata-rata",
                color="Tingkat", color_discrete_map=DEP_COLORS,
                text="Rata-rata",
                category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(showlegend=False,
                               xaxis_title="Tingkat Depresi",
                               yaxis_title="Rata-rata Jumlah Item Parah")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Semakin berat tingkat depresi, rata-rata item parah meningkat konsisten. "
                f"Ini membuktikan validitas N_SEVERE_ITEMS sebagai penanda keparahan depresi.")

        with c2:
            chart_title(th, "Skor DPQ100 (pertimbangan bunuh diri) per tingkat depresi")
            if "DPQ100" in dff.columns:
                dpq_dep = (dff.groupby("PHQ9_SEVERITY")["DPQ100"]
                             .mean().reindex(DEP_ORDER).dropna().reset_index())
                dpq_dep.columns = ["Tingkat", "Rata-rata DPQ100"]
                dpq_dep["Label"] = dpq_dep["Tingkat"].map(DEP_LABEL)
                dpq_dep["Rata-rata DPQ100"] = dpq_dep["Rata-rata DPQ100"].round(3)
                fig3 = px.bar(
                    dpq_dep, x="Label", y="Rata-rata DPQ100",
                    color="Tingkat", color_discrete_map=DEP_COLORS,
                    text="Rata-rata DPQ100",
                    category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
                )
                fig3.update_layout(**plo(th, "", 340))
                fig3.update_traces(textposition="outside")
                fig3.update_layout(showlegend=False,
                                   xaxis_title="Tingkat Depresi",
                                   yaxis_title="Rata-rata Skor DPQ100")
                st.plotly_chart(fig3, use_container_width=True)
                insight(th,
                    f"DPQ100 mengukur pikiran negatif tentang diri sendiri atau keinginan mati (PHQ-9 item 10). "
                    f"Peningkatan tajam pada kelompok depresi berat menjadi sinyal perhatian klinis penting.")
        spacer(16)

    # TAB HUBUNGAN VARIABEL
    with tab3:
        spacer(12)
        chart_title(th, "Hubungan usia dan skor depresi (sampel 600 responden)")
        samp = (dff.dropna(subset=["AGE", "PHQ9_SCORE"])
                   .sample(min(600, len(dff)), random_state=42))
        samp["Tingkat"] = samp["PHQ9_SEVERITY"].map(DEP_LABEL)
        fig = px.scatter(
            samp, x="AGE", y="PHQ9_SCORE",
            color="PHQ9_SEVERITY",
            color_discrete_map=DEP_COLORS,
            opacity=0.55,
            hover_data={
                "Tingkat":    True,
                "gender_label": True,
                "AGE":        True,
                "PHQ9_SCORE": True,
                "PHQ9_SEVERITY": False,
            },
            labels={"AGE": "Usia (tahun)", "PHQ9_SCORE": "Skor PHQ-9"},
            trendline="ols",
            category_orders={"PHQ9_SEVERITY": DEP_ORDER},
        )
        fig.update_layout(**plo(th, "", 440))
        fig.update_layout(legend_title="Tingkat Depresi")
        st.plotly_chart(fig, use_container_width=True)
        insight(th,
            f"Setiap titik = 1 responden; warna = tingkat depresinya. "
            f"Garis tren menunjukkan arah umum hubungan usia dengan skor PHQ-9.")

        divider_section(th)
        chart_title(th, "Seberapa kuat hubungan tiap faktor dengan skor depresi?")
        num_feats = {
            "Usia":                 "AGE",
            "Risiko Alkohol":       "ALCOHOL_RISK_SCORE",
            "Skor MET Total":       "TOTAL_MET_MIN",
            "Risiko Tidur":         "SLEEP_RISK_SCORE",
            "Jam Tidur Rata-rata":  "AVG_SLEEP_HOURS",
            "Jam Sedentary":        "SEDENTARY_HOURS",
            "Menit Aktivitas Berat":"VIG_MIN_WEEK",
            "Risiko Komposit":      "TOTAL_RISK_COMPOSITE",
            "PIR (Pendapatan)":     "PIR",
            "Item Parah PHQ-9":     "N_SEVERE_ITEMS",
        }
        corr_vals = {}
        for label, col in num_feats.items():
            if col in dff.columns:
                c_val = dff[["PHQ9_SCORE", col]].dropna().corr().iloc[0, 1]
                corr_vals[label] = round(c_val, 3)
        corr_df = pd.DataFrame(list(corr_vals.items()), columns=["Faktor", "Korelasi"])
        corr_df = corr_df.sort_values("Korelasi", ascending=True)
        corr_df["Warna"] = corr_df["Korelasi"].apply(
            lambda x: "#ef4444" if x > 0.3 else "#f59e0b" if x > 0 else "#10b981")
        fig2 = go.Figure(go.Bar(
            y=corr_df["Faktor"],
            x=corr_df["Korelasi"],
            orientation="h",
            marker_color=corr_df["Warna"],
            text=corr_df["Korelasi"].astype(str),
            textposition="outside",
        ))
        fig2.update_layout(**plo(th, "", 380))
        fig2.update_layout(
            xaxis_title="Kekuatan Korelasi dengan Skor PHQ-9  (-1 s/d +1)",
            yaxis_title="",
            xaxis_range=[-0.5, 1.0],
        )
        st.plotly_chart(fig2, use_container_width=True)
        insight(th,
            f"<b>Mendekati +1 (merah)</b>: faktor sangat berhubungan positif dengan depresi tinggi. "
            f"<b>Mendekati -1 (hijau)</b>: semakin tinggi faktor itu, skor depresi justru lebih rendah.")
        spacer(16)

# PAGE 4: GAYA HIDUP & RISIKO
def page_lifestyle(dff, th):
    section_header("🏃 Gaya Hidup & Risiko",
                   "Kaitan antara alkohol, aktivitas fisik, tidur, dan tingkat depresi")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["  🍺 Alkohol  ", "  💪 Aktivitas Fisik  ", "  😴 Tidur  ", "  ⚠️ Indeks Risiko  "])

    # TAB ALKOHOL
    with tab1:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Rata-rata risiko alkohol di setiap tingkat depresi")
            alc_dep = (dff.groupby("PHQ9_SEVERITY")["ALCOHOL_RISK_SCORE"]
                         .mean().reindex(DEP_ORDER).dropna().reset_index())
            alc_dep.columns = ["Tingkat", "Skor"]
            alc_dep["Label"] = alc_dep["Tingkat"].map(DEP_LABEL)
            alc_dep["Skor"]  = alc_dep["Skor"].round(2)
            fig = px.bar(
                alc_dep, x="Label", y="Skor",
                color="Tingkat", color_discrete_map=DEP_COLORS,
                text="Skor",
                category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
            )
            fig.update_layout(**plo(th, "", 340))
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False,
                              xaxis_title="", yaxis_title="Rata-rata Skor Risiko Alkohol")
            st.plotly_chart(fig, use_container_width=True)
            max_dep = alc_dep.loc[alc_dep["Skor"].idxmax(), "Label"] if len(alc_dep) else "?"
            insight(th,
                f"Kelompok <b>{max_dep}</b> memiliki rata-rata risiko alkohol tertinggi. "
                f"Ada indikasi bahwa konsumsi alkohol berlebih berkaitan dengan depresi lebih berat.")

        with c2:
            chart_title(th, "Distribusi skor risiko alkohol (0-3)")
            alc_cnt = (dff["ALCOHOL_RISK_SCORE"].value_counts().sort_index().reset_index())
            alc_cnt.columns = ["Skor", "Jumlah"]
            alc_cnt["Kategori"] = alc_cnt["Skor"].map({
                0: "Tidak Minum",
                1: "Risiko Rendah",
                2: "Risiko Sedang",
                3: "Risiko Tinggi",
            })
            fig2 = px.bar(
                alc_cnt, x="Kategori", y="Jumlah",
                color="Skor",
                color_continuous_scale=["#10b981", "#f59e0b", "#f97316", "#ef4444"],
                text="Jumlah",
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(coloraxis_showscale=False,
                               xaxis_title="", yaxis_title="Jumlah Responden")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th, "Distribusi risiko alkohol menunjukkan sebaran konsumsi alkohol di populasi ini.")

        divider_section(th)
        chart_title(th, "Proporsi binge drinker dan heavy drinker per tingkat depresi")
        binge_dep = dff.groupby("PHQ9_SEVERITY")[["BINGE_DRINKER", "HEAVY_DRINKER"]].mean() * 100
        binge_dep = binge_dep.reindex(DEP_ORDER).dropna().round(1).reset_index()
        binge_dep["Label"] = binge_dep["PHQ9_SEVERITY"].map(DEP_LABEL)
        binge_melt = binge_dep.melt(
            id_vars=["PHQ9_SEVERITY", "Label"],
            value_vars=["BINGE_DRINKER", "HEAVY_DRINKER"],
            var_name="Jenis", value_name="Persen",
        )
        binge_melt["Jenis"] = binge_melt["Jenis"].map({
            "BINGE_DRINKER": "Binge Drinker",
            "HEAVY_DRINKER": "Heavy Drinker",
        })
        fig3 = px.bar(
            binge_melt, x="Label", y="Persen",
            color="Jenis", barmode="group",
            color_discrete_map={"Binge Drinker": "#f97316", "Heavy Drinker": "#ef4444"},
            text="Persen",
            category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
        )
        fig3.update_layout(**plo(th, "", 380))
        fig3.update_traces(textposition="outside", textfont_size=10)
        fig3.update_layout(yaxis_title="% dari Kelompok", xaxis_title="Tingkat Depresi")
        st.plotly_chart(fig3, use_container_width=True)
        insight(th,
            f"Pola minum berisiko (binge/heavy) cenderung lebih tinggi pada kelompok depresi berat. "
            f"Ini bisa mencerminkan penggunaan alkohol sebagai koping negatif.")
        spacer(16)

    # TAB AKTIVITAS FISIK
    with tab2:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Distribusi kategori aktivitas fisik")
            pa_cnt = dff["PA_CATEGORY"].value_counts().reindex(PA_ORDER).dropna().reset_index()
            pa_cnt.columns = ["Kategori", "Jumlah"]
            pa_cnt["Label"]  = pa_cnt["Kategori"].map(PA_LABEL)
            pa_cnt["Persen"] = (pa_cnt["Jumlah"] / pa_cnt["Jumlah"].sum() * 100).round(1)
            pa_cnt["Teks"]   = pa_cnt.apply(lambda r: f"{r['Jumlah']:,} ({r['Persen']}%)", axis=1)
            fig = px.bar(
                pa_cnt, x="Label", y="Jumlah",
                color="Kategori",
                color_discrete_map=PA_COLORS,
                text="Teks",
                category_orders={"Label": [PA_LABEL[p] for p in PA_ORDER]},
            )
            fig.update_layout(**plo(th, "", 340))
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False,
                              xaxis_title="", yaxis_title="Jumlah Responden")
            st.plotly_chart(fig, use_container_width=True)
            insight(th,
                f"Sebagian besar responden tergolong Aktif. Namun kelompok Tidak Aktif "
                f"tetap perlu perhatian karena berpotensi berdampak pada kesehatan mental.")

        with c2:
            chart_title(th, "Rata-rata total MET menit/minggu per tingkat depresi")
            met_dep = (dff.groupby("PHQ9_SEVERITY")["TOTAL_MET_MIN"]
                         .mean().reindex(DEP_ORDER).dropna().reset_index())
            met_dep.columns = ["Tingkat", "MET"]
            met_dep["Label"] = met_dep["Tingkat"].map(DEP_LABEL)
            met_dep["MET"]   = met_dep["MET"].round(0)
            fig2 = px.bar(
                met_dep, x="Label", y="MET",
                color="Tingkat", color_discrete_map=DEP_COLORS,
                text="MET",
                category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(showlegend=False,
                               xaxis_title="", yaxis_title="Rata-rata Total MET min/minggu")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Jika kelompok depresi berat memiliki MET lebih rendah, "
                f"itu mendukung pentingnya aktivitas fisik untuk kesehatan mental.")

        divider_section(th)
        chart_title(th, "Komposisi kategori aktivitas fisik di setiap tingkat depresi")
        pa_dep = dff.groupby(["PHQ9_SEVERITY", "PA_CATEGORY"]).size().reset_index(name="n")
        tot_pa = pa_dep.groupby("PHQ9_SEVERITY")["n"].transform("sum")
        pa_dep["pct"]   = (pa_dep["n"] / tot_pa * 100).round(1)
        pa_dep["Label"] = pa_dep["PHQ9_SEVERITY"].map(DEP_LABEL)
        pa_dep["PA_LB"] = pa_dep["PA_CATEGORY"].map(PA_LABEL)
        pa_dep["Teks"]  = pa_dep["pct"].astype(str) + "%"
        fig3 = px.bar(
            pa_dep, x="Label", y="pct",
            color="PA_CATEGORY",
            color_discrete_map=PA_COLORS,
            text="Teks",
            category_orders={
                "PA_CATEGORY": PA_ORDER,
                "Label": [DEP_LABEL[d] for d in DEP_ORDER],
            },
        )
        fig3.update_layout(**plo(th, "", 400))
        fig3.update_traces(textposition="inside", textfont_size=10)
        fig3.update_layout(yaxis_title="Persentase (%)",
                           xaxis_title="Tingkat Depresi",
                           legend_title="Aktivitas Fisik")
        st.plotly_chart(fig3, use_container_width=True)
        insight(th,
            f"Perhatikan apakah proporsi 'Tidak Aktif (merah)' meningkat seiring beratnya depresi.")
        spacer(16)

    # TAB TIDUR
    with tab3:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Rata-rata jam tidur per tingkat depresi")
            sleep_dep = (dff.groupby("PHQ9_SEVERITY")["AVG_SLEEP_HOURS"]
                           .mean().reindex(DEP_ORDER).dropna().reset_index())
            sleep_dep.columns = ["Tingkat", "Jam"]
            sleep_dep["Label"] = sleep_dep["Tingkat"].map(DEP_LABEL)
            sleep_dep["Jam"]   = sleep_dep["Jam"].round(2)
            fig = px.bar(
                sleep_dep, x="Label", y="Jam",
                color="Tingkat", color_discrete_map=DEP_COLORS,
                text="Jam",
                category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
            )
            fig.update_layout(**plo(th, "", 340))
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False,
                              xaxis_title="", yaxis_title="Rata-rata Jam Tidur per Malam")
            st.plotly_chart(fig, use_container_width=True)
            insight(th,
                f"Gangguan tidur adalah salah satu gejala utama depresi. "
                f"Lihat apakah kelompok depresi berat tidur lebih sedikit atau lebih banyak (hipersomnia).")

        with c2:
            chart_title(th, "Distribusi skor risiko tidur (0-4)")
            slp_cnt = dff["SLEEP_RISK_SCORE"].value_counts().sort_index().reset_index()
            slp_cnt.columns = ["Skor Risiko Tidur", "Jumlah"]
            slp_cnt["Kategori"] = slp_cnt["Skor Risiko Tidur"].map({
                0: "Tidak Ada Risiko", 1: "Rendah", 2: "Sedang", 3: "Tinggi", 4: "Sangat Tinggi"
            })
            fig2 = px.bar(
                slp_cnt, x="Kategori", y="Jumlah",
                color="Skor Risiko Tidur",
                color_continuous_scale=["#10b981", "#3b82f6", "#f59e0b", "#f97316", "#ef4444"],
                text="Jumlah",
            )
            fig2.update_layout(**plo(th, "", 340))
            fig2.update_traces(textposition="outside")
            fig2.update_layout(coloraxis_showscale=False,
                               xaxis_title="", yaxis_title="Jumlah Responden")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"SLEEP_RISK_SCORE menggabungkan beberapa indikator masalah tidur. "
                f"Skor lebih tinggi mencerminkan lebih banyak masalah tidur yang dialami.")

        divider_section(th)
        c3, c4 = st.columns(2, gap="large")
        with c3:
            chart_title(th, "Rata-rata risiko tidur per tingkat depresi")
            slpr_dep = (dff.groupby("PHQ9_SEVERITY")["SLEEP_RISK_SCORE"]
                          .mean().reindex(DEP_ORDER).dropna().reset_index())
            slpr_dep.columns = ["Tingkat", "Risiko"]
            slpr_dep["Label"] = slpr_dep["Tingkat"].map(DEP_LABEL)
            slpr_dep["Risiko"] = slpr_dep["Risiko"].round(2)
            fig3 = px.line(
                slpr_dep, x="Label", y="Risiko",
                markers=True,
                color_discrete_sequence=["#6366f1"],
                text="Risiko",
                category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
            )
            fig3.update_traces(line_width=3, marker_size=10,
                               textposition="top center", textfont_size=11)
            fig3.update_layout(**plo(th, "", 340))
            fig3.update_layout(xaxis_title="Tingkat Depresi",
                               yaxis_title="Rata-rata Skor Risiko Tidur")
            st.plotly_chart(fig3, use_container_width=True)
            insight(th,
                f"Jika garis naik dari Minimal ke Berat, masalah tidur semakin parah "
                f"seiring beratnya depresi konsisten dengan literatur klinis.")

        with c4:
            chart_title(th, "Proporsi gangguan tidur dan sleep apnea per tingkat depresi")
            sd_dep = dff.groupby("PHQ9_SEVERITY")[["SLEEP_DISORDERED", "SLEEP_APNEA_RISK"]].mean() * 100
            sd_dep = sd_dep.reindex(DEP_ORDER).dropna().round(1).reset_index()
            sd_dep["Label"] = sd_dep["PHQ9_SEVERITY"].map(DEP_LABEL)
            sd_melt = sd_dep.melt(
                id_vars=["PHQ9_SEVERITY", "Label"],
                value_vars=["SLEEP_DISORDERED", "SLEEP_APNEA_RISK"],
                var_name="Kondisi", value_name="Persen",
            )
            sd_melt["Kondisi"] = sd_melt["Kondisi"].map({
                "SLEEP_DISORDERED": "Gangguan Tidur",
                "SLEEP_APNEA_RISK": "Risiko Sleep Apnea",
            })
            fig4 = px.bar(
                sd_melt, x="Label", y="Persen",
                color="Kondisi", barmode="group",
                color_discrete_map={
                    "Gangguan Tidur": "#8b5cf6",
                    "Risiko Sleep Apnea": "#06b6d4",
                },
                text="Persen",
                category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
            )
            fig4.update_layout(**plo(th, "", 340))
            fig4.update_traces(textposition="outside", textfont_size=10)
            fig4.update_layout(yaxis_title="% dari Kelompok",
                               xaxis_title="Tingkat Depresi",
                               legend_title="Kondisi Tidur")
            st.plotly_chart(fig4, use_container_width=True)
            insight(th,
                f"Gangguan tidur dan risiko sleep apnea keduanya berkaitan dengan kualitas tidur. "
                f"Perhatikan tren pada kelompok depresi yang lebih berat.")
        spacer(16)

    # TAB INDEKS RISIKO
    with tab4:
        spacer(12)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            chart_title(th, "Distribusi skor risiko komposit total")
            trc_cnt = (dff["TOTAL_RISK_COMPOSITE"].value_counts().sort_index().reset_index())
            trc_cnt.columns = ["Skor", "Jumlah"]
            fig = px.bar(
                trc_cnt, x="Skor", y="Jumlah",
                color="Skor",
                color_continuous_scale=["#10b981", "#f59e0b", "#f97316", "#ef4444"],
                text="Jumlah",
            )
            fig.update_layout(**plo(th, "", 360))
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False,
                              xaxis_title="Total Risk Composite Score",
                              yaxis_title="Jumlah Orang")
            st.plotly_chart(fig, use_container_width=True)
            insight(th,
                f"TOTAL_RISK_COMPOSITE menggabungkan faktor alkohol, aktivitas fisik, tidur, "
                f"dan isolasi sosial menjadi satu skor risiko gaya hidup.")

        with c2:
            chart_title(th, "Rata-rata risiko komposit per tingkat depresi")
            trc_dep = (dff.groupby("PHQ9_SEVERITY")["TOTAL_RISK_COMPOSITE"]
                         .mean().reindex(DEP_ORDER).dropna().reset_index())
            trc_dep.columns = ["Tingkat", "Skor"]
            trc_dep["Label"] = trc_dep["Tingkat"].map(DEP_LABEL)
            trc_dep["Skor"]  = trc_dep["Skor"].round(2)
            fig2 = px.line(
                trc_dep, x="Label", y="Skor",
                markers=True,
                color_discrete_sequence=["#ef4444"],
                text="Skor",
                category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
            )
            fig2.update_traces(line_width=3, marker_size=12,
                               textposition="top center", textfont_size=11)
            fig2.update_layout(**plo(th, "", 360))
            fig2.update_layout(xaxis_title="Tingkat Depresi",
                               yaxis_title="Rata-rata Total Risk Composite")
            st.plotly_chart(fig2, use_container_width=True)
            insight(th,
                f"Jika garis naik dari kiri ke kanan, semakin berat depresi semakin tinggi indeks risiko. "
                f"Ini mendukung hubungan antara gaya hidup tidak sehat dan kondisi mental yang lebih buruk.")

        divider_section(th)
        chart_title(th, "Perbandingan komponen risiko antar tingkat depresi")
        risk_cols  = ["ALCOHOL_RISK_SCORE", "SLEEP_RISK_SCORE", "SEDENTARY_HOURS"]
        risk_names = ["Risiko Alkohol", "Risiko Tidur", "Jam Sedentary"]
        risk_dep   = (dff.groupby("PHQ9_SEVERITY")[risk_cols]
                        .mean().reindex(DEP_ORDER).dropna().reset_index())
        risk_dep["Label"] = risk_dep["PHQ9_SEVERITY"].map(DEP_LABEL)

        # Normalisasi 0-1 agar perbandingan skala berbeda lebih mudah
        for col in risk_cols:
            mn, mx = risk_dep[col].min(), risk_dep[col].max()
            risk_dep[col + "_norm"] = (risk_dep[col] - mn) / (mx - mn + 1e-9)

        risk_melt = risk_dep.melt(
            id_vars=["PHQ9_SEVERITY", "Label"],
            value_vars=[c + "_norm" for c in risk_cols],
            var_name="Komponen", value_name="Nilai (norm)",
        )
        risk_melt["Komponen"] = risk_melt["Komponen"].map(
            {c + "_norm": n for c, n in zip(risk_cols, risk_names)})
        risk_melt["Nilai (norm)"] = risk_melt["Nilai (norm)"].round(3)
        fig3 = px.bar(
            risk_melt, x="Label", y="Nilai (norm)",
            color="Komponen", barmode="group",
            color_discrete_map={
                "Risiko Alkohol": "#ef4444",
                "Risiko Tidur":   "#8b5cf6",
                "Jam Sedentary":  "#f59e0b",
            },
            text="Nilai (norm)",
            category_orders={"Label": [DEP_LABEL[d] for d in DEP_ORDER]},
        )
        fig3.update_layout(**plo(th, "", 400))
        fig3.update_traces(textposition="outside", textfont_size=10)
        fig3.update_layout(yaxis_title="Nilai Ternormalisasi (0-1)",
                           xaxis_title="Tingkat Depresi",
                           legend_title="Komponen Risiko")
        st.plotly_chart(fig3, use_container_width=True)
        insight(th,
            f"Tiga komponen risiko gaya hidup ditampilkan berdampingan (dinormalisasi 0-1). "
            f"Idealnya semua nilai rendah perhatikan komponen mana yang paling meningkat "
            f"seiring beratnya depresi.")
        spacer(16)

# PAGE 5: PERTANYAAN BISNIS
def page_business(dff, th):
    section_header("💼 Pertanyaan Bisnis",
                   "Jawaban berbasis data atas pertanyaan kunci tentang depresi & gaya hidup NHANES")
 
    # MAIN QUESTION A  Siapa yang paling rentan?
    # Sub: gender, usia, pendidikan, tinggal sendiri, kemiskinan
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,{th['card']},{th['card2']});
        border:1px solid {th['border']};border-radius:16px;padding:22px 26px;margin-bottom:8px;">
        <div style="font-size:19px;font-weight:800;color:{th['text']};margin-bottom:4px;">
        🎯 Pertanyaan Utama A Siapa yang paling rentan mengalami depresi?</div>
        <div style="font-size:13px;color:{th['text3']};">
        Memetakan profil demografis & sosial-ekonomi yang berkaitan dengan risiko depresi lebih tinggi
        </div></div>""",
        unsafe_allow_html=True,
    )
    spacer(16)
    #  A1: Gender 
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"A1 · Apakah terdapat perbedaan signifikan skor PHQ-9 antara laki-laki dan perempuan?</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="large")
    with c1:
        chart_title(th, "Rata-rata & distribusi skor PHQ-9 per gender")
        phq_g = dff.groupby("gender_label")["PHQ9_SCORE"].mean().reset_index()
        phq_g["Skor"] = phq_g["PHQ9_SCORE"].round(2)
        fig = px.bar(phq_g, x="gender_label", y="Skor",
                     color="gender_label", color_discrete_map=GENDER_COLORS, text="Skor")
        fig.update_layout(**plo(th, "", 300))
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Rata-rata Skor PHQ-9")
        st.plotly_chart(fig, use_container_width=True)
 
    with c2:
        chart_title(th, "% depresi Agak Berat–Berat per gender")
        g_sev = (
            dff.groupby("gender_label")
            .apply(lambda x: (x["PHQ9_SEVERITY"].isin(["Moderately Severe","Severe"])).mean()*100)
            .reset_index()
        )
        g_sev.columns = ["Gender", "Persen"]
        g_sev["Persen"] = g_sev["Persen"].round(1)
        fig2 = px.bar(g_sev, x="Gender", y="Persen",
                      color="Gender", color_discrete_map=GENDER_COLORS, text="Persen")
        fig2.update_layout(**plo(th, "", 300))
        fig2.update_traces(textposition="outside", texttemplate="%{text}%")
        fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="% Depresi Berat+")
        st.plotly_chart(fig2, use_container_width=True)
 
    f_sc = phq_g.loc[phq_g["gender_label"]=="Perempuan","Skor"]
    m_sc = phq_g.loc[phq_g["gender_label"]=="Laki-laki","Skor"]
    f_v  = f_sc.values[0] if len(f_sc) else 0
    m_v  = m_sc.values[0] if len(m_sc) else 0
    insight(th,
        f"Perempuan memiliki rata-rata PHQ-9 <b>{f_v:.2f}</b> vs laki-laki <b>{m_v:.2f}</b> "
        f"(selisih ≈ <b>{abs(f_v-m_v):.2f} poin</b>). Pola ini konsisten dengan literatur global yang "
        f"menemukan perempuan lebih rentan depresi akibat faktor hormonal, peran sosial, dan paparan stresor. "
        f"Perbedaan ini secara klinis bermakna dan perlu diperhitungkan dalam desain intervensi berbasis gender.")
 
    divider_section(th)
 
    #  A2: Usia & Pendidikan 
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"A2 · Kelompok usia dan pendidikan mana yang paling rentan?</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="large")
    with c1:
        chart_title(th, "% depresi berat per kelompok usia")
        age_pct = (
            dff.groupby("AGE_GROUP")
            .apply(lambda x: (x["PHQ9_SEVERITY"].isin(["Moderately Severe","Severe"])).mean()*100)
            .reindex(AGE_ORDER).dropna().reset_index()
        )
        age_pct.columns = ["Usia", "Persen"]
        age_pct["Persen"] = age_pct["Persen"].round(1)
        fig = px.bar(age_pct, x="Usia", y="Persen",
                     color="Persen",
                     color_continuous_scale=["#10b981","#f59e0b","#ef4444"],
                     text="Persen")
        fig.update_layout(**plo(th, "", 300))
        fig.update_traces(textposition="outside", texttemplate="%{text}%")
        fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="% Depresi Berat+")
        st.plotly_chart(fig, use_container_width=True)
 
    with c2:
        chart_title(th, "% depresi berat per tingkat pendidikan")
        edu_pct = (
            dff.dropna(subset=["edu_label"])
            .groupby("edu_label")
            .apply(lambda x: (x["PHQ9_SEVERITY"].isin(["Moderately Severe","Severe"])).mean()*100)
            .reindex(EDU_ORDER_LABEL).dropna().reset_index()
        )
        edu_pct.columns = ["Pendidikan", "Persen"]
        edu_pct["Persen"] = edu_pct["Persen"].round(1)
        fig2 = px.bar(edu_pct, x="Persen", y="Pendidikan", orientation="h",
                      color="Persen",
                      color_continuous_scale=["#10b981","#f59e0b","#ef4444"],
                      text="Persen")
        fig2.update_layout(**plo(th, "", 300))
        fig2.update_traces(textposition="outside", texttemplate="%{text}%")
        fig2.update_layout(coloraxis_showscale=False, xaxis_title="% Depresi Berat+", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)
 
    top_age_row  = age_pct.loc[age_pct["Persen"].idxmax()] if len(age_pct) else None
    top_edu_row  = edu_pct.loc[edu_pct["Persen"].idxmax()] if len(edu_pct) else None
    insight(th,
        f"Kelompok usia <b>{top_age_row['Usia'] if top_age_row is not None else '?'}</b> "
        f"({top_age_row['Persen'] if top_age_row is not None else '?'}%) dan pendidikan "
        f"<b>{top_edu_row['Pendidikan'] if top_edu_row is not None else '?'}</b> "
        f"({top_edu_row['Persen'] if top_edu_row is not None else '?'}%) "
        f"memiliki angka depresi berat tertinggi. Rendahnya pendidikan berkaitan dengan terbatasnya "
        f"literasi kesehatan mental, akses layanan, dan sumber daya ekonomi semua faktor protektif penting.")
 
    divider_section(th)
 
    #  A3: Tinggal Sendiri
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"A3 · Apakah tinggal sendiri meningkatkan risiko depresi?</div>",
        unsafe_allow_html=True,
    )
    if "LIVING_ALONE" in dff.columns:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            chart_title(th, "Komposisi depresi Tinggal Sendiri")
            alone_df = dff[dff["LIVING_ALONE"]==1]
            if len(alone_df) > 0:
                dep_a = alone_df["PHQ9_SEVERITY"].value_counts().reindex(DEP_ORDER).dropna()
                fig_a = go.Figure(go.Pie(
                    labels=[DEP_LABEL[l] for l in dep_a.index],
                    values=dep_a.values.tolist(), hole=0.55,
                    marker_colors=[DEP_COLORS[l] for l in dep_a.index],
                    textinfo="percent+label",
                ))
                fig_a.update_layout(**plo(th, "", 300))
                fig_a.update_layout(showlegend=False)
                st.plotly_chart(fig_a, use_container_width=True)
 
        with c2:
            chart_title(th, "Komposisi depresi Bersama Orang Lain")
            notalone_df = dff[dff["LIVING_ALONE"]==0]
            if len(notalone_df) > 0:
                dep_na = notalone_df["PHQ9_SEVERITY"].value_counts().reindex(DEP_ORDER).dropna()
                fig_b = go.Figure(go.Pie(
                    labels=[DEP_LABEL[l] for l in dep_na.index],
                    values=dep_na.values.tolist(), hole=0.55,
                    marker_colors=[DEP_COLORS[l] for l in dep_na.index],
                    textinfo="percent+label",
                ))
                fig_b.update_layout(**plo(th, "", 300))
                fig_b.update_layout(showlegend=False)
                st.plotly_chart(fig_b, use_container_width=True)
 
        sev_alone    = (dff[dff["LIVING_ALONE"]==1]["PHQ9_SEVERITY"]
                          .isin(["Moderately Severe","Severe"])).mean()*100
        sev_notalone = (dff[dff["LIVING_ALONE"]==0]["PHQ9_SEVERITY"]
                          .isin(["Moderately Severe","Severe"])).mean()*100
        sc_alone = dff[dff["LIVING_ALONE"]==1]["PHQ9_SCORE"].mean()
        sc_not   = dff[dff["LIVING_ALONE"]==0]["PHQ9_SCORE"].mean()
        insight(th,
            f"Responden yang tinggal sendiri memiliki proporsi depresi berat <b>{sev_alone:.1f}%</b> "
            f"vs <b>{sev_notalone:.1f}%</b> bagi yang tinggal bersama orang lain. "
            f"Rata-rata PHQ-9 tinggal sendiri: <b>{sc_alone:.2f}</b> vs <b>{sc_not:.2f}</b>. "
            f"Isolasi sosial memutus jaringan dukungan emosional yang merupakan buffer alami terhadap stres"
            f"faktor ini penting dijadikan variabel skrining dalam produk DepreScan.")
    else:
        insight(th, "Kolom LIVING_ALONE tidak tersedia dalam subset data yang difilter.")
 
    divider_section(th)
 
    #  A4: Kemiskinan Relatif (PIR)
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"A4 · Apakah kemiskinan relatif (PIR &lt; 1.5) berkaitan dengan depresi klinis yang signifikan?</div>",
        unsafe_allow_html=True,
    )
    if "PIR" in dff.columns:
        dff2 = dff.copy()
        dff2["PIR_GROUP"] = pd.cut(
            dff2["PIR"],
            bins=[-0.01, 1.0, 1.5, 3.0, 999],
            labels=["Miskin (< 1.0)", "Hampir Miskin (1.0–1.5)", "Menengah (1.5–3.0)", "Mapan (> 3.0)"],
        )
        pir_order = ["Miskin (< 1.0)", "Hampir Miskin (1.0–1.5)", "Menengah (1.5–3.0)", "Mapan (> 3.0)"]
 
        c1, c2 = st.columns(2, gap="large")
        with c1:
            chart_title(th, "Rata-rata skor PHQ-9 per kelompok PIR")
            pir_phq = (dff2.groupby("PIR_GROUP", observed=True)["PHQ9_SCORE"]
                         .mean().reindex(pir_order).dropna().reset_index())
            pir_phq.columns = ["PIR", "Skor"]
            pir_phq["Skor"] = pir_phq["Skor"].round(2)
            fig = px.bar(pir_phq, x="PIR", y="Skor",
                         color="Skor",
                         color_continuous_scale=["#10b981","#f59e0b","#ef4444"],
                         text="Skor",
                         category_orders={"PIR": pir_order})
            fig.update_layout(**plo(th, "", 310))
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False,
                              xaxis_title="Kelompok Pendapatan (PIR)",
                              yaxis_title="Rata-rata PHQ-9", xaxis_tickangle=-15)
            st.plotly_chart(fig, use_container_width=True)
 
        with c2:
            chart_title(th, "% depresi berat per kelompok PIR")
            pir_sev = (
                dff2.groupby("PIR_GROUP", observed=True)
                .apply(lambda x: (x["PHQ9_SEVERITY"].isin(["Moderately Severe","Severe"])).mean()*100)
                .reindex(pir_order).dropna().reset_index()
            )
            pir_sev.columns = ["PIR", "Persen"]
            pir_sev["Persen"] = pir_sev["Persen"].round(1)
            fig2 = px.bar(pir_sev, x="PIR", y="Persen",
                          color="Persen",
                          color_continuous_scale=["#10b981","#f59e0b","#ef4444"],
                          text="Persen",
                          category_orders={"PIR": pir_order})
            fig2.update_layout(**plo(th, "", 310))
            fig2.update_traces(textposition="outside", texttemplate="%{text}%")
            fig2.update_layout(coloraxis_showscale=False,
                               xaxis_title="Kelompok Pendapatan (PIR)",
                               yaxis_title="% Depresi Berat+", xaxis_tickangle=-15)
            st.plotly_chart(fig2, use_container_width=True)
 
        poor_sev    = pir_sev.loc[pir_sev["PIR"]=="Miskin (< 1.0)","Persen"]
        rich_sev    = pir_sev.loc[pir_sev["PIR"]=="Mapan (> 3.0)","Persen"]
        pv = poor_sev.values[0] if len(poor_sev) else "?"
        rv = rich_sev.values[0] if len(rich_sev) else "?"
        insight(th,
            f"Kelompok paling miskin (PIR < 1.0) memiliki angka depresi berat sebesar <b>{pv}%</b> "
            f"dibandingkan <b>{rv}%</b> pada kelompok mapan (PIR > 3.0). "
            f"Kemiskinan menambah beban stres kronis, membatasi akses layanan kesehatan, dan memperburuk "
            f"faktor risiko lain seperti tidur buruk dan konsumsi alkohol menciptakan lingkaran setan depresi.")
    else:
        insight(th, "Kolom PIR tidak tersedia dalam dataset yang difilter saat ini.")

    # MAIN QUESTION B  Apakah gaya hidup tidak sehat meningkatkan risiko?
    # Sub: tidur, aktivitas fisik, alkohol

    spacer(24)
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,{th['card']},{th['card2']});
        border:1px solid {th['border']};border-radius:16px;padding:22px 26px;margin-bottom:8px;">
        <div style="font-size:19px;font-weight:800;color:{th['text']};margin-bottom:4px;">
        🏃 Pertanyaan Utama B Apakah gaya hidup tidak sehat meningkatkan risiko depresi?</div>
        <div style="font-size:13px;color:{th['text3']};">
        Menguji hubungan antara tidur, aktivitas fisik, alkohol, dan keparahan depresi
        </div></div>""",
        unsafe_allow_html=True,
    )
    spacer(16)
 
    # B1: Tidur < 6 jam
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"B1 · Apakah tidur kurang dari 6 jam berkaitan dengan skor PHQ-9 lebih tinggi?</div>",
        unsafe_allow_html=True,
    )
    if "AVG_SLEEP_HOURS" in dff.columns:
        dff3 = dff.copy()
        dff3["SLEEP_CAT"] = pd.cut(
            dff3["AVG_SLEEP_HOURS"],
            bins=[-0.01, 5.99, 7.99, 999],
            labels=["Kurang (< 6 jam)", "Normal (6–8 jam)", "Berlebih (> 8 jam)"],
        )
        sleep_order = ["Kurang (< 6 jam)", "Normal (6–8 jam)", "Berlebih (> 8 jam)"]
 
        c1, c2 = st.columns(2, gap="large")
        with c1:
            chart_title(th, "Rata-rata PHQ-9 per kategori durasi tidur")
            slp_phq = (dff3.groupby("SLEEP_CAT", observed=True)["PHQ9_SCORE"]
                         .mean().reindex(sleep_order).dropna().reset_index())
            slp_phq.columns = ["Tidur", "Skor"]
            slp_phq["Skor"] = slp_phq["Skor"].round(2)
            fig = px.bar(slp_phq, x="Tidur", y="Skor",
                         color="Skor",
                         color_continuous_scale=["#10b981","#f59e0b","#ef4444"],
                         text="Skor",
                         category_orders={"Tidur": sleep_order})
            fig.update_layout(**plo(th, "", 310))
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False,
                              xaxis_title="Kategori Durasi Tidur",
                              yaxis_title="Rata-rata PHQ-9")
            st.plotly_chart(fig, use_container_width=True)
 
        with c2:
            chart_title(th, "Komposisi tingkat depresi per kategori tidur (%)")
            dep_slp = dff3.groupby(["SLEEP_CAT","PHQ9_SEVERITY"], observed=True).size().reset_index(name="n")
            tot_slp = dep_slp.groupby("SLEEP_CAT")["n"].transform("sum")
            dep_slp["pct"] = (dep_slp["n"]/tot_slp*100).round(1)
            dep_slp["Teks"] = dep_slp["pct"].astype(str)+"%"
            fig2 = px.bar(dep_slp, x="SLEEP_CAT", y="pct",
                          color="PHQ9_SEVERITY",
                          color_discrete_map=DEP_COLORS,
                          text="Teks",
                          category_orders={"PHQ9_SEVERITY":DEP_ORDER,"SLEEP_CAT":sleep_order})
            fig2.update_layout(**plo(th, "", 310))
            fig2.update_traces(textposition="inside", textfont_size=10)
            fig2.update_layout(yaxis_title="Persentase (%)",
                               xaxis_title="Kategori Durasi Tidur",
                               legend_title="Tingkat Depresi")
            st.plotly_chart(fig2, use_container_width=True)
 
        sc_short  = dff3[dff3["SLEEP_CAT"]=="Kurang (< 6 jam)"]["PHQ9_SCORE"].mean()
        sc_normal = dff3[dff3["SLEEP_CAT"]=="Normal (6–8 jam)"]["PHQ9_SCORE"].mean()
        sc_long   = dff3[dff3["SLEEP_CAT"]=="Berlebih (> 8 jam)"]["PHQ9_SCORE"].mean()
        insight(th,
            f"Individu dengan tidur kurang dari 6 jam memiliki rata-rata PHQ-9 <b>{sc_short:.2f}</b>, "
            f"secara nyata lebih tinggi dibanding kelompok tidur normal <b>{sc_normal:.2f}</b>. "
            f"Menariknya, tidur berlebih (> 8 jam) juga berisiko (PHQ-9: <b>{sc_long:.2f}</b>), "
            f"kemungkinan mencerminkan hipersomnia sebagai gejala depresi itu sendiri. "
            f"Kualitas tidur adalah sinyal klinis dua arah yang sangat penting untuk dimonitor.")
 
    divider_section(th)
 
    # B2: Gangguan Tidur sebagai Prediktor 
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"B2 · Apakah gangguan tidur (didiagnosis dokter) merupakan prediktor terkuat di antara faktor risiko?</div>",
        unsafe_allow_html=True,
    )
    lifestyle_feature_cols = [
        "ALCOHOL_RISK_SCORE","SLEEP_RISK_SCORE","SEDENTARY_HOURS",
        "TOTAL_RISK_COMPOSITE","AVG_SLEEP_HOURS","TOTAL_MET_MIN",
        "VIG_MIN_WEEK","BINGE_DRINKER","HEAVY_DRINKER",
        "SLEEP_DISORDERED","SLEEP_APNEA_RISK",
    ]
    label_map = {
        "ALCOHOL_RISK_SCORE":  "Risiko Alkohol",
        "SLEEP_RISK_SCORE":    "Skor Risiko Tidur",
        "SEDENTARY_HOURS":     "Jam Sedentary",
        "TOTAL_RISK_COMPOSITE":"Risiko Komposit",
        "AVG_SLEEP_HOURS":     "Rata-rata Jam Tidur",
        "TOTAL_MET_MIN":       "Total MET min/minggu",
        "VIG_MIN_WEEK":        "Menit Aktivitas Berat",
        "BINGE_DRINKER":       "Binge Drinker",
        "HEAVY_DRINKER":       "Heavy Drinker",
        "SLEEP_DISORDERED":    "Gangguan Tidur (Dokter)",
        "SLEEP_APNEA_RISK":    "Risiko Sleep Apnea",
    }
    avail_cols = [c for c in lifestyle_feature_cols if c in dff.columns]
    corr_ls = (
        dff[avail_cols+["PHQ9_SCORE"]].dropna()
        .corr()["PHQ9_SCORE"].drop("PHQ9_SCORE")
        .reindex(avail_cols).dropna()
    )
    corr_ls_df = corr_ls.reset_index()
    corr_ls_df.columns = ["Fitur","Korelasi"]
    corr_ls_df["Label"] = corr_ls_df["Fitur"].map(label_map).fillna(corr_ls_df["Fitur"])
    corr_ls_df = corr_ls_df.sort_values("Korelasi", ascending=True)
    corr_ls_df["Korelasi"] = corr_ls_df["Korelasi"].round(3)
    corr_ls_df["Warna"] = corr_ls_df["Korelasi"].apply(
        lambda v: "#ef4444" if v > 0.15 else "#f59e0b" if v > 0 else "#10b981")
 
    fig_corr = px.bar(corr_ls_df, x="Korelasi", y="Label", orientation="h",
                      color="Warna", color_discrete_map="identity", text="Korelasi")
    fig_corr.update_layout(**plo(th, "", 400))
    fig_corr.update_traces(textposition="outside", textfont_size=10)
    fig_corr.update_layout(
        xaxis_title="Korelasi Pearson dengan PHQ-9 Score (-1 s/d +1)",
        yaxis_title="", showlegend=False,
        xaxis=dict(zeroline=True, zerolinecolor=th["border"], zerolinewidth=2),
    )
    st.plotly_chart(fig_corr, use_container_width=True)
 
    top_pos = corr_ls_df[corr_ls_df["Korelasi"]>0].sort_values("Korelasi",ascending=False).head(1)
    top_neg = corr_ls_df[corr_ls_df["Korelasi"]<0].sort_values("Korelasi").head(1)
    tp_name = top_pos["Label"].values[0] if len(top_pos) else "-"
    tn_name = top_neg["Label"].values[0] if len(top_neg) else "-"
    tp_r    = top_pos["Korelasi"].values[0] if len(top_pos) else 0
    tn_r    = top_neg["Korelasi"].values[0] if len(top_neg) else 0
 
    sd_corr = corr_ls_df.loc[corr_ls_df["Fitur"]=="SLEEP_DISORDERED","Korelasi"]
    sd_r    = sd_corr.values[0] if len(sd_corr) else None
    sd_rank = int((corr_ls_df["Korelasi"].abs().rank(ascending=False)
                   .loc[corr_ls_df["Fitur"]=="SLEEP_DISORDERED"]).values[0]) if sd_r else "?"
 
    insight(th,
        f"<b>{tp_name}</b> adalah faktor risiko dengan korelasi positif tertinggi (r = {tp_r:.3f}) "
        f"semakin tinggi nilainya, semakin berat depresi. "
        f"Gangguan tidur yang didiagnosis dokter berada di peringkat <b>#{sd_rank}</b> "
        f"(r = {sd_r:.3f} {'✅' if sd_r else ''}) dari semua faktor, mengkonfirmasi "
        f"bahwa ia adalah salah satu prediktor gaya hidup terkuat. "
        f"Sebaliknya, <b>{tn_name}</b> (r = {tn_r:.3f}) bersifat protektif "
        f"aktivitas fisik lebih banyak berkaitan dengan skor depresi lebih rendah.")
 
    divider_section(th)
 
    # B3: Aktivitas Fisik (WHO) 
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"B3 · Apakah individu yang tidak memenuhi panduan aktivitas fisik WHO memiliki risiko depresi lebih tinggi?</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="large")
    with c1:
        chart_title(th, "Rata-rata PHQ-9 per kategori aktivitas fisik")
        pa_phq = (dff.groupby("PA_CATEGORY")["PHQ9_SCORE"]
                    .mean().reindex(PA_ORDER).dropna().reset_index())
        pa_phq.columns = ["PA", "Skor"]
        pa_phq["Label"] = pa_phq["PA"].map(PA_LABEL)
        pa_phq["Skor"] = pa_phq["Skor"].round(2)
        fig = px.bar(pa_phq, x="Label", y="Skor",
                     color="PA", color_discrete_map=PA_COLORS, text="Skor",
                     category_orders={"Label":[PA_LABEL[p] for p in PA_ORDER]})
        fig.update_layout(**plo(th, "", 310))
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False,
                          xaxis_title="Kategori Aktivitas Fisik (WHO)",
                          yaxis_title="Rata-rata PHQ-9")
        st.plotly_chart(fig, use_container_width=True)
 
    with c2:
        chart_title(th, "% depresi berat per kategori aktivitas fisik")
        pa_sev = (
            dff.groupby("PA_CATEGORY")
            .apply(lambda x: (x["PHQ9_SEVERITY"].isin(["Moderately Severe","Severe"])).mean()*100)
            .reindex(PA_ORDER).dropna().reset_index()
        )
        pa_sev.columns = ["PA", "Persen"]
        pa_sev["Label"] = pa_sev["PA"].map(PA_LABEL)
        pa_sev["Persen"] = pa_sev["Persen"].round(1)
        fig2 = px.bar(pa_sev, x="Label", y="Persen",
                      color="PA", color_discrete_map=PA_COLORS, text="Persen",
                      category_orders={"Label":[PA_LABEL[p] for p in PA_ORDER]})
        fig2.update_layout(**plo(th, "", 310))
        fig2.update_traces(textposition="outside", texttemplate="%{text}%")
        fig2.update_layout(showlegend=False,
                           xaxis_title="Kategori Aktivitas Fisik (WHO)",
                           yaxis_title="% Depresi Berat+")
        st.plotly_chart(fig2, use_container_width=True)
 
    sev_active   = pa_sev.loc[pa_sev["PA"]=="Active","Persen"]
    sev_inactive = pa_sev.loc[pa_sev["PA"]=="Inactive","Persen"]
    av = sev_active.values[0]   if len(sev_active) else "?"
    iv = sev_inactive.values[0] if len(sev_inactive) else "?"
    insight(th,
        f"Individu yang tidak memenuhi panduan WHO (kategori 'Tidak Aktif') memiliki angka depresi berat "
        f"<b>{iv}%</b> dibandingkan <b>{av}%</b> pada kelompok aktif. "
        f"Aktivitas fisik melepaskan endorfin dan neurotransmitter (serotonin, dopamin) yang secara biologis "
        f"melindungi terhadap depresi. Rekomendasi olahraga sebaiknya menjadi bagian dari fitur intervensi DepreScan.")
 
    divider_section(th)
 
    # B4: Binge Drinking 
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{th['accent']};margin-bottom:8px;'>"
        f"B4 · Apakah perilaku binge drinking berkaitan dengan peningkatan skor PHQ-9?</div>",
        unsafe_allow_html=True,
    )
    if "BINGE_DRINKER" in dff.columns:
        c1, c2 = st.columns(2, gap="large")
        binge_map = {0: "Bukan Binge Drinker", 1: "Binge Drinker"}
        binge_colors = {"Bukan Binge Drinker": "#10b981", "Binge Drinker": "#ef4444"}
 
        with c1:
            chart_title(th, "Rata-rata PHQ-9: binge drinker vs bukan")
            bd_phq = dff.groupby("BINGE_DRINKER")["PHQ9_SCORE"].mean().reset_index()
            bd_phq["Label"] = bd_phq["BINGE_DRINKER"].map(binge_map)
            bd_phq["Skor"]  = bd_phq["PHQ9_SCORE"].round(2)
            fig = px.bar(bd_phq, x="Label", y="Skor",
                         color="Label", color_discrete_map=binge_colors, text="Skor")
            fig.update_layout(**plo(th, "", 300))
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False,
                              xaxis_title="", yaxis_title="Rata-rata PHQ-9")
            st.plotly_chart(fig, use_container_width=True)
 
        with c2:
            chart_title(th, "% depresi berat: binge drinker vs bukan")
            bd_sev = (
                dff.groupby("BINGE_DRINKER")
                .apply(lambda x: (x["PHQ9_SEVERITY"].isin(["Moderately Severe","Severe"])).mean()*100)
                .reset_index()
            )
            bd_sev.columns = ["BINGE","Persen"]
            bd_sev["Label"] = bd_sev["BINGE"].map(binge_map)
            bd_sev["Persen"] = bd_sev["Persen"].round(1)
            fig2 = px.bar(bd_sev, x="Label", y="Persen",
                          color="Label", color_discrete_map=binge_colors, text="Persen")
            fig2.update_layout(**plo(th, "", 300))
            fig2.update_traces(textposition="outside", texttemplate="%{text}%")
            fig2.update_layout(showlegend=False,
                               xaxis_title="", yaxis_title="% Depresi Berat+")
            st.plotly_chart(fig2, use_container_width=True)
 
        sc_binge   = dff[dff["BINGE_DRINKER"]==1]["PHQ9_SCORE"].mean()
        sc_nobinge = dff[dff["BINGE_DRINKER"]==0]["PHQ9_SCORE"].mean()
        sev_b = bd_sev.loc[bd_sev["BINGE"]==1,"Persen"]
        sev_nb= bd_sev.loc[bd_sev["BINGE"]==0,"Persen"]
        insight(th,
            f"Binge drinker memiliki rata-rata PHQ-9 <b>{sc_binge:.2f}</b> "
            f"vs <b>{sc_nobinge:.2f}</b> bagi yang bukan (selisih ≈ {abs(sc_binge-sc_nobinge):.2f} poin). "
            f"Proporsi depresi berat: binge drinker <b>{sev_b.values[0] if len(sev_b) else '?'}%</b> "
            f"vs non-binge <b>{sev_nb.values[0] if len(sev_nb) else '?'}%</b>. "
            f"Alkohol menekan sistem saraf pusat dan mengganggu siklus tidur dua jalur langsung menuju depresi. "
            f"Edukasi pengurangan alkohol perlu diintegrasikan dalam rekomendasi DepreScan.")
 
    # MAIN QUESTION C Perbandingan komprehensif Minimal vs Berat

    spacer(24)
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,{th['card']},{th['card2']});
        border:1px solid {th['border']};border-radius:16px;padding:22px 26px;margin-bottom:8px;">
        <div style="font-size:19px;font-weight:800;color:{th['text']};margin-bottom:4px;">
        📊 Pertanyaan Utama C Apa perbedaan nyata antara kelompok Minimal vs Berat?</div>
        <div style="font-size:13px;color:{th['text3']};">
        Perbandingan komprehensif semua faktor risiko gaya hidup antara dua kutub tingkat depresi
        </div></div>""",
        unsafe_allow_html=True,
    )
    spacer(16)
 
    minimal_df = dff[dff["PHQ9_SEVERITY"]=="Minimal"]
    severe_df  = dff[dff["PHQ9_SEVERITY"]=="Severe"]
 
    lifestyle_cols_compare = {
        "ALCOHOL_RISK_SCORE":  "Risiko Alkohol",
        "SLEEP_RISK_SCORE":    "Risiko Tidur",
        "SEDENTARY_HOURS":     "Jam Sedentary",
        "TOTAL_RISK_COMPOSITE":"Risiko Komposit",
    }
    compare_rows = []
    for col, label in lifestyle_cols_compare.items():
        if col in dff.columns:
            compare_rows.append({
                "Indikator": label,
                "Minimal":   round(minimal_df[col].mean(), 2) if len(minimal_df) > 0 else 0,
                "Berat":     round(severe_df[col].mean(),  2) if len(severe_df)  > 0 else 0,
            })
 
    compare_df = pd.DataFrame(compare_rows)
    compare_melt = compare_df.melt(id_vars="Indikator", var_name="Kelompok", value_name="Nilai")
 
    fig_cmp = px.bar(compare_melt, x="Indikator", y="Nilai",
                     color="Kelompok", barmode="group",
                     color_discrete_map={"Minimal":"#10b981","Berat":"#ef4444"},
                     text="Nilai")
    fig_cmp.update_layout(**plo(th, "", 380))
    fig_cmp.update_traces(textposition="outside", textfont_size=10)
    fig_cmp.update_layout(xaxis_title="", yaxis_title="Rata-rata Nilai",
                          legend_title="Kelompok Depresi")
    st.plotly_chart(fig_cmp, use_container_width=True)
 
    insight(th,
        "Kelompok depresi <b>Berat</b> secara konsisten memiliki nilai lebih tinggi di semua indikator risiko "
        "dibandingkan kelompok <b>Minimal</b>. Pola ini mengkonfirmasi bahwa gaya hidup tidak sehat "
        "kurang tidur, kurang gerak, konsumsi alkohol secara bersamaan berkorelasi dengan keparahan depresi. "
        "Meski data cross-sectional tidak membuktikan kausalitas, kekuatan pola ini mendukung "
        "pendekatan intervensi holistik berbasis gaya hidup yang menjadi pondasi produk DepreScan.")
 
    # RINGKASAN EKSEKUTIF

    divider_section(th)
    st.markdown(
        f"<div style='font-size:17px;font-weight:700;color:{th['text']};margin-bottom:16px;'>"
        f"📋 Ringkasan Temuan untuk Pengembangan Produk</div>",
        unsafe_allow_html=True,
    )
    findings = [
        ("🎯", "Target Pengguna Prioritas",
         "Perempuan usia 30–44 tahun, berpendidikan rendah, tinggal sendiri, dan PIR < 1.5 "
         "adalah segmen paling rentan target utama intervensi DepreScan."),
        ("😴", "Tidur sebagai Sinyal Klinis Utama",
         "Tidur < 6 jam DAN > 8 jam sama-sama berisiko. Gangguan tidur terdiagnosis adalah "
         "prediktor gaya hidup terkuat wajib jadi input utama model."),
        ("🍺", "Alkohol = Koping Negatif",
         "Binge drinking berkorelasi signifikan dengan PHQ-9 lebih tinggi. "
         "Edukasi pengurangan alkohol perlu diintegrasikan dalam rekomendasi aplikasi."),
        ("💪", "Aktivitas Fisik Bersifat Protektif",
         "Kelompok tidak aktif memiliki depresi berat lebih tinggi. "
         "Fitur rekomendasi olahraga dapat menjadi differentiator produk DepreScan."),
        ("💰", "Kemiskinan Memperbesar Semua Risiko",
         "PIR < 1.5 berkorelasi kuat dengan depresi klinis pertimbangkan aksesibilitas "
         "harga dan versi gratis/subsidi untuk segmen ini."),
        ("🏠", "Isolasi Sosial Perlu Dideteksi",
         "Tinggal sendiri meningkatkan risiko depresi berat. Pertanyaan tentang situasi sosial "
         "perlu masuk ke dalam kuesioner skrining DepreScan."),
    ]
    cols = st.columns(2, gap="large")
    for i, (icon, title, desc) in enumerate(findings):
        with cols[i % 2]:
            st.markdown(
                f"""<div style="background:{th['card']};border:1px solid {th['border']};
                border-radius:12px;padding:18px 20px;margin-bottom:16px;">
                <div style="font-size:24px;margin-bottom:8px;">{icon}</div>
                <div style="font-size:14px;font-weight:700;color:{th['text']};margin-bottom:6px;">{title}</div>
                <div style="font-size:13px;color:{th['text2']};line-height:1.7;">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    spacer(16)

# MAIN
def main():
    th  = get_theme()
    inject_css(th)
    df  = load_data()
    sel_gender, sel_dep, sel_age = render_sidebar(df)
    dff = apply_filters(df, sel_gender, sel_dep, sel_age)

    page = st.session_state.page
    if page == "overview":
        page_overview(df, dff, th)
    elif page == "demography":
        page_demography(dff, th)
    elif page == "depression":
        page_depression(dff, th)
    elif page == "lifestyle":
        page_lifestyle(dff, th)
    elif page == "business":
        page_business(dff, th)

if __name__ == "__main__":
    main()
