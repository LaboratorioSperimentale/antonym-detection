import regex as re
import csv

def generate_pattern(x, y, prefix, inner, suffix):
	query = ''

	if prefix:
		prefix = prefix.strip().split()
		for el in prefix:
			query+= f'[word="{el}"]'

	if x.startswith("!"):
		query+= f'[lemma!="{x[1:]}" & pos="ADJ"]'
	else:
		query+= f'[lemma="{x}" & pos="ADJ"]'

	if inner:
		inner = inner.strip().split()
		for el in inner:
			query+= f'[word="{el}"]'

	if y.startswith("!"):
		query+= f'[lemma!="{y[1:]}" & pos="ADJ"]'
	else:
		query+= f'[lemma="{y}" & pos="ADJ"]'

	if suffix:
		suffix = suffix.strip().split()
		for el in suffix:
			query+= f'[word="{el}"]'

	return query

def extract_pattern(string):
	pattern = re.compile(r'^(?P<prefix>.*?)(?P<x>X)(?P<inner>.*?)(?P<y>Y)(?P<suffix>.*)$')
	# s = "abc X e Y def"

	m = pattern.search(string)

	prefix, inner, suffix = m.group("prefix"), m.group("inner"), m.group("suffix")
	return prefix, inner, suffix


if __name__ == "__main__":
	patterns_filename = "data/patterns.txt"
	seeds_filename = "data/seeds.txt"
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
			patterns[line] = extract_pattern(line)

	regex_filename = "queries.txt"

	with open(f"data/{regex_filename}", "w") as fout:
		for pattern_key, pattern in patterns.items():
			for x, y in seeds:

				print(f'yes\t{pattern_key}\t{x}\t{y}\t{generate_pattern(x, y, *pattern)}', file=fout)
				print(f'yes\t{pattern_key}\t{x}\t{y}\t{generate_pattern(y, x, *pattern)}', file=fout)

				print(f'no\t{pattern_key}\t{x}\t{y}\t{generate_pattern(f"!{x}", y, *pattern)}', file=fout)
				print(f'no\t{pattern_key}\t{x}\t{y}\t{generate_pattern(x, f"!{y}", *pattern)}', file=fout)
				print(f'no\t{pattern_key}\t{x}\t{y}\t{generate_pattern(f"!{y}", x, *pattern)}', file=fout)
				print(f'no\t{pattern_key}\t{x}\t{y}\t{generate_pattern(y, f"!{x}", *pattern)}', file=fout)



 	# [lemma="alto" & pos="ADJ"][word="o"][lemma="basso" & pos="ADJ"]

	# print(len(seeds))