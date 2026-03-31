import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import gzip

# File paths
gtf_path = "../data/raw/gencode.v49.annotation.gtf.gz"
gwas_path = "../data/raw/GCST90473307.tsv.gz"

# Define GTF columns
cols = ["chr", "source", "feature", "start", "end", "score", "strand", "phase", "attribute"]

# 1. PEAKING & CHUNKING
# Standard threshold for significance
threshold = 5e-8
chunks = pd.read_csv(gwas_path, sep='\t', compression='gzip', chunksize=100000)

# Helper function to extract gene_name from the messy GTF attribute string
def extract_gene_name(attr_string):
    try:
        # Looks for 'gene_name "XYZ";' and grabs XYZ
        return attr_string.split('gene_name "')[1].split('"')[0]
    except:
        return "Unknown"

# Finding SNCA from the GTF file 
def find_gene_in_gtf(file_path, target_gene):
    with gzip.open(file_path, 'rt') as f:
        for line in f:
            if line.startswith('#'): continue
            # We look for the 'gene' feature specifically
            if '\tgene\t' in line and f'gene_name "{target_gene}"' in line:
                return line.strip().split('\t')
    return None

def find_lead_snps(df, window_size=500000):
    sorted_df = df.sort_values('p_value').copy()
    lead_snps = []
    while len(sorted_df) > 0:
        lead = sorted_df.iloc[0]
        lead_snps.append(lead)
        chrom = lead['chromosome']
        pos = lead['base_pair_location']
        mask = (sorted_df['chromosome'] == chrom) & \
               (sorted_df['base_pair_location'] >= pos - window_size) & \
               (sorted_df['base_pair_location'] <= pos + window_size)
        sorted_df = sorted_df[~mask]
    return pd.DataFrame(lead_snps)

def generate_windows(lead_snps_df, gencode_df, window_size=1000000):
    half_window = window_size // 2
    experiments = []

    for _, snp in lead_snps_df.iterrows():
        snp_pos = int(snp['base_pair_location'])
        # Standardize: make sure chromosome is just a string number (e.g., "4")
        chrom_raw = str(snp['chromosome']).replace('chr', '')
        
        win_start = snp_pos - half_window
        win_end = snp_pos + half_window
        
        # Standardize gencode 'chr' column to match (remove 'chr' prefix if exists)
        gencode_chroms = gencode_df['chr'].astype(str).str.replace('chr', '')
        
        overlapping_genes = gencode_df[
            (gencode_chroms == chrom_raw) & 
            (gencode_df['end'] >= win_start) & 
            (gencode_df['start'] <= win_end)
        ]
        
        if not overlapping_genes.empty:
            # Use our helper function to get clean names like "SNCA"
            gene_names = [extract_gene_name(attr) for attr in overlapping_genes['attribute'].tolist()]
        else:
            gene_names = ["No Gene Nearby"]
        
        experiments.append({
            'chrom': f"chr{chrom_raw}", # Keep 'chr' prefix for AlphaGenome input
            'snp_pos': snp_pos,
            'genes_in_window': gene_names,
            'p_val': snp['p_value'],
            'ref': snp['other_allele'],
            'alt': snp['effect_allele']
        })
        
    return pd.DataFrame(experiments)

# 2. GET GENCODE DATA
snca_data = find_gene_in_gtf(gtf_path, "SNCA")
if snca_data:
    gene_dict = dict(zip(cols, snca_data))
    gencode_df = pd.DataFrame([gene_dict]).copy()
    # Convert coordinates to numbers for math
    gencode_df['start'] = pd.to_numeric(gencode_df['start'])
    gencode_df['end'] = pd.to_numeric(gencode_df['end'])
else:
    print("Error: SNCA not found in GTF file.")
    exit()

# 3. GET GWAS HITS
significant_snps = []
for chunk in chunks:
    hits = chunk[chunk['p_value'] < threshold]
    significant_snps.append(hits)
gwas_hits = pd.concat(significant_snps)

# 4. CLUMP & GENERATE WINDOWS
lead_snps_df = find_lead_snps(gwas_hits)
final_windows = generate_windows(lead_snps_df, gencode_df)

print("\n--- ALPHA GENOME EXPERIMENT LIST ---")
# Increased head to 24 so you see all your lead SNPs
print(final_windows[['chrom', 'snp_pos', 'genes_in_window', 'p_val']].head(24))

# Save the final task list to a CSV for your records and for the next stage
output_path = "../data/processed/alphagenome_task_list.csv"
final_windows.to_csv(output_path, index=False)

print(f"\nSuccess! Experiment manifest saved to: {output_path}")
print("You now have the 'GPS Coordinates' for 24 distinct Parkinson's experiments.")