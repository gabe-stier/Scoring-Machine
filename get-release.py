import sys

import requests

url = "https://api.github.com/repos/gabe-stier/Scoring-Machine/git/refs/tags"

payload = {}
headers = {
	'Authorization': f'token {sys.argv[1]}',
	'Accept':        'application/vnd.github.v3+json'
	}

response = requests.request("GET", url, headers=headers, data=payload)

val = response.json()
tags = []
for ref in val:
	tag = ref['ref']
	if not 'latest' in tag:
		tags.append(tag.split('/')[2])
top_tag = max(tags)
print(f'::set-output name=last_tag::{top_tag}')
