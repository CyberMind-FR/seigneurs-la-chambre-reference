#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
import yaml
from PIL import Image
from reportlab import rl_config
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A1,A2,A4,A5,landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
rl_config.useA85=0
ROOT=Path(__file__).resolve().parents[1]
def sha256(p):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for ch in iter(lambda:f.read(1<<20),b''): h.update(ch)
    return h.hexdigest()
def page_entry(mapping,page_no):
    for k in (f"{page_no:02d}",str(page_no),page_no):
        if k in mapping: return mapping[k] or {}
    return {}
PAGE_SIZES={'A1':A1,'A2':A2,'A4':A4,'A5':A5,'A4-landscape':landscape(A4)}
def draw_page(c,page_no,image_path,box,registry,qr_ref,bg,qr_overlay=True,metrics=None):
    x,y,bw,bh=box; c.setFillColor(HexColor(bg)); c.rect(x,y,bw,bh,stroke=0,fill=1)
    if image_path is None: return
    with Image.open(image_path) as im: iw,ih=im.size
    scale=min(bw/iw,bh/ih); dw,dh=iw*scale,ih*scale; dx=x+(bw-dw)/2; dy=y+(bh-dh)/2
    c.drawImage(ImageReader(str(image_path)),dx,dy,width=dw,height=dh,preserveAspectRatio=True,mask='auto')
    if page_no is not None and qr_overlay:
        pdata=page_entry(registry.get('pages',{}),page_no); rw,rh=qr_ref
        for q in pdata.get('qrs',[]):
            b=q['placement_px']; qx=dx+(b['x']/rw)*dw; qw=(b['w']/rw)*dw; qh=(b['h']/rh)*dh; qy=dy+dh-((b['y']+b['h'])/rh)*dh
            qa=ROOT/q['asset']; c.drawImage(ImageReader(str(qa)),qx,qy,width=qw,height=qh,preserveAspectRatio=False,mask='auto')
    if metrics is not None:
        metrics.append({'page':page_no,'source_px':[iw,ih],'effective_ppi':round(min(iw/(dw/72),ih/(dh/72)),1)})
def seq(path,size,pages,assets,reg,qr_ref,bg,qr_overlay):
    m=[]; c=canvas.Canvas(str(path),pagesize=size,pageCompression=1); pw,ph=size
    for p in pages: draw_page(c,p,assets.get(p) if p else None,(0,0,pw,ph),reg,qr_ref,bg,qr_overlay,m); c.showPage()
    c.save(); return m
def imposed(path,pairs,size,physical,assets,reg,qr_ref,bg,qr_overlay):
    pw,ph=size; half=pw/2; m=[]; c=canvas.Canvas(str(path),pagesize=size,pageCompression=1)
    for lp,rp in pairs:
        l=physical[lp]; r=physical[rp]
        draw_page(c,l,assets.get(l) if l else None,(0,0,half,ph),reg,qr_ref,bg,qr_overlay,m); draw_page(c,r,assets.get(r) if r else None,(half,0,half,ph),reg,qr_ref,bg,qr_overlay,m); c.showPage()
    c.save(); return m
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default=str(ROOT/'build-config.yaml')); ap.add_argument('--out',default=None); a=ap.parse_args()
    cfg=yaml.safe_load(Path(a.config).read_text(encoding='utf-8')); out=Path(a.out).resolve() if a.out else ROOT/cfg['release']['dist_dir']; out.mkdir(parents=True,exist_ok=True)
    for old in out.iterdir():
        if old.is_file(): old.unlink()
    src=cfg['source']; count=int(src['page_count']); assets={}
    order={int(k):v for k,v in src['canonical_order'].items()}
    if sorted(order) != list(range(1,count+1)):
        raise ValueError('source.canonical_order must match page_count')
    for p in range(1,count+1):
        f=ROOT/src['assets_dir']/src['pattern'].format(page=p)
        if not f.exists():
            raise FileNotFoundError(f)
        assets[p]=f
    reg=yaml.safe_load((ROOT/src['qr_registry']).read_text(encoding='utf-8')); ref=src['qr_reference_canvas']; qr_ref=(int(ref['width']),int(ref['height'])); render=cfg['render']; bg=render['background']; qr_overlay=bool(render['qr_overlay']); o=cfg['outputs']
    if not render['preserve_aspect_ratio'] or render['crop']:
        raise ValueError('Only preserve_aspect_ratio=true and crop=false are supported')
    ppi_min=float(render['effective_ppi_min'])
    report={'project':cfg['project'],'version':cfg['version'],'render':{'background':bg,'qr_rule':render['qr_rule'],'effective_ppi_min':ppi_min},'release':{'github_artifact_name':cfg['release']['github_artifact_name'],'release_on_tags':cfg['release']['release_on_tags']},'outputs':{}}
    pdfs=[]
    def add_output(name,metrics):
        report['outputs'][name]=metrics
        low=[m for m in metrics if m['effective_ppi'] < ppi_min]
        for m in low: print(f"WARNING: {name} page {m['page']}: effective PPI {m['effective_ppi']} < {ppi_min:g}")
    c=o['sequential_16']
    if c['enabled']:
        if int(c['pages']) != count: raise ValueError('sequential_16.pages must match page_count')
        p1=out/c['filename']; add_output(p1.name,seq(p1,PAGE_SIZES[c['page_size']],list(range(1,count+1)),assets,reg,qr_ref,bg,qr_overlay)); pdfs.append(p1)
    physical={n:n for n in range(1,17)} if count==16 else ({**{n:n for n in range(1,15)},15:None,16:15})
    c=o['booklet_a5']
    if c['enabled']:
        if int(c['pages']) != 16: raise ValueError('booklet_a5.pages must be 16')
        p=out/c['filename']; add_output(p.name,seq(p,PAGE_SIZES[c['page_size']],[physical[n] for n in range(1,17)],assets,reg,qr_ref,bg,qr_overlay)); pdfs.append(p)
    c=o['imposed_a4']
    if c['enabled']:
        p=out/c['filename']; add_output(p.name,imposed(p,c['imposition'],PAGE_SIZES[c['page_size']],physical,assets,reg,qr_ref,bg,qr_overlay)); pdfs.append(p)
    for key in ('panels_a2','panels_a1'):
        c=o[key]
        if c['enabled']:
            if int(c['pages']) != count: raise ValueError(f'{key}.pages must match page_count')
            p=out/c['filename']; add_output(p.name,seq(p,PAGE_SIZES[c['page_size']],list(range(1,count+1)),assets,reg,qr_ref,bg,qr_overlay)); pdfs.append(p)
    rp=out/cfg['release']['report']; rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    sp=out/cfg['release']['checksums']; sp.write_text(''.join(f"{sha256(p)}  {p.name}\n" for p in [*pdfs,rp]),encoding='utf-8')
    zp=out/cfg['release']['bundle'];
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in [*pdfs,rp,sp]: z.write(p,p.name)
    print('PDF BUILD OK')
if __name__=='__main__': raise SystemExit(main())
