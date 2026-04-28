## Directions

### Problems and Solution
1. Solves the "Long-Range 3D Looping" Bottleneck
  - The Previous Gap: Earlier papers struggled to prove how a distal enhancer actually touched its target gene without performing difficult, imperfect 3D mapping experiments (like TCC or Hi-C) in lab-grown cancer cells.
  - The AlphaGenome Solution: Instead of requiring physical experiments, AlphaGenome takes a massive 1-megabase (1 million base pairs) window of DNA sequence as its input. Because 99% of validated enhancer-gene pairs fall within this 1-megabase distance, the AI can mathematically predict these long-range 3D chromatin contact maps and successfully link distal enhancers to their target promoters purely from the sequence

2. The major remaining gap is their inability to capture how single non-coding Alzheimer’s variants simultaneously disrupt long-range 3D chromatin architecture and RNA splicing or alternative polyadenylation (APA)

Solution: Scientists have compiled massive lists of genetic variations linked to Alzheimer's disease, but physical laboratory tests cannot determine how these variations actually cause the illness because they only examine tiny, isolated fragments rather than the full, complex structure of the genome. Furthermore, current artificial intelligence tools have critical blind spots, as they can predict either the physical shape of the genes or their chemical behavior, but never both at the same time. Our research asks: which specific genetic variations act as the true triggers for Alzheimer's when their effects on both physical structure and chemical rules are evaluated simultaneously? To solve this, we will combine three distinct artificial intelligence models into a single, unified system and analyze thousands of recently discovered Alzheimer's variations across massive, continuous segments of DNA. By merging these predictions, we will prove exactly which variations physically break the folding structure and disrupt the chemical instructions of the genome, uncovering the precise causes of the disease that previous tests were too narrow to detect.

Our three models: AlphaGenome, EpiModX, INTERACT
- AlphaGenome successfully models 1Mb sequences and 3D loops, but it completely ignores DNA methylation and predicts general molecular consequences rather than specific Alzheimer's pathological states

- EpiModX predicts disease-specific histone modifications (distinguishing between healthy and AD brains) but lacks 3D structural predictions

- INTERACT models DNA methylation but is restricted to short 2-kb windows and limited cell types