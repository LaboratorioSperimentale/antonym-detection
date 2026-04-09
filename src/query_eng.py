import argparse
import regex as re
from tqdm import tqdm
import multiprocessing
import pathlib

regular_expression_positive = {}
regular_expression_negative = {}


def clean_token(token):

	token = re.sub(r'_.', '', token)
	token = re.sub(r" +([,;:!?.])", r"\1", token)
	token = re.sub(r"([\(\[«])\s+", r"\1", token)
	token = re.sub(r" +([\)\]»])", r"\1", token)
	token = re.sub(r" *' *", "'", token)

	return token


def valid_sentence_length(text, min_tokens=10, max_tokens=50):
	n_tokens = len(text.split())
	return min_tokens < n_tokens < max_tokens


def process_paragraph(current_paragraph,
					regular_expression_positive,
					regular_expression_negative,
					output_file):

	string_paragraph = " ".join(current_paragraph)

	matched_pos = set()  # (X_found, Y_found, pattern_template) already matched
	for query, (query_sentence, (x, y, pattern)) in regular_expression_positive.items():
		match = re.search(query, string_paragraph)

		if match:
			X_found = match.group(1)
			Y_found = match.group(2)
			if any(pattern in q_pat for (xf, yf, q_pat) in matched_pos
				   if xf == X_found and yf == Y_found):
				continue
			matched_pos.add((X_found, Y_found, pattern))
			match = re.search(query_sentence, string_paragraph)

			if match:
				extraction = f"yes\t{pattern}\t{X_found}\t{Y_found}\t{x} - {y}\t{query.pattern}\t{match.group(1)}\t{match.group(2)}\t{match.group(5)}"
				extraction = clean_token(extraction)
				sentence = f"{match.group(1)} {match.group(2)} {match.group(5)}"
				sentence = clean_token(sentence)
				if valid_sentence_length(sentence):
					print(extraction, file=output_file)

	matched_neg = set()  # (X_found, Y_found, pattern_template) already matched
	for query, (query_sentence, (x, y, pattern)) in regular_expression_negative.items():
		match = re.search(query, string_paragraph)

		if match:
			X_found = match.group(1)
			Y_found = match.group(2)
			if any(pattern in q_pat for (xf, yf, q_pat) in matched_neg
				   if xf == X_found and yf == Y_found):
				continue
			matched_neg.add((X_found, Y_found, pattern))
			match = re.search(query_sentence, string_paragraph)

			if match:
				extraction = f"no\t{pattern}\t{X_found}\t{Y_found}\t{x} - {y}\t{query.pattern}\t{match.group(1)}\t{match.group(2)}\t{match.group(5)}"
				extraction = clean_token(extraction)
				sentence = f"{match.group(1)} {match.group(2)} {match.group(5)}"
				sentence = clean_token(sentence)
				if valid_sentence_length(sentence):
					print(extraction, file=output_file)


def process_batch(file_batch, re_pos, re_neg, output_path, position):


	with open(output_path, "w") as fout:
		print("class\tpattern\tX_found\tY_found\tpair\tquery\tcontext_pre\tcostr\tcontext_post", file=fout)

		for file_path in tqdm(file_batch, desc=output_path.stem, position=position*2, leave=True):
			current_paragraph = []

			with open(file_path, "r", encoding="latin-1") as f:
				for riga in tqdm(f, desc=file_path.stem, position=position*2+1, leave=False):
					riga = riga.strip().split("\t")

					if len(riga) < 4:
						continue

					if riga[2] == "<p>":
						process_paragraph(current_paragraph,
									re_pos, re_neg,
									fout)
						# for line in
						# 	print(line, file=fout)
						current_paragraph = []
					else:
						current_paragraph.append(riga[1] + "_" + riga[3][0])


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

	m = pattern.search(string)

	prefix, inner, suffix = m.group("prefix"), m.group("inner"), m.group("suffix")
	return prefix, inner, suffix



if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("input_root", type=pathlib.Path)
	parser.add_argument("--workers", type=int, default=4)
	args = parser.parse_args()

	all_files = list(args.input_root.rglob("*.txt"))

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

	re_pos_compiled = dict(sorted(
		{
			re.compile(q): (re.compile(rf'[.?!]([^.?!]*)({q})([^.?!]*[.?!])'), v)
			for q, v in regular_expression_positive.items()
		}.items(),
		key=lambda item: len(item[1][1][2]), reverse=True
	))
	re_neg_compiled = dict(sorted(
		{
			re.compile(q): (re.compile(rf'[.?!]([^.?!]*)({q})([^.?!]*[.?!])'), v)
			for q, v in regular_expression_negative.items()
		}.items(),
		key=lambda item: len(item[1][1][2]), reverse=True
	))

	n_batches = args.workers
	batches = [all_files[i::n_batches] for i in range(n_batches)]

	batch_args = [
		(batch, re_pos_compiled, re_neg_compiled,
		pathlib.Path(f"data/output_eng_{i}.tsv"), i)
		for i, batch in enumerate(batches)
	]

	with multiprocessing.Pool(processes=n_batches) as pool:
		pool.starmap(process_batch, batch_args)
