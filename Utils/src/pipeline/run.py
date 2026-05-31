import json

from src.config.settings import *
from src.preproc.gather import *
from src.preproc.assess import *
from src.preproc.clean import *
from src.preproc.merge import *
from src.features.target import *
from src.features.demographics import *
from src.features.alcohol import *
from src.features.activity import *
from src.features.sleep import *
from src.features.feature_engineering import *
from src.features.eda import *
from src.experiments.ab_testing import *

def run_full_pipeline(paths=None, o_dataset=O_DATASET, o_plot=O_PLOT, o_json=O_JSON, o_abtest=O_ABTEST, run_eda_flag=True,
                      run_ab_flag=True):
    """
    Master pipeline — jalankan seluruh alur dari raw XPT hingga data siap model.

    Urutan eksekusi:
    ┌─────────────────────────────────────────────────┐
    │ 1. GATHER     — Load semua file XPT             │
    │ 2. ASSESS     — Audit kualitas data raw         │
    │ 3. CLEAN      — Wrangling & cleaning per modul  │
    │ 4. MERGE      — Inner join by SEQN              │
    │ 5. TARGET     — Build PHQ-9 score & labels      │
    │ 6. FEATURES   — Build domain features           │
    │ 7. ENGINEER   — Interaction & composite features│
    │ 8. EDA        — Visualisasi & statistik         │
    │ 9. A/B TEST   — Hypothesis testing              │
    │ 10. SAVE      — Export clean dataset            │
    └─────────────────────────────────────────────────┘

    Args:
        paths:        dict {name: filepath} ke file XPT. None → RAW_PATHS.
        output_dir:   Direktori output.
        run_eda_flag: Jika False, skip EDA (lebih cepat).
        run_ab_flag:  Jika False, skip A/B testing.

    Returns:
        pd.DataFrame: Dataset final siap model.
    """
    print("\n" + "╔" + "═"*58 + "╗")
    print("║  NHANES 2017-2018 Mental Health Risk Pipeline            ║")
    print("╚" + "═"*58 + "╝")

    # STEP 1: GATHER
    raw_dfs = gather_raw_data(paths=paths)

    # STEP 2: ASSESS
    assess_reports = assess_all(raw_dfs)

    # STEP 3: CLEAN
    clean_dfs = clean_all(raw_dfs)

    # STEP 4: MERGE
    df = merge_all(clean_dfs, how="inner")

    # STEP 5: TARGET
    print("\n" + "=" * 60)
    print("BUILDING TARGET VARIABLE (PHQ-9)")
    print("=" * 60)
    df = build_phq9_target(df)

    # STEP 6: FEATURES
    print("\n" + "=" * 60)
    print("BUILDING DOMAIN FEATURES")
    print("=" * 60)
    df = build_demo_features(df)
    df = build_alcohol_features(df)
    df = build_activity_features(df)
    df = build_sleep_features(df)

    # STEP 7: FEATURE ENGINEERING
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING (INTERACTIONS & COMPOSITES)")
    print("=" * 60)
    df = engineer_all_features(df)

    # STEP 8: EDA
    if run_eda_flag:
        _ = run_eda(df, output_dir=o_plot)

    # STEP 9: A/B TESTING
    if run_ab_flag:
        ab_results = run_ab_test(df, output_dir=o_abtest)

    # STEP 10: SAVE
    print("\n" + "=" * 60)
    print("SAVING FINAL DATASETS")
    print("=" * 60)

    # Dataset lengkap
    save_artifact(df, "nhanes_mental_health_clean", o_dataset[0])

    # Dataset fitur saja (tanpa raw DPQ items, siap dimasukkan ke model)
    raw_dpq_cols = PHQ9_ITEMS + [f"{i}_SEVERE" for i in PHQ9_ITEMS]
    raw_nhanes_cols = ["ALQ111","ALQ121","ALQ130","ALQ151",
                       "PAQ605","PAQ620","PAQ635","PAQ650","PAQ665",
                       "PAD615","PAD630","PAD645","PAD660","PAD675","PAD680",
                       "SLD012","SLD013","SLQ030","SLQ040","SLQ050","SLQ120",
                       "GENDER","RACE","EDUCATION","MARITAL","INCOME_CAT","PIR"]

    model_exclude = raw_dpq_cols  # jangan drop target dan raw scores
    model_df = df.drop(columns=[c for c in model_exclude if c in df.columns])
    save_artifact(model_df, "nhanes_model_ready", o_dataset[1])

    # Metadata kolom
    col_info = {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "target_cols": ["PHQ9_SCORE", "PHQ9_SEVERITY", "PHQ9_LABEL", "PHQ9_BINARY"],
        "feature_cols": [c for c in df.columns if c not in
                         ["SEQN","PHQ9_SCORE","PHQ9_SEVERITY","PHQ9_LABEL","PHQ9_BINARY"] +
                         raw_dpq_cols],
        "class_distribution": df["PHQ9_SEVERITY"].value_counts().to_dict(),
        "binary_positive_rate": round(df["PHQ9_BINARY"].mean(), 4),
    }
    meta_path = os.path.join(o_json, "pipeline_metadata.json")
    # Pastikan folder ada sebelum membuat/menyimpan file di dalamnya
    os.makedirs(o_json, exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(col_info, f, indent=2, default=str)
    print(f"  Metadata saved: {meta_path}")

    # SUMMARY
    print("\n" + "╔" + "═"*58 + "╗")
    print("║  PIPELINE COMPLETE                                       ║")
    print("╠" + "═"*58 + "╣")
    print(f"║  Final dataset  : {len(df):,} rows × {len(df.columns)} columns{' ':>16}║")
    print(f"║  PHQ-9 Positive : {df['PHQ9_BINARY'].sum():,} ({df['PHQ9_BINARY'].mean()*100:.1f}%){' ':>29}║")
    n_feat = len(col_info["feature_cols"])
    print(f"║  Model features : {n_feat}{' ':>{38-len(str(n_feat))}} ║")
    print(f"║  Output dir     : outputs\ ~/data,plot,json,abtest       ║")
    print("╚" + "═"*58 + "╝\n")

    return df

if __name__ == "__main__":
    run_full_pipeline()