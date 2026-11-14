import os,re,json,sys,unicodedata
SRC=sys.argv[1]; OUT=sys.argv[2]
R=os.path.join(SRC,'Ponniyin-Selvan-')
parts={1:['Chapter-1'],2:['Chapter-2'],3:['Chapter-3'],4:['Chapter-4','Chapter-4.1'],5:['Chapter-5','Chapter-5.1']}
nat=lambda s:[int(x) if x.isdigit() else x for x in re.split(r'(\d+)',s)]
HEAD=re.compile(r'^\s*அத்தியாயம்\s*(\d+)\s*[-–]\s*(.*)$')
def clean(p):
    p=p.replace('\u200c','').replace('\u200b','').replace('\ufeff','')
    p=p.replace('\\u200c','').replace('\\u200b','')
    p=p.replace("\\'","'").replace('\\"','"')
    p=re.sub(r'[ \t\u00a0]+',' ',p).strip()
    # add a space after sentence punctuation glued to next word (keeps numbers like 1.5)
    p=re.sub(r'([.!?])(?=[\u0B80-\u0BFF“‘"])',r'\1 ',p)
    return p
books={}
for b,ds in parts.items():
    chs={}
    for d in ds:
        for f in sorted(os.listdir(os.path.join(R,d)),key=nat):
            t=open(os.path.join(R,d,f),encoding='utf-8').read().strip()
            if t.startswith("'") or t.startswith('"'): t=t[1:]
            if t.endswith("'") or t.endswith('"'): t=t[:-1]
            lines=t.replace('\\n','\n').split('\n')
            m=HEAD.match(lines[0].replace('\u200c',''))
            if not m: continue
            n=int(m.group(1)); title=clean(m.group(2))
            paras=[clean(x) for x in lines[1:]]
            chs[n]={'n':n,'title':title,'paras':[x for x in paras if x]}
    books[b]=chs
# --- fill Book 1 chapters 46-57 from clean single-line text, using PDF text for chapter boundaries
V=open(os.path.join(SRC,'text_generation_ponniyin_selvan/ponniyin_selvan.txt'),encoding='utf-8').read()
P=open(os.path.join(SRC,'Ponniyn-Selvan-RNN-Chatbot-Assignment/data/ponniyin-selvan.txt'),encoding='utf-8').read().replace('\u200c','')
hs=[]
seen=set()
for m in re.finditer(r'அத்தியாயம்\s*(\d+)\s*[-–]\s*([^\n]*)',P[:700000]):
    n=int(m.group(1))
    if 46<=n<=57 and n not in seen:
        seen.add(n); hs.append((n,m.group(2).strip(),m.end()))
def anchor(pos):
    body=re.sub(r'\s+',' ',P[pos:pos+600]).strip()
    words=body.split(' ')
    for i in range(0,30):
        cand=' '.join(words[i:i+4])
        if len(cand)<15: continue
        j=V.find(cand, 500000)
        if j>0 and j<800000:
            # walk back to the start of that sentence/paragraph in V
            k=j
            # move back over preceding words that were in nitin before our candidate
            pre=' '.join(words[:i])
            if pre and V[j-len(pre)-1:j-1]==pre: k=j-len(pre)-1
            elif pre:
                k=V.rfind(words[0],j-len(pre)-40,j)
                if k<0: k=j
            return k
    raise SystemExit('no anchor for pos %d'%pos)
starts=[(n,t,anchor(p)) for n,t,p in hs]
end1=V.find('அந்தி நேரம் அமைதி பெற்று')
for idx,(n,t,s) in enumerate(starts):
    e=starts[idx+1][2] if idx+1<len(starts) else end1
    seg=V[s:e]
    paras=re.split(r'(?<=[.!?”’"\'])(?=[^\s.!?”’"\',)])',seg)
    books[1][n]={'n':n,'title':clean(t),'paras':[clean(x) for x in paras if clean(x)]}
meta=[('புது வெள்ளம்','New Floods','The Fresh Floods','pudhu-vellam'),('சுழற்காற்று','The Whirlwind','Whirlwind','suzhar-katru'),('கொலை வாள்','The Killer Sword','Sword of Slaughter','kolai-vaal'),('மணிமகுடம்','The Jewelled Crown','The Crown','mani-magudam'),('தியாக சிகரம்','The Pinnacle of Sacrifice','Pinnacle of Sacrifice','thiyaga-sigaram')]
manifest={'books':[]}
for b in range(1,6):
    chs=books[b]; nums=sorted(chs)
    assert nums==list(range(1,len(nums)+1)),(b,nums)
    os.makedirs(os.path.join(OUT,str(b)),exist_ok=True)
    clist=[]
    for n in nums:
        c=chs[n]
        chars=sum(len(p) for p in c['paras'])
        words=sum(len(p.split()) for p in c['paras'])
        json.dump({'book':b,'n':n,'title':c['title'],'paras':c['paras']},open(os.path.join(OUT,str(b),f'{n}.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
        clist.append({'n':n,'title':c['title'],'words':words,'min':max(1,round(words/120))})
    ta,en,_,slug=meta[b-1]
    manifest['books'].append({'id':b,'ta':ta,'en':en,'slug':slug,'chapters':clist,'words':sum(c['words'] for c in clist)})
    print(b,len(nums),'chapters',sum(c['words'] for c in clist),'words')
json.dump(manifest,open(os.path.join(OUT,'manifest.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
# ---- scene hints for illustrations (kind + time of day) from title and opening text
KINDS={
 'sea':['கடல்','கப்பல்','படகு','கோடிக்கரை','தீவு','அலை','சுழல்','துறைமுக','மரக்கலம்','கலங்கரை','நாகை','இலங்கை','ஈழ'],
 'river':['ஏரி','ஆற்ற','ஆறு','காவேரி','நதி','வெள்ள','ஓடம்','கரையில்','கொள்ளிட','குளம்','அரிசிலாறு','முதலை','நீர்'],
 'temple':['கோயில்','ஆலய','சிவ','பெருமாள்','விஹார','விகார','சந்நிதி','பட்டர்','புத்த','தெய்வ','பூஜை','குருக்கள்'],
 'palace':['மாளிகை','அரண்மனை','அந்தப்புர','மண்டப','சபை','அரியணை','சிம்மாசன','மகுட','மந்திராலோசனை','சக்கரவர்த்தி','இளவரச'],
 'forest':['காடு','காட்டு','அரண்ய','வனம்','மலை','மரத்','குகை','புதர்'],
 'town':['வீதி','நகர','பழையாறை','தஞ்சை','கோட்டை','சந்தை','ஊர்','கடைவீதி','குடந்தை','காஞ்சி','மாமல்லபுர'],
}
TIMES={'night':['இரவு','நிலா','நிலவு','நள்ளிரவு','நடுநிசி','இருள்','சந்திர','நிலவறை','நட்சத்திர','இருட்டு','தீவர்த்தி'],
       'dusk':['அந்தி','மாலை','அஸ்தமி','சாயங்கால'],
       'dawn':['காலை','உதய','விடியற்','பொழுது புலர','விடிந்த']}
DEF={1:'river',2:'sea',3:'forest',4:'palace',5:'temple'}
for bk in manifest['books']:
    b=bk['id']
    for c in bk['chapters']:
        ch=books[b][c['n']]
        txt=ch['title']*4+' '+' '.join(ch['paras'][:4])[:1500]
        sc={k:sum(txt.count(w) for w in ws) for k,ws in KINDS.items()}
        best=max(sc,key=sc.get)
        c['k']=best if sc[best]>0 else DEF[b]
        ts={k:sum(txt.count(w) for w in ws) for k,ws in TIMES.items()}
        bt=max(ts,key=ts.get)
        c['t']=bt if ts[bt]>0 else ''
json.dump(manifest,open(os.path.join(OUT,'manifest.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
from collections import Counter
print(Counter(c['k'] for bk in manifest['books'] for c in bk['chapters']), Counter(c['t'] for bk in manifest['books'] for c in bk['chapters']))
