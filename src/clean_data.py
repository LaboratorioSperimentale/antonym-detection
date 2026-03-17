import pandas as pd 
import re
from simplemma import lemmatize
import tqdm


def clean_underscore(df_dedup):
	df_dedup = df_dedup.copy()
	df_dedup["text"] = df_dedup["text"].str.replace(r"(?<=[\w'])_(?=[\w'])", " ", regex=True)
	return df_dedup


def find_adjective(df_dedup):

	rows_to_remove = set()

	for index, row in tqdm.tqdm(df_dedup.iterrows(), desc="Finding adjectives"):

		df_dedup.at[index, "context_pre"] = "__MISSING__"
		df_dedup.at[index, "costr"] = "__MISSING__"
		df_dedup.at[index, "context_post"] = "__MISSING__"
		
		if row["text"] == "":
			rows_to_remove.add(row)
			continue

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
			# middle_word = match_yes.group(2)
			middle_word = inner.strip()
			adj_2 = match_yes.group(2)

			adj_1_regex = lemma_to_regex(adj_1)
			adj_2_regex = lemma_to_regex(adj_2)

			pattern = rf'\b({adj_1_regex})\s+({re.escape(middle_word)})\s+({adj_2_regex})\b'
			match_text = re.search(pattern, text)

			if match_text:
				found_x = match_text.group(1)
				found_y = match_text.group(3)
				# lemma_y = lemmatize(found_y, "it")
				# df_dedup.at[index, "Y"] = lemma_y
				df_dedup.at[index, "X"] = found_x
				df_dedup.at[index, "Y"] = found_y

				costr = prefix + match_text.group(1) + " " + match_text.group(2) + " " + match_text.group(3) + suffix
    
				df_dedup.at[index, "context_pre"] = text.split(costr)[0]
				df_dedup.at[index, "costr"] = costr

				df_dedup.at[index, "context_post"] = text.split(costr)[1]
			else:
				rows_to_remove.add(index)
				# print(f"ISSUE")
				# print(row)
				# input()
			
		match1 = re.search(
			r'\[lemma="([^"]+)"\s*&\s*pos="ADJ"\](?:\[word="[^"]+"\])+\[lemma!="([^"]+)"\s*&\s*pos="ADJ"\]',
			query,
			flags=re.IGNORECASE
		)
		
		if match1:
			any_match = True
			adj_1 = match1.group(1)
			# middle_word = match_yes.group(2)
			middle_word = inner.strip()
			adj_2 = match1.group(2)

			adj_1_regex = lemma_to_regex(adj_1)

			pattern = rf'\b({adj_1_regex})\s+({re.escape(middle_word)})\s+(\w+)\b'
			match_text = re.search(pattern, text)

			if match_text:
				found_x = match_text.group(1)
				found_y = match_text.group(3)
				# lemma_y = lemmatize(found_y, "it")
				# df_dedup.at[index, "Y"] = lemma_y
				df_dedup.at[index, "X"] = found_x
				df_dedup.at[index, "Y"] = found_y

				costr = prefix + match_text.group(1) + " " + match_text.group(2)	+ " " + match_text.group(3) + suffix
	
				df_dedup.at[index, "context_pre"] = text.split(costr)[0]
				df_dedup.at[index, "costr"] = costr
				df_dedup.at[index, "context_post"] = text.split(costr)[1]
			else:
				rows_to_remove.add(index)
				# print(f"ISSUE")
				# print(row)
				# input()				

		match2 = re.search(
			r'\[lemma!="([^"]+)"\s*&\s*pos="ADJ"\](?:\[word="[^"]+"\])+\[lemma="([^"]+)"\s*&\s*pos="ADJ"\]',
			query,
			flags=re.IGNORECASE
		)

		if match2:
			any_match = True
			adj_1 = match2.group(1)
			# middle_word = match_yes.group(2)
			middle_word = inner.strip()
			adj_2 = match2.group(2)

			adj_2_regex = lemma_to_regex(adj_2)	

			pattern = rf'\b(\w+)\s+({re.escape(middle_word)})\s+({adj_2_regex})\b'
			match_text = re.search(pattern, text)
			if match_text:
				found_x = match_text.group(1)
				found_y = match_text.group(1)
				# lemma_x = lemmatize(found_x, "it")
				df_dedup.at[index, "X"] = found_x
				df_dedup.at[index, "Y"] = found_y

				costr = prefix + match_text.group(1) + " " + match_text.group(2)	+ " " + match_text.group(3) + suffix
				df_dedup.at[index, "context_pre"] = text.split(costr)[0]
				df_dedup.at[index, "costr"] = costr
				df_dedup.at[index, "context_post"] = text.split(costr)[1]
			else:
				rows_to_remove.add(index)
				# print(f"ISSUE")
				# print(row)
				# input()
    
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

	for text, group in tqdm.tqdm(df.groupby("text"), desc="Deduplicating"):

		indices = group.index.tolist()
		for i in indices:
			for j in indices:
				if i != j:
					q_i = str(df.loc[i, "query"])
					q_j = str(df.loc[j, "query"])

					if is_contained(q_i, q_j):
						rows_to_remove.add(i)
						break

	df_removed = df.loc[list(rows_to_remove)]	
	df_dedup = df.drop(index=list(rows_to_remove))

	return df_dedup, df_removed


if __name__ == "__main__":

	df = pd.read_csv("data/output.tsv", sep="\t", dtype = str)
	df = df.dropna(subset=["text"])

	df_dedup, df_removed = deduplicate_by_most_specific_query(df)
	df_dedup.to_csv("data/OLD_output_dedup.tsv", sep="\t", index=False)
	df_removed.to_csv("data/OLD_output_removed.tsv", sep="\t", index=False)

	print("=== RIGHE ELIMINATE ===")
	if len(df_removed) > 0:
		print(f"Removed: {len(df_removed)} rows")
	else: 
		print("Nessuna riga eliminata.")

	df_dedup, df_removed = find_adjective(df_dedup)
	df_removed.to_csv("data/OLD_output_removed_step2.tsv", sep="\t", index=False)
	df_dedup.to_csv("data/OLD_output_adjective.tsv", sep="\t", index=False)


	df_dedup = clean_underscore(df_dedup)

	df_dedup.to_csv("data/OLD_output_underscore.tsv", sep="\t", index=False)


# def build_pattern_regex(pattern, x_regex, y_regex):
# 	pattern = str(pattern).strip()



# 	regex = pattern

# 	# spazi normali -> uno o più spazi
# 	regex = regex.replace(" ", r"\s+")

# 	# punteggiatura specifica
# 	regex = regex.replace(",", r"\s*,\s*")
# 	regex = regex.replace("?", r"\?")
 
#  	# sostituzione placeholder
# 	regex = regex.replace("X", x_regex)
# 	regex = regex.replace("Y", y_regex)

# 	return regex


# def division(df_dedup):
# 	df_dedup = df_dedup.copy()
	
# 	df_dedup["context_pre"] = ""
# 	df_dedup["costr"] = ""
# 	df_dedup["context_post"] = ""
	
# 	for index, row in df_dedup.iterrows():
# 		text = str(row["text"])
# 		pattern = str(row["pattern"])
# 		x = str(row["X"])
# 		y = str(row["Y"])
	
# 		x_regex = lemma_to_regex(x)
# 		y_regex = lemma_to_regex(y)
	
# 		pattern_regex = build_pattern_regex(pattern, x_regex, y_regex)
# 		match = re.search(pattern_regex, text, flags=re.IGNORECASE)

# 		if match:
# 			start, end = match.span()
# 			df_dedup.at[index, "context_pre"] = text[:start]
# 			df_dedup.at[index, "costr"] = text[start:end]
# 			df_dedup.at[index, "context_post"] = text[end:]
   
# 		# else:
# 		# 	print(f"Pattern non trovato per riga {index}:")
# 		# 	print(f"Text: {text}")
# 		# 	print(f"Pattern: {pattern}")
# 		# 	print(f"X: {x}, Y: {y}")
# 		# 	print(f"Regex usato: {pattern_regex}")
# 		# 	input()

# 	return df_dedup

 
# df_dedup = division(df_dedup)

# df_dedup.to_csv("data/OLD_output_division.tsv", sep="\t", index=False)

	

	
	
# def clean_text():
# 	df_dedup = df_dedup.copy()
# togli spazi primo di punteggiatura
# togli spazi prima e dopo apostrofo 
# ma se prima di spazio prirma di apostrofo ce po, togli solo spazio ptima di apostrofo
# 	return df_dedup