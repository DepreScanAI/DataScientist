import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config.settings import OUTPUT_DIR, RACE_MAP, EDUC_MAP, PHQ9_ITEMS, PHQ9_ITEM_LABELS
from src.utils.io import save_figure

warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid", palette="muted")

def run_eda(df, output_dir=OUTPUT_DIR):
    """
    Exploratory Data Analysis — menghasilkan visualisasi dan statistik deskriptif.

    Plot yang dihasilkan:
    1. phq9_distribution.png   : Histogram PHQ-9 score + severity breakdown
    2. demographics.png        : Distribusi gender, usia, ras, pendidikan
    3. sleep_vs_phq9.png       : Boxplot tidur berdasarkan depresi severity
    4. activity_vs_phq9.png    : MET-minutes vs PHQ-9 kategori
    5. alcohol_vs_phq9.png     : Alkohol risk vs PHQ-9
    6. correlation_heatmap.png : Korelasi antar fitur numerik
    7. phq9_items_severity.png : Rata-rata skor per item PHQ-9 per severity
    8. risk_factors_bar.png    : Prevalensi risk factors per depression level

    Args:
        df:         pd.DataFrame final.
        output_dir: Direktori output.

    Returns:
        dict: Statistik deskriptif utama.
    """
    os.makedirs(output_dir, exist_ok=True)
    stats_out = {}

    print("\n" + "=" * 60)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    # 1. PHQ-9 Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("PHQ-9 Score Distribution (NHANES 2017-2018)", fontsize=14, fontweight="bold")

    # Histogram
    ax = axes[0]
    ax.hist(df["PHQ9_SCORE"], bins=28, range=(0, 27), color="#4c7be0", edgecolor="white", alpha=0.8)
    ax.axvline(10, color="red", linestyle="--", linewidth=1.5, label="Clinical threshold (≥10)")
    ax.set_xlabel("PHQ-9 Total Score")
    ax.set_ylabel("Count")
    ax.set_title("Score Distribution")
    ax.legend()

    # Severity pie
    ax2 = axes[1]
    sev_counts = df["PHQ9_SEVERITY"].value_counts()
    order = ["Minimal","Mild","Moderate","Moderately Severe","Severe"]
    sev_ordered = sev_counts.reindex([s for s in order if s in sev_counts.index])
    colors = ["#2dd4a0","#fbbf24","#f97316","#ef4444","#7c3aed"][:len(sev_ordered)]
    ax2.pie(sev_ordered, labels=sev_ordered.index, autopct="%1.1f%%",
            colors=colors, startangle=90)
    ax2.set_title("Depression Severity Distribution")

    plt.tight_layout()
    save_figure(fig, "phq9_distribution", output_dir)

    # Statistik deskriptif PHQ-9
    stats_out["phq9"] = {
        "mean":   round(df["PHQ9_SCORE"].mean(), 2),
        "median": int(df["PHQ9_SCORE"].median()),
        "std":    round(df["PHQ9_SCORE"].std(), 2),
        "pct_clinically_significant": round(df["PHQ9_BINARY"].mean() * 100, 1),
    }
    print(f"\n  PHQ-9 Mean={stats_out['phq9']['mean']}, "
          f"Median={stats_out['phq9']['median']}, "
          f"Clinically significant: {stats_out['phq9']['pct_clinically_significant']}%")

    # 2. Demographics
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Demographics Overview", fontsize=14, fontweight="bold")

    # Gender
    ax = axes[0][0]
    gender_dist = df["GENDER"].map({1: "Male", 2: "Female"}).value_counts()
    ax.bar(gender_dist.index, gender_dist.values, color=["#4c7be0","#e07c5a"])
    ax.set_title("Gender Distribution")
    ax.set_ylabel("Count")

    # Age histogram
    ax = axes[0][1]
    ax.hist(df["AGE"], bins=30, color="#7c4ee0", edgecolor="white", alpha=0.8)
    ax.set_title("Age Distribution")
    ax.set_xlabel("Age (years)")

    # Race
    ax = axes[1][0]
    race_dist = df["RACE"].map(RACE_MAP).value_counts()
    ax.barh(race_dist.index, race_dist.values, color="#4cade0")
    ax.set_title("Race/Ethnicity")

    # Education
    ax = axes[1][1]
    educ_dist = df["EDUCATION"].map(EDUC_MAP).value_counts()
    ax.bar(range(len(educ_dist)), educ_dist.values, color="#40c98a")
    ax.set_xticks(range(len(educ_dist)))
    ax.set_xticklabels(educ_dist.index, rotation=30, ha="right", fontsize=9)
    ax.set_title("Education Level")

    plt.tight_layout()
    save_figure(fig, "demographics", output_dir)

    # 3. Sleep vs PHQ-9
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Sleep vs Depression Severity", fontsize=14, fontweight="bold")

    order = ["Minimal","Mild","Moderate","Moderately Severe","Severe"]
    order_present = [s for s in order if s in df["PHQ9_SEVERITY"].unique()]

    ax = axes[0]
    grouped_data = [df.loc[df["PHQ9_SEVERITY"]==s, "AVG_SLEEP_HOURS"].dropna()
                    for s in order_present]
    ax.boxplot(grouped_data, labels=order_present, patch_artist=True)
    ax.set_title("Avg Sleep Hours by Severity")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=30)

    ax = axes[1]
    grouped_data2 = [df.loc[df["PHQ9_SEVERITY"]==s, "SOCIAL_JETLAG"].dropna()
                     for s in order_present]
    ax.boxplot(grouped_data2, labels=order_present, patch_artist=True)
    ax.set_title("Social Jetlag (hours)")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=30)

    ax = axes[2]
    short_by_sev = df.groupby("PHQ9_SEVERITY")["SHORT_SLEEPER"].mean() * 100
    short_by_sev = short_by_sev.reindex(order_present)
    ax.bar(short_by_sev.index, short_by_sev.values, color="#ef4444", alpha=0.8)
    ax.set_title("% Short Sleepers by Severity")
    ax.set_ylabel("% with <6h sleep")
    ax.tick_params(axis="x", rotation=30)

    plt.tight_layout()
    save_figure(fig, "sleep_vs_phq9", output_dir)

    # 4. Activity vs PHQ-9
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Physical Activity vs Depression", fontsize=14, fontweight="bold")

    ax = axes[0]
    grouped_log = [df.loc[df["PHQ9_SEVERITY"]==s, "LOG_MET"].dropna()
                   for s in order_present]
    ax.boxplot(grouped_log, labels=order_present, patch_artist=True)
    ax.tick_params(axis="x", rotation=30)
    ax.set_title("Log(MET-minutes/week) by Severity")

    ax = axes[1]
    inactive_by_sev = df.groupby("PHQ9_SEVERITY")["PHYSICALLY_INACTIVE"].mean() * 100
    inactive_by_sev = inactive_by_sev.reindex(order_present)
    bars = ax.bar(inactive_by_sev.index, inactive_by_sev.values,
                  color=["#2dd4a0","#fbbf24","#f97316","#ef4444","#7c3aed"][:len(inactive_by_sev)])
    ax.set_title("% Physically Inactive by Severity")
    ax.set_ylabel("% Inactive")
    ax.tick_params(axis="x", rotation=30)

    plt.tight_layout()
    save_figure(fig, "activity_vs_phq9", output_dir)

    # 5. Correlation Heatmap
    numeric_features = [
        "PHQ9_SCORE","AVG_SLEEP_HOURS","SLEEP_DEVIATION","SOCIAL_JETLAG",
        "SLEEP_RISK_SCORE","ALCOHOL_RISK_SCORE","TOTAL_MET_MIN",
        "SEDENTARY_HOURS","AGE","PIR","TOTAL_RISK_COMPOSITE",
        "N_SEVERE_ITEMS","LOG_MET",
    ]
    numeric_features = [c for c in numeric_features if c in df.columns]
    corr_matrix = df[numeric_features].corr()

    fig, ax = plt.subplots(figsize=(13, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f",
                cmap="RdYlGn_r", center=0, vmin=-1, vmax=1,
                linewidths=0.5, ax=ax, annot_kws={"size": 8})
    ax.set_title("Feature Correlation Matrix\n(NHANES 2017-2018 Mental Health Data)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    save_figure(fig, "correlation_heatmap", output_dir)

    # 6. PHQ-9 Item Severity Profile
    fig, ax = plt.subplots(figsize=(13, 6))
    item_means = df.groupby("PHQ9_SEVERITY")[PHQ9_ITEMS].mean()
    item_means = item_means.reindex(order_present)
    item_means.columns = [PHQ9_ITEM_LABELS[c][:30] for c in item_means.columns]

    item_means.T.plot(kind="bar", ax=ax, colormap="viridis", alpha=0.85, edgecolor="white")
    ax.set_title("Mean PHQ-9 Item Score by Depression Severity",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("Mean Score (0-3)")
    ax.set_xlabel("PHQ-9 Item")
    ax.tick_params(axis="x", rotation=40)
    ax.legend(title="Severity", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    save_figure(fig, "phq9_items_severity", output_dir)

    # 7. Risk Factors Prevalence
    fig, ax = plt.subplots(figsize=(12, 6))
    risk_cols = ["SHORT_SLEEPER","SLEEP_DISORDERED","BINGE_DRINKER",
                 "HEAVY_DRINKER","PHYSICALLY_INACTIVE","SEDENTARY_HIGH",
                 "LIVING_ALONE","SLEEP_APNEA_RISK"]
    risk_cols = [c for c in risk_cols if c in df.columns]

    risk_prev = df.groupby("PHQ9_BINARY")[risk_cols].mean() * 100
    risk_prev.T.plot(kind="barh", ax=ax, color=["#2dd4a0","#ef4444"], alpha=0.8)
    ax.set_title("Risk Factor Prevalence: Non-Depressed vs Clinically Significant",
                 fontsize=12, fontweight="bold")
    ax.set_xlabel("Prevalence (%)")
    ax.legend(["PHQ-9 < 10 (Non)", "PHQ-9 ≥ 10 (Significant)"])
    plt.tight_layout()
    save_figure(fig, "risk_factors_bar", output_dir)

    print(f"\n  EDA complete. All figures saved to: {output_dir}/")
    return stats_out