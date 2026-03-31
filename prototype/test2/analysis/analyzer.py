import pandas as pd
from pyfaidx import Fasta
import alphagenome as ag
import matplotlib.pyplot as plt
from alphagenome.visualization import plot_components as ag_plt
import alphagenome.models.dna_client as ag_client
from dotenv import load_dotenv
import os
import numpy as np
load_dotenv()

# 1. Setup paths
csv_path = "../data/processed/alphagenome_task_list.csv"
genome_path = "../data/raw/hg38.fa" # Make sure this is UNZIPPED


# 2. Load your "Instruction Set"
tasks = pd.read_csv(csv_path)

# 3. Open the Reference Genome (the indexer)
# This will create a small .fai file next to your .fa file
genome = Fasta(genome_path)

# validation
# # 2. Get the specific task for SNCA
# snca_task = tasks.iloc[0]
# snp_pos = int(snca_task['snp_pos'])
# chrom = snca_task['chrom']

# # --- INSERT THE PEEK HERE ---
# print(f"\n--- DEBUG: NEIGHBORHOOD PEEK FOR {chrom}:{snp_pos} ---")
# peek_start = snp_pos - 6 
# peek_end = snp_pos + 5
# # Fetching the tiny string
# peek_seq = str(genome[chrom][peek_start:peek_end]).upper()

# print(f"11-bp String:  {peek_seq}")
# print(f"Target Letter: {peek_seq[5]} (at pos {snp_pos})")
# print(f"Left Side:     {peek_seq[:5]}")
# print(f"Right Side:    {peek_seq[6:]}")
# print(f"GWAS Expected: {snca_task['ref']}")

def prepare_sequences(task_row, genome, window_size=1000000):
    chrom = task_row['chrom']
    snp_pos = int(task_row['snp_pos'])
    ref_letter = task_row['ref'].upper()
    alt_letter = task_row['alt'].upper()
    
    # 1. Define the 1Mb boundaries
    half_win = window_size // 2
    start = snp_pos - half_win
    end = snp_pos + half_win
    
    # 2. Fetch the sequence
    # We use .upper() to ensure we aren't dealing with mixed case
    healthy_seq = str(genome[chrom][start:end]).upper()
    
    # 3. FIX THE INDEX: 
    # Because Python strings start at 0 and Genomic coordinates at 1,
    # the exact center of our window is at snp_pos - start - 1
    local_idx = snp_pos - start - 1
    
    # 4. Final Validation Check
    actual_ref = healthy_seq[local_idx]
    if actual_ref != ref_letter:
        print(f"CRITICAL ERROR: Ref at index {local_idx} is {actual_ref}, but expected {ref_letter}")
        # If this happens, it means we are still off-by-one
        return None, None

    # 5. Create the Parkinson's version
    seq_list = list(healthy_seq)
    seq_list[local_idx] = alt_letter
    disease_seq = "".join(seq_list)
    
    return healthy_seq, disease_seq

# --- RUN FOR ROW 0 (SNCA) ---
snca_task = tasks.iloc[0]
wildtype, mutant = prepare_sequences(snca_task,genome,window_size=1048576)

# print(f"Success! Generated two 1Mb sequences for {snca_task['chrom']}:{snca_task['snp_pos']}")
# print(f"Healthy sequence starts with: {wildtype[:50]}...")

# 1. Load the Neuro-specific model
api_key = os.getenv('API_KEY')
client = ag_client.create(api_key=api_key)

metadata = {
    "ontology_terms": ["UBERON:0000955"], 
    "requested_outputs": [
        ag_client.OutputType.CAGE,      # Expression
        ag_client.OutputType.DNASE,     # Chromatin State
        ag_client.OutputType.CHIP_TF,   # TF Binding
        ag_client.OutputType.CONTACT_MAPS # HI-C (3D)
    ]
}

def run_alphagenome_inference(wt_seq, mt_seq):
    print("Sending sequences to AlphaGenome API...")
    
    # We pass the Enum list here
    wt_results = client.predict_sequence(
        sequence=wt_seq,
        ontology_terms=metadata["ontology_terms"], # Brain
        requested_outputs=metadata["requested_outputs"]
    )
    
    mt_results = client.predict_sequence(
        sequence=mt_seq,
        ontology_terms=metadata["ontology_terms"],
        requested_outputs=metadata["requested_outputs"]
    )
    
    return wt_results, mt_results


def plot_experiment_results(wt_preds, mt_preds, task_row):
    print("\n--- Generating Functional Analysis Plots ---")

    def process_track(track_obj, label="track"):
        # 1. Safety Check: Does the attribute exist and have values?
        if not hasattr(track_obj, 'values') or track_obj.values is None:
            print(f"Warning: {label} object has no values. Returning zeros.")
            return np.zeros(8192)
        
        data = np.array(track_obj.values)
        
        # 2. Check for empty data (IndexError prevention)
        if data.size == 0:
            print(f"Warning: {label} data is empty. Returning zeros.")
            return np.zeros(8192)

        # 3. Handle multi-channel data (e.g., (1048576, 2))
        # We take the first channel [:, 0] if multiple exist
        if len(data.shape) > 1:
            data = data[:, 0]
        
        # 4. Downsample from 1,048,576 to 8,192 bins (128bp means)
        # This makes the 'spikes' visible and aligns with Matplotlib
        try:
            # Reshape to (8192, 128) and average each row
            return data.reshape(8192, -1).mean(axis=1)
        except ValueError:
            print(f"Note: {label} shape {data.shape} is not 2^20. Returning as is.")
            return data

    # --- Step 1: Process all 3 linear modalities ---
    wt_cage = process_track(wt_preds.cage, "CAGE")
    mt_cage = process_track(mt_preds.cage, "CAGE")
    
    # Note: Use .dnase or .atac depending on your 'requested_outputs'
    wt_chrom = process_track(wt_preds.dnase, "DNASE") 
    mt_chrom = process_track(mt_preds.dnase, "DNASE")
    
    wt_tf = process_track(wt_preds.chip_tf, "TF Binding")
    mt_tf = process_track(mt_preds.chip_tf, "TF Binding")

    # --- Step 2: Setup Plotting Surface ---
    fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=False)
    num_bins = len(wt_cage)
    x_axis = np.arange(num_bins)
    snp_bin = 4096 # The center of an 8192-bin window

    # Plot 1: Gene Expression (CAGE)
    axes[0].plot(x_axis, wt_cage, color='#1f77b4', label='Healthy (WT)', alpha=0.7)
    axes[0].plot(x_axis, mt_cage, color='#d62728', label='Parkinson\'s (MT)', alpha=0.7)
    axes[0].set_title(f"SNCA Expression (CAGE) | {task_row['chrom']}:{task_row['snp_pos']}", fontsize=14)
    axes[0].set_ylabel("Signal Intensity")
    axes[0].legend(loc='upper right')

    # Plot 2: Chromatin Accessibility (DNASE)
    # Using fill_between for that professional 'Genomic Track' look
    axes[1].fill_between(x_axis, 0, wt_chrom, color='gray', alpha=0.3, label='WT Openness')
    axes[1].plot(x_axis, mt_chrom, color='#ff7f0e', label='MT Openness', linewidth=1)
    axes[1].set_title("Chromatin Accessibility (DNASE-seq)", fontsize=12)
    axes[1].set_ylabel("Accessibility")
    axes[1].legend(loc='upper right')

    # Plot 3: Transcription Factor (TF) Binding
    axes[2].plot(x_axis, wt_tf, color='green', label='WT TF Binding', alpha=0.6)
    axes[2].plot(x_axis, mt_tf, color='purple', label='MT TF Binding', alpha=0.6)
    axes[2].set_title("Transcription Factor Binding (ChIP-seq)", fontsize=12)
    axes[2].set_ylabel("Binding Probability")
    axes[2].legend(loc='upper right')

    # Plot 4: Functional Impact (Delta Track)
    # This is the 'Money Shot' for your presentation
    delta = mt_cage - wt_cage
    axes[3].bar(x_axis, delta, color='magenta', width=1.0, label='Expression Delta')
    # Draw a line exactly where the SNP is
    axes[3].axvline(x=snp_bin, color='black', linestyle='--', linewidth=1.5, label='SNP Location')
    axes[3].set_title("Net Functional Impact (Mutant - Healthy)", fontsize=12, fontweight='bold')
    axes[3].set_xlabel("Genomic Coordinate (Bins of 128bp)")
    axes[3].legend(loc='upper right')

    # Zoomed Window: Only show the center 200 bins for the Delta
    axes[3].set_xlim(snp_bin - 100, snp_bin + 100)

    plt.tight_layout()
    plot_filename = f"snca_impact_{task_row['chrom']}_{task_row['snp_pos']}.png"
    plt.savefig(f"../output/graphs/{plot_filename}", dpi=300)
    print(f"SUCCESS: Analysis visualization saved to {plot_filename}")

def get_modality_summary(wt_pred_obj, mt_pred_obj, attr_name, mode='local'):
    """
    Extracts signal using two different scopes:
    - 'local': Looks only at the 100bp surrounding the SNP (The Evidence).
    - 'global': Looks at the highest peak in the entire 1Mb window (The Result).
    """
    try:
        if not hasattr(wt_pred_obj, attr_name):
            return 0.0, 0.0, 0.0
        
        # Get raw values and take first channel
        wt_data = np.array(getattr(wt_pred_obj, attr_name).values)[:, 0]
        mt_data = np.array(getattr(mt_pred_obj, attr_name).values)[:, 0]
        
        if wt_data.size == 0:
            return 0.0, 0.0, 0.0
            
        if mode == 'global':
            # FIND THE "CRIME": Look for the highest peak anywhere (The Promoter)
            wt_val = np.max(wt_data)
            mt_val = np.max(mt_data)
        else:
            # FIND THE "FINGERPRINT": Look exactly at the SNP (The Switch)
            snp_idx = 524288
            wt_val = np.max(wt_data[snp_idx-50 : snp_idx+50])
            mt_val = np.max(mt_data[snp_idx-50 : snp_idx+50])
        
        return float(wt_val), float(mt_val), float(mt_val - wt_val)
        
    except Exception as e:
        print(f"Error processing {attr_name}: {e}")
        return 0.0, 0.0, 0.0

# --- EXECUTION: Connecting the Cause to the Effect ---
wt_preds, mt_preds = run_alphagenome_inference(wildtype, mutant)

# 1. We look at CAGE GLOBALLY to find the gene's response
cage_wt, cage_mt, cage_delta = get_modality_summary(wt_preds, mt_preds, 'cage', mode='global')

# 2. We look at DNASE and TF LOCALLY to find the mutation's physical impact
dnase_wt, dnase_mt, dnase_delta = get_modality_summary(wt_preds, mt_preds, 'dnase', mode='local')
tf_wt, tf_mt, tf_delta = get_modality_summary(wt_preds, mt_preds, 'chip_tf', mode='local')
hic_wt, hic_mt, hic_delta = get_modality_summary(wt_preds, mt_preds, 'contact_maps', mode='local')

# --- FINAL RESEARCH TABLE ---
print("\n" + "="*75)
print(f"RESEARCH SUMMARY: rs356168 Functional Analysis")
print("="*75)
print(f"{'Modality':<28} | {'Scope':<10} | {'Healthy':<10} | {'Mutant':<10} | {'Delta'}")
print("-"*75)

print(f"{'Gene Expression (CAGE)':<28} | {'GLOBAL':<10} | {cage_wt:<10.4f} | {cage_mt:<10.4f} | {cage_delta:+.4f}")
print(f"{'Chromatin Access (DNASE)':<28} | {'LOCAL':<10} | {dnase_wt:<10.4f} | {dnase_mt:<10.4f} | {dnase_delta:+.4f}")
print(f"{'TF Binding (CHIP_TF)':<28} | {'LOCAL':<10} | {tf_wt:<10.4f} | {tf_mt:<10.4f} | {tf_delta:+.4f}")
print(f"{'3D Looping (Hi-C)':<28} | {'LOCAL':<10} | {hic_wt:<10.4f} | {hic_mt:<10.4f} | {hic_delta:+.4f}")
print("="*75)

# Run the visualization
plot_experiment_results(wt_preds, mt_preds, snca_task)
