import os
import re
import requests
from bs4 import BeautifulSoup


# Data is typically accessed from here: https://www.fms.treas.gov/dts/index.html
# However, this page uses an iframe to display data links; we read directly from the URL referenced in the iframe.
SITE_ROOT = 'https://www.fms.treas.gov/'
DATA_INDEX_SUBPATH = 'fmsweb/DTSFilesDisplayAction.do'
RAW_DIR = os.path.join('.', 'data', 'raw')


def get_file_name_from_url(url):
    name_query_ptn = re.compile('name=(\d+\.txt)')
    match = re.search(name_query_ptn, url)
    if match is not None:
        return match.groups()[0]
    else:
        return None


def main():
    index_response = requests.get(SITE_ROOT + DATA_INDEX_SUBPATH)
    soup = BeautifulSoup(index_response.content, 'html5lib')

    links = [obj['href'] for obj in soup.findAll('a', href=True, text=re.compile(r'.*Text File'))]
    available_files = [{'url': link, 'file_name': get_file_name_from_url(link)} for link in links]

    downloaded_files = os.listdir(RAW_DIR)

    for file in available_files:
        if file['file_name'] not in downloaded_files:
            print(f"File [{file['file_name']}] not found; beginning download.")
            response = requests.get(SITE_ROOT + file['url'])

            with open(os.path.join(RAW_DIR, file['file_name']), 'wb') as f:
                f.write(response.content)

            print(f"Download of [{file['file_name']}] complete.")

        else:
            print(f"File [{file['file_name']}] already downloaded; skipping.")


if __name__ == '__main__':
    main()
