from pathlib import Path
import hashlib, urllib.request, zipfile, io
p=Path(__file__).resolve().parent
url='https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip'
b=urllib.request.urlopen(url,timeout=60).read()
z=zipfile.ZipFile(io.BytesIO(b))
hour=z.read('hour.csv')
assert hashlib.sha256(hour).hexdigest()=='e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f','Source changed. Investigate before training.'
(p/'hour.csv').write_bytes(hour)
(p/'DATA_README.txt').write_bytes(z.read('Readme.txt'))
print('Verified original source and README from',url)
