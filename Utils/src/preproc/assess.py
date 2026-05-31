import warnings
import numpy as np
import pandas as pd

from src.utils.sentinel import *

warnings.filterwarnings("ignore")

def assess_dataframe(df, name="DataFrame", decode_first=True):
    """
    ASSESS — Audit kualitas data satu DataFrame.

    Menghasilkan laporan:
    1. Shape & dtypes
    2. Missing values (raw NaN + sentinel-0 yang belum di-decode)
    3. Nilai unik per kolom
    4. Duplikat pada SEQN (ID respondent)
    5. Outlier sederhana (IQR method) untuk kolom numerik kontinu

    Catatan sentinel: NHANES meng-encode integer 0 sebagai 5.397605e-79
    dalam format XPT. Fungsi ini melaporkan keduanya — NaN asli DAN
    sentinel-0 — agar analis bisa membedakan "tidak menjawab" vs "nol nyata".

    Args:
        df:           pd.DataFrame yang akan diaudit.
        name:         Label dataset untuk output.
        decode_first: Jika True, lakukan decode sentinel sebelum hitung missing.

    Returns:
        dict: Laporan kualitas data.
    """
    print(f"\n{'─'*55}")
    print(f"ASSESS: {name}")
    print(f"{'─'*55}")

    report = {"name": name, "shape": df.shape}

    # 1. Shape
    print(f"  Shape        : {df.shape[0]:,} rows × {df.shape[1]} cols")

    # 2. Sentinel count (sebelum decode)
    sentinel_counts = {}
    for col in df.columns:
        if df[col].dtype in [np.float64, np.float32]:
            n_sent = is_sentinel_zero(df[col]).sum()
            if n_sent > 0:
                sentinel_counts[col] = int(n_sent)
    if sentinel_counts:
        print(f"  Sentinel-0   : {len(sentinel_counts)} kolom terdeteksi")
        for col, cnt in list(sentinel_counts.items())[:8]:
            print(f"    {col:20s}: {cnt:5d} nilai sentinel (= nilai 0)")
    report["sentinel_counts"] = sentinel_counts

    # 3. Missing values setelah decode
    if decode_first:
        df_dec = df.copy()
        for col in df_dec.columns:
            if df_dec[col].dtype in [np.float64, np.float32]:
                df_dec[col] = decode_column(df_dec[col])
        df_eval = df_dec
    else:
        df_eval = df

    miss = df_eval.isnull().sum()
    miss_pct = (miss / len(df_eval) * 100).round(1)
    miss_df = pd.DataFrame({"missing_n": miss, "missing_pct": miss_pct})
    miss_df = miss_df[miss_df["missing_n"] > 0].sort_values("missing_pct", ascending=False)

    print(f"  Missing vals : {len(miss_df)} kolom memiliki NaN (setelah decode)")
    if len(miss_df) > 0:
        print(miss_df.head(10).to_string())
    report["missing_summary"] = miss_df

    # 4. Duplikat SEQN
    if "SEQN" in df.columns:
        n_dup = df["SEQN"].duplicated().sum()
        print(f"  Dup SEQN     : {n_dup}")
        report["seqn_duplicates"] = int(n_dup)

    # 5. Nilai unik (hanya kolom non-ID)
    uniq = {}
    for col in df.columns:
        if col != "SEQN":
            uniq[col] = int(df_eval[col].nunique())
    report["unique_values"] = uniq

    # 6. Outlier IQR untuk kolom numerik
    outlier_report = {}
    for col in df_eval.select_dtypes(include=np.number).columns:
        if col == "SEQN":
            continue
        q1, q3 = df_eval[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            continue
        n_out = ((df_eval[col] < q1 - 1.5*iqr) | (df_eval[col] > q3 + 1.5*iqr)).sum()
        if n_out > 0:
            outlier_report[col] = int(n_out)

    report["outlier_iqr"] = outlier_report
    print(f"  Outlier (IQR): {len(outlier_report)} kolom memiliki outlier potensial")

    return report


def assess_all(raw_dfs):
    """
    Jalankan assess_dataframe untuk semua file NHANES.

    Args:
        raw_dfs: dict[str, pd.DataFrame] dari gather_raw_data.

    Returns:
        dict[str, dict]: Laporan per dataset.
    """
    print("\n" + "=" * 60)
    print("ASSESSING ALL DATASETS")
    print("=" * 60)
    reports = {}
    for name, df in raw_dfs.items():
        reports[name] = assess_dataframe(df, name=name)
    return reports