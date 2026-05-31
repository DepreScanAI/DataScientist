import numpy as np

from src.config.settings import PHQ9_ITEMS

def engineer_all_features(df):
    """
    Feature Engineering lanjutan — membuat fitur interaksi, polinomial,
    dan domain-specific composites yang lebih informatif untuk model.

    Fitur interaksi yang dibuat:

    1. SLEEP_X_INACTIVE    : SHORT_SLEEPER × PHYSICALLY_INACTIVE
       → Kombinasi kurang tidur + tidak aktif (risiko depresi sangat tinggi)

    2. ALCOHOL_X_SEDENTARY : ALCOHOL_RISK_SCORE × SEDENTARY_HIGH
       → Minum alkohol + gaya hidup sedentary

    3. LONELINESS_PROXY    : LIVING_ALONE × (UNRESTED_FREQ ≥ 2)
       → Proxy kesepian dari living alone + sering merasa tidak segar

    4. SLEEP_ALCOHOL_SUM   : SLEEP_RISK_SCORE + ALCOHOL_RISK_SCORE
       → Beban total dua faktor mayor

    5. ACTIVE_FEMALE_YOUNG : GENDER_F × PHYSICALLY_INACTIVE × (AGE ≤ 44)
       → Wanita muda inaktif (kelompok rentan)

    6. AGE_SLEEP_INTERACT  : AGE × SLEEP_DEVIATION
       → Penuaan + gangguan tidur (efek kumulatif)

    7. PIR_INACTIVE        : (PIR < 1.5) × PHYSICALLY_INACTIVE
       → Kemiskinan + inaktif fisik

    8. TOTAL_RISK_COMPOSITE: Weighted sum dari semua risk scores
       = 2×PHQ_SLEEP + 1.5×ALCOHOL + 1×ACTIVITY + 0.5×SEDENTARY

    9. LOG_MET             : log(TOTAL_MET_MIN + 1) (normalisasi distribusi MET)

    10. SLEEP_CAT_ORDINAL  : 0=Normal, 1=Short, 2=Long (untuk tree-based models)

    Args:
        df: pd.DataFrame setelah build_*_features.

    Returns:
        pd.DataFrame dengan fitur engineering tambahan.
    """
    df = df.copy()

    # 1. Sleep × Activity interaction
    df["SLEEP_X_INACTIVE"] = df["SHORT_SLEEPER"] * df["PHYSICALLY_INACTIVE"]

    # 2. Alcohol × Sedentary
    df["ALCOHOL_X_SEDENTARY"] = df["ALCOHOL_RISK_SCORE"] * df["SEDENTARY_HIGH"]

    # 3. Loneliness proxy
    df["LONELINESS_PROXY"] = (
        df["LIVING_ALONE"] * (df["UNRESTED_FREQ"] >= 2).astype(int)
    )

    # 4. Sleep + Alcohol combined burden
    df["SLEEP_ALCOHOL_SUM"] = df["SLEEP_RISK_SCORE"] + df["ALCOHOL_RISK_SCORE"]

    # 5. Active female young (intersectionality)
    age_young = (df["AGE"] <= 44).astype(int)
    df["ACTIVE_FEMALE_YOUNG"] = df["GENDER_F"] * df["PHYSICALLY_INACTIVE"] * age_young

    # 6. Age × Sleep deviation
    df["AGE_SLEEP_INTERACT"] = df["AGE"] * df["SLEEP_DEVIATION"]

    # 7. Poverty × Inactive
    pir_poor = (df["PIR"] < 1.5).astype(int)
    df["PIR_INACTIVE"] = pir_poor * df["PHYSICALLY_INACTIVE"]

    # 8. Total risk composite (domain-weighted)
    df["TOTAL_RISK_COMPOSITE"] = (
        2.0 * df["SLEEP_RISK_SCORE"] +
        1.5 * df["ALCOHOL_RISK_SCORE"] +
        1.0 * df["PHYSICALLY_INACTIVE"] +
        0.5 * df["SEDENTARY_HIGH"]
    )

    # 9. Log-transformed MET (right-skewed distribution)
    df["LOG_MET"] = np.log1p(df["TOTAL_MET_MIN"])

    # 10. Sleep category ordinal
    df["SLEEP_CAT_ORDINAL"] = 0  # Normal
    df.loc[df["SHORT_SLEEPER"] == 1, "SLEEP_CAT_ORDINAL"] = 1
    df.loc[df["LONG_SLEEPER"]  == 1, "SLEEP_CAT_ORDINAL"] = 2

    # 11. PHQ item flags (any item score = 3, i.e., "nearly every day")
    for item in PHQ9_ITEMS:
        df[f"{item}_SEVERE"] = (df[item] == 3).astype(int)
    df["N_SEVERE_ITEMS"] = df[[f"{i}_SEVERE" for i in PHQ9_ITEMS]].sum(axis=1)

    new_cols = [
        "SLEEP_X_INACTIVE","ALCOHOL_X_SEDENTARY","LONELINESS_PROXY",
        "SLEEP_ALCOHOL_SUM","ACTIVE_FEMALE_YOUNG","AGE_SLEEP_INTERACT",
        "PIR_INACTIVE","TOTAL_RISK_COMPOSITE","LOG_MET","SLEEP_CAT_ORDINAL",
        "N_SEVERE_ITEMS",
    ]
    print(f"  [engineer_all_features] Created {len(new_cols)} interaction features")
    return df