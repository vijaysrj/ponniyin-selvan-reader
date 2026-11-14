import json,gzip,base64,sys,os
root=sys.argv[1]
sys.argv=[a for a in sys.argv if a!='--standalone'] + (['--standalone'] if '--standalone' in sys.argv else [])
s=open(os.path.join(root,'src.html')).read()
m=json.load(open(os.path.join(root,'data/manifest.json')))
blocks=['<script type="application/json" id="ps-manifest">'+json.dumps(m,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>']
for bk in m['books']:
    d={c['n']:json.load(open(os.path.join(root,f"data/{bk['id']}/{c['n']}.json")))['paras'] for c in bk['chapters']}
    gz=gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),9)
    blocks.append(f'<script type="application/octet-stream" id="ps-book-{bk["id"]}">'+base64.b64encode(gz).decode()+'</script>')
marker='<div id="app"></div>'
assert s.count(marker)==1
s=s.replace(marker,'\n'.join(blocks)+'\n'+marker)
out=sys.argv[2] if len(sys.argv)>2 else os.path.join(root,'index.html')
if '--standalone' in sys.argv:
    # Full document for normal hosting (Vercel). The Claude artifact host adds this shell itself.
    head_end=s.index('<style>')
    s=('<!doctype html>\n<html lang="ta">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<meta name="description" content="கல்கியின் பொன்னியின் செல்வன், ஐந்து பாகங்களும் 293 அத்தியாயங்களும், இலவசமாக இணையத்தில் படிக்கலாம்.">\n'
       '<meta property="og:type" content="book">\n'
       '<meta property="og:site_name" content="பொன்னியின் செல்வன்">\n'
       '<meta property="og:title" content="பொன்னியின் செல்வன் · கல்கி">\n'
       '<meta property="og:description" content="ஐந்து பாகங்கள் · 293 அத்தியாயங்கள். இலவசமாக இணையத்தில் படிக்கலாம்.">\n'
       '<meta property="og:url" content="https://ponniyin-selvan-reader.vercel.app/">\n'
       '<meta property="og:image" content="https://ponniyin-selvan-reader.vercel.app/og.jpg">\n'
       '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
       '<meta property="og:image:alt" content="பொன்னியின் செல்வன் ஐந்து பாக அட்டைகள்">\n'
       '<meta name="twitter:card" content="summary_large_image">\n'
       '<meta name="twitter:image" content="https://ponniyin-selvan-reader.vercel.app/og.jpg">\n'
       '<meta name="theme-color" content="#efeee8" media="(prefers-color-scheme: light)">\n'
       '<meta name="theme-color" content="#111219" media="(prefers-color-scheme: dark)">\n'
       '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
       + s[:head_end] + s[head_end:s.index('</style>')+8] + '\n</head>\n<body>\n' + s[s.index('</style>')+8:] + '\n</body>\n</html>\n')
open(out,'w').write(s)
print(len(s)//1024,'KB')
