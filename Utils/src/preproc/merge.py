def merge_all(clean_dfs, how="inner"):
    """
    MERGE — Gabungkan semua DataFrame bersih menggunakan SEQN sebagai key.

    Strategi join:
    - Inner join: hanya pertahankan responden yang ada di SEMUA dataset.
      Ini menghasilkan dataset paling bersih untuk supervised learning.
    - Justifikasi: PHQ-9 (DPQ_J) hanya diukur pada MEC-subsample ~5,533
      responden. Ini adalah bottleneck — inner join ke DEMO akan kehilangan
      ~3,700 responden yang tidak menjalani pemeriksaan MEC.

    Urutan merge: DPQ (target) → DEMO → ALQ → PAQ → SLQ

    Args:
        clean_dfs: dict[str, pd.DataFrame] dari clean_all.
        how:       Tipe join ('inner' direkomendasikan untuk ML).

    Returns:
        pd.DataFrame: Dataset gabungan.
    """
    print("\n" + "=" * 60)
    print("MERGING ALL DATASETS")
    print("=" * 60)

    # Mulai dari DPQ (target variable)
    merged = clean_dfs["DPQ_J"].copy()
    print(f"  Base (DPQ_J):  {len(merged):,} rows")

    for name in ["DEMO_J", "ALQ_J", "PAQ_J", "SLQ_J"]:
        df = clean_dfs[name]
        before = len(merged)
        merged = merged.merge(df, on="SEQN", how=how)
        print(f"  After merge {name}: {len(merged):,} rows (lost {before-len(merged):,})")

    print(f"\n  FINAL MERGED: {merged.shape[0]:,} rows × {merged.shape[1]} cols")
    return merged