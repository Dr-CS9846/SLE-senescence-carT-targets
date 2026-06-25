# Methods

## Data Sources

### Primary bulk cohort (N=68)
GSE318067: 34 SLE patients + 34 age/ethnicity/sex-matched healthy controls. Patients stratified by disease activity: Inactive (n=8), Mild (n=17), Moderate (n=8), Severe (n=1).

**Transcriptomics**: Affymetrix microarray  
**Proteomics**: 
- SomaLogic SOMAscan (1,129 proteins)
- Rules Based Medicine panel (282 proteins)

### Discovery cohorts (N=6)
- GSE162577: 2 SLE + 1 HC, 10X Genomics scRNA-seq
- GSE142016: 3 SLE, HiSeq scRNA-seq (subseries of GSE139360)

### Tissue validation (N=25)
GSE36700: Synovial biopsies - 4 SLE, 5 OA, 7 RA, 5 MIC, 4 SA

All data are publicly available at GEO (https://www.ncbi.nlm.nih.gov/geo/).

## Senescence Scoring

Senescence was quantified using three independent methods to ensure robustness:

**1. Canonical markers** (6 genes)
- CDKN2A, CDKN1A, CDKN2B, TP53, RB1, E2F1
- Mean expression Z-normalized per sample

**2. SASP signature** (7 genes)
- IL6, CXCL8, MMP3, MMP9, SERPINE1, TNF, IGFBP7
- Senescence-associated secretory phenotype
- Mean expression Z-normalized

**3. SenMayo panel** (125 genes)
- Comprehensive senescence signature from Saul et al. (MSigDB)
- AUCell ranking-based scoring

**Consensus definition**: Cells/samples scoring in top quartile on ≥2 of 3 methods were classified as senescent.

## CAR-T Target Prioritization

### Differential expression
For each cell type, senescent vs. non-senescent cells compared using Wilcoxon rank-sum test.
- Threshold: log2FC > 1.0, adjusted p < 0.05
- Genes filtered to surface-expressed proteins (Human Protein Atlas)

### Multi-criteria ranking
For each candidate antigen:
1. Fold-change in senescent cells (scRNA-seq)
2. Validation in bulk RNA-seq (GSE318067)
3. Validation in proteomics (SomaLogic, RBM)
4. Correlation with SLEDAI
5. Specificity to SLE vs. OA/RA
6. Prior CAR-T evidence in literature
7. Safety profile (tissue expression)

### Top candidates
Ranked by integrated evidence:
1. **CSPG4** - log2FC 2.8-3.1, SLEDAI r=0.58
2. **CD44** - log2FC 1.9-2.2, SLEDAI r=0.52
3. **ICAM1** - log2FC 1.8-2.2, SLEDAI r=0.45

## Statistical Analysis

All tests two-sided with α = 0.05.

**Correlation**: Spearman rank correlation for senescence score vs. disease markers (SLEDAI, C3, C4, anti-dsDNA).

**Differential expression**: Wilcoxon rank-sum test with FDR correction (Benjamini-Hochberg).

**Cross-disease comparison**: Kruskal-Wallis test with post-hoc Wilcoxon tests (SLE vs. OA vs. RA).

**ROC analysis**: Senescence score vs. disease status; AUC with 95% CI.

## Software

- R 4.1.3 with Seurat 4.1
- Python 3.8+ with pandas, numpy, scikit-learn
- Statistical tests: native R/Python implementations

## Reproducibility

Complete analysis pipeline: `scripts/multiomics_integration.py`

Generates:
- Harmonized metadata (99 samples, 8 cohorts)
- Senescence scores (68 bulk samples)
- Expression matrices (SomaLogic 1,129×68, RBM 282×68)
- Data quality report (JSON)

**Runtime**: ~30 seconds on standard laptop

**Data availability**: All processed datasets in `data/processed/`
