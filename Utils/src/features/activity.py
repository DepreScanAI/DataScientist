def build_activity_features(df):
    """
    Bangun fitur aktivitas fisik dari PAQ.

    WHO merekomendasikan 150 menit/minggu aktivitas moderat atau
    75 menit/minggu aktivitas vigorous untuk orang dewasa.

    Fitur yang dibuat:

    TOTAL_MET_MIN   : Total MET-minutes per minggu
                      MET-min = durasi × frekuensi × MET_coefficient
                      Vigorous: MET=8.0, Moderate: MET=4.0, Walk: MET=3.3
    VIG_MIN_WEEK    : Menit vigorous per minggu (PAD615 × 5 asumsi 5 hari kerja)
    MOD_MIN_WEEK    : Menit moderate per minggu
    SEDENTARY_HOURS : PAD680 / 60 (jam sedentary per hari)
    SEDENTARY_HIGH  : 1 jika sedentary > 8 jam/hari
    MEETS_PA_GUIDELINE: 1 jika TOTAL_MET_MIN ≥ 500 (setara ~150 mnt/minggu moderate)
    PHYSICALLY_INACTIVE: 1 jika TOTAL_MET_MIN < 150 (inaktif total)
    PA_CATEGORY     : "Active", "Insufficiently Active", "Inactive"

    Args:
        df: pd.DataFrame.

    Returns:
        pd.DataFrame dengan fitur aktivitas.
    """
    df = df.copy()

    # MET coefficients (standar WHO/GPAQ)
    MET_VIG  = 8.0
    MET_MOD  = 4.0
    MET_WALK = 3.3
    WORK_DAYS_DEFAULT = 5  # hari kerja per minggu (jika tidak ada data frekuensi)

    # Isi NaN durasi dengan 0 (jika domain = No, sudah diset 0 di clean_paq)
    dur_cols = ["PAD615","PAD630","PAD645","PAD660","PAD675"]
    for col in dur_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    """
    Hitung MET-minutes per minggu
    PAD615 = vigorous work min/day → × 5 days/week asumsi
    PAD660 = vigorous leisure min/day → × frekuensi (default 3)
    Untuk simplifikasi (tidak ada data frekuensi per domain),
    kita asumsikan 5 hari untuk work domain, 3 hari untuk leisure.
    """
    df["VIG_MIN_WEEK"] = (
        df.get("PAD615", 0) * 5 +
        df.get("PAD660", 0) * 3
    )
    df["MOD_MIN_WEEK"] = (
        df.get("PAD630", 0) * 5 +
        df.get("PAD645", 0) * 5 +
        df.get("PAD675", 0) * 3
    )

    df["TOTAL_MET_MIN"] = (
        df["VIG_MIN_WEEK"]  * MET_VIG +
        df["MOD_MIN_WEEK"]  * MET_MOD
    )

    # Sedentary
    df["SEDENTARY_HOURS"] = df["PAD680"] / 60.0
    df["SEDENTARY_HIGH"]  = (df["SEDENTARY_HOURS"] > 8).astype(int)

    # PA Guidelines
    # 500 MET-min/week ≈ 150 mnt moderate/wk (WHO threshold)
    df["MEETS_PA_GUIDELINE"]  = (df["TOTAL_MET_MIN"] >= 500).astype(int)
    df["PHYSICALLY_INACTIVE"] = (df["TOTAL_MET_MIN"] < 150).astype(int)

    def _pa_cat(row):
        if row["TOTAL_MET_MIN"] >= 500:
            return "Active"
        elif row["TOTAL_MET_MIN"] >= 150:
            return "Insufficiently Active"
        return "Inactive"

    df["PA_CATEGORY"] = df.apply(_pa_cat, axis=1)

    pct_active   = df["MEETS_PA_GUIDELINE"].mean() * 100
    pct_inactive = df["PHYSICALLY_INACTIVE"].mean() * 100
    print(f"  [build_activity_features] Active (≥500 MET-min): {pct_active:.1f}%")
    print(f"  [build_activity_features] Inactive (<150 MET-min): {pct_inactive:.1f}%")
    return df