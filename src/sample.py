# import math
import pandas as pd
import argparse


# def balanced_sample(group_df, target):
# 	"""Sample `target` rows from group_df, distributed as evenly as possible
# 	across (X_found, Y_found) types to maximise lexical diversity."""
# 	subgroups = [
# 		subdf for _, subdf in group_df.groupby(["X_found", "Y_found"])
# 	]
# 	# Sort ascending so smallest groups get their full quota first,
# 	# letting the remaining budget flow to larger groups.
# 	subgroups.sort(key=len)

# 	samples = []
# 	remaining = target
# 	n_remaining = len(subgroups)

# 	for subdf in subgroups:
# 		if remaining == 0:
# 			break
# 		quota = math.ceil(remaining / n_remaining)
# 		take = min(quota, len(subdf))
# 		if take > 0:
# 			samples.append(subdf.sample(take, random_state=42))
# 		remaining -= take
# 		n_remaining -= 1

# 	return pd.concat(samples, ignore_index=True) if samples else pd.DataFrame(columns=group_df.columns)


# if __name__ == "__main__":
# 	yes_counts = pd.read_csv("data/yes_instances_eng.tsv", sep="\t")
# 	df = pd.read_csv("data/output_eng.tsv", sep="\t", dtype=str)

# 	df_yes = df[df["class"] == "yes"]
# 	df_no  = df[df["class"] == "no"]

# 	sampled_no_parts = []

# 	for _, row in yes_counts.iterrows():
# 		pattern   = row["pattern"]
# 		pair      = row["pair"]
# 		yes_count = int(row["count"])
# 		target    = yes_count * 2

# 		group_no = df_no[(df_no["pattern"] == pattern) & (df_no["pair"] == pair)]

# 		if len(group_no) == 0:
# 			print(f"WARNING: no 'no' instances for {pattern!r} / {pair!r} — skipping")
# 			continue

# 		if len(group_no) <= target:
# 			sampled = group_no.copy()
# 			if len(group_no) < target:
# 				print(f"  {pattern!r} / {pair!r}: requested {target}, only {len(group_no)} available — taking all")
# 		else:
# 			sampled = balanced_sample(group_no, target)

# 		n_types = group_no.groupby(["X_found", "Y_found"]).ngroups
# 		print(f"  {pattern!r} / {pair!r}: yes={yes_count}, sampled_no={len(sampled)} (from {n_types} X/Y types)")
# 		sampled_no_parts.append(sampled)

# 	df_sampled_no = pd.concat(sampled_no_parts, ignore_index=True) if sampled_no_parts else pd.DataFrame()

# 	df_out = pd.concat([df_yes, df_sampled_no], ignore_index=True)
# 	df_out = df_out.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
# 	df_out.to_csv("data/sample_eng.tsv", sep="\t", index=False)

# 	print(f"\nYes instances  : {len(df_yes)}")
# 	print(f"Sampled no     : {len(df_sampled_no)}")
# 	print(f"Total          : {len(df_out)}")
# 	print(f"Written to data/sample.tsv")








def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--input", default="data/output_clean_eng.tsv")
	parser.add_argument("--sep", default="\t")
	parser.add_argument("--output_yes", default="data/dataset/eng_positive.tsv")
	parser.add_argument("--output_no", default="data/dataset/eng_negatives.tsv")
	args = parser.parse_args()
 
	
	df = pd.read_csv(args.input, sep=args.sep, dtype=str)

	df_yes = df[df["class"] == "yes"].copy()

	sampled_yes = (
		df_yes.groupby(["pair", "pattern"], group_keys=False)
			.apply(lambda g: g.sample(n=min(len(g), 100), random_state=42))
			.reset_index(drop=True)
	)

	sampled_yes.to_csv(args.output_yes, args.sep, index=False)


	print(f"Yes originali: {len(df_yes)}")
	print(f"Yes campionate: {len(sampled_yes)}")


	df_no = df[df["class"] == "no"].copy()

	sampled_no = (
		df_no.groupby(["pair", "pattern"], group_keys=False)
			.apply(lambda g: g.sample(n=min(len(g), 150), random_state=42))
			.reset_index(drop=True)
	)

	sampled_no.to_csv(args.output_no, args.sep, index=False)

	print(f"NO originali: {len(df_no)}")
	print(f"NO campionate: {len(sampled_no)}")


if __name__ == "__main__":
	main()