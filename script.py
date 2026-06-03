import csv
import glob
import json
import os
import random
import requests
import time

apisDirectoryFilename = 'APIs.guru.json' # Downloaded from https://api.apis.guru/v2/list.json

collectionOfApis = []
numberOfApis = 100 # Number of OpenAPI specs to get from the directory.
savedSpecUrls = set()

def getApiTitle(api: json):
    return api['versions'][api['preferred']]['info']['title']

def getApiUrl(api: json):
    return api['versions'][api['preferred']]['swaggerUrl']

# Delete previously downloaded OpenAPI specs:
for f in glob.glob('download/*.json'):
    os.remove(f)

with open(apisDirectoryFilename) as f:
    listOfApis = list(
        json.load(f).values()
    )

for _ in range(numberOfApis):
    while True:
        selectedApi = random.choice(listOfApis)

        apiTitle = getApiTitle(selectedApi)
        specUrl = getApiUrl(selectedApi)

        if specUrl in savedSpecUrls or 'webhooks' in json.dumps(selectedApi):
            continue # The API is already in the collection or contains webhooks.
        else:
            time.sleep(1)

            r = requests.get(specUrl, timeout = 60)

            if r.status_code == 200:
                if len(r.content) <= 100 * 1024:
                    collectionOfApis.append((apiTitle, specUrl, r.text))
                    savedSpecUrls.add(specUrl)

                    break

                continue # The spec file size is greater than 100 KB.
            else:
                print(f'Failed to download OpenAPI spec from "{specUrl}" (status code: {r.status_code}).')

                continue # GET request failed.

with open('download/urls.csv', 'w') as f:
    f = csv.writer(f, quoting = csv.QUOTE_ALL)
    f.writerow(['Title', 'URL'])

    for apiTitle, specUrl, oas in collectionOfApis:
        f.writerow([apiTitle, specUrl])

        # Save the OpenAPI spec to disk:
        specFilename = ''.join([c for c in apiTitle if c.isalnum()])

        with open('download/' + specFilename + '.json', 'w') as specFile:
            specFile.write(oas)