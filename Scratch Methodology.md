Methodology
Overall study design
This study aims to identify noncoding “regulatory hotspots” around the amyloid precursor protein gene (APP) and the microtubuleassociated protein tau gene (MAPT) that are predicted to strongly influence gene expression and alternative splicing in brain tissues. We will leverage AlphaGenome, a deep learning model and API developed by Google DeepMind, which predicts multiple functional genomic readouts directly from DNA sequence, including RNA expression, chromatin accessibility, histone modifications, transcription factor binding, splicing features, and longrange chromatin contacts
Rather than analyzing whole individual genomes, we will adopt a variant-centric regulatory genetics approach: we will consider the human reference genome in the regions surrounding APP and MAPT, introduce real or in silico sequence variants, and use AlphaGenome to predict how each variant perturbs regulatory readouts in brainrelevant tracks. We will then aggregate these predictions to construct a “regulatory sensitivity map,” highlighting noncoding intervals where small sequence changes are predicted to cause large effects on APP/MAPT expression or splicing in neuronal and glial contexts.
The methodology has the following main components:
1. Definition of target loci (APP and MAPT genomic windows).
2. Selection of brainrelevant functional genomics tracks within AlphaGenome.
3. Compilation of variant sets (Alzheimer’s GWAS/QTL variants and in silico mutagenesis variants).
4. Use of the AlphaGenome API to compute variant effect predictions across expression and splicing modalities.
5. Construction of expression and splicing “sensitivity maps” and identification of regulatory hotspots.
6. Integration with external Alzheimer’s genetics and regulatory annotations.
7. (Optional) Development of auxiliary models or scoring schemes on top of AlphaGenome outputs.
8. Assessment of methodological and biological contributions.


1. Definition of genomic regions for APP and MAPT
1.1. Gene selection
We focus on two Alzheimer’srelevant genes:
* APP (Amyloid Precursor Protein): encodes the precursor of amyloid? peptides, whose aggregation into amyloid plaques is a hallmark of Alzheimer’s disease pathology.
* MAPT (Microtubule-Associated Protein Tau): encodes tau, which forms neurofibrillary tangles when abnormally phosphorylated or misregulated, another key pathological feature of Alzheimer’s disease.[ppl-ai-file-upload.s3.amazonaws]?
These genes represent central nodes in amyloid and tau biology, respectively, and are therefore natural targets for investigating regulatory variation.
1.2. Genomic windows
For each gene, we will define a genomic window that encompasses:
* The full gene body (all exons and introns).
* Upstream and downstream flanking regions that may contain promoters, enhancers, and other regulatory elements.
A typical choice is ±250–500 kilobases (kb) around the transcription start site (TSS) and transcription end site (TES), constrained by the maximum 1 megabase (Mb) input context that AlphaGenome is designed to accept. For example:[ppl-ai-file-upload.s3.amazonaws]?
* APP window: a contiguous region of length up to ~1 Mb centered on the APP gene.
* MAPT window: similarly defined for MAPT, ensuring that all known exons and introns are included, with additional upstream/downstream sequence to capture putative regulatory elements.
If necessary, windows may be slightly adjusted to align with AlphaGenome’s recommended 1 Mb input interval boundaries.[ppl-ai-file-upload.s3.amazonaws]?

2. Selection of brainrelevant AlphaGenome tracks
AlphaGenome predicts thousands of functional genomic tracks: perbase or perbin values representing experimental assays such as RNAseq (expression), DNaseseq/ATACseq (chromatin accessibility), histone modification ChIPseq, transcription factor ChIPseq, splice site usage, splice junction counts, and HiC/MicroC contact maps across many cell and tissue types.alphagenomedocs+1[ppl-ai-file-upload.s3.amazonaws]?
2.1. Track types (modalities)
We will focus on two primary modality groups:
1. Expressionrelated tracks
o RNAseq coverage: predicted read coverage along the gene and surrounding region, from which genelevel or exonlevel expression can be derived.
o Optionally, CAGE or PROcap tracks (transcription initiation) to understand promoter activity.[ppl-ai-file-upload.s3.amazonaws]?
2. Splicingrelated tracks
o Splice site predictions: probabilities of donor/acceptor splice sites at singlebase resolution.
o Splice site usage: predicted usage (e.g., percent spliced in) of individual splice sites.
o Splice junction counts: predicted read counts for specific exon–exon junctions, reflecting actual splicing events.[ppl-ai-file-upload.s3.amazonaws]?
These modalities are directly relevant to APP and MAPT transcript levels and isoform usage in brain tissues.
2.2. Brainrelevant tissue and celltype tracks
From AlphaGenome’s metadata, we will select tracks corresponding to:
* Human brain tissues (e.g., cortex, hippocampus, frontal cortex, temporal cortex) where available.
* Neuronal and glial cell types (e.g., neuronal cell lines, astrocytelike lines, microglialike cells) if present in the AlphaGenome training data.[alphagenomedocs]?[ppl-ai-file-upload.s3.amazonaws]?
These brainrelated tracks will be the primary context for variant effect analysis. To aid interpretation, we may optionally choose a nonbrain tissue (e.g., liver) as a comparator to assess tissue specificity of predicted effects.

3. Compilation of variant sets
Our analysis will consider two main classes of sequence variants:
1. Observed variants: variants from human genetic studies (GWAS/eQTL/sQTL) near APP and MAPT.
2. In silico variants: dense systematic mutations we introduce computationally to map sensitivity.
3.1. Observed genetic variants
3.1.1. Alzheimer’s GWAS variants
We will extract single nucleotide polymorphisms (SNPs) and small indels from large Alzheimer’s disease genomewide association studies (GWAS) that lie within or near the APP and MAPT windows.pmc.ncbi.nlm.nih+1
* For each GWAS locus intersecting these windows, we will retrieve the index SNP and its credible set (the set of variants with high posterior probability of causality in finemapping analyses, when available).
* We will annotate variants with GWAS summary statistics (effect size, pvalue) and any reported functional annotations.
3.1.2. Brain eQTL and sQTL variants
Where available, we will incorporate variants identified as expression quantitative trait loci (eQTLs) or splicing QTLs (sQTLs) for APP and MAPT in brain tissue datasets such as GTEx or large brain consortia. These variants directly link genotype to variation in expression or splicing in human brain, providing a valuable reference for evaluating AlphaGenome’s predictions.[nature]?[ppl-ai-file-upload.s3.amazonaws]?
3.2. In silico mutagenesis variants
To obtain a dense regulatory sensitivity map, we will perform in silico mutagenesis: a computational procedure where we systematically introduce hypothetical variants into the reference sequence.
3.2.1. Tiled singlenucleotide substitutions
Within predefined subregions of the APP and MAPT windows, we will generate singlenucleotide substitutions at many positions. Priority subregions include:
* Promoters and proximal upstream regions.
* 5? and 3? untranslated regions (UTRs).
* Introns near exon–intron junctions (splice sites).
* Intronic and intergenic regions with known or predicted regulatory marks (e.g., enhancers).
For each selected base, we can either:
* Cycle through all three possible alternative nucleotides (A?C/G/T etc.), or
* Sample a subset of variants to remain within API rate limits.
The result is a large set of hypothetical variants that densely sample the regulatory landscape around APP and MAPT.
3.2.2. Variant representation
Each variant (observed or in silico) will be represented by:
* Chromosome, position, reference allele, alternative allele (chr, pos, REF, ALT).
* Gene window (APP or MAPT), and any known annotations (e.g., intronic, exonic, upstream, GWAS hit, eQTL, sQTL).
This structured representation will feed into the AlphaGenome variant effect API.

4. Variant effect prediction using the AlphaGenome API
4.1. Overview of AlphaGenome variant prediction
AlphaGenome is a sequencetofunction deep learning model trained on human and mouse genomes to predict thousands of genomic tracks from 1 Mb of DNA sequence. The publicly available API allows users to:[deepmind]?[ppl-ai-file-upload.s3.amazonaws]?
* Submit a 1 Mb genomic interval and obtain predicted tracks.
* Submit a reference interval plus a variant (or a set of variants) and obtain variant effect predictions, which quantify the difference between predicted tracks for the reference and alternate alleles.github+1
Variant effect predictions can be summarized into modalityspecific variant scores, such as predicted:
* Change in gene expression (e.g., RNAseq genelevel log fold change) for a target gene.
* Change in splice junction counts or splice site usage.
* Change in chromatin accessibility or histone mark signal at or near the variant.[ppl-ai-file-upload.s3.amazonaws]?
These scoring strategies follow those described in the AlphaGenome paper for eQTLs, sQTLs, and chromatin QTLs.[nature]?[ppl-ai-file-upload.s3.amazonaws]?
4.2. API setup and query structure
We will use the official Python client library for the AlphaGenome API. For each variant, the typical workflow is:[github]?
1. Identify the 1 Mb interval that contains the variant and the relevant gene (APP or MAPT).
2. Call a variant prediction endpoint, specifying:
o The genomic interval.
o The variant (chr, pos, REF, ALT).
o The outputs/tracks of interest (brain RNAseq, brain splicing tracks, etc.).
3. Retrieve:
o Predicted reference and alternate tracks for the selected modalities, or
o Precomputed variant scores summarizing REF vs ALT differences for each modality and tissue.biomcp+1
We will pay attention to API usage limits and likely batch variants by locus and by modality to remain efficient.
4.3. Expressionrelated variant scores
For each variant, and for each brain expression track:
* We will obtain a genelevel expression effect score for APP or MAPT, analogous to an eQTL effect.[nature]?[ppl-ai-file-upload.s3.amazonaws]?
o This is typically computed by aggregating predicted RNAseq coverage over the gene body (or exons) under the REF and ALT sequences, and taking a difference or log fold change (ALT ? REF).
* The result is a pervariant, pertissue expression ? score that approximates “how much this variant would change APP or MAPT expression in this brain tissue.”
We may also record local expression changes around specific exons or promoters to refine interpretation.
4.4. Splicingrelated variant scores
For splicing, AlphaGenome provides:
* Splice site probabilities (donor/acceptor).
* Splice site usage estimates.
* Splice junction count predictions.[ppl-ai-file-upload.s3.amazonaws]?
For each variant, we will:
* Extract junctionlevel and sitelevel variant scores around the APP or MAPT splice graph. For example:
o Change in predicted junction counts connecting specific exons.
o Change in predicted usage of particular donor or acceptor sites.
* Summarize these into interpretable metrics such as:
o ? inclusion of exon X (approximate change in percent spliced in, PSI).
o ? usage of canonical vs alternative junctions for key exons.
These splicing scores mirror the strategies used in the AlphaGenome paper to evaluate splicing QTLs and ClinVar splicing variants.[ppl-ai-file-upload.s3.amazonaws]?
4.5. Optional chromatin and TFbinding variant scores
To understand whether expression/splicing hotspots coincide with changes in local regulatory chromatin state, we may also collect:
* ? DNase/ATAC accessibility at or near the variant in brain tracks.
* ? histone marks associated with active enhancers/promoters (e.g., H3K27ac).
* ? binding for specific transcription factors implicated in neuronal regulation, if predicted tracks exist.[ppl-ai-file-upload.s3.amazonaws]?
These features help link regulatory hotspots to underlying regulatory mechanisms (e.g., altered enhancer activity).
4.6. Data storage and quality control
All variantlevel predictions will be stored in structured tables with fields including:
* Variant identifier, position, gene (APP/MAPT), and annotation (e.g., intron, exon, UTR).
* For each brain tissue/track:
o Expression ? score.
o Splicing ? scores (junctions, sites).
o Optional chromatin/TF ? scores.
* Flags indicating whether predictions meet minimum quality or coverage thresholds.
We will perform basic sanity checks, such as distributional inspection of scores and consistency across nearby variants.

5. Construction of regulatory sensitivity maps and hotspot identification
5.1. Sensitivity definition
For a given gene (APP or MAPT), tissue (e.g., cortex), and modality (expression or splicing), we define regulatory sensitivity at a genomic position as the magnitude of change in a downstream readout (expression or splicing) induced by a variant at or near that position.
Formally, for a given variant vat position pand its variant score ?f_vfor a modality f(e.g., APP expression in cortex), regulatory sensitivity is approximated by ??f_v?. Larger values indicate that small sequence changes at pstrongly perturb the regulatory output.
5.2. Aggregation across variants
To construct a continuous sensitivity map along each gene’s window:
1. For in silico mutagenesis variants (densely tiled), we assign the expression/splicing ? score to the mutated base’s coordinate.
2. We optionally smooth the scores along the genome using a sliding window (e.g., median or maximum over ±N bp) to reduce noise.
3. We separately construct:
o An expression sensitivity track: perposition or perbin sensitivity of APP/MAPT expression in each brain tissue.
o A splicing sensitivity track: perposition or perbin sensitivity of splicing outcomes (e.g., canonical junction usage) for APP/MAPT.
For observed variants (GWAS, eQTL, sQTL), we overlay their positions and scores on these maps but treat them as sparse measurements rather than dense coverage.
5.3. Hotspot detection
We define a regulatory hotspot as a contiguous genomic interval where the sensitivity measure exceeds a chosen threshold.
Practical steps:
* For each gene and tissue, compute the distribution of sensitivity scores across all in silico variants.
* Choose thresholds based on quantiles (e.g., top 1–5% of scores) or empirical distribution to define “highsensitivity” variants.
* Merge neighboring highsensitivity positions into intervals to form hotspots.
* Record for each hotspot:
o Genomic coordinates.
o Peak sensitivity values.
o Whether it primarily reflects expression effects, splicing effects, or both.
o Tissue specificity (brainspecific vs also present in nonbrain tracks).

6. Integration with external genetic and regulatory data
6.1. Overlap with Alzheimer’s GWAS and QTL loci
For each hotspot:
* Assess whether it overlaps:
o GWAS index SNPs or credible set variants for Alzheimer’s disease.
o APP/MAPT eQTL or sQTL variants identified in brain tissues.
* Compare the density of GWAS/QTL variants within hotspots versus matched control regions (e.g., random regions with similar distance to TSS and local LD), to evaluate enrichment.
This supports conclusions such as “APP hotspots identified by AlphaGenome are enriched for Alzheimer’s GWAS signals,” indicating concordance between regulatory sensitivity and disease association.
6.2. Overlap with known regulatory annotations
Using public regulatory atlases (e.g., ENCODE, Roadmap Epigenomics, brain ATAC/ChIP datasets), we will annotate hotspots with:
* Chromatin state labels (promoter, enhancer, repressed).
* DNase/ATAC peaks and histone mark peaks (e.g., H3K27ac, H3K4me3) in neuronal and glial cells.
* TF motif instances relevant to neuronal regulation.
This allows interpretation of hotspots as:
* Promoterproximal regions likely affecting initiation.
* Distal enhancers.
* Intronic regulatory elements affecting splicing (e.g., splicing enhancers/silencers).

7. Optional modeling on top of AlphaGenome outputs
Although AlphaGenome provides powerful variant effect predictions, additional models can be built on top for prioritization and interpretation.
7.1. Composite regulatory impact scores
We may define gene and tissuespecific composite scores that combine:
* Expression ? scores.
* Splicing ? scores.
* Chromatin/TF ? scores.
For example, a composite “APP brain regulatory impact score” could be a weighted combination of absolute expression and splicing changes in brain tracks. We can explore different weighting schemes and assess their ability to prioritize known GWAS/eQTL variants near APP/MAPT.
7.2. Supervised ranking models
Using GWAS/eQTL/sQTL labels:
* Train simple supervised models (e.g., logistic regression, random forest) that take AlphaGenomederived features as input and predict whether a variant is likely to be causal or noncausal for APP/MAPTrelated regulation.
* Evaluate performance via crossvalidation and compare to baselines (e.g., distance to TSS, conservation).
The goal here is not to outcompete all existing finemapping methods, but to show how AlphaGenome features add mechanistic information to prioritization for Alzheimer’s genes.

8. Interpretation and expected contributions
8.1. Methodological contribution
Methodologically, this study demonstrates a general workflow for using AlphaGenome’s API to construct genecentric regulatory sensitivity maps:
* Starting from 1 Mb DNA sequence and a set of real + in silico variants.
* Obtaining modalityspecific variant effect predictions (expression, splicing, chromatin) in relevant tissues.
* Aggregating these into interpretable, genefocused regulatory hotspot maps.
This workflow can be reused for other genes or diseases beyond Alzheimer’s.
8.2. Biological contribution
Biologically, the study is expected to:
* Provide a detailed picture of where around APP and MAPT noncoding variants are most likely to significantly alter gene expression and splicing in brain contexts.
* Reveal whether APP and MAPT exhibit distinct regulatory architectures (e.g., APP more promoter/UTRsensitive; MAPT more intronic splicingsensitive) that may reflect their different roles in amyloid vs tau pathology.
* Highlight specific intronic or distal hotspots that are plausible mechanistic mediators of amyloid and tau dysregulation, suggesting concrete targets for future experimental followup (e.g., minigene splicing assays, CRISPR perturbations).
8.3. Integration with Alzheimer’s genetics
By comparing AlphaGenomedefined hotspots to Alzheimer’s GWAS and brain QTL data:
* We will assess whether the regulatory hotspots predicted by AlphaGenome coincide with regions carrying strong genetic evidence for disease association.
* Where overlap is observed, we can propose mechanistic interpretations for previously “anonymous” noncoding associations (e.g., “this credibleset SNP likely increases inclusion of MAPT exon X in neurons”).
* Where AlphaGenome identifies highimpact hotspots that currently lack GWAS signals, we can propose them as testable hypotheses for future genetic and functional studies.
8.4. Overall contribution
In summary, this work will contribute:
* A reproducible, AlphaGenomebased methodology for genecentric regulatory mapping.
* The first detailed regulatory sensitivity maps for APP and MAPT in brain tissues, integrating expression and splicing modalities.
* A prioritized set of noncoding regions and variants that represent plausible mechanistic links between DNA sequence variation and amyloid/tau dysregulation in Alzheimer’s disease.
These outputs can guide both computational followup (e.g., model refinement, broader locus screening) and experimental work aimed at validating noncoding mechanisms in neurodegeneration.

