#!/usr/bin/env python3
"""Page 03 layered-composition prototype.

This script does not OCR or invent content. It measures candidate non-paper regions,
exports a diagnostic overlay/contact sheet, extracts only configured fragment boxes,
and creates a control PDF with a real text layer and the deterministic QR SVG.

The first run is intentionally diagnostic: measured candidates are written to JSON.
Human-reviewed boxes can then be copied into prototypes/page-03/fragment-boxes.yaml.
"""
from pathlib import Path
import hashlib, json, re, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/page-03.jpg"
OUT = ROOT / "dist/prototype-page-03"
BOXES = ROOT / "prototypes/page-03/fragment-boxes.yaml"


def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()


def measure_candidates(img):
    """Find large visually dense regions without OCR. Results are candidates only."""
    rgb=np.asarray(img.convert('RGB'))
    gray=cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # Estimate paper by high local brightness; dense ink/image regions become foreground.
    blur=cv2.GaussianBlur(gray,(0,0),9)
    fg=(blur < 225).astype(np.uint8)*255
    # Join illustration texture, while avoiding line-by-line text becoming huge blocks.
    k=cv2.getStructuringElement(cv2.MORPH_RECT,(13,13))
    dense=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,k,iterations=2)
    n, labels, stats, _=cv2.connectedComponentsWithStats(dense,8)
    H,W=gray.shape
    cand=[]
    for i in range(1,n):
        x,y,w,h,area=map(int,stats[i])
        frac=area/(W*H)
        if area < 0.004*W*H: continue
        if w < 0.08*W or h < 0.04*H: continue
        # reject almost-full-page components
        if w > .94*W and h > .94*H: continue
        cand.append(dict(x=x,y=y,w=w,h=h,area=area,area_fraction=round(frac,6)))
    cand.sort(key=lambda b:(b['y'],b['x']))
    return cand


def diagnostic(img,cand):
    d=img.copy().convert('RGB'); dr=ImageDraw.Draw(d)
    for i,b in enumerate(cand,1):
        x,y,w,h=b['x'],b['y'],b['w'],b['h']
        dr.rectangle((x,y,x+w,y+h),outline=(255,0,0),width=max(2,img.width//700))
        dr.text((x+4,y+4),str(i),fill=(255,0,0))
    d.save(OUT/'candidate-overlay.jpg',quality=92)
    # contact sheet
    thumbs=[]
    for i,b in enumerate(cand,1):
        crop=img.crop((b['x'],b['y'],b['x']+b['w'],b['y']+b['h']))
        crop.thumbnail((420,300))
        thumbs.append((i,crop.copy()))
    if thumbs:
        cols=3; cellw=450; cellh=340
        sheet=Image.new('RGB',(cellw*cols,cellh*((len(thumbs)+cols-1)//cols)),'white')
        sd=ImageDraw.Draw(sheet)
        for j,(i,t) in enumerate(thumbs):
            x=(j%cols)*cellw; y=(j//cols)*cellh
            sheet.paste(t,(x+10,y+25)); sd.text((x+10,y+5),f'candidate {i}',fill='black')
        sheet.save(OUT/'candidate-contact-sheet.jpg',quality=92)


def extract_reviewed(img):
    if not BOXES.exists(): return []
    data=yaml.safe_load(BOXES.read_text()) or {}
    produced=[]
    for f in data.get('fragments',[]):
        if f.get('status') != 'APPROVED': continue
        x,y,w,h=[int(f['bbox_px'][k]) for k in ('x','y','w','h')]
        if min(x,y,w,h)<0 or x+w>img.width or y+h>img.height:
            raise SystemExit(f"invalid bbox for {f['id']}")
        p=OUT/'fragments'/f"{f['id']}.png"; p.parent.mkdir(parents=True,exist_ok=True)
        img.crop((x,y,x+w,y+h)).save(p)
        produced.append({'id':f['id'],'path':str(p.relative_to(ROOT)),'bbox_px':dict(x=x,y=y,w=w,h=h),'sha256':sha256(p)})
    return produced


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    img=Image.open(SRC)
    cand=measure_candidates(img)
    (OUT/'measurement.json').write_text(json.dumps({
        'source':str(SRC.relative_to(ROOT)), 'source_sha256':sha256(SRC),
        'width_px':img.width,'height_px':img.height,'candidates':cand
    },indent=2)+"\n")
    diagnostic(img,cand)
    produced=extract_reviewed(img)
    (OUT/'fragments.json').write_text(json.dumps({'produced':produced},indent=2)+"\n")
    print(f"page03 {img.width}x{img.height}; candidates={len(cand)}; approved_fragments={len(produced)}")
    print(f"diagnostics: {OUT.relative_to(ROOT)}")

if __name__=='__main__': main()
