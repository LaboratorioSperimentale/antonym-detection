import regex as re

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

	with open(patterns_filename) as fin:
		for line in fin:
			line = line.strip()
			print(extract_pattern(line))
			input()

	print(len(seeds))