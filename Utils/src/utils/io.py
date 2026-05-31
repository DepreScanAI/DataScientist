import os
import warnings
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from src.config.settings import *

warnings.filterwarnings("ignore")

def load_xpt(path, verbose=True):
    """
    Baca file SAS XPT (Transport format) menggunakan pandas.read_sas.

    NHANES mendistribusikan semua data dalam format SAS Transport (.xpt).
    File ini mengandung metadata variabel (label, format) yang disimpan
    sebagai atribut SAS.

    Args:
        path:    Path ke file .xpt.
        verbose: Jika True, print ringkasan file.

    Returns:
        pd.DataFrame raw (belum di-decode).
    """
    df = pd.read_sas(path, format="xport", encoding="latin-1")
    if verbose:
        print(f"  Loaded: {os.path.basename(path)}")
        print(f"    Rows: {len(df):,}  |  Columns: {len(df.columns)}")
        print(f"    Columns: {list(df.columns)}")
    return df


def save_artifact(df, name, output_dir=O_DATASET):
    """
    Simpan DataFrame sebagai CSV ke direktori output.

    Args:
        df:         pd.DataFrame yang akan disimpan.
        name:       Nama file (tanpa ekstensi).
        output_dir: Direktori tujuan.

    Returns:
        str: Path file yang disimpan.
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"  Saved: {path}  ({len(df):,} rows × {len(df.columns)} cols)")
    return path


def save_figure(fig, name, output_dir=O_PLOT, dpi=150):
    """
    Simpan matplotlib Figure ke file PNG.

    Args:
        fig:        matplotlib Figure.
        name:       Nama file (tanpa ekstensi).
        output_dir: Direktori tujuan.
        dpi:        Resolusi gambar.

    Returns:
        str: Path file yang disimpan.
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}.png")
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  Figure saved: {path}")
    return path