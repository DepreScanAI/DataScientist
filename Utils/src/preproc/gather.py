import os
import warnings
import numpy as np
import pandas as pd

from src.utils.sentinel import *
from src.utils.io import load_xpt

warnings.filterwarnings("ignore")

def gather_raw_data(paths=None, verbose=True):
    """
    GATHER — Tahap pertama Data Wrangling.

    Memuat semua file XPT NHANES 2017-2018 ke dalam dictionary DataFrame.
    Tidak ada transformasi apapun di tahap ini; data disimpan persis
    seperti yang dikembalikan pandas.read_sas.

    Sumber data:
        - DEMO_J: Demographics (9,254 respondents, 46 variables)
        - ALQ_J:  Alcohol Use Questionnaire (5,533, 10 variables)
        - DPQ_J:  Depression Screener / PHQ-9 (5,533, 11 variables)
        - PAQ_J:  Physical Activity Questionnaire (5,856, 17 variables)
        - SLQ_J:  Sleep Disorders Questionnaire (6,161, 11 variables)

    Catatan ukuran: DPQ & ALQ memiliki jumlah baris sama (5,533) karena
    keduanya diterapkan pada subsamel yang sama (MEC subsample).

    Args:
        paths:   Dict {name: filepath}. Jika None, gunakan RAW_PATHS.
        verbose: Print ringkasan setiap file.

    Returns:
        dict[str, pd.DataFrame]: Raw DataFrames per modul NHANES.
    """
    if paths is None:
        paths = RAW_PATHS

    print("=" * 60)
    print("GATHERING RAW DATA")
    print("=" * 60)

    raw = {}
    for name, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"File tidak ditemukan: {path}\n"
                f"Update RAW_PATHS di src/config/settings.py"
            )
        raw[name] = load_xpt(path, verbose=verbose)

    print(f"\n  Total files loaded: {len(raw)}")
    return raw