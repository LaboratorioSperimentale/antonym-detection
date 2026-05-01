"""Compute pairwise Cohen's kappa (overall and per category) for each dataset."""

import csv
import pathlib
from collections import Counter
from itertools import combinations

ANNOTATORS = ["GG", "LS", "LP"]
DATASETS = ["eng_neg", "eng_pos", "ita_neg", "ita_pos"]
DATA_DIR = pathlib.Path("data/agreement")
LABEL_COL = "antonymous_value"
OUT_PATH = DATA_DIR / "agreement_results.tsv"


def cohen_kappa(a: list[str], b: list[str]) -> float:
    assert len(a) == len(b)
    n = len(a)
    labels = sorted(set(a) | set(b))
    p_o = sum(x == y for x, y in zip(a, b)) / n
    count_a = Counter(a)
    count_b = Counter(b)
    p_e = sum((count_a[l] / n) * (count_b[l] / n) for l in labels)
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1 - p_e)


def cohen_kappa_binary(a: list[str], b: list[str], label: str) -> float:
    """Binary κ: label vs. rest."""
    a_bin = [label if x == label else "OTHER" for x in a]
    b_bin = [label if x == label else "OTHER" for x in b]
    return cohen_kappa(a_bin, b_bin)


def load_labels(path: pathlib.Path) -> dict[str, dict[str, str]]:
    data: dict[str, dict[str, str]] = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            sid = row["sent_id"]
            data[sid] = {ann: row[f"{LABEL_COL}_{ann}"] for ann in ANNOTATORS}
    return data


if __name__ == "__main__":
    out_rows = []

    for dataset in DATASETS:
        data = load_labels(DATA_DIR / f"{dataset}.csv")
        sids = list(data)
        labels = {ann: [data[sid][ann] for sid in sids] for ann in ANNOTATORS}
        all_labels = sorted(set(l for ann in ANNOTATORS for l in labels[ann] if l))

        print(f"\n{dataset} (n={len(sids)})")

        header = f"  {'':6}" + "".join(f"{l:>14}" for l in all_labels)
        print(header)
        for ann in ANNOTATORS:
            counts = Counter(labels[ann])
            row = f"  {ann:6}" + "".join(f"{counts.get(l, 0):>14}" for l in all_labels)
            print(row)

        for ann_a, ann_b in combinations(ANNOTATORS, 2):
            k_overall = cohen_kappa(labels[ann_a], labels[ann_b])
            print(f"  {ann_a} vs {ann_b}: κ = {k_overall:.4f}")
            out_rows.append({
                "dataset": dataset,
                "pair": f"{ann_a}_vs_{ann_b}",
                "category": "OVERALL",
                "kappa": round(k_overall, 4),
            })
            for lbl in all_labels:
                k_lbl = cohen_kappa_binary(labels[ann_a], labels[ann_b], lbl)
                out_rows.append({
                    "dataset": dataset,
                    "pair": f"{ann_a}_vs_{ann_b}",
                    "category": lbl,
                    "kappa": round(k_lbl, 4),
                })

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["dataset", "pair", "category", "kappa"],
                                delimiter="\t")
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"\nResults written to {OUT_PATH}")
