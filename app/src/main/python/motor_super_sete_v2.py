import re, math, itertools

PERIMETROS=[20,30,40,50,60,70,80,90,100,120,140,160,180]
TOP=4

def slope(v):
    n=len(v)
    if n<2:return 0.0
    mx=(n-1)/2; my=sum(v)/n
    den=sum((i-mx)**2 for i in range(n))
    return 0.0 if den==0 else sum((i-mx)*(y-my) for i,y in enumerate(v))/den

def clamp(x,a,b): return max(a,min(b,x))

def parse(text):
    hist=[]
    for line in text.splitlines():
        line=line.strip()
        if not line: continue
        parts=re.split(r'[;|\t,]+',line)
        jogo=None
        for i in range(max(0,len(parts)-6)):
            bloco=parts[i:i+7]
            if len(bloco)==7 and all(re.fullmatch(r'\d',x.strip() or 'x') for x in bloco):
                jogo=tuple(int(x.strip()) for x in bloco); break
        nums=[int(x) for x in re.findall(r'\d+',line)]
        if jogo is None and len(nums)>=8:
            for i in range(1,len(nums)-6):
                b=nums[i:i+7]
                if all(0<=x<=9 for x in b): jogo=tuple(b); break
        if jogo is None: continue
        concurso=nums[0] if nums else len(hist)+1
        hist.append((concurso,jogo))
    hist.sort(key=lambda x:x[0])
    if len(hist)<10: raise ValueError('Histórico insuficiente ou formato não reconhecido.')
    return hist

def rep(a,b): return sum(1 for i in range(7) if a[i]==b[i])
def dist(vals):
    d={i:0 for i in range(8)}
    for x in vals:
        if x in d:d[x]+=1
    return d

def prever_repeticoes(hist):
    vals=[rep(hist[i-1][1],hist[i][1]) for i in range(1,len(hist))]
    u,p,a=vals[-1],vals[-2],vals[-3]
    geral=dist(vals); rec=dist(vals[-120:])
    d1=dist([vals[i+1] for i in range(len(vals)-1) if vals[i]==u])
    d2=dist([vals[i+1] for i in range(1,len(vals)-1) if vals[i-1]==p and vals[i]==u])
    d3=dist([vals[i+1] for i in range(2,len(vals)-1) if vals[i-2]==a and vals[i-1]==p and vals[i]==u])
    start=max(0,len(vals)-120)
    d1r=dist([vals[i+1] for i in range(start,len(vals)-1) if vals[i]==u])
    tg=max(1,sum(geral.values())); tr=max(1,sum(rec.values())); t1=max(1,sum(d1.values())); t1r=max(1,sum(d1r.values())); t2=sum(d2.values()); t3=sum(d3.values())
    scores={}
    for r in range(8):
        s=(geral[r]/tg)*18+(rec[r]/tr)*20+(d1[r]/t1)*30+(d1r[r]/t1r)*22
        if t2>=4:s+=(d2[r]/t2)*45
        elif t2>0:s+=(d2[r]/t2)*18
        if t3>=3:s+=(d3[r]/t3)*35
        elif t3>0:s+=(d3[r]/t3)*10
        if r>=5:s*=0.60
        scores[r]=s
    ranking=sorted(range(8),key=lambda r:(scores[r],d2[r],d1[r],rec[r],geral[r],-r),reverse=True)
    return ranking[0],(a,p,u),scores,d2,d1,rec,geral

def forca(col,dig,janela):
    s=[1 if j[col]==dig else 0 for _,j in janela]; n=len(s)
    def freq(k):
        x=s[-min(k,n):]; return sum(x)/len(x)*100
    f20,f10,f5=freq(20),freq(10),freq(5)
    f30=freq(30); ft=sum(s)/n*100
    pesos=list(range(1,n+1)); temp=sum(v*w for v,w in zip(s,pesos))/sum(pesos)*100
    m=max(1,n//2); crescimento=sum(s[m:])/max(1,len(s[m:]))-sum(s[:m])/len(s[:m])
    atraso=n
    for k,v in enumerate(reversed(s)):
        if v: atraso=k; break
    bonus=1 if atraso==0 else 3 if atraso<=2 else 2 if atraso<=5 else 1 if atraso<=8 else 0
    sc=ft*.10+f30*.15+f20*.20+f10*.26+f5*.12+temp*.14+clamp(slope(s)*220,-10,10)+clamp(slope(s[-30:])*130,-10,10)+clamp(slope(s[-20:])*120,-12,12)+clamp(slope(s[-10:])*100,-15,15)+clamp(crescimento*35,-12,12)+bonus
    return sc

def escolher_perimetro(hist):
    best=None
    for p in PERIMETROS:
        if len(hist)<p: continue
        jan=hist[-p:]; total=0
        for c in range(7):
            vals=sorted([(forca(c,d,jan),d) for d in range(10)],reverse=True)
            total+=vals[0][0]
        if best is None or total>best[0]: best=(total,p)
    return best[1]

def analisar_texto(text):
    hist=parse(text)
    previsto,padrao,scores,d2,d1,rec,geral=prever_repeticoes(hist)
    p=escolher_perimetro(hist)
    janela=hist[-p:]
    ultimo=hist[-1][1]
    rankings=[]; dados=[]
    for c in range(7):
        vals=sorted([(forca(c,d,janela),d) for d in range(10)],reverse=True)
        rankings.append([d for _,d in vals]); dados.append({d:s for s,d in vals})
    op=[]
    for c in range(7):
        lst=list(rankings[c][:TOP])
        if ultimo[c] not in lst: lst[-1]=ultimo[c]
        op.append(tuple(dict.fromkeys(lst)))
    melhor=None
    for jogo in itertools.product(*op):
        if sum(jogo[i]==ultimo[i] for i in range(7)) != previsto: continue
        serie=[]; inval=False
        for _,resultado in janela:
            ac=sum(jogo[i]==resultado[i] for i in range(7))
            if ac>=6: inval=True; break
            serie.append(ac)
        if inval: continue
        q2,q3,q4,q5=serie.count(2),serie.count(3),serie.count(4),serie.count(5)
        u5,u10,u20,u30=serie[-5:],serie[-10:],serie[-20:],serie[-30:]
        t5,t10,t20,t30=u5.count(3),u10.count(3),u20.count(3),u30.count(3)
        q45,q410,q420,q430=u5.count(4),u10.count(4),u20.count(4),u30.count(4)
        q510,q520=u10.count(5),u20.count(5)
        d10,d20,d30=u10.count(2),u20.count(2),u30.count(2)
        qtd_blocos=min(10,len(serie)); tam=max(1,math.ceil(len(serie)/qtd_blocos))
        tb=[]; qb=[]; qib=[]; pontos=[]
        for ini in range(0,len(serie),tam):
            trecho=serie[ini:ini+tam]
            dd,tt,qq,qi=trecho.count(2),trecho.count(3),trecho.count(4),trecho.count(5)
            tb.append(tt); qb.append(qq); qib.append(qi)
            pontos.append(dd*1.0+tt*5.0+qq*13.0+qi*15.0)
        bterno=sum(x>0 for x in tb); bquadra=sum(x>0 for x in qb)
        slb=slope(pontos)
        metade=max(1,len(pontos)//2)
        crescimento=sum(pontos[metade:])/max(1,len(pontos[metade:]))-sum(pontos[:metade])/len(pontos[:metade])
        subidas=sum(b>a for a,b in zip(pontos,pontos[1:]))
        fm=sum(dados[c][jogo[c]] for c in range(7))/7
        score=(q3*12+q4*30+q5*6+q2 + t30*2+t20*4+t10*7+t5*11 + q430*4+q420*7+q410*11+q45*15 + q520+q510*1.5 + d30*.5+d20*.8+d10*1.2 + bterno*4+bquadra*7 + clamp(slope(serie)*30,-8,8)+clamp(slope(u30)*40,-10,10)+clamp(slope(u20)*50,-12,12)+clamp(slope(u10)*60,-15,15)+clamp(slb*8,-20,20)+clamp(crescimento*2,-20,20)+subidas*2+fm*.15)
        chave=(q410,q420,t10,t20,q4,bquadra,bterno,q3,slb,crescimento,q5,q2,score,jogo)
        if melhor is None or chave>melhor[0]:
            melhor=(chave,jogo,(q2,q3,q4,q5),t30,t20,t10,t5,q430,q420,q410,q45,tb,qb,pontos,slb,crescimento,score)
    if melhor is None: raise ValueError('Nenhum jogo válido encontrado.')
    _,jogo,qq,t30,t20,t10,t5,q430,q420,q410,q45,tb,qb,pontos,slb,cresc,score=melhor
    reps=[str(i+1) for i in range(7) if jogo[i]==ultimo[i]]
    return (f"SUPER SETE - ENGROSSANDO O TALO V2\n\nÚltimo concurso: {hist[-1][0]}\nÚltimo resultado: " + ' | '.join(f'C{i+1}:{ultimo[i]}' for i in range(7)) +
            f"\nPadrão anterior: {padrao[1]} -> {padrao[2]}\nRepetição prevista: {previsto}\nPerímetro do talo: {p}\n\nMELHOR JOGO: " + ' | '.join(f'C{i+1}:{jogo[i]}' for i in range(7)) +
            "\nDígitos: " + ' '.join(map(str,jogo)) + "\nColunas repetidas: " + (', '.join(reps) if reps else 'nenhuma') +
            f"\n\nDuques {qq[0]} | Ternos {qq[1]} | Quadras {qq[2]} | Quinas {qq[3]} | 6=0 | 7=0" +
            f"\nTernos 30/20/10/5: {t30}/{t20}/{t10}/{t5}" + f"\nQuadras 30/20/10/5: {q430}/{q420}/{q410}/{q45}" +
            f"\nTernos por bloco: {tb}\nQuadras por bloco: {qb}\nPontos: {pontos}\nSLOPE: {slb:+.4f} | Crescimento: {cresc:+.2f} | Score: {score:.2f}")
