from pathlib import Path
import json
p=Path(__file__).resolve().parent
s=(p/'template.html').read_text()
payload='const MODEL='+ (p/'model.json').read_text()+';const RESULTS='+(p/'results.json').read_text()+';const RECORDS='+(p/'test_records.json').read_text()+';'
for tag,text in [('PAYLOAD',payload),('ENGINE',(p/'engine.js').read_text()),('APP',(p/'app.js').read_text())]:s=s.replace('/*__'+tag+'__*/',text)
(p/'index.html').write_text(s)
print('Built',len(s.encode()),'bytes')
