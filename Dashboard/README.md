# DepreScan - Dashboard Analisis Kesehatan Mental NHANES
### Visualisasi Interaktif Data NHANES 2017-2018 untuk Deteksi Risiko Depresi
**Coding Camp 2026 powered by DBS Foundation · Tim CC26-PSU066 · Tema: Healthy Lives & Well-being**

> ⚠️ **Disclaimer:** Hasil DepreScan adalah indikasi awal, **bukan diagnosis klinis**. Jika kamu membutuhkan bantuan segera, hubungi **119 ext. 8** (Kemenkes RI) atau **Into The Light Indonesia: 021-7884-5555**.

---

## Daftar Isi
- [Gambaran Proyek](#gambaran-proyek)
- [Struktur Repositori](#struktur-repositori)
- [Dependensi & Instalasi](#dependensi--instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Arsitektur Kode](#arsitektur-kode)
  - [1. Konfigurasi Halaman & State Management](#1-konfigurasi-halaman--state-management)
  - [2. Sistem Tema (Dark / Light Mode)](#2-sistem-tema-dark--light-mode)
  - [3. Konstanta & Mapping](#3-konstanta--mapping)
  - [4. Load Data & Caching](#4-load-data--caching)
  - [5. Helper Functions](#5-helper-functions)
  - [6. Sidebar & Filter Global](#6-sidebar--filter-global)
  - [7. Halaman Dashboard](#7-halaman-dashboard)
- [Struktur Halaman Dashboard](#struktur-halaman-dashboard)
  - [📊 Ringkasan Utama](#-ringkasan-utama)
  - [👥 Demografi](#-demografi)
  - [🧠 Analisis Depresi](#-analisis-depresi)
  - [🏃 Gaya Hidup & Risiko](#-gaya-hidup--risiko)
  - [💼 Pertanyaan Bisnis](#-pertanyaan-bisnis)
- [Pertanyaan Bisnis & Metode Visualisasi](#pertanyaan-bisnis--metode-visualisasi)
- [Dataset](#dataset)
- [Referensi](#referensi)

---

## Gambaran Proyek

Repository ini berisi **dashboard analitik interaktif** berbasis Streamlit yang memvisualisasikan hasil pipeline data dari dataset NHANES 2017-2018 untuk mengeksplorasi pola kesehatan mental, khususnya depresi berdasarkan skor PHQ-9.

Dashboard ini merupakan komponen **frontend analitik** dari proyek DepreScan, yang dikembangkan secara terpisah dari pipeline data science (lihat repo deprescan-data-science). Input utama dashboard adalah file `Final_Data.csv` output bersih dari pipeline preprocessing yang mengandung **5.088 responden × 78 variabel**.

**Mengapa dashboard terpisah?**  
Pemisahan antara pipeline (`deprescan-data-science`) dan dashboard (`DepreScan-Dashboard`) mengikuti prinsip *separation of concerns* pipeline dapat dijalankan ulang untuk update dataset tanpa menyentuh kode visualisasi, dan sebaliknya.

> 🔗 **Live Demo:** [deprescan-dashboard.streamlit.app](https://deprescan-dashboard.streamlit.app/)  
> 📦 **Pipeline Repo:** [fbrianzy/DepreScan-Utils](https://github.com/fbrianzy/DepreScan-Utils)

---

## Struktur Repositori

```
DepreScan-Dashboard/
│
├── dashboard_nhanes_Final.py    # Entry point seluruh kode dashboard (~2.160 baris)
├── Final_Data.csv               # Dataset input (5.088 baris × 78 kolom)
├── requirements.txt             # Dependensi Python
└── README.md                    # Dokumen ini
```

> **Catatan:** Seluruh logika dashboard diimplementasikan dalam satu file `dashboard_nhanes_Final.py` dengan arsitektur modular berbasis fungsi. Tidak ada file CSS, JS, atau konfigurasi eksternal tema sepenuhnya dikelola via `st.markdown()` dengan CSS injection.

---

## Dependensi & Instalasi

**Prasyarat:** Python ≥ 3.10

```bash
pip install streamlit pandas numpy plotly
```

Atau via `requirements.txt`:

```bash
pip install -r requirements.txt
```

| Library | Versi Direkomendasikan | Digunakan untuk |
|---------|----------------------|-----------------|
| `streamlit` | ≥ 1.32 | Framework UI, session state, sidebar, tabs, metrics |
| `pandas` | ≥ 2.0 | Load CSV, groupby, pivot, melt, value_counts |
| `numpy` | ≥ 1.26 | Normalisasi heatmap, operasi numerik |
| `plotly` | ≥ 5.18 | Seluruh visualisasi interaktif (px + go) |

---

## Cara Menjalankan

### 1. Clone repositori

```bash
git clone https://github.com/FaishalBayuPratama/DepreScan-Dashboard.git
cd DepreScan-Dashboard
```

### 2. Install dependensi

```bash
pip install -r requirements.txt
```

### 3. Pastikan `Final_Data.csv` ada di direktori yang sama

```
DepreScan-Dashboard/
├── dashboard_nhanes_Final.py
└── Final_Data.csv               ← wajib ada di sini
```

Jika belum punya `Final_Data.csv`, jalankan pipeline dari repo deprescan-data-science terlebih dahulu:

```bash
# Di repo deprescan-data-science
python main.py
# Lalu salin output ke sini:
cp data/processed/nhanes_model_ready.csv ../DepreScan-Dashboard/Final_Data.csv
```

### 4. Jalankan dashboard

```bash
streamlit run dashboard_nhanes_Final.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`.

---

## Arsitektur Kode

Seluruh kode berada dalam `dashboard_nhanes_Final.py` (~2.160 baris) yang diorganisasi menjadi blok-blok berikut:

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. PAGE CONFIG & SESSION STATE   (baris 1-22)                      │
│  2. THEME SYSTEM (get_theme)      (baris 25-59)                     │
│  3. CONSTANTS & MAPPINGS          (baris 62-121)                    │
│  4. DATA LOADING (load_data)      (baris 125-138)                   │
│  5. HELPER FUNCTIONS              (baris 142-276)                   │
│  6. SIDEBAR & FILTERS             (baris 278-355)                   │
│  7. PAGE FUNCTIONS                (baris 358-2133)                  │
│     ├── render_top10_heatmap()                                       │
│     ├── page_overview()                                              │
│     ├── page_demography()                                            │
│     ├── page_depression()                                            │
│     ├── page_lifestyle()                                             │
│     └── page_business()                                             │
│  8. MAIN ENTRYPOINT               (baris 2137-2158)                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 1. Konfigurasi Halaman & State Management

```python
st.set_page_config(
    page_title="Dashboard Kesehatan Mental NHANES",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Persistent state antar interaksi user
if "dark" not in st.session_state:
    st.session_state.dark = True      # default: dark mode aktif
if "page" not in st.session_state:
    st.session_state.page = "overview"  # default: halaman pertama
```

Navigasi antar halaman dikendalikan via `st.session_state.page` setiap tombol sidebar memanggil `st.rerun()` untuk me-refresh tampilan tanpa reload penuh. Pendekatan ini dipilih karena Streamlit tidak memiliki built-in router.

---

### 2. Sistem Tema (Dark / Light Mode)

```python
def get_theme() -> dict:
    if st.session_state.dark:
        return {"bg": "#0f1117", "card": "#1a1d27", "accent": "#3b82f6", ...}
    else:
        return {"bg": "#f0f4ff", "card": "#ffffff", "accent": "#3b82f6", ...}
```

Fungsi `get_theme()` mengembalikan dictionary token warna yang digunakan secara konsisten di seluruh komponen:

| Token | Dark Mode | Light Mode | Digunakan Pada |
|-------|-----------|------------|---------------|
| `bg` | `#0f1117` | `#f0f4ff` | Background halaman utama |
| `card` | `#1a1d27` | `#ffffff` | Latar chart, metric container |
| `card2` | `#22263a` | `#e8eeff` | Badge, hover state |
| `text` | `#e2e8f0` | `#1e293b` | Teks utama |
| `text2` | `#94a3b8` | `#475569` | Teks sekunder, insight box |
| `border` | `#2d3748` | `#dde5ff` | Garis pembatas |
| `accent` | `#3b82f6` | `#3b82f6` | Warna aktif, tombol primer |
| `plot_bg` | `#1a1d27` | `#ffffff` | Background canvas Plotly |
| `paper_bg` | `#1a1d27` | `#f0f4ff` | Background paper Plotly |
| `grid` | `#2d3748` | `#e2e8f0` | Gridline chart |
| `insight_bg` | `#1e2a3a` | `#eff6ff` | Latar kotak insight |
| `insight_border` | `#3b82f6` | `#3b82f6` | Garis kiri kotak insight |

Tema diaplikasikan ke Plotly lewat `plo(th)` dan ke komponen Streamlit lewat `inject_css(th)`.

**CSS Injection** dilakukan via `st.markdown(..., unsafe_allow_html=True)` untuk meng-override default Streamlit, mencakup: metric container, button gradient, tab styling, sidebar background, dan font Inter dari Google Fonts.

---

### 3. Konstanta & Mapping

```python
# Urutan tampilan kategori depresi (digunakan di semua chart)
DEP_ORDER = ["Minimal", "Mild", "Moderate", "Moderately Severe", "Severe"]

# Warna konsisten per kategori
DEP_COLORS = {
    "Minimal": "#10b981", "Mild": "#3b82f6", "Moderate": "#f59e0b",
    "Moderately Severe": "#f97316", "Severe": "#ef4444",
}

# Label Bahasa Indonesia untuk display
DEP_LABEL = {"Minimal": "Minimal", "Mild": "Ringan", ..., "Severe": "Berat"}

# Mapping kode numerik NHANES ke label teks
RACE_MAP   = {1.0: "Mexican American", 3.0: "Non-Hispanic White", ...}
EDU_MAP    = {1.0: "< SMP", 2.0: "SMP-SMA awal", ..., 5.0: "Sarjana ke atas"}
MARITAL_MAP = {1.0: "Menikah", 2.0: "Janda/Duda", ..., 6.0: "Hidup Bersama"}

# Kolom yang dikecualikan dari analisis korelasi fitur
EXCLUDED_FEATURES = {"PHQ9_SCORE", "SEQN", "PHQ9_LABEL", "PHQ9_BINARY", "PHQ9_SEVERITY"}
```

Semua mapping ini digunakan konsisten di seluruh halaman untuk memastikan label Bahasa Indonesia tampil seragam tanpa transformasi ad-hoc di masing-masing fungsi chart.

---

### 4. Load Data & Caching

```python
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("Final_Data.csv")
    df["gender_label"]  = df["GENDER"].map({1.0: "Laki-laki", 2.0: "Perempuan"})
    df["edu_label"]     = df["EDUCATION"].map(EDU_MAP)
    df["race_label"]    = df["RACE"].map(RACE_MAP)
    df["marital_label"] = df["MARITAL"].map(MARITAL_MAP)
    df["pa_label"]      = df["PA_CATEGORY"].map(PA_LABEL)
    return df
```

Decorator `@st.cache_data` memastikan CSV hanya dibaca dari disk sekali seluruh proses berikutnya menggunakan objek DataFrame yang di-cache di memori. Kolom label teks ditambahkan saat load (bukan per-chart) sehingga tidak ada overhead berulang.

**Input:** `Final_Data.csv` 5.088 baris × 78 kolom  
**Output kolom tambahan:** `gender_label`, `edu_label`, `race_label`, `marital_label`, `pa_label`

---

### 5. Helper Functions

Empat fungsi utilitas yang dipakai di seluruh halaman:

#### `plo(th, title, height)` Layout Plotly Standar
```python
def plo(th, title="", height=380) -> dict:
    """Mengembalikan dict layout Plotly yang tema-aware.
    Digunakan via fig.update_layout(**plo(th, "Judul Chart", 340))
    """
```
Menstandarisasi margin, warna background, font, dan gridline semua chart agar konsisten dengan tema aktif.

#### `insight(th, text)` Kotak Interpretasi
```python
def insight(th, text: str):
    """Render kotak biru (💡 Insight:) di bawah setiap chart."""
```
Setiap chart selalu diikuti kotak insight berisi interpretasi otomatis berbasis nilai aktual dari data yang difilter. Teks insight dibangun menggunakan f-string dengan nilai yang dihitung dinamis (bukan teks statis).

#### `chart_title(th, text)` Label Chart
```python
def chart_title(th, text: str):
    """Render judul chart dengan font 13px semi-bold, tema-aware."""
```

#### `section_header(title, subtitle)` Judul Halaman
```python
def section_header(title: str, subtitle: str = ""):
    """Render heading halaman berukuran 24px bold + subtitle 13px abu-abu."""
```

---

### 6. Sidebar & Filter Global

```python
def render_sidebar(df) -> tuple[str, list, tuple]:
    """Render sidebar navigasi + filter, return (sel_gender, sel_dep, sel_age)."""
```

Sidebar berisi dua bagian terpisah:

**Navigasi Halaman** 5 tombol dengan logika aktif/non-aktif:
```python
for key, label in pages:
    active = (st.session_state.page == key)
    if st.button(label, type="primary" if active else "secondary"):
        st.session_state.page = key
        st.rerun()
```

**Filter Data Global** (diaplikasikan ke semua halaman):

| Filter | Widget | Default |
|--------|--------|---------|
| Jenis Kelamin | `st.selectbox` | "Semua" |
| Tingkat Depresi | `st.multiselect` | Semua 5 kategori |
| Rentang Usia | `st.slider` | [min, max] dari data |
| Mode Gelap | `st.toggle` | Aktif |

Filter diterapkan via fungsi `apply_filters()`:
```python
def apply_filters(df, sel_gender, sel_dep, sel_age) -> pd.DataFrame:
    dff = df.copy()
    if sel_gender != "Semua":
        dff = dff[dff["gender_label"] == sel_gender]
    if sel_dep:
        dff = dff[dff["PHQ9_SEVERITY"].isin(sel_dep)]
    dff = dff[(dff["AGE"] >= sel_age[0]) & (dff["AGE"] <= sel_age[1])]
    return dff
```

`dff` (filtered DataFrame) diteruskan ke semua fungsi halaman semua chart berjalan di atas subset yang sama.

---

### 7. Halaman Dashboard

Setiap halaman diimplementasikan sebagai fungsi independen yang menerima `(dff, th)` sebagai argumen. Fungsi `page_overview` juga menerima `df` (unfiltered) untuk menampilkan total responden.

```python
def main():
    th  = get_theme()
    inject_css(th)
    df  = load_data()
    sel_gender, sel_dep, sel_age = render_sidebar(df)
    dff = apply_filters(df, sel_gender, sel_dep, sel_age)

    page = st.session_state.page
    if   page == "overview":   page_overview(df, dff, th)
    elif page == "demography": page_demography(dff, th)
    elif page == "depression": page_depression(dff, th)
    elif page == "lifestyle":  page_lifestyle(dff, th)
    elif page == "business":   page_business(dff, th)
```

---

## Struktur Halaman Dashboard

### 📊 Ringkasan Utama
**Fungsi:** `page_overview(df, dff, th)`

| Komponen | Tipe Chart | Variabel |
|----------|-----------|----------|
| Banner filter aktif | Markdown HTML | `n_filt` / `n_total` |
| 5 KPI metrics | `st.metric` | AGE mean, PHQ9 mean, % Minimal, % Severe+ |
| Komposisi tingkat depresi | Donut chart `go.Pie` | `PHQ9_SEVERITY` |
| Distribusi gender | Donut chart `go.Pie` | `GENDER` |
| Sebaran kelompok usia | Bar chart `px.bar` | `AGE_GROUP` |
| Rata-rata PHQ-9 per level | Bar chart `px.bar` + warna per kategori | `PHQ9_SEVERITY`, `PHQ9_SCORE` |
| Distribusi pendidikan | Horizontal bar `px.bar` | `EDUCATION` |
| **Top 10 Fitur Heatmap** | `px.imshow` + anotasi nilai | Korelasi Pearson vs PHQ9_SCORE |

**Top 10 Heatmap Detail Teknis:**
```python
# 1. Hitung korelasi semua fitur numerik vs PHQ9_SCORE
corr_with_phq = df[feature_cols + ["PHQ9_SCORE"]].dropna().corr()["PHQ9_SCORE"]

# 2. Ambil 10 fitur dengan |r| tertinggi
top10_cols = corr_with_phq.abs().sort_values(ascending=False).head(10).index.tolist()

# 3. Hitung rata-rata nilai per (fitur × level depresi)
# 4. Normalisasi per baris ke [0, 1] agar gradasi warna sebanding antar fitur
hm_norm = hm_df.apply(lambda r: (r - r.min()) / (r.max() - r.min() + 1e-9), axis=1)

# 5. Render dengan color_continuous_scale="RdYlGn_r" + anotasi nilai asli
```

---

### 👥 Demografi
**Fungsi:** `page_demography(dff, th)`

Diorganisasi dalam **4 tab** (`st.tabs`):

| Tab | Isi | Chart Types |
|-----|-----|-------------|
| 👫 Jenis Kelamin | PHQ-9 rata-rata, stacked bar %, grouped bar absolut | `px.bar`, `go.Pie` |
| 🎓 Pendidikan | PHQ-9 per jenjang, % depresi sedang-berat, stacked 100% | `px.bar` horizontal |
| 🎂 Kelompok Usia | Line trend PHQ-9, % berat per usia, stacked 100% | `px.line`, `px.bar` |
| 🌍 Ras & Status | PHQ-9 per ras, PHQ-9 per status pernikahan, donut tinggal sendiri | `px.bar`, `go.Pie` |

---

### 🧠 Analisis Depresi
**Fungsi:** `page_depression(dff, th)`

Diorganisasi dalam **3 tab**:

| Tab | Isi | Chart Types |
|-----|-----|-------------|
| 📊 Distribusi Skor | Histogram PHQ-9 total + overlay per kategori, funnel chart | `px.histogram`, `go.Funnel` |
| 🔢 Item PHQ-9 | Distribusi N_SEVERE_ITEMS, rata-rata per level, DPQ100 per level | `px.bar` |
| 🔗 Hubungan Variabel | Scatter AGE vs PHQ-9 + trendline OLS, horizontal bar korelasi Pearson | `px.scatter`, `go.Bar` |

**Scatter plot dengan OLS trendline:**
```python
fig = px.scatter(
    samp, x="AGE", y="PHQ9_SCORE",
    color="PHQ9_SEVERITY",
    color_discrete_map=DEP_COLORS,
    trendline="ols",          # requires statsmodels
    opacity=0.55,
)
```

---

### 🏃 Gaya Hidup & Risiko
**Fungsi:** `page_lifestyle(dff, th)`

Diorganisasi dalam **4 tab**:

| Tab | Fitur yang Dianalisis | Visualisasi Utama |
|-----|-----------------------|-------------------|
| 🍺 Alkohol | `ALCOHOL_RISK_SCORE`, `BINGE_DRINKER`, `HEAVY_DRINKER` | Bar per level depresi, grouped bar binge vs heavy |
| 💪 Aktivitas Fisik | `PA_CATEGORY`, `TOTAL_MET_MIN`, `SEDENTARY_HOURS` | Bar distribusi PA, bar MET per level, stacked 100% |
| 😴 Tidur | `AVG_SLEEP_HOURS`, `SLEEP_RISK_SCORE`, `SLEEP_DISORDERED`, `SLEEP_APNEA_RISK` | Bar jam tidur per level, line risiko tidur, grouped bar gangguan |
| ⚠️ Indeks Risiko | `TOTAL_RISK_COMPOSITE` | Bar distribusi skor komposit, line rata-rata per level, grouped bar 3 komponen (dinormalisasi 0-1) |

**Normalisasi komponen risiko untuk perbandingan skala berbeda:**
```python
for col in risk_cols:
    mn, mx = risk_dep[col].min(), risk_dep[col].max()
    risk_dep[col + "_norm"] = (risk_dep[col] - mn) / (mx - mn + 1e-9)
```

---

### 💼 Pertanyaan Bisnis
**Fungsi:** `page_business(dff, th)`

Lihat bagian [Pertanyaan Bisnis & Metode Visualisasi](#pertanyaan-bisnis--metode-visualisasi) di bawah.

---

## Pertanyaan Bisnis & Metode Visualisasi

Dashboard menjawab **3 pertanyaan utama** yang masing-masing memiliki sub-pertanyaan berbasis data.

---

### 🎯 Pertanyaan Utama A Siapa yang paling rentan mengalami depresi?

#### A1 · Apakah ada perbedaan skor PHQ-9 antara laki-laki dan perempuan?

| Visualisasi | Variabel | Metode |
|-------------|----------|--------|
| Bar rata-rata PHQ-9 per gender | `gender_label`, `PHQ9_SCORE` | `groupby().mean()` |
| Bar % depresi berat+ per gender | `gender_label`, `PHQ9_SEVERITY` | `apply(lambda: isin().mean() * 100)` |

Didukung oleh uji hipotesis A/B Testing pipeline (Mann-Whitney U, **r = 0.156, p < 0.001**).

#### A2 · Apakah yang tinggal sendiri memiliki skor PHQ-9 lebih tinggi?

| Visualisasi | Variabel | Metode |
|-------------|----------|--------|
| Bar rata-rata PHQ-9: sendiri vs bersama | `LIVING_ALONE`, `PHQ9_SCORE` | `groupby().mean()` |
| Donut distribusi depresi sendiri | `LIVING_ALONE==1`, `PHQ9_SEVERITY` | `value_counts().reindex(DEP_ORDER)` |
| Donut distribusi depresi bersama | `LIVING_ALONE==0`, `PHQ9_SEVERITY` | `value_counts().reindex(DEP_ORDER)` |

Didukung oleh uji A/B Testing pipeline (Mann-Whitney U, **r = 0.162, p < 0.001**).

#### A3 · Apakah kemiskinan relatif (PIR < 1.5) berkaitan dengan depresi lebih tinggi?

| Visualisasi | Variabel | Metode |
|-------------|----------|--------|
| Bar rata-rata PHQ-9 per kelompok PIR | `PIR_GROUP` (4 bin: <1.0, 1.0-1.5, 1.5-3.0, >3.0) | `pd.cut()` + `groupby().mean()` |
| Bar % depresi berat per kelompok PIR | `PIR_GROUP`, `PHQ9_SEVERITY` | `apply(lambda: isin().mean() * 100)` |

Didukung oleh uji A/B Testing pipeline (Chi-square, **V = 0.090, p < 0.001**).

---

### 🏃 Pertanyaan Utama B Apakah gaya hidup tidak sehat meningkatkan risiko depresi?

#### B1 · Apakah tidur < 6 jam berkaitan dengan skor PHQ-9 lebih tinggi?

```python
# Binning durasi tidur menjadi 3 kategori
dff["SLEEP_CAT"] = pd.cut(
    dff["AVG_SLEEP_HOURS"],
    bins=[-0.01, 5.99, 7.99, 999],
    labels=["Kurang (< 6 jam)", "Normal (6-8 jam)", "Berlebih (> 8 jam)"],
)
```

| Visualisasi | Output |
|-------------|--------|
| Bar rata-rata PHQ-9 per kategori tidur | PHQ-9 Kurang vs Normal vs Berlebih |
| Stacked bar komposisi depresi per kategori tidur | % per tingkat depresi di tiap bin tidur |

Didukung oleh uji A/B Testing pipeline (Mann-Whitney U, **r = 0.159, p < 0.001**).

#### B2 · Apakah yang tidak memenuhi panduan aktivitas fisik WHO memiliki depresi lebih tinggi?

Panduan WHO: ≥ 150 menit aktivitas moderat atau ≥ 75 menit aktivitas berat per minggu, diimplementasikan sebagai `PA_CATEGORY` (Active / Insufficiently Active / Inactive).

| Visualisasi | Variabel |
|-------------|----------|
| Stacked 100% bar komposisi depresi per PA_CATEGORY | `PA_CATEGORY`, `PHQ9_SEVERITY` |
| Bar % depresi berat per PA_CATEGORY | `PA_CATEGORY`, `PHQ9_SEVERITY` |

Didukung oleh uji A/B Testing pipeline (Mann-Whitney U, **r = 0.066, p < 0.001**).

#### B3 · Apakah binge drinking berkaitan dengan skor PHQ-9 lebih tinggi?

| Visualisasi | Variabel |
|-------------|----------|
| Bar rata-rata PHQ-9: binge vs bukan | `BINGE_DRINKER`, `PHQ9_SCORE` |
| Bar % depresi berat: binge vs bukan | `BINGE_DRINKER`, `PHQ9_SEVERITY` |

Didukung oleh uji A/B Testing pipeline (Mann-Whitney U, **r = 0.208, p < 0.001**).

---

### 🔍 Pertanyaan Utama C Apa perbedaan nyata antara kelompok Minimal vs Berat?

Perbandingan komprehensif rata-rata semua indikator risiko gaya hidup antara dua kutub tingkat depresi:

```python
minimal_df = dff[dff["PHQ9_SEVERITY"] == "Minimal"]
severe_df  = dff[dff["PHQ9_SEVERITY"] == "Severe"]

compare_rows = [
    {"Indikator": "Risiko Alkohol",   "Minimal": minimal_df["ALCOHOL_RISK_SCORE"].mean(), ...},
    {"Indikator": "Risiko Tidur",     "Minimal": minimal_df["SLEEP_RISK_SCORE"].mean(),   ...},
    {"Indikator": "Jam Sedentary",    "Minimal": minimal_df["SEDENTARY_HOURS"].mean(),     ...},
    {"Indikator": "Risiko Komposit",  "Minimal": minimal_df["TOTAL_RISK_COMPOSITE"].mean(),...},
]
```

Ditampilkan sebagai **grouped bar chart** hijau (Minimal) vs merah (Berat) per indikator.

---

### Ringkasan Temuan (Eksekutif Summary)

Dashboard diakhiri dengan 6 kartu temuan untuk keputusan pengembangan produk:

| # | Temuan | Implikasi Produk |
|---|--------|-----------------|
| 🎯 | Perempuan 30-44 tahun, PIR < 1.5, tinggal sendiri paling rentan | Target segmen utama DepreScan |
| 😴 | Gangguan tidur terdiagnosis = prediktor terkuat (effect size Medium, r = 0.442) | Pertanyaan tidur wajib ada di kuesioner |
| 🍺 | Binge drinking naik seiring depresi berat | Tambahkan edukasi alkohol di rekomendasi |
| 💪 | Kelompok tidak aktif memiliki depresi berat lebih tinggi | Fitur rekomendasi olahraga |
| 💰 | PIR < 1.5 → depresi klinis lebih tinggi secara signifikan | Pertimbangkan versi gratis/subsidi |
| 🏠 | Tinggal sendiri meningkatkan risiko | Tambah pertanyaan situasi sosial ke skrining |

---

## Dataset

**Input:** `Final_Data.csv` output langsung dari pipeline [DepreScan-Utils](https://github.com/fbrianzy/DepreScan-Utils)

| Properti | Nilai |
|----------|-------|
| Jumlah baris | 5.088 responden |
| Jumlah kolom | 78 variabel |
| Sumber asli | NHANES 2017-2018 (5 modul XPT) |
| Target variabel | `PHQ9_SCORE` (0-27), `PHQ9_SEVERITY` (5 kelas), `PHQ9_BINARY` (0/1) |
| Distribusi kelas | Minimal 74.4% · Mild 16.5% · Moderate 5.7% · Mod.Severe 2.5% · Severe 0.8% |

Kolom-kolom kunci yang digunakan dashboard:

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `PHQ9_SCORE` | int | Skor total PHQ-9 (0-27) |
| `PHQ9_SEVERITY` | str | 5 kategori depresi |
| `PHQ9_BINARY` | int | 1 jika PHQ9_SCORE ≥ 10 |
| `GENDER` | float | 1=Laki-laki, 2=Perempuan |
| `AGE` | float | Usia dalam tahun |
| `AGE_GROUP` | str | Kelompok usia (18-29, ..., 75+) |
| `EDUCATION` | float | Jenjang pendidikan (1-5) |
| `RACE` | float | Kode ras/etnis NHANES |
| `MARITAL` | float | Status pernikahan (1-6) |
| `LIVING_ALONE` | int | 1 jika tidak memiliki pasangan |
| `PIR` | float | Poverty Income Ratio |
| `AVG_SLEEP_HOURS` | float | Rata-rata jam tidur/malam |
| `SLEEP_RISK_SCORE` | int | Skor risiko tidur (0-4) |
| `SLEEP_DISORDERED` | int | 1 jika diagnosis gangguan tidur |
| `SLEEP_APNEA_RISK` | int | 1 jika risiko sleep apnea |
| `PA_CATEGORY` | str | Active / Insufficiently Active / Inactive |
| `TOTAL_MET_MIN` | float | Total MET menit/minggu |
| `SEDENTARY_HOURS` | float | Jam duduk/hari |
| `ALCOHOL_RISK_SCORE` | int | Skor risiko alkohol (0-3) |
| `BINGE_DRINKER` | int | 1 jika binge drinker |
| `HEAVY_DRINKER` | int | 1 jika heavy drinker |
| `TOTAL_RISK_COMPOSITE` | float | Skor risiko komposit tertimbang |
| `N_SEVERE_ITEMS` | int | Jumlah item PHQ-9 dengan skor ≥ 2 |
| `DPQ100` | float | Item ke-10 PHQ (pikiran menyakiti diri) |

---

## Referensi

1. Kroenke, K., Spitzer, R. L., & Williams, J. B. W. (2001). [The PHQ-9: Validity of a brief depression severity measure. *Journal of General Internal Medicine, 16*(9), 606-613.](https://pmc.ncbi.nlm.nih.gov/articles/PMC1495268/)
2. National Center for Health Statistics. (2020). *National Health and Nutrition Examination Survey Data 2017-2018*. CDC/NCHS. https://wwwn.cdc.gov/nchs/nhanes/
3. World Health Organization. (2020). *WHO guidelines on physical activity and sedentary behaviour*. WHO Press.
4. Cappuccio, F. P., et al. (2010). [Sleep duration predicts cardiovascular outcomes. *European Heart Journal, 32*(12), 1484-1492.](https://pubmed.ncbi.nlm.nih.gov/21300732/)

---

<div align="center">

**DepreScan · CC26-PSU066 · Coding Camp 2026 powered by DBS Foundation**

</div>
