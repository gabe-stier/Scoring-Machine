import requests
import sys

url = "https://api.github.com/repos/gabe-stier/Scoring-Machine/git/refs/tags"

payload={}
headers = {
  'Accept': 'application/vnd.github.v3+json',
  'Authorization': f'token {sys.argv[1]}'
}

response = requests.request("GET", url, headers=headers, data=payload)

val = response.json()
tags = []
for ref in val:
	tag = ref['ref']
	if not 'latest' in tag:
		tags.append(tag.split('/')[2])
top_tag = max(tags)
print(f'::set-output name=last_tag::$(echo \'{top_tag}\')')
