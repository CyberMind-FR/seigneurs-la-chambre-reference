#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, cv2, fitz, numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
cfg=yaml.safe_load((ROOT/'build-config.yaml').read_text(encoding='utf-8')) or {}
reg=yaml.safe_load((ROOT/cfg['source']['qr_registry']).read_text(encoding='utf-8')) or {}
dist=ROOT/cfg['release']['dist_dir']
pdf=dist/cfg['outputs']['sequential_16']['filename']
if not pdf.exists():
    print(f'FINAL PDF VALIDATION FAILED\n - missing {pdf}')
    sys.exit(1)

doc=fitz.open(pdf)
ref=cfg['source']['qr_reference_canvas']; rw,rh=float(ref['width']),float(ref['height'])
errors=[]
detector=cv2.QRCodeDetector()
zoom=3.0

for pkey,pdata in reg.get('pages',{}).items():
    page_no=int(pkey)
    qrs=pdata.get('qrs',[])
    if not qrs: continue
    page=doc[page_no-1]
    pix=page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),alpha=False)
    arr=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
    img=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)

    with Image.open(ROOT/'assets'/f'page-{page_no:02d}.jpg') as im:
        iw,ih=im.size
    W,H=pix.width,pix.height
    scale=min(W/iw,H/ih); dw,dh=iw*scale,ih*scale
    dx=(W-dw)/2; dy=(H-dh)/2

    for q in qrs:
        b=q['placement_px']
        x=int(round(dx+(b['x']/rw)*dw))
        y=int(round(dy+(b['y']/rh)*dh))
        w=int(round((b['w']/rw)*dw))
        h=int(round((b['h']/rh)*dh))
        pad=max(8,int(round(min(w,h)*0.10)))
        crop=img[max(0,y-pad):min(H,y+h+pad),max(0,x-pad):min(W,x+w+pad)]
        crop=cv2.resize(crop,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
        decoded,_,_=detector.detectAndDecode(crop)
        if decoded != q['payload']:
            errors.append(f"page {page_no} / {q['id']}: final PDF decoded={decoded!r}, expected={q['payload']!r}")

doc.close()
if errors:
    print('FINAL PDF QR VALIDATION FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print('FINAL PDF QR VALIDATION OK')
