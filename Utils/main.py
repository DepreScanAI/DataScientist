from src.config.settings import *
from src.pipeline.run import *

if __name__ == "__main__":
    """
    Cara penggunaan:
        python main.py

    Ubah RAW_PATHS di bagian src/config/settings.py di atas untuk
    menyesuaikan lokasi file XPT Anda.

    Output yang dihasilkan di folder 'data/' 'outputs/':
        data/interim/nhanes_mental_health_clean.csv   — Dataset lengkap semua kolom
        data/processed/nhanes_model_ready.csv         — Dataset siap model (fitur + target)
        outputs/json/pipeline_metadata.json           — Info kolom, class distribution
        outputs/plot/phq9_distribution.png
        outputs/plot/demographics.png
        outputs/plot/sleep_vs_phq9.png
        outputs/plot/activity_vs_phq9.png
        outputs/plot/correlation_heatmap.png
        outputs/plot/phq9_items_severity.png
        outputs/plot/risk_factors_bar.png
        outputs/abtest/ab_test_boxplots.png           — Visualisasi Hasil AB Testing
        outputs/abtest/ab_test_results.csv            — Hasil AB Testing
    """

    df_final = run_full_pipeline()

    print("\nContoh 5 baris pertama dataset final:")
    print(df_final[["SEQN","AGE","PHQ9_SCORE","PHQ9_SEVERITY","AVG_SLEEP_HOURS","TOTAL_MET_MIN","ALCOHOL_RISK_SCORE"]].head())
