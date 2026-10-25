import struct, sys, pandas as pd
def read_dbf(path, enc='latin-1'):
    with open(path,'rb') as f:
        h=f.read(32)
        n,hl,rl=struct.unpack('<IHH',h[4:12])
        fields=[]
        while True:
            d=f.read(32)
            if d[0]==0x0D: break
            name=d[:11].split(b'\x00')[0].decode(enc)
            fields.append((name,chr(d[11]),d[16]))
        f.seek(hl)
        raw=f.read(n*rl)
    rows=[]
    for i in range(n):
        rec=raw[i*rl:(i+1)*rl]
        if rec[:1]==b'*': continue
        pos=1; row=[]
        for name,t,ln in fields:
            row.append(rec[pos:pos+ln].decode(enc,errors='replace').strip()); pos+=ln
        rows.append(row)
    return pd.DataFrame(rows,columns=[f[0] for f in fields]), fields, n, rl
if __name__=='__main__':
    df,fields,n,rl=read_dbf(sys.argv[1])
    print(n,rl,fields); print(df.head(5).to_string())
    df.to_parquet(sys.argv[2]) if len(sys.argv)>2 else None
