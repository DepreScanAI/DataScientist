import pandas as pd

def build_demo_features(df):
    """
    Bangun fitur demographics dari kolom cleaned.

    Transformasi:
    - AGE_GROUP: Binning usia menjadi 5 kelompok klinisi
      (18-29, 30-44, 45-59, 60-74, 75+)
    - GENDER: 1=Male → 0, 2=Female → 1 (binary encoding)
    - EDUCATION_ORD: Pendidikan sebagai ordinal 1-5 (sudah ordinal aslinya)
    - PIR_GROUP: Poverty Income Ratio dikategorikan
      (<1.0=Poor, 1-2=Near poor, 2-4=Middle, ≥4=High)
    - LIVING_ALONE: 1 jika tidak menikah dan tidak tinggal bersama pasangan
    - MARITAL_BINARY: 1=Married/Partner (protektif), 0=Other

    Missing handling:
    - EDUCATION: imputasi dengan median pada usia ≥20 (valid domain)
    - MARITAL: imputasi dengan mode
    - INCOME_CAT: imputasi dengan mode
    - PIR: imputasi dengan median

    Args:
        df: pd.DataFrame merged.

    Returns:
        pd.DataFrame dengan fitur demographics baru.
    """
    df = df.copy()

    # AGE_GROUP
    bins   = [17, 29, 44, 59, 74, 120]
    labels = ["18-29","30-44","45-59","60-74","75+"]
    df["AGE_GROUP"] = pd.cut(df["AGE"], bins=bins, labels=labels, right=True)

    """
    GENDER encoding
    1=Male→0, 2=Female→1 (konsisten dengan literatur: female lebih tinggi risiko)
    """
    df["GENDER_F"] = (df["GENDER"] == 2).astype(int)

    # EDUCATION imputation & ordinal
    mask_adult = df["AGE"] >= 20
    med_edu = df.loc[mask_adult, "EDUCATION"].median()
    df.loc[mask_adult & df["EDUCATION"].isnull(), "EDUCATION"] = med_edu
    # Usia 18-19: DMDEDUC3 tidak tersedia dalam dataset ini, isi dengan 2
    df["EDUCATION"] = df["EDUCATION"].fillna(2)
    df["EDUCATION_ORD"] = df["EDUCATION"].astype(int)

    # MARITAL
    mode_mar = df["MARITAL"].mode()
    df["MARITAL"] = df["MARITAL"].fillna(mode_mar[0] if len(mode_mar) > 0 else 1)
    df["MARITAL_BINARY"] = df["MARITAL"].isin([1, 6]).astype(int)  # Married or partner
    df["LIVING_ALONE"]   = df["MARITAL"].isin([2, 3, 4, 5]).astype(int)

    # INCOME imputation
    mode_inc = df["INCOME_CAT"].mode()
    df["INCOME_CAT"] = df["INCOME_CAT"].fillna(mode_inc[0] if len(mode_inc) > 0 else 7)

    # PIR imputation & group
    med_pir = df["PIR"].median()
    df["PIR"] = df["PIR"].fillna(med_pir)
    df["PIR_GROUP"] = pd.cut(
        df["PIR"],
        bins=[-0.001, 1.0, 2.0, 4.0, 5.01],
        labels=["Poor","Near poor","Middle","High"],
        right=True,
    )

    print(f"  [build_demo_features] Added: AGE_GROUP, GENDER_F, EDUCATION_ORD, "
          f"MARITAL_BINARY, LIVING_ALONE, PIR_GROUP")
    return df