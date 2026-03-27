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

def process_paragraph (current_paragraph, regular_expression_positive, regular_expression_negative):

	string_paragraph = " ".join(current_paragraph)
 
	for query in regular_expression_positive:
		match = re.search(query, string_paragraph)
		if match:
			X_found = match.group(1)
			Y_found = match.group(2)
		# 	print("\nPOSITIVE MATCH")
		# 	print("query:", query)
		# 	print("Match:", match.group())
		# 	print("Paragraph:", string_paragraph)
   
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
			istance = "yes"

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
	
	input_root = pathlib.Path("/media/CORPORA/CORPORA/COCA/coca-wlp/wlp_news_znw")
	
	all_files = list(input_root.rglob("*.txt"))
	print(all_files)
	patterns_filename = "data/eng_patterns.txt"
	seeds_filename = "data/eng_seeds.txt"
	seeds = set()

	with open ("output_eng.tsv", "w") as file_output:
		
		
		
		with open(seeds_filename) as fin:
			for line in fin:
				linesplit = line.strip().split()
				sorted_linesplit = sorted(linesplit)
				seeds.add((sorted_linesplit[0], sorted_linesplit[1]))

		# patterns = set()
		patterns = {}

		with open(patterns_filename) as fin:
			for line in fin:
				line = line.strip()
				# patterns.add(extract_pattern(line))
				patterns[extract_pattern(line)]=line


		for pattern in patterns:
			for x, y in seeds:
				regular_expression_positive[((generate_pattern_positive(x, y, *pattern)))] = (x, y, patterns[pattern])
				# print(generate_pattern(x, y, *pattern))
				regular_expression_positive[((generate_pattern_positive(y, x, *pattern)))] = (x, y, patterns[pattern])
				# print(generate_pattern(y, x, *pattern))
				regular_expression_negative[((generate_pattern_negative(x, y, *pattern, "left")))] = (x, y, patterns[pattern])
				# print(generate_pattern_negative(x, y, *pattern, "left"))
				regular_expression_negative[((generate_pattern_negative(x, y, *pattern, "right")))] = (x, y, patterns[pattern])
				# print(generate_pattern_negative(x, y, *pattern, "right"))
				regular_expression_negative[((generate_pattern_negative(y, x, *pattern, "left")))] = (x, y, patterns[pattern])
				# print(generate_pattern_negative(y, x, *pattern, "left"))
				regular_expression_negative[((generate_pattern_negative(y, x, *pattern, "right")))] = (x, y, patterns[pattern])
				# print(generate_pattern_negative(y, x, *pattern, "right"))
		

		pbar = tqdm(all_files)	
		for file in pbar:
			pbar.set_description(file.stem)
			with open(file, "r", encoding="latin-1") as f:
				for riga in tqdm(f, desc="processing_file"):
					riga = riga.strip()
					
					riga = riga.split("\t")
			
					if len(riga) < 4:
						continue
					
					elif riga[2] == "<p>":
						
						process_paragraph(current_paragraph, regular_expression_positive, regular_expression_negative)
						current_paragraph = []
				
					else:            
						current_paragraph.append(riga[1] + "_" + riga[3][0])