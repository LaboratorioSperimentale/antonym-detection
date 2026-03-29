import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
import regex as re
import random
import csv
import copy
import tqdm


BASE = "https://corpora.ficlit.unibo.it/TCORIS/"
WRAPPER_URL = urljoin(BASE, "Wrapper.php")

log = open("data/log.txt", "w")

def build_request(query_str):

	data = {
		"Verbose": "1",
		"Username": "free",
		"Password": "access",
		"Query": f'{query_str}',
		"Time": "ALL",
		"SubCorpus": "ALL",
		"Reduce": "10000",
		"Sort": "0",
		"Colloc": "0",
		"ColMethod": "4"
	}

	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:148.0) Gecko/20100101 Firefox/148.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.9",
		"Accept-Encoding": "gzip, deflate, br, zstd",
		"Content-Type": "application/x-www-form-urlencoded",
		"Origin": "https://corpora.ficlit.unibo.it",
		"Referer": "https://corpora.ficlit.unibo.it/TCORIS/",
		"Connection": "keep-alive",
		"Upgrade-Insecure-Requests": "1"
	}

	cookies = {
		"_cs_c": "1",
		"_cs_id": "cbd3ed34-b383-acc6-eef2-e8712362e439.1751688893.57.1773310368.1773310356.1751633580.1785852893911.1.x",
		"cc_v1_accepted_providers": "dummy_group_1,youtube,facebook,vimeo,linkedin",
		"cc_v1_hide_prompt": "1"
	}

	return headers, cookies, data


queries_file = "data/queries.tsv"

with open(queries_file) as fin:
	csvreader = csv.DictReader(fin, delimiter="\t")
	csvwriter = csv.DictWriter(open("data/output.tsv", "w"), fieldnames=csvreader.fieldnames+["sent_id", "text"], delimiter="\t")
	csvwriter.writeheader()

	session = requests.Session()

	pbar = tqdm.tqdm(csvreader)

	for line in pbar:
		pbar.set_description(f"{line['pattern']} - {line['X']} - {line['Y']}")
	# for line in tqdm.tqdm(csvreader):
		header, cookie, data = build_request(line["query"])
		resp = session.post(WRAPPER_URL, data=data, headers=header, cookies=cookie)
		resp.raise_for_status()

		soup = BeautifulSoup(resp.text, "html.parser")
		links = [
			urljoin(BASE, a["href"])
			for a in soup.select('a[href^="Context.php?"]')
		]
		print(f"Found {len(links)} context links", file=log)

		results = []
		for link in tqdm.tqdm(links):
			r = session.get(link, headers=header)
			r.raise_for_status()

			page = BeautifulSoup(r.text, "html.parser")
			m = re.search(r'#text\s*=\s*(.*?)\s*<br>', r.text, re.S)
			text = m.group(1) if m else None
			m = re.search(r'#sent_id\s*=\s*(.*?)\s*<br>', r.text, re.S)
			sent_id = m.group(1) if m else None

			new_line = copy.deepcopy(line)
			new_line["sent_id"] = sent_id
			new_line["text"] = text

			csvwriter.writerow(new_line)

			time.sleep(1+random.randint(0,3))
