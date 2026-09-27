#!/usr/bin/env python3
"""Reproduce JLCPCB coated grounded-coplanar calculations (geometry only, no PCB upload)."""
import websocket,urllib.request,json,uuid,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator/docs/rf';uid=uuid.uuid4().hex
ws=websocket.create_connection('wss://tools.jlc.com/jlcTools/webSocket/'+uid,timeout=25);results=[]
for copper in [.035,.04064]:
 for gap in [.15,.20]:
  params={'dCalculateMode':3,'H1':.2104/.0254,'Er1':4.4,'W1':.26/.0254,'W2':.26/.0254-.5,'G1':20,'D1':gap/.0254,'T1':copper/.0254,'C1':1.2,'C2':.6,'CEr':3.8,'isLinkComputingMode':False,'W2LinkW1Incr':.5,'ZoTol':.5}
  aid=uuid.uuid4().hex;body={'accessId':aid,'impedance_calc_mark':'CoatedCoplanarWaveguideWithLowerGnd1B','paramMd5':hashlib.md5(json.dumps(params,separators=(',',':')).encode()).hexdigest(),'impedance_calc_arg':params,'uuid':uid}
  req=urllib.request.Request('https://jlcpcb.com/api/jlcTools/impedance/calc',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  response=json.load(urllib.request.urlopen(req,timeout=20))
  while True:
   message=json.loads(ws.recv())
   if message.get('accessId')==aid:break
  results.append({'width_mm':.26,'gap_mm':gap,'copper_mm':copper,'request':body,'response':message});print(copper,gap,message.get('impedance_calc_result'),flush=True)
  (D/'gps-feed-jlc.json').write_text(json.dumps(results,indent=2)+'\n')
ws.close()
