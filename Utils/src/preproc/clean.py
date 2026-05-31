import warnings
import numpy as np
import pandas as pd

from src.utils.sentinel import *

warnings.filterwarnings("ignore")

def clean_demo(df_raw):
    """
    CLEAN — Demographics (DEMO_J).

    Variabel yang dipertahankan dan logika cleaning:

    SEQN       : ID respondent — key join, tidak diubah
    RIAGENDR   : 1=Male, 2=Female — bersih (tidak ada missing)
    RIDAGEYR   : Usia dalam tahun. Usia <1 tahun di-encode sebagai
                 sentinel-0 (0.0 setelah decode). Kita filter usia ≥18
                 karena PHQ-9 ditujukan untuk dewasa.
    RIDRETH3   : Ras/Etnis 6-kategori — bersih
    DMDEDUC2   : Pendidikan (adults 20+). Kode 7/9 = Refused/DK → NaN.
                 NaN pada usia <20 adalah VALID (DMDEDUC3 digunakan untuk
                 remaja) — kita biarkan NaN pada under-20 dan imputasi median
                 pada 20+.
    DMDMARTL   : Status perkawinan (adults 20+). Kode 77=Refused → NaN.
    INDHHIN2   : Pendapatan rumah tangga. Kode 77/99 → NaN.
    INDFMPIR   : Poverty Income Ratio (rasio kontinu 0-5). Sentinel-0 valid
                 (artinya PIR sangat rendah). 5.0 adalah cap atas.
    WTMEC2YR   : Sampling weight (untuk weighted analysis, opsional).

    Returns:
        pd.DataFrame dengan kolom yang sudah dibersihkan dan direname.
    """
    df = df_raw.copy()

    # Decode sentinel
    sentinel_cols = ["RIDAGEYR", "INDFMPIR"]
    for col in sentinel_cols:
        if col in df.columns:
            df[col] = decode_sentinel_zero(df[col])

    # Replace Refused/DK
    df["DMDEDUC2"] = replace_nhanes_missing(df["DMDEDUC2"])
    df["DMDMARTL"] = replace_nhanes_missing(df["DMDMARTL"], [77])
    df["INDHHIN2"] = replace_nhanes_missing(df["INDHHIN2"], [77, 99])

    # Filter adults ≥18
    # PHQ-9 dalam NHANES hanya valid untuk 18+
    df = df[df["RIDAGEYR"] >= 18].copy()
    print(f"  [clean_demo] Filter adults 18+: {len(df):,} rows retained")

    # Pilih dan rename kolom
    cols_keep = {
        "SEQN":     "SEQN",
        "RIAGENDR": "GENDER",
        "RIDAGEYR": "AGE",
        "RIDRETH3": "RACE",
        "DMDEDUC2": "EDUCATION",
        "DMDMARTL": "MARITAL",
        "INDHHIN2": "INCOME_CAT",
        "INDFMPIR": "PIR",
        "WTMEC2YR": "WEIGHT_MEC",
    }
    df = df[[c for c in cols_keep if c in df.columns]].rename(columns=cols_keep)

    # Verifikasi tidak ada duplikat SEQN
    assert df["SEQN"].nunique() == len(df), "Duplikat SEQN ditemukan di DEMO_J!"

    print(f"  [clean_demo] Final shape: {df.shape}")
    return df

def clean_dpq(df_raw):
    """
    CLEAN — Depression Screener PHQ-9 (DPQ_J).

    PHQ-9 (Patient Health Questionnaire-9) adalah instrumen skrining
    depresi terstandarisasi. 9 item pertama (DPQ010–DPQ090) masing-masing
    dinilai 0–3 (0=Not at all, 3=Nearly every day). Total skor 0–27.

    Kode 7=Refused, 9=Don't know → NaN.
    Sentinel-0 (5.397605e-79) → 0 (artinya "Not at all").

    Strategi missing:
    - Jika semua 9 item NaN → drop (tidak ada informasi)
    - Jika sebagian NaN (≤4 item) → imputasi dengan median item yang ada
      (pendekatan konservatif sesuai pedoman scoring PHQ-9)
    - Jika >4 item NaN → drop (skor tidak reliable)

    DPQ100 (tingkat kesulitan fungsional) dipertahankan sebagai fitur
    tambahan tapi tidak masuk ke PHQ-9 total score.

    Returns:
        pd.DataFrame dengan kolom DPQ010-DPQ090 (decoded), DPQ100, SEQN.
    """
    df = df_raw.copy()

    # Decode semua item PHQ-9
    phq_cols = PHQ9_ITEMS + ["DPQ100"]
    for col in phq_cols:
        if col in df.columns:
            df[col] = decode_column(df[col])

    # Count missing per row
    df["_n_missing_phq"] = df[PHQ9_ITEMS].isnull().sum(axis=1)

    before = len(df)

    # Drop jika semua item missing
    df = df[df["_n_missing_phq"] < 9].copy()
    print(f"  [clean_dpq] Drop all-missing PHQ: {before - len(df)} rows dropped")

    # Drop jika >4 item missing
    before2 = len(df)
    df = df[df["_n_missing_phq"] <= 4].copy()
    print(f"  [clean_dpq] Drop >4 missing PHQ: {before2 - len(df)} rows dropped")

    # Imputasi partial missing dengan median per-item
    for col in PHQ9_ITEMS:
        med = df[col].median()
        n_imp = df[col].isnull().sum()
        if n_imp > 0:
            df[col] = df[col].fillna(med)
            print(f"  [clean_dpq] Imputed {n_imp} missing in {col} with median={med:.1f}")

    df = df.drop(columns=["_n_missing_phq"])
    df = df[["SEQN"] + phq_cols].copy()

    print(f"  [clean_dpq] Final shape: {df.shape}")
    return df


def clean_alq(df_raw):
    """
    CLEAN — Alcohol Use Questionnaire (ALQ_J).

    Alur logika kuesioner NHANES ALQ (2017-2018):
    ┌─────────────────────────────────────────────────────────────────┐
    │ ALQ111: Pernah minum ≥12 drinks sepanjang hidup?                │
    │   2=No → SKIP semua → alcohol_ever=0, semua metrics=0           │
    │   1=Yes → lanjut ke ALQ121                                      │
    │                                                                 │
    │ ALQ121: Seberapa sering minum past 12 months?                   │
    │   0=Never past year → alcohol_current=0, current metrics=0      │
    │   1-10=Frequency code → lanjut ke ALQ130                        │
    │                                                                 │
    │ ALQ130: Avg drinks/day on drinking days (1-15+)                 │
    │ ALQ151: Binge drink past year? 1=Yes, 2=No                      │
    │ ALQ170: # drinks on occasions past 30 days                      │
    └─────────────────────────────────────────────────────────────────┘

    Kode khusus:
    - ALQ121=0: "Never in past 12 months" (tetap current drinker = 0)
    - ALQ130 nilai 777/999 → NaN; nilai ≥15 dianggal valid (heavy drinker)

    Returns:
        pd.DataFrame bersih dengan kolom ALQ111, ALQ121, ALQ130,
        ALQ151, SEQN.
    """
    df = df_raw.copy()

    # Decode sentinel (ALQ121=0 adalah valid "never")
    for col in ["ALQ121", "ALQ142", "ALQ270", "ALQ280", "ALQ290", "ALQ170"]:
        if col in df.columns:
            df[col] = decode_sentinel_zero(df[col])

    # Replace Refused/DK
    df["ALQ111"] = replace_nhanes_missing(df["ALQ111"], [7, 9])
    df["ALQ121"] = replace_nhanes_missing(df["ALQ121"], [77, 99])
    df["ALQ130"] = replace_nhanes_missing(df["ALQ130"], [777, 999])
    df["ALQ151"] = replace_nhanes_missing(df["ALQ151"], [7, 9])

    # Isi ALQ111=2 (never drinker) → ALQ121=0, ALQ130=0
    mask_never = df["ALQ111"] == 2
    df.loc[mask_never, "ALQ121"] = 0.0
    df.loc[mask_never, "ALQ130"] = 0.0
    df.loc[mask_never, "ALQ151"] = 2.0  # No binge

    # ALQ121=0 (no drinks past year) → ALQ130=0
    mask_no_year = df["ALQ121"] == 0
    df.loc[mask_no_year, "ALQ130"] = 0.0

    keep = ["SEQN", "ALQ111", "ALQ121", "ALQ130", "ALQ151"]
    df = df[[c for c in keep if c in df.columns]].copy()

    print(f"  [clean_alq] Final shape: {df.shape}")
    return df


def clean_paq(df_raw):
    """
    CLEAN — Physical Activity Questionnaire (PAQ_J).

    Struktur PAQ 2017-2018 mengikuti GPAQ (Global Physical Activity
    Questionnaire). Terdapat 5 domain aktivitas, masing-masing dengan
    pertanyaan "ya/tidak" dan jika ya, frekuensi & durasi.

    Domain:
    1. Vigorous work:     PAQ605 (Y/N), PAQ610 (days/wk), PAD615 (min/day)
    2. Moderate work:     PAQ620 (Y/N), PAQ625 (days/wk), PAD630 (min/day)
    3. Walk/cycle:        PAQ635 (Y/N), PAQ640 (days/wk), PAD645 (min/day)
    4. Vigorous leisure:  PAQ650 (Y/N), PAQ655 (days/wk), PAD660 (min/day)
    5. Moderate leisure:  PAQ665 (Y/N), PAQ670 (days/wk), PAD675 (min/day)
    6. Sedentary:         PAD680 (min/day, 9999=DK)

    Logika skip: jika PAQ605=2 (No), maka PAQ610/PAD615 seharusnya NaN
    (di-skip oleh interviewer). Kita isi NaN tersebut dengan 0.

    PAD680 (sedentary): nilai 9999 = "Don't know" → NaN, lalu imputasi median.

    Returns:
        pd.DataFrame bersih.
    """
    df = df_raw.copy()

    # Decode Refused/DK pada Y/N fields
    yn_cols = ["PAQ605","PAQ620","PAQ635","PAQ640","PAQ650","PAQ655","PAQ665","PAQ670"]
    for col in yn_cols:
        if col in df.columns:
            df[col] = replace_nhanes_missing(df[col], [9])

    # Decode duration cols (sentinel-0 tidak mungkin untuk durasi)
    dur_cols = ["PAD615","PAD630","PAD645","PAD660","PAD675"]
    for col in dur_cols:
        if col in df.columns:
            df[col] = replace_nhanes_missing(df[col], [9999])

    # Sedentary: 9999=DK → NaN
    if "PAD680" in df.columns:
        df["PAD680"] = df["PAD680"].replace(9999, np.nan)
        df["PAD680"] = decode_sentinel_zero(df["PAD680"])

    # Logika skip: jika domain = "No", set durasi = 0
    skip_pairs = [
        ("PAQ605", ["PAD615"]),
        ("PAQ620", ["PAD630"]),
        ("PAQ635", ["PAD645"]),
        ("PAQ650", ["PAD660"]),
        ("PAQ665", ["PAD675"]),
    ]
    for yn_col, dur_list in skip_pairs:
        if yn_col in df.columns:
            mask_no = df[yn_col] == 2  # 2=No
            for dur_col in dur_list:
                if dur_col in df.columns:
                    df.loc[mask_no, dur_col] = df.loc[mask_no, dur_col].fillna(0.0)

    keep = ["SEQN","PAQ605","PAQ620","PAQ635","PAQ650","PAQ665",
            "PAD615","PAD630","PAD645","PAD660","PAD675","PAD680"]
    df = df[[c for c in keep if c in df.columns]].copy()

    # Imputasi sedentary dengan median
    med_sed = df["PAD680"].median()
    n_imp = df["PAD680"].isnull().sum()
    df["PAD680"] = df["PAD680"].fillna(med_sed)
    print(f"  [clean_paq] Imputed {n_imp} sedentary NaN with median={med_sed:.0f} min")
    print(f"  [clean_paq] Final shape: {df.shape}")
    return df


def clean_slq(df_raw):
    """
    CLEAN — Sleep Questionnaire (SLQ_J).

    Variabel utama:
    - SLD012: Weekday sleep hours (kontinu, range 2-14)
    - SLD013: Weekend sleep hours (kontinu, range 2-14)
    - SLQ030: Snoring frequency (0-3, 7/9 → NaN)
    - SLQ040: Snorting/stop breathing (0-3, 7/9 → NaN)
    - SLQ050: Told doctor sleep trouble? 1=Yes, 2=No (9→NaN)
    - SLQ120: Unrested feeling frequency (0-4, 9→NaN)

    SLD012/SLD013 adalah derived variables (dihitung dari waktu tidur dan
    bangun yang dilaporkan responden) sehingga lebih reliable dibanding
    SLQ300/SLQ310 (raw time strings).

    Outlier: nilai SLD012/SLD013 < 2 jam atau > 16 jam sangat tidak mungkin
    secara biologis → cap pada [2, 16].

    Returns:
        pd.DataFrame bersih.
    """
    df = df_raw.copy()

    # Decode sentinel pada SLQ030, SLQ040, SLQ120 (0 = valid "never")
    for col in ["SLQ030","SLQ040","SLQ120"]:
        if col in df.columns:
            df[col] = decode_sentinel_zero(df[col])

    # Replace Refused/DK
    for col in ["SLQ030","SLQ040"]:
        df[col] = replace_nhanes_missing(df[col], [7, 9])
    df["SLQ050"] = replace_nhanes_missing(df["SLQ050"], [9])
    df["SLQ120"] = replace_nhanes_missing(df["SLQ120"], [9])

    # Cap outlier sleep hours [2, 16]
    for col in ["SLD012","SLD013"]:
        if col in df.columns:
            before = df[col].isnull().sum()
            df[col] = df[col].clip(lower=2, upper=16)
            # Outlier di luar rentang BISA dibiarkan setelah clipping
            # Imputasi NaN dengan median
            med = df[col].median()
            df[col] = df[col].fillna(med)
            after = df[col].isnull().sum()
            print(f"  [clean_slq] {col}: {before} NaN imputed with median={med:.1f}")

    # Imputasi ordinal dengan mode
    for col in ["SLQ030","SLQ040","SLQ120"]:
        if col in df.columns:
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                n_imp = df[col].isnull().sum()
                df[col] = df[col].fillna(mode_val[0])

    keep = ["SEQN","SLD012","SLD013","SLQ030","SLQ040","SLQ050","SLQ120"]
    df = df[[c for c in keep if c in df.columns]].copy()

    print(f"  [clean_slq] Final shape: {df.shape}")
    return df


def clean_all(raw_dfs):
    """
    Jalankan semua fungsi clean_* dan kembalikan dict DataFrame bersih.

    Args:
        raw_dfs: dict dari gather_raw_data.

    Returns:
        dict[str, pd.DataFrame]: Clean DataFrames.
    """
    print("\n" + "=" * 60)
    print("CLEANING ALL DATASETS")
    print("=" * 60)
    clean = {
        "DEMO_J": clean_demo(raw_dfs["DEMO_J"]),
        "ALQ_J":  clean_alq(raw_dfs["ALQ_J"]),
        "DPQ_J":  clean_dpq(raw_dfs["DPQ_J"]),
        "PAQ_J":  clean_paq(raw_dfs["PAQ_J"]),
        "SLQ_J":  clean_slq(raw_dfs["SLQ_J"]),
    }
    return clean