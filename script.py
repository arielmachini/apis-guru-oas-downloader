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

def getApiTitle(api: json):
    return api['versions'][api['preferred']]['info']['title']

def getApiUrl(api: json):
    return api['versions'][api['preferred']]['link']

# Delete previously downloaded specifications:
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

        if (apiTitle, specUrl) in collectionOfApis or 'webhooks' in json.dumps(selectedApi):
            continue # Select another API from the directory.
        else:
            collectionOfApis.append((apiTitle, specUrl))

            break

with open('download/urls.csv', 'w') as f:
    w = csv.writer(f, quoting = csv.QUOTE_ALL)
    w.writerow(['Title', 'URL'])

    for apiTitle, specUrl in collectionOfApis:
        w.writerow([apiTitle, specUrl])

        # Save the OpenAPI specification to disk:
        r = requests.get(specUrl, timeout = 60)

        if r.status_code == 200:
            specFilename = ''.join([c for c in apiTitle if c.isalnum()])

            with open('download/' + specFilename + '.json', 'w') as f:
                f.write(r.text)
        else:
            print(f'Failed to download OpenAPI specification from "{specUrl}" (status code: {r.status_code}).')

        time.sleep(1)