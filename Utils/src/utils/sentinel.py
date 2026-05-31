import warnings
import pandas as pd
import numpy as np

from src.config.settings import *

warnings.filterwarnings("ignore")

def is_sentinel_zero(value, tol=SENTINEL_ZERO_TOL):
    """
    Deteksi apakah suatu nilai adalah sentinel-0 NHANES (5.397605e-79).

    Dalam format SAS XPT, integer 0 di-encode sebagai floating-point khusus
    yang sangat kecil (~5.4e-79). pandas.read_sas mempertahankan nilai ini
    apa adanya alih-alih mengkonversinya ke 0.

    Args:
        value: Nilai yang diperiksa (scalar, Series, atau array-like).
        tol:   Toleransi perbandingan floating-point.

    Returns:
        bool atau boolean Series/array.
    """
    if isinstance(value, (pd.Series, np.ndarray)):
        return np.abs(value - SENTINEL_ZERO) < tol
    if pd.isna(value):
        return False
    return abs(value - SENTINEL_ZERO) < tol


def decode_sentinel_zero(series):
    """
    Konversi nilai sentinel-0 NHANES menjadi integer 0 pada pd.Series.

    Args:
        series: pd.Series dengan kemungkinan nilai sentinel 5.397605e-79.

    Returns:
        pd.Series dengan sentinel diganti 0.0 (tipe float dipertahankan).
    """
    mask = is_sentinel_zero(series)
    return series.where(~mask, other=0.0)


def replace_nhanes_missing(series, missing_codes=None):
    """
    Ganti kode NHANES 'Refused' (7/77/777) dan 'Don't Know' (9/99/999)
    dengan NaN.

    NHANES menggunakan kode berbeda tergantung panjang field:
    - 1-digit items: 7=Refused, 9=Don't know
    - 2-digit items: 77=Refused, 99=Don't know
    - 3-digit items: 777=Refused, 999=Don't know

    Args:
        series:        pd.Series numerik.
        missing_codes: List kode yang harus diganti NaN.

    Returns:
        pd.Series dengan kode tersebut diganti NaN.
    """
    if missing_codes is None:
        missing_codes = NHANES_MISSING_CODES
    return series.replace(missing_codes, np.nan)


def decode_column(series):
    """
    Pipeline decode lengkap untuk satu kolom NHANES:
    1. Sentinel-0 → 0
    2. Refused/Don't-know → NaN

    Args:
        series: pd.Series raw dari read_sas.

    Returns:
        pd.Series yang sudah didecode.
    """
    s = decode_sentinel_zero(series)
    s = replace_nhanes_missing(s)
    return s