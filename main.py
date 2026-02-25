import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from alphagenome.models import dna_client, dna_output, variant_scorers
from alphagenome.visualization import plot_components
from alphagenome.data import gene_annotation, genome, track_data, transcript
from dotenv import load_dotenv
load_dotenv()
import os
API_KEY = os.getenv("SECRET_KEY")
client = dna_client.create(API_KEY)

def load_and_parse_gtf(filepath):
    print("Loading and parsing GTF file... this might take a minute depending on file size.")
    cols = ['Chromosome', 'source', 'Feature', 'Start', 'End', 'score', 'Strand', 'Frame', 'attribute']
    df = pd.read_csv(filepath, sep='\t', comment='#', names=cols, low_memory=False)
    
    df['transcript_type'] = df['attribute'].str.extract(r'transcript_type "([^"]+)"')
    df['transcript_biotype'] = df['attribute'].str.extract(r'transcript_biotype "([^"]+)"') 
    df['gene_name'] = df['attribute'].str.extract(r'gene_name "([^"]+)"')
    df['transcript_id'] = df['attribute'].str.extract(r'transcript_id "([^"]+)"')
    df['gene_id'] = df['attribute'].str.extract(r'gene_id "([^"]+)"')
    return df

gtf_path = "C:/Users/siama/Projects/research/alphaGenome/gencode.v43.annotation.gtf.gz"
gtf_df = load_and_parse_gtf(gtf_path)

gtf = gene_annotation.filter_protein_coding(gtf_df)
gtf = gene_annotation.filter_to_longest_transcript(gtf)

variant = genome.Variant(
    chromosome='chr22', 
    position=36201698, 
    reference_bases='A', 
    alternate_bases='C'
)

analysis_interval = variant.reference_interval.resize(2**20) 
zoom_interval = genome.Interval('chr22', 36195000, 36220000)

extractor = transcript.TranscriptExtractor(gtf)
transcripts = extractor.extract(zoom_interval)

requested_outputs = [dna_output.OutputType.RNA_SEQ]
ontology_terms = ['UBERON:0001157'] # Transverse Colon tissue

print("Running DeepMind AlphaGenome predictions...")
variant_output = client.predict_variant(
    variant=variant,
    interval=analysis_interval,
    requested_outputs=requested_outputs,
    ontology_terms=ontology_terms
)

ref_tracks = variant_output.reference.rna_seq
alt_tracks = variant_output.alternate.rna_seq

scorers = [variant_scorers.GeneMaskLFCScorer(requested_output=dna_output.OutputType.RNA_SEQ)]

print("Calculating variant severity score...")
scores_anndata_list = client.score_variant(
    variant=variant, 
    interval=analysis_interval, 
    variant_scorers=scorers
)

tidy_scores_df = variant_scorers.tidy_scores(scores_anndata_list)
print("\nVariant Impact Scores:")
print(tidy_scores_df[['gene_name', 'track_name', 'raw_score', 'quantile_score']].head())

is_neg_strand = (ref_tracks.metadata['strand'] == '-').values

ref_neg_tracks = ref_tracks.filter_tracks(is_neg_strand)
alt_neg_tracks = alt_tracks.filter_tracks(is_neg_strand)

print("Generating visualizations...")
plot_components.plot(
    components=[
        plot_components.OverlaidTracks({'REF': ref_neg_tracks, 'ALT': alt_neg_tracks}),
        plot_components.TranscriptAnnotation(transcripts)
    ],
    annotations=[
        plot_components.VariantAnnotation([variant])
    ],
    interval=zoom_interval, 
    title=f"Impact of {variant.chromosome}:{variant.position}:{variant.reference_bases}>{variant.alternate_bases} on APOL4 Expression in Colon Tissue"
)

output_filename = "APOL4_variant_impact.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"Success! Plot saved to your folder as {output_filename}")