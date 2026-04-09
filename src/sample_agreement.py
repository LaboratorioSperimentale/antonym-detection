import argparse
import pandas as pd
import numpy as np


def stratified_sample_2d(
    df,
    n_total,
    strata_cols=("pattern", "pair"),
    random_state=42,
    prioritize="random" 
):
    counts = (
        df.groupby(list(strata_cols))
        .size()
        .reset_index(name="N")
    )


    n_strata = len(counts)


    if prioritize == "rare":
        counts = counts.sort_values("N", ascending=True).reset_index(drop=True)
    elif prioritize == "frequent":
        counts = counts.sort_values("N", ascending=False).reset_index(drop=True)
    elif prioritize == "random":
        counts = counts.sample(frac=1, random_state=random_state).reset_index(drop=True)
    else:
        raise ValueError("prioritize must be one of: rare, frequent, random")

    counts["final_alloc"] = 0

    # Dai 1 a quanti più strati possibile
    k = min(n_total, n_strata)
    counts.loc[:k-1, "final_alloc"] = 1

    sampled_parts = []

    for _, row in counts.iterrows():
        alloc = int(row["final_alloc"])
        if alloc == 0:
            continue

        mask = np.ones(len(df), dtype=bool)
        for c in strata_cols:
            mask &= df[c] == row[c]

        group_df = df.loc[mask]

        sampled_group = group_df.sample(
            n=alloc,
            random_state=random_state
        )
        sampled_parts.append(sampled_group)

    sampled_df = pd.concat(sampled_parts, ignore_index=True)

    allocation_df = counts[list(strata_cols) + ["N", "final_alloc"]].rename(
        columns={"N": "population", "final_alloc": "sample_n"}
    )

    return sampled_df, allocation_df


def main():
    parser = argparse.ArgumentParser(description="2D stratified sampling from CSV")

    parser.add_argument("input_file", help="Input CSV file")
    parser.add_argument("output_file", help="Output sampled CSV file")

    parser.add_argument("--n", type=int, default=100, help="Total sample size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")


    parser.add_argument(
        "--strata_cols",
        nargs=2,
        default=["pattern", "pair"],
        help="Columns for stratification (2D)"
    )



    args = parser.parse_args()

    # load data

    df = pd.read_csv(args.input_file, sep="\t")

    # sampling
    sampled_df, allocation_df = stratified_sample_2d(
        df,
        n_total=args.n,
        strata_cols=tuple(args.strata_cols),

        random_state=args.seed
    )

    # save outputs
    sampled_df.to_csv(args.output_file, sep="\t", index=False)
    allocation_df.to_csv(args.output_file + ".allocation.tsv", sep="\t", index=False)

    print("\nTop strata by sample size:")
    print(allocation_df.sort_values("sample_n", ascending=False).head(20))

    print("\nTotal sampled:", len(sampled_df))


if __name__ == "__main__":
    main()