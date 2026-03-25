# Alzheimer’s Disease Variant Prioritization & AlphaGenome Input Design

## 1. Biological Context: What Happens in Alzheimer’s Disease?

Before selecting datasets or designing mutations, it is critical to understand the biological mechanisms underlying Alzheimer’s disease.

### Key Questions

- What are the molecular and cellular changes that occur as an individual transitions from a healthy state to Alzheimer’s disease?
- Why does brain atrophy (shrinkage) occur in AD?
- What roles do:
  - Amyloid-beta (Aβ) plaque accumulation  
  - Tau protein tangles  
  - Neuronal loss and synaptic dysfunction  
  play in disease progression?

### Context

Alzheimer’s disease is characterized by:
- Accumulation of amyloid-beta plaques (linked to APP processing)
- Formation of neurofibrillary tangles (linked to MAPT/tau dysfunction)
- Progressive neuronal degeneration, leading to brain volume loss

Understanding these mechanisms helps guide:
- Which genes to prioritize  
- Which tissues and modalities are most relevant  
- What types of variants may be functionally meaningful  

---

## 2. Gene Focus: APP and MAPT

We have identified two primary genes of interest:

- APP (Amyloid Precursor Protein)  
- MAPT (Microtubule-Associated Protein Tau)  

### Key Questions

- What public datasets and prior research exist for these genes?
- What are the known:
  - Variants (SNPs, indels, structural variants)  
  - Regulatory elements  
  - Expression patterns across tissues  
- What causal chains are already known?  
  - Example: Mutation X → altered splicing/expression → protein dysfunction → AD phenotype  

### Context

We aim to gather:
- High-resolution genomic and transcriptomic data  
- Mechanistic insights linking genetic variation to disease outcomes  
- Previously validated associations from literature and databases  

---

## 3. Modalities of Interest

AlphaGenome supports multiple genomic modalities, but we must determine which are most relevant for Alzheimer’s disease.

### Key Questions

- Which modalities should we prioritize?
  - RNA-Seq (gene expression)  
  - Splicing (isoform variation)  
  - Additional modalities (if relevant) such as chromatin accessibility or transcription factor binding  
- Are we focusing only on:
  - RNA expression (eQTLs)  
  - Splicing variation (sQTLs)  
  or expanding beyond?

### Context

The choice of modalities directly affects:
- Input data requirements  
- Biological interpretability  
- Computational cost and complexity  

---

## 4. Variant Generation Strategy (Informed ISM Approach)

We aim to generate a large-scale variant dataset for model input, but **a brute-force mutation strategy across entire gene regions is not computationally efficient and will introduce significant noise**.

Instead, we propose a **two-stage, informed variant generation strategy**.

### Stage 1: Region Prioritization

Before generating mutations, we must first identify **regions of interest (ROIs)** that are most likely to have functional and disease relevance.

### Key Questions

- Do we already have **predefined high-confidence regions**, such as:
  - GWAS significant loci  
  - Known regulatory elements (promoters, enhancers)  
  - Splice junctions  
- Or do we need to **derive these regions ourselves** using:
  - GWAS data (disease-associated peaks)  
  - eQTL data (expression-associated regions)  
  - sQTL data (splicing-associated regions)  

- If deriving:
  - How do we define and extract **peaks or hotspots** from these datasets?
  - What thresholds (e.g., p-values, effect sizes) will define a “region of interest”?

---

### Stage 2: Targeted In Silico Mutagenesis (ISM)

Once regions are prioritized, we apply mutation strategies **only within these regions**, rather than across the entire gene.

### Key Questions

- What mutation density should we use within selected regions?
  - Every base pair with all substitutions?  
  - Every 5 base pairs?  
  - Adaptive density based on signal strength?  

- What is the **minimum mutation coverage** required to:
  - Capture meaningful biological variation  
  - Remain computationally feasible  

### Context

This approach ensures:
- Reduced computational cost  
- Higher signal-to-noise ratio  
- Better biological relevance of predictions  

---

## 5. Genetic Analysis Methods

We need to define which genetic association methods will guide variant selection and prioritization.

### Methods Under Consideration

- GWAS → identifies disease-associated variants  
- eQTL analysis → links variants to gene expression changes  
- sQTL analysis → links variants to splicing changes  

### Key Questions

- How will we integrate these methods?
- Should GWAS define the primary regions, with eQTL/sQTL refining them?
- Or should all methods contribute equally to region selection?

### Context

Each method provides a different layer of insight:
- GWAS → disease association  
- eQTL → regulatory impact  
- sQTL → transcript-level changes  

---

## 6. Region and Variant Prioritization

Given the large datasets, we must define what to extract and prioritize.

### Key Questions

- What are our regions of interest (ROIs)?
  - Gene bodies (APP, MAPT)  
  - Promoters  
  - Enhancers  
  - Splice sites  

- Which variants are most important?
  - High-effect GWAS hits  
  - Variants with strong eQTL/sQTL signals  
  - Variants in regulatory hotspots  

### Selection Criteria

We need to define:
- Statistical thresholds (p-values, effect sizes)  
- Region boundaries around peaks  
- Variant density per region  

---

## 7. Final Output: Variant Dataset (CSV Format)

The final goal is to produce a structured CSV file containing all variants to be evaluated.

### Required Fields (Proposed)

- Chromosome  
- Position  
- Reference allele  
- Alternate allele  
- Gene (e.g., APP, MAPT)  
- Variant source:
  - GWAS / eQTL / sQTL / ISM  
- Region type (promoter, exon, intron, enhancer, etc.)  
- Modality relevance (RNA-seq, splicing, etc.)  

### Key Questions

- What exact schema should the CSV follow for AlphaGenome compatibility?
- How do we ensure consistency across:
  - Known variants  
  - Synthetic mutations  

---

---
Note: Ignore Point 7 for now
---

## Summary of Decisions Needed

1. Biological mechanisms to prioritize in Alzheimer’s disease  
2. Depth and sources of data for APP and MAPT  
3. Selection of genomic modalities  
4. Strategy for defining regions of interest (predefined vs derived)  
5. Mutation density and targeted ISM strategy  
6. Integration of GWAS, eQTL, and sQTL methods  
7. Final dataset structure and formatting  

---

## Next Steps

- Identify available datasets (GWAS, eQTL, sQTL)  
- Decide whether to use existing annotated regions or derive new ones  
- Define peak extraction and region selection criteria  
- Implement targeted mutation pipeline  
- Export standardized CSV for AlphaGenome input  
