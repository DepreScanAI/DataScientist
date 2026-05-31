import numpy as np

def build_alcohol_features(df):
    """
    Bangun fitur alkohol dari ALQ.

    Fitur yang dibuat:

    ALCOHOL_EVER     : 1 jika pernah minum ≥12 drinks seumur hidup
    ALCOHOL_CURRENT  : 1 jika minum di tahun lalu (ALQ121 > 0)
    DRINK_FREQ_SCORE : Skor frekuensi 0-10 dari ALQ121
                       0=never, 10=daily (invert dari kode NHANES)
    AVG_DRINKS_DAY   : ALQ130 (drinks per hari saat minum)
    BINGE_DRINKER    : 1 jika ALQ151=1 (binge past year)
    HEAVY_DRINKER    : 1 jika AVG_DRINKS_DAY > 4 (NIAAA threshold)
    ALCOHOL_RISK_SCORE: Komposit 0-3 berdasarkan current, binge, heavy

    Missing strategy:
    - ALQ111 NaN: asumsikan never (0) — konservatif
    - ALQ121 NaN pada ever-drinker: median imputasi
    - ALQ130 NaN pada current drinker: median imputasi

    Args:
        df: pd.DataFrame.

    Returns:
        pd.DataFrame dengan fitur alkohol.
    """
    df = df.copy()

    # ALCOHOL_EVER
    df["ALQ111"] = df["ALQ111"].fillna(2)  # NaN → assume never
    df["ALCOHOL_EVER"] = (df["ALQ111"] == 1).astype(int)

    # ALCOHOL_CURRENT
    df["ALQ121"] = df["ALQ121"].fillna(0)
    df["ALCOHOL_CURRENT"] = (df["ALQ121"] > 0).astype(int)

    """
    DRINK_FREQ_SCORE (0=never → 0, 1=daily → 10)
    ALQ121 encoding: 0=never, 1=every day, 2=5-6/wk, ..., 10=1-2/yr
    Invert: skor tinggi = sering minum
    """
    freq_score_map = {0: 0, 1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
                      6: 5, 7: 4, 8: 3, 9: 2, 10: 1}
    df["DRINK_FREQ_SCORE"] = df["ALQ121"].map(freq_score_map).fillna(0)

    # AVG_DRINKS_DAY
    med_drinks = df.loc[df["ALCOHOL_CURRENT"] == 1, "ALQ130"].median()
    df["ALQ130"] = df["ALQ130"].fillna(0)
    # Current drinker dengan ALQ130 NaN → imputasi median
    mask_cur_nan = (df["ALCOHOL_CURRENT"] == 1) & (df["ALQ130"] == 0)
    df.loc[mask_cur_nan, "ALQ130"] = med_drinks if not np.isnan(med_drinks) else 2.0
    df["AVG_DRINKS_DAY"] = df["ALQ130"]

    # BINGE_DRINKER
    df["ALQ151"] = df["ALQ151"].fillna(2)
    df["BINGE_DRINKER"] = (df["ALQ151"] == 1).astype(int)

    # HEAVY_DRINKER (>4 drinks/day, NIAAA definition)
    df["HEAVY_DRINKER"] = (df["AVG_DRINKS_DAY"] > 4).astype(int)

    # ALCOHOL_RISK_SCORE
    df["ALCOHOL_RISK_SCORE"] = (
        df["ALCOHOL_CURRENT"] +
        df["BINGE_DRINKER"] +
        df["HEAVY_DRINKER"]
    )

    print(f"  [build_alcohol_features] Current drinkers: "
          f"{df['ALCOHOL_CURRENT'].sum():,} ({df['ALCOHOL_CURRENT'].mean()*100:.1f}%)")
    print(f"  [build_alcohol_features] Binge drinkers: "
          f"{df['BINGE_DRINKER'].sum():,}")
    return df