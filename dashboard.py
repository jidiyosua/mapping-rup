import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════════
# CONFIG & BRANDING
# ══════════════════════════════════════════════════════════════════
st.set_page_config(page_title="RUP 2026 vs Realisasi 2025 | Telkomsel Enterprise", layout="wide", page_icon="📊")

RED = "#ED1C24"
DARK_RED = "#B71520"
NAVY = "#1A1A2E"
DARK_BG = "#0F0F1E"
CARD_BG = "#16213E"
GRAY = "#8892A0"
WHITE = "#FFFFFF"
GREEN = "#00C48C"
AMBER = "#FFB800"
LIGHT_GRAY = "#E8EDF2"

COLORS_SEQ = [RED, "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#87CEEB"]

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    .stApp { background-color: #0A0A1A; }
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #E8EDF2;
    }
    
    .main-header {
        background: linear-gradient(135deg, #ED1C24 0%, #B71520 50%, #1A1A2E 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(237, 28, 36, 0.15);
    }
    .main-header h1 {
        color: white;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.8);
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #16213E 0%, #1A1A2E 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-label {
        color: #8892A0;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
        line-height: 1.1;
    }
    .metric-sub {
        color: #8892A0;
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }
    .metric-red .metric-value { color: #ED1C24; }
    .metric-green .metric-value { color: #00C48C; }
    .metric-amber .metric-value { color: #FFB800; }
    
    .section-title {
        color: white;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 1.8rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ED1C24;
        display: inline-block;
    }
    
    .insight-box {
        background: linear-gradient(145deg, rgba(237,28,36,0.08), rgba(26,26,46,0.9));
        border-left: 3px solid #ED1C24;
        border-radius: 0 10px 10px 0;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        font-size: 0.85rem;
        color: #C8CDD5;
    }
    .insight-box strong { color: white; }
    
    .tag-exact {
        background: rgba(0,196,140,0.15);
        color: #00C48C;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tag-partial {
        background: rgba(255,184,0,0.15);
        color: #FFB800;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tag-none {
        background: rgba(136,146,160,0.15);
        color: #8892A0;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A2E 0%, #0F0F1E 100%);
    }
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stMultiSelect label {
        color: #E8EDF2 !important;
        font-weight: 600;
    }
    
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    
    div[data-testid="stExpander"] {
        background: #16213E;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_excel("data_FILLED.xlsx", dtype=str)
    df["Pagu__Rp"] = pd.to_numeric(df["Pagu__Rp"], errors="coerce")
    df["Total_Pelaksanaan_Rp (2025)"] = pd.to_numeric(df["Total_Pelaksanaan_Rp (2025)"], errors="coerce")
    df["Pagu_Rp (2025)"] = pd.to_numeric(df["Pagu_Rp (2025)"], errors="coerce")
    
    # Match status
    def get_match_status(row):
        ket = str(row.get("Keterangan") or "").strip().lower()
        if "partial" in ket:
            return "Partial Match"
        elif row.get("Nama_Pemenang (2025)") and str(row.get("Nama_Pemenang (2025)")).strip():
            return "Exact Match"
        else:
            return "Belum Terealisasi"
    
    df["Match_Status"] = df.apply(get_match_status, axis=1)
    
    # Forward fill for grouped rows (continuation rows have NaN in Paket)
    df["_is_main"] = df["Paket"].notna()
    
    return df

df = load_data()
df_main = df[df["_is_main"]].copy()

# ══════════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔍 Filter Data")
    st.markdown("---")
    
    products = sorted(df_main["Product"].dropna().unique().tolist())
    sel_product = st.multiselect("Produk", products, default=products)
    
    klpds = sorted(df_main["K_L_PD"].dropna().unique().tolist())
    sel_klpd = st.multiselect("K/L/Pemda", klpds, default=klpds)
    
    match_opts = ["Exact Match", "Partial Match", "Belum Terealisasi"]
    sel_match = st.multiselect("Status Realisasi", match_opts, default=match_opts)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#8892A0; font-size:0.7rem; padding:1rem 0;'>
        <strong style='color:#ED1C24;'>Telkomsel Enterprise</strong><br>
        Bid Management — EBPM<br>
        Data Intelligence Dashboard
    </div>
    """, unsafe_allow_html=True)

# Apply filters on main rows
mask = (
    df_main["Product"].isin(sel_product) &
    df_main["K_L_PD"].isin(sel_klpd) &
    df_main["Match_Status"].isin(sel_match)
)
df_filtered_main = df_main[mask]

# Also get all rows (including continuation) for filtered main IDs
filtered_ids = df_filtered_main["ID"].dropna().unique()
df_all_filtered = df[df["ID"].isin(filtered_ids) | (df["ID"].isna() & df.index.isin(
    [i for idx in df_filtered_main.index for i in range(idx, min(idx + 50, len(df))) 
     if not df.loc[i, "_is_main"] or i == idx]
))]

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>📊 Mapping RUP 2026 vs Realisasi 2025</h1>
    <p>Analisis Pencocokan Perencanaan Pengadaan dengan Data Realisasi — Telkomsel Enterprise Bid Management</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# KPI METRICS
# ══════════════════════════════════════════════════════════════════
total_paket = len(df_filtered_main)
total_pagu = df_filtered_main["Pagu__Rp"].sum()
total_realisasi = df[df["ID"].isin(filtered_ids)]["Total_Pelaksanaan_Rp (2025)"].sum()

exact_count = (df_filtered_main["Match_Status"] == "Exact Match").sum()
partial_count = (df_filtered_main["Match_Status"] == "Partial Match").sum()
belum_count = (df_filtered_main["Match_Status"] == "Belum Terealisasi").sum()
match_rate = ((exact_count + partial_count) / total_paket * 100) if total_paket > 0 else 0

has_pemenang = df[df["ID"].isin(filtered_ids)]["Nama_Pemenang (2025)"].dropna().str.strip().ne("").sum()
unique_vendors = df[df["ID"].isin(filtered_ids)]["Nama_Pemenang (2025)"].dropna().str.strip().replace("", pd.NA).dropna().nunique()

def fmt_rp(val):
    if pd.isna(val) or val == 0:
        return "Rp 0"
    if val >= 1e12:
        return f"Rp {val/1e12:.1f} T"
    if val >= 1e9:
        return f"Rp {val/1e9:.1f} M"
    if val >= 1e6:
        return f"Rp {val/1e6:.0f} Jt"
    return f"Rp {val:,.0f}"

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="metric-card metric-red">
        <div class="metric-label">Total Paket RUP</div>
        <div class="metric-value">{total_paket}</div>
        <div class="metric-sub">Paket pengadaan 2026</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Pagu 2026</div>
        <div class="metric-value">{fmt_rp(total_pagu)}</div>
        <div class="metric-sub">Anggaran perencanaan</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card metric-green">
        <div class="metric-label">Match Rate</div>
        <div class="metric-value">{match_rate:.0f}%</div>
        <div class="metric-sub">{exact_count + partial_count} dari {total_paket} paket</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card metric-green">
        <div class="metric-label">Exact Match</div>
        <div class="metric-value">{exact_count}</div>
        <div class="metric-sub">Paket & instansi cocok</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="metric-card metric-amber">
        <div class="metric-label">Partial Match</div>
        <div class="metric-value">{partial_count}</div>
        <div class="metric-sub">Instansi cocok, paket beda</div>
    </div>""", unsafe_allow_html=True)
with c6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Belum Terealisasi</div>
        <div class="metric-value">{belum_count}</div>
        <div class="metric-sub">Peluang baru 2026</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ROW 2: MATCH STATUS + PRODUCT BREAKDOWN
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Distribusi Realisasi & Produk</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.3])

with col_left:
    # Donut chart: Match status
    status_counts = df_filtered_main["Match_Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Jumlah"]
    color_map = {"Exact Match": GREEN, "Partial Match": AMBER, "Belum Terealisasi": GRAY}
    
    fig_donut = go.Figure(go.Pie(
        labels=status_counts["Status"],
        values=status_counts["Jumlah"],
        hole=0.6,
        marker=dict(colors=[color_map.get(s, GRAY) for s in status_counts["Status"]]),
        textinfo="label+value+percent",
        textfont=dict(size=13, family="Plus Jakarta Sans"),
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>"
    ))
    fig_donut.update_layout(
        title=dict(text="Status Pencocokan Realisasi", font=dict(size=15, color=WHITE, family="Plus Jakarta Sans")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=LIGHT_GRAY, family="Plus Jakarta Sans"),
        showlegend=False, height=380, margin=dict(t=50, b=20, l=20, r=20),
        annotations=[dict(text=f"<b>{total_paket}</b><br>Paket", x=0.5, y=0.5, font_size=18, font_color=WHITE, showarrow=False)]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    # Stacked bar: Product vs Match Status
    prod_match = df_filtered_main.groupby(["Product", "Match_Status"]).size().reset_index(name="Jumlah")
    
    fig_bar = px.bar(
        prod_match, x="Product", y="Jumlah", color="Match_Status",
        color_discrete_map=color_map, barmode="stack",
        text="Jumlah"
    )
    fig_bar.update_layout(
        title=dict(text="Realisasi per Produk Telkomsel", font=dict(size=15, color=WHITE, family="Plus Jakarta Sans")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=LIGHT_GRAY, family="Plus Jakarta Sans"),
        xaxis=dict(title="", gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=12)),
        yaxis=dict(title="Jumlah Paket", gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        height=380, margin=dict(t=70, b=20, l=20, r=20)
    )
    fig_bar.update_traces(textposition="inside", textfont_size=12)
    st.plotly_chart(fig_bar, use_container_width=True)

# Insight box
exact_pct = (exact_count / total_paket * 100) if total_paket else 0
partial_pct = (partial_count / total_paket * 100) if total_paket else 0
st.markdown(f"""
<div class="insight-box">
    💡 <strong>{exact_pct:.0f}% paket</strong> memiliki kecocokan penuh (Exact Match) dengan data realisasi 2025, 
    dan <strong>{partial_pct:.0f}%</strong> memiliki kecocokan parsial (instansi & satker sama, nama paket berbeda). 
    Sisanya <strong>{belum_count} paket</strong> merupakan peluang baru yang belum ada realisasi di 2025.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ROW 3: INSTANSI + PAGU ANALYSIS
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🏛️ Analisis per Instansi (K/L/Pemda)</div>', unsafe_allow_html=True)

col_l, col_r = st.columns([1.2, 1])

with col_l:
    inst = df_filtered_main.groupby("K_L_PD").agg(
        Jumlah_Paket=("Paket", "count"),
        Pagu_Total=("Pagu__Rp", "sum"),
        Terealisasi=("Match_Status", lambda x: (x.isin(["Exact Match", "Partial Match"])).sum())
    ).reset_index().sort_values("Jumlah_Paket", ascending=True)
    
    fig_inst = go.Figure()
    fig_inst.add_trace(go.Bar(
        y=inst["K_L_PD"], x=inst["Jumlah_Paket"], orientation="h",
        name="Total Paket", marker_color=NAVY,
        text=inst["Jumlah_Paket"], textposition="inside",
        textfont=dict(color="white", size=11)
    ))
    fig_inst.add_trace(go.Bar(
        y=inst["K_L_PD"], x=inst["Terealisasi"], orientation="h",
        name="Terealisasi", marker_color=RED,
        text=inst["Terealisasi"], textposition="inside",
        textfont=dict(color="white", size=11)
    ))
    fig_inst.update_layout(
        title=dict(text="Jumlah Paket per Instansi", font=dict(size=15, color=WHITE, family="Plus Jakarta Sans")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=LIGHT_GRAY, family="Plus Jakarta Sans"),
        barmode="overlay", height=max(380, len(inst) * 35 + 80),
        xaxis=dict(title="Jumlah Paket", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="", tickfont=dict(size=11)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        margin=dict(t=70, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_inst, use_container_width=True)

with col_r:
    inst_pagu = inst.sort_values("Pagu_Total", ascending=True)
    inst_pagu["Pagu_Label"] = inst_pagu["Pagu_Total"].apply(fmt_rp)
    
    fig_pagu = go.Figure(go.Bar(
        y=inst_pagu["K_L_PD"], x=inst_pagu["Pagu_Total"], orientation="h",
        marker=dict(color=inst_pagu["Pagu_Total"], colorscale=[[0, "#FF6B6B"], [1, RED]]),
        text=inst_pagu["Pagu_Label"], textposition="outside",
        textfont=dict(size=11, color=LIGHT_GRAY)
    ))
    fig_pagu.update_layout(
        title=dict(text="Pagu Anggaran per Instansi (RUP 2026)", font=dict(size=15, color=WHITE, family="Plus Jakarta Sans")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=LIGHT_GRAY, family="Plus Jakarta Sans"),
        height=max(380, len(inst_pagu) * 35 + 80),
        xaxis=dict(title="", gridcolor="rgba(255,255,255,0.05)", showticklabels=False),
        yaxis=dict(title="", tickfont=dict(size=11)),
        margin=dict(t=70, b=20, l=20, r=120),
        showlegend=False
    )
    st.plotly_chart(fig_pagu, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# ROW 4: TOP VENDORS
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🏢 Top Pemenang Realisasi 2025</div>', unsafe_allow_html=True)

df_vendors = df[df["ID"].isin(filtered_ids)].copy()
df_vendors = df_vendors[df_vendors["Nama_Pemenang (2025)"].notna() & (df_vendors["Nama_Pemenang (2025)"].str.strip() != "")]

if len(df_vendors) > 0:
    vendor_agg = df_vendors.groupby("Nama_Pemenang (2025)").agg(
        Jumlah_Transaksi=("Nama_Pemenang (2025)", "count"),
        Total_Nilai=("Total_Pelaksanaan_Rp (2025)", "sum")
    ).reset_index().sort_values("Total_Nilai", ascending=False).head(15)
    
    vendor_agg["Nilai_Label"] = vendor_agg["Total_Nilai"].apply(fmt_rp)
    
    fig_vendor = go.Figure(go.Bar(
        x=vendor_agg["Total_Nilai"],
        y=vendor_agg["Nama_Pemenang (2025)"],
        orientation="h",
        marker=dict(color=RED, line=dict(width=0)),
        text=[f"{row['Nilai_Label']}  ({row['Jumlah_Transaksi']}x)" for _, row in vendor_agg.iterrows()],
        textposition="outside",
        textfont=dict(size=11, color=LIGHT_GRAY)
    ))
    fig_vendor.update_layout(
        title=dict(text="Top 15 Vendor berdasarkan Total Nilai Pelaksanaan", font=dict(size=15, color=WHITE, family="Plus Jakarta Sans")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=LIGHT_GRAY, family="Plus Jakarta Sans"),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
        xaxis=dict(showticklabels=False, gridcolor="rgba(255,255,255,0.05)"),
        height=max(400, len(vendor_agg) * 30 + 100),
        margin=dict(t=60, b=20, l=20, r=140),
        showlegend=False
    )
    st.plotly_chart(fig_vendor, use_container_width=True)
else:
    st.info("Tidak ada data vendor untuk filter yang dipilih.")

# ══════════════════════════════════════════════════════════════════
# ROW 5: STAKEHOLDER BREAKDOWN
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">👥 Distribusi Stakeholder & Metode Pengadaan</div>', unsafe_allow_html=True)

col_s1, col_s2 = st.columns(2)

with col_s1:
    stk = df_filtered_main["Stakeholder"].value_counts().reset_index()
    stk.columns = ["Stakeholder", "Jumlah"]
    fig_stk = go.Figure(go.Pie(
        labels=stk["Stakeholder"], values=stk["Jumlah"],
        marker=dict(colors=[RED, "#FF6B6B", NAVY]),
        textinfo="label+value+percent",
        textfont=dict(size=12, family="Plus Jakarta Sans"),
        hole=0.5
    ))
    fig_stk.update_layout(
        title=dict(text="Pembagian Stakeholder", font=dict(size=15, color=WHITE, family="Plus Jakarta Sans")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=LIGHT_GRAY, family="Plus Jakarta Sans"),
        showlegend=False, height=350, margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_stk, use_container_width=True)

with col_s2:
    metode_data = df_vendors["Metode_Pemilihan (2025)"].dropna().value_counts().reset_index()
    metode_data.columns = ["Metode", "Jumlah"]
    if len(metode_data) > 0:
        fig_met = go.Figure(go.Bar(
            x=metode_data["Metode"], y=metode_data["Jumlah"],
            marker_color=[RED, "#FF6B6B", NAVY, AMBER][:len(metode_data)],
            text=metode_data["Jumlah"], textposition="outside",
            textfont=dict(size=13, color=WHITE)
        ))
        fig_met.update_layout(
            title=dict(text="Metode Pemilihan Realisasi 2025", font=dict(size=15, color=WHITE, family="Plus Jakarta Sans")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=LIGHT_GRAY, family="Plus Jakarta Sans"),
            xaxis=dict(title="", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Jumlah", gridcolor="rgba(255,255,255,0.05)"),
            height=350, margin=dict(t=50, b=20, l=20, r=20), showlegend=False
        )
        st.plotly_chart(fig_met, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# ROW 6: DETAIL TABLE
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📋 Detail Data Paket</div>', unsafe_allow_html=True)

display_cols = [
    "K_L_PD", "Satuan_Kerja", "Paket", "Product", "Pagu__Rp",
    "Match_Status", "Nama_Pemenang (2025)", "Total_Pelaksanaan_Rp (2025)",
    "Nama_Paket (2025)", "Metode_Pemilihan (2025)", "Stakeholder"
]
existing_cols = [c for c in display_cols if c in df_filtered_main.columns]

df_display = df_filtered_main[existing_cols].copy()
df_display.columns = [c.replace("_", " ").replace(" (2025)", " '25") for c in existing_cols]

st.dataframe(
    df_display,
    use_container_width=True,
    height=500,
    column_config={
        "Pagu  Rp": st.column_config.NumberColumn(format="Rp %d"),
        "Total Pelaksanaan Rp '25": st.column_config.NumberColumn(format="Rp %d"),
    }
)

# ══════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; color:#8892A0; font-size:0.75rem; padding:1rem 0;">
    <strong style="color:#ED1C24;">Telkomsel Enterprise</strong> — Bid Management (EBPM) | 
    Data: RUP 2026 & Realisasi INAPROC 2025 | 
    Total {len(df)} baris data ({len(df_main)} paket utama) | 
    Dashboard dibuat oleh Tim Data Intelligence
</div>
""", unsafe_allow_html=True)
