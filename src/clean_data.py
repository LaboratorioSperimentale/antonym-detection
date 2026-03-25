import html
import re
import tqdm
import pandas as pd


def detokenize(text):
	if not isinstance(text, str):
		return text

	# Decode HTML entities (&quot; → ", &amp; → &, etc.)
	text = html.unescape(text)

	# Fix apostrophes: word ' word → word'word (but not "po'" which is a standalone word)
	text = re.sub(r"\b(\w+) ' (\w)", lambda m: m.group(1) + "'" + m.group(2) if m.group(1).lower() != "po" else m.group(0), text)
	text = re.sub(r"(\w) '(\s|$)", r"\1'\2", text)

	# Remove space before punctuation
	text = re.sub(r"\s+([,;:!?.])", r"\1", text)

	# Remove space after opening bracket/parenthesis
	text = re.sub(r"([\(\[«])\s+", r"\1", text)

	# Remove space before closing bracket/parenthesis
	text = re.sub(r"\s+([\)\]»])", r"\1", text)

	return text.strip()


def apply_detokenize(df):
	df = df.copy()
	for col in ["text", "context_pre", "costr", "context_post"]:
		if col in df.columns:
			df[col] = df[col].apply(detokenize)
	return df


def clean_underscore(df_dedup):
	df_dedup = df_dedup.copy()
	for col in ["text", "context_pre", "costr", "context_post"]:
		if col in df_dedup.columns:
			df_dedup[col] = df_dedup[col].str.replace(r"(?<=[\w'])_(?=[\w'])", " ", regex=True)
	return df_dedup


def find_adjective(df_dedup):

	rows_to_remove = set()
	df_dedup["pair"] =  df_dedup["X"] + f" - " + df_dedup["Y"]

	df_dedup["X_lemma"] = df_dedup["X"]
	df_dedup["Y_lemma"] = df_dedup["Y"]

	for index, row in tqdm.tqdm(df_dedup.iterrows(), desc="Finding adjectives"):

		df_dedup.at[index, "context_pre"] = "__MISSING__"
		df_dedup.at[index, "costr"] = "__MISSING__"
		df_dedup.at[index, "context_post"] = "__MISSING__"

		# if row["text"] == "":
		# 	rows_to_remove.add(row)
		# 	continue

		query = str(row["query"])
		text = str(row["text"])

		row["X_found"] = row["X"]
		row["Y_found"] = row["Y"]
		row["matched_pattern"] = ""

		prefix = row["pattern"].split("X")[0]
		inner = row["pattern"].split("X")[1].split("Y")[0]
		suffix = row["pattern"].split("Y")[-1]

		# if row["class"] == "yes":
		# 	continue
		any_match=False
		match_yes = re.search(
			r'\[lemma="([^"]+)"\s*&\s*pos="ADJ"\](?:\[word="[^"]+"\])+\[lemma="([^"]+)"\s*&\s*pos="ADJ"\]',
			query,
			flags=re.IGNORECASE
		)

		if match_yes:
			any_match = True
			adj_1 = match_yes.group(1)
			middle_word = inner.strip()
			adj_2 = match_yes.group(2)

			adj_1_regex = lemma_to_regex(adj_1)
			adj_2_regex = lemma_to_regex(adj_2)

			pattern = rf'\b({adj_1_regex})\s+({re.escape(middle_word)})\s+({adj_2_regex})\b'
			match_text = re.search(pattern, text)

			if match_text:
				found_x = match_text.group(1)
				found_y = match_text.group(3)
				df_dedup.at[index, "X_found"] = found_x
				df_dedup.at[index, "Y_found"] = found_y

				costr = prefix + match_text.group(1) + " " + match_text.group(2) + " " + match_text.group(3) + suffix

				df_dedup.at[index, "context_pre"] = text.split(costr)[0]
				df_dedup.at[index, "costr"] = costr

				df_dedup.at[index, "context_post"] = text.split(costr)[1]
			else:
				rows_to_remove.add(index)

		match1 = re.search(
			r'\[lemma="([^"]+)"\s*&\s*pos="ADJ"\](?:\[word="[^"]+"\])+\[lemma!="([^"]+)"\s*&\s*pos="ADJ"\]',
			query,
			flags=re.IGNORECASE
		)

		if match1:
			any_match = True
			adj_1 = match1.group(1)
			middle_word = inner.strip()
			adj_2 = match1.group(2)

			adj_1_regex = lemma_to_regex(adj_1)

			pattern = rf'\b({adj_1_regex})\s+({re.escape(middle_word)})\s+(\w+)\b'
			match_text = re.search(pattern, text)

			if match_text:
				found_x = match_text.group(1)
				found_y = match_text.group(3)
				df_dedup.at[index, "X_found"] = found_x
				df_dedup.at[index, "Y_found"] = found_y

				costr = prefix + match_text.group(1) + " " + match_text.group(2)	+ " " + match_text.group(3) + suffix

				df_dedup.at[index, "context_pre"] = text.split(costr)[0]
				df_dedup.at[index, "costr"] = costr
				df_dedup.at[index, "context_post"] = text.split(costr)[1]
			else:
				rows_to_remove.add(index)

		match2 = re.search(
			r'\[lemma!="([^"]+)"\s*&\s*pos="ADJ"\](?:\[word="[^"]+"\])+\[lemma="([^"]+)"\s*&\s*pos="ADJ"\]',
			query,
			flags=re.IGNORECASE
		)

		if match2:
			any_match = True
			adj_1 = match2.group(1)
			middle_word = inner.strip()
			adj_2 = match2.group(2)

			adj_2_regex = lemma_to_regex(adj_2)

			pattern = rf'\b(\w+)\s+({re.escape(middle_word)})\s+({adj_2_regex})\b'
			match_text = re.search(pattern, text)
			if match_text:
				found_x = match_text.group(1)
				found_y = match_text.group(3)
				df_dedup.at[index, "X_found"] = found_x
				df_dedup.at[index, "Y_found"] = found_y

				costr = prefix + match_text.group(1) + " " + match_text.group(2)	+ " " + match_text.group(3) + suffix
				df_dedup.at[index, "context_pre"] = text.split(costr)[0]
				df_dedup.at[index, "costr"] = costr
				df_dedup.at[index, "context_post"] = text.split(costr)[1]
			else:
				rows_to_remove.add(index)

		if not any_match:
			print(f"ISSUE")
			print(row)
			input()

	df_removed = df_dedup.loc[list(rows_to_remove)]
	df_dedup = df_dedup.drop(index=list(rows_to_remove))

	return df_dedup, df_removed

def lemma_to_regex(lemma):
	return re.escape(lemma[:-1]) + r'\w*'

def is_contained(short_q, long_q):
	return short_q != long_q and short_q in long_q

def deduplicate_by_most_specific_query(df):

	rows_to_remove = set()

	for _, group in tqdm.tqdm(df.groupby("text"), desc="Deduplicating"):

		indices = group.index.tolist()
		for i in indices:
			for j in indices:
				if i != j:
					q_i = str(df.loc[i, "query"])
					q_j = str(df.loc[j, "query"])

					if is_contained(q_i, q_j):
						rows_to_remove.add(i)
						# break

	df_removed = df.loc[list(rows_to_remove)]
	df_dedup = df.drop(index=list(rows_to_remove))

	# Drop any remaining duplicates by sent_id (different patterns, neither a substring of the other)
	# keeping the row with the longest (most specific) query
	# df_dedup = df_dedup.sort_values("query", key=lambda s: s.str.len(), ascending=False)
	# extra_removed = df_dedup[df_dedup.duplicated(subset=["sent_id"], keep="first")]
	# df_removed = pd.concat([df_removed, extra_removed])
	# df_dedup = df_dedup.drop_duplicates(subset=["sent_id"], keep="first")

	return df_dedup, df_removed


if __name__ == "__main__":

	df = pd.read_csv("data/output.tsv", sep="\t", dtype = str)
	n_before = len(df)
	df = df.dropna(subset=["text"])

	print("=== STEP 0: empty text removal ===")
	print(f"Removed: {n_before - len(df)} rows ({n_before} → {len(df)})")

	n_before = len(df)
	df = df[df["text"].str.split().str.len().between(10, 100)]
	print("=== STEP 0b: sentence length filter (10–100 tokens) ===")
	print(f"Removed: {n_before - len(df)} rows ({n_before} → {len(df)})")

	df_dedup, df_removed = deduplicate_by_most_specific_query(df)
	print("=== STEP 1: deduplication ===")
	if len(df_removed) > 0:
		print(f"Removed: {len(df_removed)} rows")
	else:
		print("Nessuna riga eliminata.")

	df_dedup, df_removed2 = find_adjective(df_dedup)
	print("=== STEP 2: find adjectives ===")
	if len(df_removed2) > 0:
		print(f"Removed: {len(df_removed2)} rows (pattern not found in text)")

	df_dedup = clean_underscore(df_dedup)
	df_dedup = apply_detokenize(df_dedup)

	cols = ["class", "pattern", "X_found", "Y_found",
        "pair", "query", "sent_id",
        "context_pre", "costr", "context_post"]
	df_dedup = df_dedup[cols]

	df_dedup.to_csv("data/output_clean.tsv", sep="\t", index=False)
	print(f"=== DONE: {len(df_dedup)} rows written to data/output_clean.tsv ===")

	print("\n=== STATS: 'yes' instances per (pattern, pair) ===")
	yes_counts = (
		df_dedup[df_dedup["class"] == "yes"]
		.groupby(["pattern", "pair"])
		.size()
		.reset_index(name="count")
		.sort_values("count", ascending=False)
	)
	yes_counts.to_csv("data/yes_instances.tsv", sep="\t", index=False)

	print("\n=== STATS: 'no' instances per (X_found, Y_found) ===")
	no_counts = (
		df_dedup[df_dedup["class"] == "no"]
		.groupby(["pattern", "pair"])
		.size()
		.reset_index(name="count")
		.sort_values("count", ascending=False)
	)
	no_counts.to_csv("data/no_instances.tsv", sep="\t", index=False)