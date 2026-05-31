def build_sleep_features(df):
    """
    Bangun fitur tidur dari SLQ.

    Referensi: National Sleep Foundation merekomendasikan 7-9 jam untuk
    orang dewasa. <6 jam atau >9 jam dikaitkan dengan risiko kesehatan mental
    yang lebih tinggi (Matthew Walker, 2017; Cappuccio et al., 2010).

    Fitur yang dibuat:

    AVG_SLEEP_HOURS  : Rata-rata weekday (SLD012) dan weekend (SLD013)
    SLEEP_DEVIATION  : |AVG_SLEEP_HOURS - 8| (deviasi dari optimal 8 jam)
    SOCIAL_JETLAG    : |SLD013 - SLD012| (selisih weekend-weekday sleep)
    SHORT_SLEEPER    : 1 jika AVG_SLEEP_HOURS < 6
    LONG_SLEEPER     : 1 jika AVG_SLEEP_HOURS > 9
    SLEEP_DISORDERED : 1 jika SLQ050=1 (pernah didiagnosa gangguan tidur)
    SNORING_FREQ     : SLQ030 ordinal 0-3
    SLEEP_APNEA_RISK : 1 jika SLQ040 ≥ 2 (stop breathing ≥ 3-4 malam/minggu)
    UNRESTED_FREQ    : SLQ120 ordinal 0-4
    SLEEP_RISK_SCORE : Komposit 0-5 (SHORT + LONG + DISORDERED + APNEA + UNRESTED≥2)

    Args:
        df: pd.DataFrame.

    Returns:
        pd.DataFrame dengan fitur tidur.
    """
    df = df.copy()

    # Rata-rata tidur
    df["AVG_SLEEP_HOURS"] = (df["SLD012"] + df["SLD013"]) / 2.0

    # Deviasi dari 8 jam
    df["SLEEP_DEVIATION"] = (df["AVG_SLEEP_HOURS"] - 8).abs()

    # Social Jetlag
    df["SOCIAL_JETLAG"] = (df["SLD013"] - df["SLD012"]).abs()

    # Sleep duration categories
    df["SHORT_SLEEPER"] = (df["AVG_SLEEP_HOURS"] < 6).astype(int)
    df["LONG_SLEEPER"]  = (df["AVG_SLEEP_HOURS"] > 9).astype(int)
    df["NORMAL_SLEEPER"]= ((df["AVG_SLEEP_HOURS"] >= 6) & (df["AVG_SLEEP_HOURS"] <= 9)).astype(int)

    # Sleep disorder (told by doctor)
    df["SLQ050"] = df["SLQ050"].fillna(2)  # NaN → No
    df["SLEEP_DISORDERED"] = (df["SLQ050"] == 1).astype(int)

    # Sleep apnea risk
    df["SLEEP_APNEA_RISK"] = (df["SLQ040"] >= 2).astype(int)

    # Unrested frequency
    df["UNRESTED_FREQ"] = df["SLQ120"].fillna(0).astype(int)

    # Composite sleep risk score
    df["SLEEP_RISK_SCORE"] = (
        df["SHORT_SLEEPER"] +
        df["LONG_SLEEPER"] +
        df["SLEEP_DISORDERED"] +
        df["SLEEP_APNEA_RISK"] +
        (df["UNRESTED_FREQ"] >= 2).astype(int)
    )

    pct_short = df["SHORT_SLEEPER"].mean() * 100
    pct_disordered = df["SLEEP_DISORDERED"].mean() * 100
    print(f"  [build_sleep_features] Short sleepers (<6h): {pct_short:.1f}%")
    print(f"  [build_sleep_features] Sleep disordered: {pct_disordered:.1f}%")
    return df