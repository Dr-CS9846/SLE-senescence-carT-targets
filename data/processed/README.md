# Multi-Omics Integration Dataset: SLE Senescence Study

## Overview
This directory contains integrated, harmonized multi-omics data from the SLE senescence and CAR-T target discovery study.

## Files

### Metadata
- **01_METADATA_Integrated_All_Cohorts.csv** - Master metadata table combining all cohorts (N=112 samples)
- **02_METADATA_GSE318067_PrimaryBulkCohort.csv** - Primary bulk transcriptomics/proteomics cohort (N=68)

### Proteomics
- **03_PROTEOMICS_SomaLogic_Expression.csv** - SomaLogic SOMAscan protein expression (1,129 proteins × 68 samples)
- **04_PROTEOMICS_RBM_Expression.csv** - Rules Based Medicine protein panel expression

### Senescence Signatures
- **05_SENESCENCE_Scores_GSE318067.csv** - Computed senescence scores for primary bulk cohort

### QA/QC
- **00_DATA_QUALITY_REPORT.json** - Data integration summary statistics

## Data Sources

### Primary Bulk Transcriptomics & Proteomics (N=68)
- **GSE318067** - Adult SLE patients (n=34) vs. healthy controls (n=34)
  - Affymetrix transcriptomics
  - SomaLogic SOMAscan proteomics (1,129 proteins)
  - Rules Based Medicine (RBM) proteomics
  - Disease activity stratification: Inactive, Mild, Moderate, Severe
  - Age, ethnicity, sex-matched controls
  - **Reference:** Ward et al., NIEHS

### Discovery scRNA-seq (N=6)
- **GSE162577** - 2 SLE + 1 HC, 10X Genomics
- **GSE142016** - 3 SLE, HiSeq (subseries of GSE139360)
- Combined: 5 SLE + 1 HC PBMC samples

### Tissue-Level Validation (N=25)
- **GSE36700** - Synovial biopsies
  - 4 SLE, 5 OA, 7 RA, 5 MIC, 4 SA
  - Microarray
  - Cross-disease comparison

## Sample Counts

| Cohort | SLE Patients | HC Controls | Total |
|--------|-------------|------------|-------|
| GSE318067 (Primary Bulk) | 34 | 34 | 68 |
| scRNA-seq (Discovery) | 5 | 1 | 6 |
| GSE36700 (Tissue) | 4 | 12 (OA/RA) | 16 |
| **TOTAL** | **43** | **47** | **90** |

## Disease Activity Distribution (GSE318067)

- **Healthy Controls (HC):** 34
- **SLE Inactive:** 8
- **SLE Mild:** 17
- **SLE Moderate:** 8
- **SLE Severe:** 1

## Senescence Signatures

### Canonical Senescence Markers (6 genes)
- CDKN2A, CDKN1A, CDKN2B, TP53, RB1, E2F1

### SASP (Senescence-Associated Secretory Phenotype) Genes (7 genes)
- IL6, CXCL8, MMP3, MMP9, SERPINE1, TNF, IGFBP7

### CAR-T Target Candidates (12 genes)
- CSPG4, CD38, ICAM1, VCAM1, CD44, EGFR, PLAU, ADAM10, MRC1, DPP4, CX3CR1, B2M

## Integration Methods

1. **Metadata harmonization:** Parsed series matrix files (GSE162577, GSE142016, GSE36700) and Excel proteomics files (GSE318067)
2. **Disease stratification:** Assigned disease activity based on sample titles (Inactive/Mild/Moderate/Severe)
3. **Senescence scoring:** Computed mean expression of SASP proteins from SomaLogic data, Z-normalized
4. **Data quality:** Filtered out unknown/metadata-only rows; kept only samples with complete metadata

## Usage

All files are CSV format (comma-separated values). Load into R/Python with:

```python
import pandas as pd
metadata = pd.read_csv('01_METADATA_Integrated_All_Cohorts.csv')
proteomics_soma = pd.read_csv('03_PROTEOMICS_SomaLogic_Expression.csv')
senescence = pd.read_csv('05_SENESCENCE_Scores_GSE318067.csv')
```

## Reproducibility

This dataset was generated using the `multiomics_integration.py` script:

```bash
python multiomics_integration.py
```

Input files (raw GEO downloads) are in `../datasets/`

## Publication

This integrated dataset is part of the manuscript:
**"Multi-omics senescence profiling identifies CSPG4 and CD44 as senescence-associated CAR-T targets in systemic lupus erythematosus"**

Submitted to: *Lupus Journal*

## License & Citation

Data are publicly available from GEO. If using this integration, please cite:
- Original GEO datasets (GSE162577, GSE142016, GSE318067, GSE36700)
- This integration pipeline
- The associated manuscript

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
