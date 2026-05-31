from src.config.settings import PHQ9_ITEMS, PHQ9_THRESHOLDS, DEPRESSION_LABEL_MAP

def build_phq9_target(df):
    """
    Bangun variabel target PHQ-9 dari 9 item DPQ.

    Kalkulasi:
        PHQ9_SCORE = sum(DPQ010 + DPQ020 + ... + DPQ090)
        Range: 0–27

    Klasifikasi depresi (Kroenke, Spitzer & Williams, 2001):
        0–4   : Minimal depression
        5–9   : Mild depression
        10–14 : Moderate depression
        15–19 : Moderately severe depression
        20–27 : Severe depression

    Binary threshold untuk skrining klinis:
        PHQ9_BINARY = 1 jika PHQ9_SCORE ≥ 10, else 0
        (Sensitifitas 88%, Spesifisitas 88% untuk MDD - Kroenke 2001)

    Args:
        df: pd.DataFrame setelah merge (harus mengandung DPQ010-DPQ090).

    Returns:
        pd.DataFrame dengan kolom tambahan:
            PHQ9_SCORE    : skor total 0-27
            PHQ9_SEVERITY : label kategoris ('Minimal', ..., 'Severe')
            PHQ9_LABEL    : integer 0-4 (untuk multi-class)
            PHQ9_BINARY   : 0/1 (untuk binary classification)
    """
    df = df.copy()

    # Pastikan semua item ada
    missing_items = [c for c in PHQ9_ITEMS if c not in df.columns]
    if missing_items:
        raise ValueError(f"Kolom PHQ-9 tidak ditemukan: {missing_items}")

    # Total score
    df["PHQ9_SCORE"] = df[PHQ9_ITEMS].sum(axis=1).round().astype(int)

    # Severity label
    def _severity(score):
        for label, (lo, hi) in PHQ9_THRESHOLDS.items():
            if lo <= score <= hi:
                return label
        return "Severe"

    df["PHQ9_SEVERITY"] = df["PHQ9_SCORE"].apply(_severity)
    df["PHQ9_LABEL"]    = df["PHQ9_SEVERITY"].map(DEPRESSION_LABEL_MAP)
    df["PHQ9_BINARY"]   = (df["PHQ9_SCORE"] >= 10).astype(int)

    # Distribusi
    print("\n  PHQ-9 Score Distribution:")
    dist = df["PHQ9_SEVERITY"].value_counts(normalize=True).sort_index() * 100
    for sev, pct in dist.items():
        n = (df["PHQ9_SEVERITY"] == sev).sum()
        print(f"    {sev:25s}: {n:5d} ({pct:.1f}%)")

    print(f"\n  Binary (PHQ ≥ 10): {df['PHQ9_BINARY'].sum():,} ({df['PHQ9_BINARY'].mean()*100:.1f}%)")
    return df