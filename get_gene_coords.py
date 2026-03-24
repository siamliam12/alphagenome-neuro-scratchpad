import pandas as pd
import math

gtf_path = "../data/raw/gencode.v49.annotation.gtf.gz"
cols = ['chr','source','feature','start','end','score','strand','frame','attribute']
gtf = pd.read_csv(gtf_path, sep='\t', comment='#', names=cols, low_memory=False)
# df = pd.read_csv(gtf_path, sep='\t', comment='#', header=None)
# print(df.head())

# extract gene_name and gene_type
gtf['gene_name'] = gtf['attribute'].str.extract(r'gene_name "([^"]+)"')
gtf['gene_type'] = gtf['attribute'].str.extract(r'gene_type "([^"]+)"')

genes = gtf[(gtf['feature'] == 'gene') & (gtf['gene_type'] == 'protein_coding')]

app = genes[genes['gene_name'] == 'APP']
mapt = genes[genes['gene_name'] == 'MAPT']

# print(app)
# print(mapt)

def make_window(row,gene_name,padding=250_000):
    return pd.Series({
        'gene': gene_name, 
        'chr':row['chr'],
        'window_start': max(1, row['start'] - padding),
        'window_end': row['end'] + padding
    })

app_win = make_window(app.iloc[0],gene_name='APP')
mapt_win = make_window(mapt.iloc[0],gene_name='MAPT')

windows = pd.DataFrame([app_win,mapt_win])

windows.to_csv("../data/processed/app_mapt_windows.csv", index=False)