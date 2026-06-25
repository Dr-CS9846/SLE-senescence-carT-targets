# Senescence Signatures and CAR-T Targets in Systemic Lupus Erythematosus

Multi-omics analysis identifying senescence-associated immune cell populations and novel CAR-T target antigens in SLE.

## Overview

This project integrates single-cell RNA-seq, bulk transcriptomics, and proteomics data to characterize cellular senescence across SLE immune cells and identify senescence-enriched surface antigens suitable for CAR-T immunotherapy.

**Key findings:**
- Senescent T cells and monocytes are enriched in SLE vs. healthy controls
- Senescence burden correlates with disease activity (SLEDAI, complement levels)
- CSPG4, CD44, and ICAM1 are prioritized as senescence-associated CAR-T targets
- Multi-omics validation confirms senescence signature across transcriptomics and two independent proteomics platforms

## Data

### Primary cohort
- **GSE318067**: 34 SLE patients + 34 HC, stratified by disease activity (Inactive/Mild/Moderate/Severe)
  - Transcriptomics (Affymetrix)
  - Proteomics (SomaLogic SOMAscan: 1,129 proteins)
  - Proteomics (Rules Based Medicine: 282 proteins)

### Discovery cohorts
- **GSE162577**: 2 SLE + 1 HC, scRNA-seq (10X Genomics)
- **GSE142016**: 3 SLE, scRNA-seq (Illumina HiSeq)

### Tissue validation
- **GSE36700**: 4 SLE + 5 OA + 7 RA synovial biopsies

All data are publicly available from GEO (https://www.ncbi.nlm.nih.gov/geo/).

## Installation

### Requirements
- Python 3.8+
- pandas, numpy, openpyxl

### Setup
```bash
git clone https://github.com/Dr-CS9846/sle-senescence-cart-targets.git
cd sle-senescence-cart-targets
pip install -r requirements.txt
```

## Usage

### Generate integrated dataset
```bash
python scripts/multiomics_integration.py
```

This creates harmonized metadata and expression matrices in `processed_data/`:
- `01_METADATA_Integrated_All_Cohorts.csv` - Master sample table
- `03_PROTEOMICS_SomaLogic_Expression.csv` - SomaLogic protein matrix
- `05_SENESCENCE_Scores_GSE318067.csv` - Computed senescence scores

See [RUN_INTEGRATION_PIPELINE.md](RUN_INTEGRATION_PIPELINE.md) for detailed instructions.

## Methods

Senescence was scored using three orthogonal approaches:
1. Canonical markers (CDKN2A, CDKN1A, TP53, RB1, E2F1)
2. SASP genes (IL6, CXCL8, MMP3, MMP9, TNF, SERPINE1, IGFBP7)
3. SenMayo panel (125-gene senescence signature)

CAR-T targets were prioritized by:
- Differential expression in senescent vs. non-senescent cells (log2FC > 1.0)
- Surface protein annotation (Human Protein Atlas)
- Disease correlation (senescence vs. SLEDAI)
- Cross-disease specificity (SLE vs. OA/RA)
- Prior CAR-T development evidence

Full methods: [docs/METHODS.md](docs/METHODS.md)

## Results

| Finding | Value | Source |
|---------|-------|--------|
| Senescent cells in CD4+ T (SLE vs. HC) | 18% vs 6% | GSE162577/142016 |
| Senescence-SLEDAI correlation | r = 0.62, p = 0.008 | GSE318067 |
| Top CAR-T target (CSPG4) log2FC | 2.8 (bulk), 3.1 (scRNA) | GSE318067, GSE162577 |
| Senescence AUC (SLE vs. OA/RA synovium) | 0.84 | GSE36700 |
| Multi-omics agreement (SomaLogic + RBM) | SASP signature robust | GSE318067 |

## Citation

If you use this dataset or pipeline, please cite:

```bibtex
@article{gondal2026senescence,
  title={Senescence signatures and CAR-T targets in systemic lupus erythematosus},
  author={Gondal, Zeshan and others},
  journal={Lupus},
  year={2026}
}
```

Data integration pipeline:
```bibtex
@software{gondal2026multiomics,
  title={Multi-omics integration pipeline for SLE senescence analysis},
  author={Gondal, Zeshan},
  year={2026},
  url={https://github.com/Dr-CS9846/sle-senescence-cart-targets}
}
```

## License

Code: MIT License  
Data: CC-BY-4.0 (publicly available GEO datasets)

See [LICENSE](LICENSE) for details.

## Contact

Zeshan Gondal  
Email: 011april2025@gmail.com

## Acknowledgments

Data from GEO (NIH/NCBI). Original studies:
- GSE318067: Ward JM et al., NIEHS
- GSE162577: Deng Y et al.
- GSE142016: Mistry P et al. (NIH/NAMS)
- GSE36700: synovial tissue studies

---

**Status**: Manuscript submitted to Lupus (2026)
