## 1. Inputs

will have four main inputs:

1. **Gene coordinates (from GENCODE)**  
   - For APP and MAPT you get:
     - chromosome,  
     - start and end positions,  
     - exon/intron structure.  
   - You define windows around them, e.g.:
     - `APP_window = [APP_start − 250kb, APP_end + 250kb]`  
     - `MAPT_window = [MAPT_start − 250kb, MAPT_end + 250kb]`.

2. **Brain tissues and modalities (AlphaGenome metadata)**  
   - Tissues (examples): cortex, hippocampus, neuron‑like, glia.  
   - Modalities (output types):  
     - `RNA_SEQ` (expression),  
     - `SPLICE_JUNCTIONS`, `SPLICE_SITE_USAGE` (splicing).

3. **Real variants (GWAS/eQTL/sQTL)**  
   - A table with rows like:  
     - `chr, pos, ref, alt, source_type (GWAS/eQTL/sQTL), gene, beta_AD, p_AD, beta_expr, beta_splice, ...`.
 /bGWAS DATASET(https://statfungen.github.io/xqtl-resources/xqtl-data/gwas/Bellenguez_AD/)
 /bAlzheimer’s curated variant portal(https://advp.niagads.org/)
 Brain eQTL/sQTL data(https://github.com/broadinstitute/gtex-v8/blob/master/README.md)
 Regional Variation of Splicing QTLs in Human Brain(https://pmc.ncbi.nlm.nih.gov/articles/PMC7413857/)
 An xQTL map integrates the genetic architecture of the human brain’s transcriptome and epigenome(https://pmc.ncbi.nlm.nih.gov/articles/PMC5785926/)
4. **In‑silico variants (you generate)**  
   - You programmatically create variants in your APP/MAPT windows:  
     - e.g. one SNV every N bp in promoters, introns, UTRs, etc.  
   - Each row: `chr, pos, ref, alt, gene, variant_type='in_silico'`.

All these variants (real + in‑silico) are stored in one or more CSV/DataFrames.

***

## 2. Core computation: calling AlphaGenome on each variant

For each variant in your table, you run a **variant effect prediction** through AlphaGenome.

### 2.1. One-variant view

Given a single row:

```text
chr = 17
pos = 44001000
ref = T
alt = C
gene = MAPT
```

Code will:

1. **Create a Variant object**  
   - `variant = Variant(chromosome='chr17', position=44001000, reference_bases='T', alternate_bases='C')`

2. **Define the 1 Mb analysis interval around it**  
   - e.g. `interval = variant.reference_interval.resize(2**20)` (AlphaGenome’s 1 Mb window).

3. **Call AlphaGenome**  
   ```python
   variant_output = client.predict_variant(
       variant=variant,
       interval=interval,
       requested_outputs={RNA_SEQ, SPLICE_JUNCTIONS, SPLICE_SITE_USAGE},
       ontology_terms=brain_ontology_terms
   )
   ```
   - AlphaGenome:
     - takes reference sequence for `interval` → predicts tracks (REF)  
     - flips T→C at `pos` → predicts tracks again (ALT).

4. **Compute effect scores** using scorers  
   - For expression:
     ```python
     expr_scorer = GeneMaskLFCScorer(OutputType.RNA_SEQ)
     ```
   - For splicing:
     - whatever scorer they provide for splice junctions / usage (e.g., JunctionDeltaScorer, PSI scorer).

   Then:

   ```python
   scores = client.score_variant(
       variant=variant,
       interval=interval,
       variant_scorers=[expr_scorer, splice_scorer]
   )
   tidy = tidy_scores(scores)
   ```

This yields **numeric effect scores** for that variant and each gene/tissue/modality.

### 2.2. Batch view

In practice, you’ll:

- loop over all variants in APP/MAPT windows,  
- or better, process them in batches per region to reuse intervals,  
- accumulate all `tidy` tables into one big DataFrame.

***

## 3. What data is computed (contents of the score table)

After scoring many variants, you get a table roughly like:

| chr | pos | ref | alt | gene | tissue          | modality | effect_name              | effect_value |
|-----|-----|-----|-----|------|-----------------|----------|--------------------------|--------------|
| 17  | 44001000 | T | C | MAPT | frontal_cortex  | expr     | delta_expr               | -0.75        |
| 17  | 44001000 | T | C | MAPT | frontal_cortex  | splice   | delta_junction_exon9-10  | +0.30        |
| 17  | 44001000 | T | C | MAPT | hippocampus     | expr     | delta_expr               | -0.60        |
| 21  | 27500000 | G | A | APP  | frontal_cortex  | expr     | delta_expr               | +0.40        |
| 21  | 27500000 | G | A | APP  | frontal_cortex  | splice   | delta_junction_exon7-8   | -0.10        |
| ... | ...      |...|...| ...  | ...             | ...      | ...                      | ...          |

Where:

- `effect_value` is the **predicted effect** (REF vs ALT):
  - expression: log fold change or similar.  
  - splicing: change in junction usage, PSI, etc.

You can also pivot this into a more compact form:

| chr | pos | ref | alt | gene | tissue | delta_expr | delta_splice_exon9-10 | delta_splice_exon10-11 | ... |
|-----|-----|-----|-----|------|--------|------------|-----------------------|------------------------|-----|

This table is the **main computed output** of your code.

***

## 4. Outputs and downstream processing

Once you have that big score table, your code will do a second phase of computation:

### 4.1. Per-gene, per-tissue sensitivity maps

For a given gene and tissue (e.g. MAPT, frontal cortex):

- Filter the table to `gene='MAPT', tissue='frontal_cortex'`.  
- For each variant position, look at `|delta_expr|` and/or key `|delta_splice_*|`.  
- Plot `effect_value` vs genomic position:
  - x-axis: position within MAPT window  
  - y-axis: effect magnitude  
- Optionally smooth or compute rolling maxima to highlight **hotspots** where many nearby variants have large values.

Code-wise, that’s:

- groupby / sort,  
- rolling window operations in pandas,  
- matplotlib/plotly for plotting.

### 4.2. Hotspot detection

You can:

- Define a threshold, e.g. top 5% of |effect_value|.  
- Mark variants above that threshold.  
- Merge neighboring high-effect variants into intervals (hotspots).

The output could be a new table:

| hotspot_id | gene | start     | end       | tissue          | main_modality | peak_effect | n_variants |
|-----------|------|-----------|----------|-----------------|--------------|------------|-----------|
| MAPT_HS1  | MAPT | 44,000,000 | 44,005,000 | frontal_cortex  | splice       | 0.85       | 120       |
| APP_HS1   | APP  | 27,500,000 | 27,503,000 | hippocampus     | expr         | 1.10       | 80        |

That’s a **summarized output** your code will produce.

### 4.3. Compare with GWAS/QTL

You then merge in GWAS/eQTL/sQTL info:

- For each variant row, add columns:
  - `beta_AD`, `p_AD` (from GWAS),  
  - `beta_expr_GTEx`, `beta_splice_GTEx`, etc., where available.

Then you can:

- compute whether strong AlphaGenome effects align with strong GWAS/QTL evidence,  
- count how many GWAS variants fall inside each hotspot, etc.

This is all table joins and summary stats.

### 4.4. Visualization outputs

For a few selected variants/hotspots, your code will also:

- call AlphaGenome again to get full REF and ALT **tracks** (not just scores):  
  - e.g., predicted RNA‑seq curves across APP/MAPT  
  - splicing tracks.  
- plot REF vs ALT tracks with gene annotation and variant markers (like your APOL4 test code did).

These become figure PNGs / SVGs.

***

## 5. Summary of code/data flow

Putting it all together:

1. **Preparation**  
   - Load GENCODE → get APP/MAPT windows.  
   - Load AlphaGenome metadata → choose brain tissues and modalities.  
   - Load GWAS and QTL tables → filter to APP/MAPT windows.  
   - Generate in‑silico variants in APP/MAPT windows.  
   - Combine variants into one DataFrame.

2. **Main AlphaGenome pass**  
   - Loop over variants (and maybe batch them):  
     - Build `Variant` objects.  
     - Define 1 Mb `interval`s.  
     - Call `predict_variant` + `score_variant` for chosen tissues/modalities.  
     - Append `tidy_scores` to a master scores table.

3. **Analysis phase**  
   - From the scores table:
     - build sensitivity maps (effect vs position),  
     - detect hotspots,  
     - annotate variants with GWAS/QTL info,  
     - summarize by gene, tissue, modality.

4. **Outputs**  
   - Main numeric outputs:
     - per-variant effect score table (CSV/Parquet).  
     - per-hotspot summary table.  
   - Visual outputs:
     - sensitivity plots (effect vs coordinate).  
     - track plots (REF vs ALT) for key variants.  
   - Written interpretation (outside code):
     - which hotspots look most important,  
     - which variants have strong, plausible regulatory effects on APP/MAPT in brain,  
     - how that ties back to Alzheimer’s.


That’s the full data/computation flow future code will implement.

