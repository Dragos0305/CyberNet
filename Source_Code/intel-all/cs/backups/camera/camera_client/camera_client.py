#!/usr/bin/env python3
#
# Feed Downloader - Developed by TemuNix
#
# This software was developed by TemuNix for the purpose of downloading
# security camera feeds. Please be aware of the following:
# 1. Access to all camera feeds requires a valid password ("public" for public the public feed)
# 2. Users must ensure they enter the correct credentials for access.
#
# Disclaimer: TemuNix assumes no responsibility for any use of this software beyond its intended purpose.

import requests
import argparse
import base64
import re
parser = argparse.ArgumentParser(description="TemuNix Industrial Camera Feed Downloader")
parser.add_argument("hostname", help="The hostname of the server you are trying to reach", type=str)
parser.add_argument("--feed", help="Name of the feed to download", type=str, default="public")
parser.add_argument("--password", help="Password for the specified feed", type=str, default="public")
args = parser.parse_args()

url = f'http://{args.hostname}:41824/{args.feed}/feed.mp4'
print(f"temunix: downloading feed {url}")

session = requests.Session()
request = requests.Request(method='GET', url=url, auth=(args.feed, args.password))
prep = request.prepare()
prep.url = url
response = session.send(prep)
header = response.headers

if response.headers['Content-Type'] == 'video/mp4':
    filename = re.findall('(?<=filename=").+(?=")', response.headers['Content-Disposition'])[0]
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(response.content))
    print("temunix: OK")
else:
    print(response.text)
