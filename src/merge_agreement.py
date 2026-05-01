"""Merge per-annotator agreement CSVs into one file per dataset.

Joins on sent_id, adds individual antonymous_value columns per annotator,
and computes a majority-vote label.
"""

import csv
import pathlib
from collections import Counter

ANNOTATORS = ["GG", "LS", "LP"]
DATASETS = ["eng_neg", "eng_pos", "ita_neg", "ita_pos"]
DATA_DIR = pathlib.Path("data/agreement")

LABEL_COL = "antonymous_value"
BASE_COLS = ["sent_id", "class", "pattern", "X_found", "Y_found",
             "pair", "context_pre", "costr", "context_post"]


def majority_vote(labels: list[str]) -> str:
    valid = [l for l in labels if l]
    if not valid:
        return ""
    (winner, count), = Counter(valid).most_common(1)
    # with 3 annotators and binary labels there's always a majority,
    # but flag ties just in case
    if count == 1:
        return "DISAGREEMENT"
    return winner


LABEL_NORM = {"IDYPSINCRATIC": "IDIOSYNCRATIC"}


def normalize_label(label: str) -> str:
    return LABEL_NORM.get(label.strip(), label.strip())


def load_annotator(path: pathlib.Path) -> dict[str, dict]:
    rows = {}
    with open(path, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            sid = row["sent_id"].strip()
            if sid:
                row[LABEL_COL] = normalize_label(row[LABEL_COL])
                rows[sid] = row
    return rows


def merge_dataset(dataset: str) -> None:
    annotator_data = {
        ann: load_annotator(DATA_DIR / f"{dataset}_{ann}.csv")
        for ann in ANNOTATORS
    }

    # sent_ids present in all annotators
    common_ids = set.intersection(*(set(d) for d in annotator_data.values()))

    # preserve order from first annotator, keeping only common ids
    first_ann = ANNOTATORS[0]
    ordered_ids = [sid for sid in annotator_data[first_ann] if sid in common_ids]

    out_cols = BASE_COLS + [f"{LABEL_COL}_{ann}" for ann in ANNOTATORS] + ["majority_vote"]
    out_path = DATA_DIR / f"{dataset}.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_cols)
        writer.writeheader()
        for sid in ordered_ids:
            base = {col: annotator_data[first_ann][sid].get(col, "") for col in BASE_COLS}
            labels = [annotator_data[ann][sid].get(LABEL_COL, "").strip() for ann in ANNOTATORS]
            label_cols = {f"{LABEL_COL}_{ann}": lbl for ann, lbl in zip(ANNOTATORS, labels)}
            writer.writerow({**base, **label_cols, "majority_vote": majority_vote(labels)})

    print(f"Wrote {len(ordered_ids)} rows → {out_path}")


if __name__ == "__main__":
    for dataset in DATASETS:
        merge_dataset(dataset)
