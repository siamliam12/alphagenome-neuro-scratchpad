import pandas as pd

gwas_path = "../data/raw/gwas-association-downloaded_2026-03-18-accessionId_GCST90027158.tsv"
gwas = pd.read_csv(gwas_path, sep='\t',low_memory=False)
# print(gwas.columns)
# print(gwas.head())

windows = pd.read_csv("C:/Users/siama/Projects/research/alphaGenome/prototype/data/processed/app_mapt_windows.csv")

def subset_to_window(df,chr_col,pos_col,window_row):
    mask = (
        (df[chr_col].astype(str) == window_row['chr'].replace('chr','')) & 
        (df[pos_col] >= window_row['window_start']) &
        (df[pos_col] <= window_row['window_end'])
    )
    return df[mask].copy()

app_win = windows[windows['gene']=='APP'].iloc
mapt_win = windows[windows['gene']=='MAPT'].iloc

app_gwas = subset_to_window(gwas, 'chromosome', 'base_pair_location', app_win)
mapt_gwas = subset_to_window(gwas, 'chromosome', 'base_pair_location', mapt_win)

app_gwas['gene'] = 'APP'
mapt_gwas['gene'] = 'MAPT'

gwas_sub = pd.concat([app_gwas, mapt_gwas], ignore_index=True)
gwas_sub.to_csv("data/processed/app_mapt_gwas_variants.csv", index=False)