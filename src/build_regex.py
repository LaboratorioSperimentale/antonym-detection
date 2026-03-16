import regex as re

def generate_pattern(x, y, prefix, inner, suffix):
	query = ''

	if prefix:
		prefix = prefix.strip().split()
		for el in prefix:
			query+= f'[word="{el}"]'

	query+= f'[lemma="{x}" & pos="ADJ"]'

	if inner:
		inner = inner.strip().split()
		for el in inner:
			query+= f'[word="{el}"]'

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

	patterns = set()

	with open(patterns_filename) as fin:
		for line in fin:
			line = line.strip()
			patterns.add(extract_pattern(line))

	regex_filename = "queries.txt"

	with open(f"data/{regex_filename}", "w") as fout:
		for pattern in patterns:
			for x, y in seeds:
				print(generate_pattern(x, y, *pattern), file=fout)
				print(generate_pattern(y, x, *pattern), file=fout)
				# input()



 	# [lemma="alto" & pos="ADJ"][word="o"][lemma="basso" & pos="ADJ"]

	# print(len(seeds))