import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config.settings import OUTPUT_DIR
from src.utils.io import save_figure, save_artifact

from scipy import stats
from scipy.stats import chi2_contingency, mannwhitneyu, shapiro

warnings.filterwarnings("ignore")

def run_ab_test(df, output_dir=OUTPUT_DIR):
    """
    A/B Testing — Uji hipotesis untuk memvalidasi signifikansi perbedaan
    antar kelompok pada setiap faktor risiko.

    Desain eksperimen:
    - "Group A" = responden TANPA faktor risiko tertentu (control)
    - "Group B" = responden DENGAN faktor risiko (treatment)
    - Outcome = PHQ9_SCORE (kontinu) atau PHQ9_BINARY (proporsi)

    Rangkaian uji yang dilakukan:

    Test 1 — SHORT SLEEPER vs NORMAL
        H₀: Tidak ada perbedaan PHQ-9 antara short sleeper dan normal sleeper
        H₁: Short sleeper memiliki PHQ-9 lebih tinggi (one-tailed)
        Metode: Mann-Whitney U (distribusi tidak normal → non-parametric)

    Test 2 — PHYSICALLY INACTIVE vs ACTIVE
        H₀: Tidak ada perbedaan PHQ-9 antara inaktif dan aktif
        H₁: Inaktif memiliki PHQ-9 lebih tinggi
        Metode: Mann-Whitney U

    Test 3 — GENDER DIFFERENCE
        H₀: PHQ-9 tidak berbeda antara pria dan wanita
        H₁: Ada perbedaan (two-tailed)
        Metode: Mann-Whitney U

    Test 4 — LIVING ALONE vs WITH PARTNER
        H₀: Status tinggal sendiri tidak mempengaruhi PHQ-9
        Metode: Mann-Whitney U

    Test 5 — SLEEP DISORDER (diagnosed) vs NO DISORDER
        Metode: Mann-Whitney U

    Test 6 — INCOME GROUPS (Low vs High PIR) → Depression rate
        H₀: Proportion PHQ≥10 tidak berbeda antar income group
        Metode: Chi-square test of proportions

    Test 7 — ALCOHOL (binge) vs NON-BINGE
        Metode: Mann-Whitney U

    Output:
        DataFrame ringkasan dengan kolom: test_name, group_a_n, group_b_n,
        group_a_mean, group_b_mean, statistic, p_value, effect_size,
        significant, interpretation

    Effect size: Cohen's d (untuk U-test menggunakan rank-biserial correlation r)
        r = 1 - (2U)/(n₁n₂)
        |r| < 0.1 = negligible, 0.1-0.3 = small, 0.3-0.5 = medium, > 0.5 = large

    Args:
        df:         pd.DataFrame final.
        output_dir: Direktori output.

    Returns:
        pd.DataFrame: Tabel ringkasan hasil A/B test.
    """
    print("\n" + "=" * 60)
    print("A/B TESTING — HYPOTHESIS TESTING")
    print("=" * 60)
    ALPHA = 0.05

    results = []

    def mann_whitney_test(name, group_a, group_b, alternative="greater"):
        """
        Helper: Mann-Whitney U test dengan effect size rank-biserial r.
        Shapiro-Wilk pada subsample untuk konfirmasi non-normalitas
        """
        sample_a = group_a.sample(min(50, len(group_a)), random_state=42)
        sample_b = group_b.sample(min(50, len(group_b)), random_state=42)
        _, p_norm_a = shapiro(sample_a)
        _, p_norm_b = shapiro(sample_b)

        stat, p_val = mannwhitneyu(group_a, group_b, alternative=alternative)

        # Rank-biserial correlation (effect size)
        n_a, n_b = len(group_a), len(group_b)
        r = 1 - (2 * stat) / (n_a * n_b)
        r = abs(r)
        if r < 0.1:   effect_label = "Negligible"
        elif r < 0.3: effect_label = "Small"
        elif r < 0.5: effect_label = "Medium"
        else:         effect_label = "Large"

        return {
            "test_name":   name,
            "test_type":   "Mann-Whitney U",
            "alternative": alternative,
            "group_a_n":   n_a,
            "group_b_n":   n_b,
            "group_a_mean": round(group_a.mean(), 3),
            "group_b_mean": round(group_b.mean(), 3),
            "group_a_median": round(group_a.median(), 3),
            "group_b_median": round(group_b.median(), 3),
            "statistic":   round(stat, 2),
            "p_value":     round(p_val, 6),
            "effect_size_r": round(r, 4),
            "effect_label": effect_label,
            "normal_a":    p_norm_a > 0.05,
            "normal_b":    p_norm_b > 0.05,
            "significant": p_val < ALPHA,
            "interpretation": (
                f"{'REJECT H₀' if p_val < ALPHA else 'FAIL TO REJECT H₀'}: "
                f"p={p_val:.4f} ({'significant' if p_val < ALPHA else 'not significant'}) "
                f"| Effect: {effect_label} (r={r:.3f})"
            ),
        }

    def chi2_test(name, group_col, outcome_col):
        """Helper: Chi-square test untuk proporsi biner."""
        ct = pd.crosstab(df[group_col], df[outcome_col])
        chi2, p_val, dof, expected = chi2_contingency(ct)
        # Cramér's V effect size
        n = ct.sum().sum()
        min_dim = min(ct.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0

        if cramers_v < 0.1:   effect_label = "Negligible"
        elif cramers_v < 0.3: effect_label = "Small"
        elif cramers_v < 0.5: effect_label = "Medium"
        else:                  effect_label = "Large"

        return {
            "test_name":   name,
            "test_type":   "Chi-Square",
            "alternative": "two-sided",
            "group_a_n":   ct.iloc[0].sum(),
            "group_b_n":   ct.iloc[1].sum() if len(ct) > 1 else 0,
            "group_a_mean": round(ct.iloc[0, 1] / ct.iloc[0].sum(), 3) if 1 in ct.columns else 0,
            "group_b_mean": round(ct.iloc[1, 1] / ct.iloc[1].sum(), 3) if (1 in ct.columns and len(ct) > 1) else 0,
            "group_a_median": None,
            "group_b_median": None,
            "statistic":   round(chi2, 2),
            "p_value":     round(p_val, 6),
            "effect_size_r": round(cramers_v, 4),
            "effect_label": effect_label,
            "normal_a":    None,
            "normal_b":    None,
            "significant": p_val < ALPHA,
            "interpretation": (
                f"{'REJECT H₀' if p_val < ALPHA else 'FAIL TO REJECT H₀'}: "
                f"p={p_val:.4f} | Cramér's V={cramers_v:.3f} ({effect_label})"
            ),
        }

    # Test 1: Short Sleeper vs Normal
    a1 = df.loc[df["SHORT_SLEEPER"] == 0, "PHQ9_SCORE"]
    b1 = df.loc[df["SHORT_SLEEPER"] == 1, "PHQ9_SCORE"]
    r1 = mann_whitney_test("Short Sleeper vs Normal (PHQ-9)", a1, b1, "less")
    r1["group_a_label"] = "Normal sleeper (≥6h)"
    r1["group_b_label"] = "Short sleeper (<6h)"
    results.append(r1)

    # Test 2: Physically Inactive vs Active
    a2 = df.loc[df["PHYSICALLY_INACTIVE"] == 0, "PHQ9_SCORE"]
    b2 = df.loc[df["PHYSICALLY_INACTIVE"] == 1, "PHQ9_SCORE"]
    r2 = mann_whitney_test("Inactive vs Active (PHQ-9)", a2, b2, "less")
    r2["group_a_label"] = "Active (≥150 MET-min)"
    r2["group_b_label"] = "Inactive (<150 MET-min)"
    results.append(r2)

    # Test 3: Gender difference
    a3 = df.loc[df["GENDER"] == 1, "PHQ9_SCORE"]  # Male
    b3 = df.loc[df["GENDER"] == 2, "PHQ9_SCORE"]  # Female
    r3 = mann_whitney_test("Male vs Female (PHQ-9)", a3, b3, "two-sided")
    r3["group_a_label"] = "Male"
    r3["group_b_label"] = "Female"
    results.append(r3)

    # Test 4: Living alone vs With Partner
    a4 = df.loc[df["LIVING_ALONE"] == 0, "PHQ9_SCORE"]
    b4 = df.loc[df["LIVING_ALONE"] == 1, "PHQ9_SCORE"]
    r4 = mann_whitney_test("With partner vs Living alone (PHQ-9)", a4, b4, "less")
    r4["group_a_label"] = "With partner/married"
    r4["group_b_label"] = "Living alone"
    results.append(r4)

    # Test 5: Sleep Disorder (diagnosed)
    a5 = df.loc[df["SLEEP_DISORDERED"] == 0, "PHQ9_SCORE"]
    b5 = df.loc[df["SLEEP_DISORDERED"] == 1, "PHQ9_SCORE"]
    r5 = mann_whitney_test("No disorder vs Sleep disordered (PHQ-9)", a5, b5, "less")
    r5["group_a_label"] = "No sleep disorder"
    r5["group_b_label"] = "Has sleep disorder"
    results.append(r5)

    # Test 6: Income group (chi-square)
    df["INCOME_BINARY"] = (df["PIR"] < 1.5).astype(int)
    r6 = chi2_test("Low vs High Income (Depression Rate)", "INCOME_BINARY", "PHQ9_BINARY")
    r6["group_a_label"] = "Higher income (PIR ≥ 1.5)"
    r6["group_b_label"] = "Low income (PIR < 1.5)"
    results.append(r6)

    # Test 7: Binge Drinker vs Non-Binge
    a7 = df.loc[df["BINGE_DRINKER"] == 0, "PHQ9_SCORE"]
    b7 = df.loc[df["BINGE_DRINKER"] == 1, "PHQ9_SCORE"]
    r7 = mann_whitney_test("Non-binge vs Binge drinker (PHQ-9)", a7, b7, "less")
    r7["group_a_label"] = "Non-binge drinker"
    r7["group_b_label"] = "Binge drinker"
    results.append(r7)

    # Test 8: Sedentary High vs Low
    a8 = df.loc[df["SEDENTARY_HIGH"] == 0, "PHQ9_SCORE"]
    b8 = df.loc[df["SEDENTARY_HIGH"] == 1, "PHQ9_SCORE"]
    r8 = mann_whitney_test("Low sedentary vs High sedentary (PHQ-9)", a8, b8, "less")
    r8["group_a_label"] = "Sedentary ≤8h/day"
    r8["group_b_label"] = "Sedentary >8h/day"
    results.append(r8)

    # Compile results
    result_df = pd.DataFrame(results)

    # Print summary
    print(f"\n  {'TEST NAME':<50} {'SIG':>4}  {'p-value':>9}  {'EFFECT':>10}  INTERPRET")
    print("  " + "─" * 100)
    for _, row in result_df.iterrows():
        sig_mark = "✓" if row["significant"] else "✗"
        print(f"  {row['test_name']:<50} {sig_mark:>4}  "
              f"{row['p_value']:>9.5f}  {row['effect_label']:>10}  {row['interpretation'][:60]}")

    # Visualization
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("A/B Testing: PHQ-9 Score by Risk Factor Groups\n(NHANES 2017-2018)",
                 fontsize=14, fontweight="bold")

    test_pairs = [
        ("SHORT_SLEEPER", "PHQ9_SCORE", "Short Sleeper", ["Normal (≥6h)", "Short (<6h)"]),
        ("PHYSICALLY_INACTIVE", "PHQ9_SCORE", "Physical Activity", ["Active", "Inactive"]),
        ("GENDER_F", "PHQ9_SCORE", "Gender", ["Male", "Female"]),
        ("LIVING_ALONE", "PHQ9_SCORE", "Living Situation", ["W/ Partner", "Alone"]),
        ("SLEEP_DISORDERED", "PHQ9_SCORE", "Sleep Disorder", ["No Disorder", "Diagnosed"]),
        ("BINGE_DRINKER", "PHQ9_SCORE", "Alcohol (Binge)", ["Non-Binge", "Binge"]),
    ]

    for idx, (group_col, outcome_col, title, labels) in enumerate(test_pairs):
        ax = axes[idx // 3][idx % 3]
        if group_col not in df.columns:
            continue
        groups = [df.loc[df[group_col] == v, outcome_col].dropna() for v in [0, 1]]
        bplot = ax.boxplot(groups, labels=labels, patch_artist=True,
                           medianprops=dict(color="white", linewidth=2))
        colors_box = ["#2dd4a0", "#ef4444"]
        for patch, color in zip(bplot["boxes"], colors_box):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Annotate p-value
        test_row = result_df[result_df["test_name"].str.startswith(
            title.split("(")[0].strip())]
        if len(test_row) > 0:
            p = test_row.iloc[0]["p_value"]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            ax.set_title(f"{title}\n(p={p:.4f} {sig})", fontsize=10)
        else:
            ax.set_title(title, fontsize=10)

        ax.set_ylabel("PHQ-9 Score")

    plt.tight_layout()
    save_figure(fig, "ab_test_boxplots", output_dir)

    # Save result table
    save_artifact(result_df, "ab_test_results", output_dir)

    return result_df

if __name__ == "__main__":
    run_ab_test()