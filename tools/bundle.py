import json,gzip,base64,sys,os
root=sys.argv[1]
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
open(os.path.join(root,'index.html'),'w').write(s)
print(len(s)//1024,'KB')
