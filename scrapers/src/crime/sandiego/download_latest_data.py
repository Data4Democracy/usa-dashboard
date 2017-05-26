"""Download last 180 days of crime data in San Diego

NOTES
* Only crimes in the last 180 days can be downloaded.
* Data seems to be updated weekly
* Data are in the encoding format 'cp1252'
"""

import requests
import zipfile
import io

zip_file_url = 'http://www.sandag.org/programs/public_safety/arjis/CrimeData/crimedata.zip'
r = requests.get(zip_file_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()
