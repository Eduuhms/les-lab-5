"""
Statistical analysis of experiment results.

Reads results/results.csv and produces:
  - Descriptive statistics per scenario × API type
  - Shapiro-Wilk normality test
  - Wilcoxon signed-rank test (or paired t-test if data is normal)
  - Cohen's d effect size
  - Summary CSVs in results/

Usage:
    python analyze.py
"""

import os
import sys
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
import numpy as np
from scipy import stats

RESULTS_FILE = os.path.join("results", "results.csv")

SCENARIO_LABELS = {
    "single_book_card": "Single Book — Card View",
    "book_list": "Book List (10 items)",
    "book_full_detail": "Single Book — Detail View",
}


def divider(char="─", width=70):
    print(char * width)


def section(title: str):
    print()
    divider("═")
    print(f"  {title}")
    divider("═")


def describe(series: pd.Series, label: str):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    print(f"  {label}:")
    print(f"    N        : {len(series)}")
    print(f"    Média    : {series.mean():.4f}")
    print(f"    Mediana  : {series.median():.4f}")
    print(f"    Desvio P.: {series.std():.4f}")
    print(f"    Mín      : {series.min():.4f}")
    print(f"    Máx      : {series.max():.4f}")
    print(f"    IIQ (Q1–Q3): {q1:.4f} – {q3:.4f}")


def cohens_d(a: pd.Series, b: pd.Series) -> float:
    pooled = np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
    return (a.mean() - b.mean()) / pooled if pooled > 0 else 0.0


def effect_label(d: float) -> str:
    ad = abs(d)
    if ad < 0.2:
        return "negligível"
    if ad < 0.5:
        return "pequeno"
    if ad < 0.8:
        return "médio"
    return "grande"


def analyse_metric(df: pd.DataFrame, col: str, col_label: str, unit: str) -> pd.DataFrame:
    section(f"RQ — {col_label} ({unit})")
    rows = []

    for scenario_key, scenario_label in SCENARIO_LABELS.items():
        sub = df[df["scenario"] == scenario_key]
        if sub.empty:
            continue

        rest = sub[sub["api_type"] == "REST"][col]
        gql = sub[sub["api_type"] == "GraphQL"][col]

        print(f"\n── Cenário: {scenario_label}")
        describe(rest, "REST")
        describe(gql, "GraphQL")

        # Normality
        _, p_rest = stats.shapiro(rest)
        _, p_gql = stats.shapiro(gql)
        print(f"\n  Shapiro-Wilk:")
        print(f"    REST    p={p_rest:.4f}  ({'normal' if p_rest > 0.05 else 'não-normal'})")
        print(f"    GraphQL p={p_gql:.4f}  ({'normal' if p_gql > 0.05 else 'não-normal'})")

        # Significance test — choose based on normality
        both_normal = p_rest > 0.05 and p_gql > 0.05
        if both_normal:
            stat, p_val = stats.ttest_rel(rest.values, gql.values)
            test_name = "t de Student pareado"
        else:
            stat, p_val = stats.wilcoxon(rest.values, gql.values)
            test_name = "Wilcoxon com sinal e postos"

        print(f"\n  {test_name}: estatística={stat:.4f}, p={p_val:.6f}")

        alpha = 0.05
        reject = p_val < alpha
        if reject:
            if rest.median() > gql.median():
                direction = "GraphQL menor/mais rápido"
            else:
                direction = "REST menor/mais rápido"
            conclusion = f"Rejeitar H₀ — diferença significativa ({direction})"
        else:
            conclusion = "Não rejeitar H₀ — sem diferença significativa"

        d = cohens_d(rest, gql)
        print(f"  Conclusão (α={alpha}): {conclusion}")
        print(f"  Tamanho de efeito (Cohen's d): {d:.4f}  [{effect_label(d)}]")

        pct_diff = (rest.median() - gql.median()) / rest.median() * 100 if rest.median() != 0 else 0

        rows.append(
            {
                "Cenário": scenario_label,
                "REST_média": round(rest.mean(), 4),
                "GQL_média": round(gql.mean(), 4),
                "REST_mediana": round(rest.median(), 4),
                "GQL_mediana": round(gql.median(), 4),
                "Redução(%)": round(pct_diff, 2),
                "p_valor": round(p_val, 6),
                "Significativo": "Sim" if reject else "Não",
                "Cohen_d": round(d, 4),
                "Efeito": effect_label(d),
            }
        )

    return pd.DataFrame(rows)


def main():
    if not os.path.exists(RESULTS_FILE):
        print(f"ERRO: {RESULTS_FILE} não encontrado.")
        print("Execute experiment.py primeiro.")
        sys.exit(1)

    df = pd.read_csv(RESULTS_FILE)
    print(f"\nCarregadas {len(df)} medições de {RESULTS_FILE}")
    print(f"Cenários  : {sorted(df['scenario'].unique())}")
    print(f"Tipos     : {sorted(df['api_type'].unique())}")
    counts = df.groupby(["scenario", "api_type"]).size()
    print(f"Trials por combinação:\n{counts.to_string()}")

    time_summary = analyse_metric(df, "response_time_ms", "Tempo de Resposta", "ms")
    size_summary = analyse_metric(df, "response_size_bytes", "Tamanho de Resposta", "bytes")

    section("Resumo Final")
    print("\n── RQ1: Tempo de Resposta")
    print(time_summary.to_string(index=False))
    print("\n── RQ2: Tamanho de Resposta")
    print(size_summary.to_string(index=False))

    time_summary.to_csv("results/summary_time.csv", index=False, encoding="utf-8")
    size_summary.to_csv("results/summary_size.csv", index=False, encoding="utf-8")
    print("\nResumos salvos em results/summary_time.csv e results/summary_size.csv")


if __name__ == "__main__":
    main()
