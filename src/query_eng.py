import regex as re
from tqdm import tqdm
import glob
import pathlib

current_paragraph = []
regular_expression_positive = {}
regular_expression_negative = {}


def clean_token(token):

	token = re.sub(r'_.', '', token)

	token = re.sub(r"\s+([,;:!?.])", r"\1", token)

	token = re.sub(r"([\(\[«])\s+", r"\1", token)

	token = re.sub(r"\s+([\)\]»])", r"\1", token)

	token = re.sub(r"\s*'\s*", "'", token)

	return token


def valid_sentence_length(text, min_tokens=10, max_tokens=50):
	n_tokens = len(text.split())
	return min_tokens < n_tokens < max_tokens

def process_paragraph (current_paragraph,
                    regular_expression_positive,
                    regular_expression_negative):

	string_paragraph = " ".join(current_paragraph)

	for query in regular_expression_positive:
		match = re.search(query, string_paragraph)

		if match:
			X_found = match.group(1)
			Y_found = match.group(2)

			query_sentence = rf'[.?!]([^.?!]*)({query})([^.?!]*[.?!])'
			match = re.search(query_sentence, string_paragraph)
			x, y, pattern = regular_expression_positive[query]
			istance = "yes"

			if match:
				extraction = f"{istance}\t{pattern}\t{X_found}\t{Y_found}\t{x} - {y}\t{query}\t{match.group(1)}\t{match.group(2)}\t{match.group(5)}"
				extraction = clean_token(extraction)
				if valid_sentence_length(extraction):
					print(extraction, file = file_output)

	for query in regular_expression_negative:
		match = re.search(query, string_paragraph)
		if match:
			X_found = match.group(1)
			Y_found = match.group(2)
			# print("\nNEGATIVE MATCH")
			# print("query:", query)
			# print("Match:", match.group())
			# print("Paragraph:", string_paragraph)

			query_sentence = rf'[.?!]([^.?!]*)({query})([^.?!]*[.?!])'
			match = re.search(query_sentence, string_paragraph)
			x, y, pattern = regular_expression_negative[query]
			istance = "no"

			if match:
				extraction = f"{istance}\t{pattern}\t{X_found}\t{Y_found}\t{x} - {y}\t{query}\t{match.group(1)}\t{match.group(2)}\t{match.group(5)}"
				extraction = clean_token(extraction)
				if valid_sentence_length(extraction):
					print(extraction, file = file_output)

def generate_pattern_positive(x, y, prefix, inner, suffix):

	query = ''

	if prefix:
		prefix = prefix.strip().split()
		for el in prefix:
			query+=rf'{el}_. '

	query+= rf'({x})_j '


	if inner:
		inner = inner.strip().split()
		for el in inner:
			query+= rf'{el}_. '

	query+= rf'({y})_j '

	if suffix:
		suffix = suffix.strip().split()
		for el in suffix:
			query+= rf'{el}_. '

	return query.strip()


def generate_pattern_negative(x, y, prefix, inner, suffix, side):

	query = ''

	if prefix:
		prefix = prefix.strip().split()
		for el in prefix:
			query+=rf'{el}_. '

	if side == "left":

		query += rf'(?!{x})(\b\w+)_j '

	if side == "right":

		query+= rf'(\b{x})_j '

	if inner:
		inner = inner.strip().split()
		for el in inner:
			query+= rf'{el}_. '

	if side == "left":

		query+= rf'(\b{y})_j '

	if side == "right":

		query += rf'(?!{y})(\b\w+)_j '

	if suffix:
		suffix = suffix.strip().split()
		for el in suffix:
			query+= rf'{el}_. '

	return query.strip()


def extract_pattern(string):
	pattern = re.compile(r'^(?P<prefix>.*?)(?P<x>X)(?P<inner>.*?)(?P<y>Y)(?P<suffix>.*)$')
	# s = "abc X e Y def"

	m = pattern.search(string)

	prefix, inner, suffix = m.group("prefix"), m.group("inner"), m.group("suffix")
	return prefix, inner, suffix



if __name__ == "__main__":

	input_root = pathlib.Path("data/coca/")

	all_files = list(input_root.rglob("*.txt"))
	print(all_files)

	patterns_filename = "data/eng_patterns.txt"
	seeds_filename = "data/eng_seeds.txt"

	seeds = set()
	with open(seeds_filename) as fin:
		for line in fin:
			linesplit = line.strip().split()
			sorted_linesplit = sorted(linesplit)
			seeds.add((sorted_linesplit[0], sorted_linesplit[1]))

	patterns = {}

	with open(patterns_filename) as fin:
		for line in fin:
			line = line.strip()
			patterns[extract_pattern(line)]=line

	with open("data/eng_queries.txt", "w") as file_queries:

		print("class\tpattern\tX\tY\tquery", file=file_queries)

		for pattern in patterns:
			for x, y in seeds:
				positive_one = generate_pattern_positive(x, y, *pattern)
				positive_two = generate_pattern_positive(y, x, *pattern)

				regular_expression_positive[positive_one] = (x, y, patterns[pattern])
				regular_expression_positive[positive_two] = (x, y, patterns[pattern])

				negative_one = generate_pattern_negative(x, y, *pattern, "left")
				negative_two = generate_pattern_negative(x, y, *pattern, "right")
				negative_three = generate_pattern_negative(y, x, *pattern, "left")
				negative_four = generate_pattern_negative(y, x, *pattern, "right")

				regular_expression_negative[negative_one] = (x, y, patterns[pattern])
				regular_expression_negative[negative_two] = (x, y, patterns[pattern])
				regular_expression_negative[negative_three] = (x, y, patterns[pattern])
				regular_expression_negative[negative_four] = (x, y, patterns[pattern])

				print(f"yes\t{patterns[pattern]}\t{x}\t{y}\t{positive_one}", file=file_queries)
				print(f"yes\t{patterns[pattern]}\t{x}\t{y}\t{positive_two}", file=file_queries)
				print(f"no\t{patterns[pattern]}\t{x}\t{y}\t{negative_one}", file=file_queries)
				print(f"no\t{patterns[pattern]}\t{x}\t{y}\t{negative_two}", file=file_queries)
				print(f"no\t{patterns[pattern]}\t{x}\t{y}\t{negative_three}", file=file_queries)
				print(f"no\t{patterns[pattern]}\t{x}\t{y}\t{negative_four}", file=file_queries)

	with open ("data/output_eng.tsv", "w") as file_output:

		pbar = tqdm(all_files)
		for file in pbar:
			pbar.set_description(file.stem)

			with open(file, "r", encoding="latin-1") as f:

				for riga in tqdm(f, desc="processing_file"):

					riga = riga.strip().split("\t")

					if len(riga) < 4:
						continue

					if riga[2] == "<p>":
						process_paragraph(current_paragraph,
								regular_expression_positive,
								regular_expression_negative)
						current_paragraph = []
					else:
						current_paragraph.append(riga[1] + "_" + riga[3][0])