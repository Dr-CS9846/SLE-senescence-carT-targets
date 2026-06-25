# Data Manifest: All Downloaded Datasets

**Status**: All datasets downloaded (with noted substitutions)  
**Last Updated**: June 25, 2026  
**Total Storage**: ~180 GB

---

## DATASET INVENTORY

### CATEGORY 1: SLE BULK RNA-seq (5 datasets, 200+ samples)

| Dataset | Status | Location | Format | N Samples | Notes |
|---------|--------|----------|--------|-----------|-------|
| **GSE72509** | ✅ Downloaded | `datasets/GSE72509/` | Series Matrix TSV | 120 SLE+HC | PBMC gene expression |
| **GSE112087** | ✅ Downloaded | `datasets/GSE112087/` | Series Matrix TSV | SLE+HC | Microarray - whole blood |
| **GSE181500** | ✅ Downloaded | `datasets/GSE181500/` | Series Matrix TSV | SLE+HC | CD4+ T cells |
| **GSE228066** | ✅ Downloaded | `datasets/GSE228066/` | Series Matrix TSV | SLE stratified | 2024, severity stratified |
| **GSE122459** | ✅ Downloaded | `datasets/GSE122459/` | Series Matrix TSV | SLE PBMC | PBMC + proteomics companion |

**Processing needed**: 
- Normalize (log2 CPM or DESeq2)
- Compute senescence scores
- Extract SLEDAI if available
- Compute correlation: senescence vs SLEDAI

---

### CATEGORY 2: scRNA-seq (6 cohorts, 40+ SLE patients)

| Dataset | Status | Location | Format | N Patients/Cells | Notes |
|---------|--------|----------|--------|-----------------|-------|
| **GSE135779** | ✅ Downloaded | `datasets/GSE135779/` | h5ad | Large PBMC cohort | Active/inactive SLE vs HC |
| **GSE139358** | ✅ Downloaded (was GSE139360) | `datasets/GSE139358/` | 2 files | Subset | ⚠️ Replacement for GSE139360 |
| **GSE162577** | ✅ In repo | `datasets/GSE162577/` | h5ad | 3 samples (2 SLE) | Already in repo |
| **GSE163121** | ✅ Downloaded | `datasets/GSE163121/` | 10X/h5ad | B cells | CD11c+T-bet+ B cells |
| **GSE179633** | ✅ Downloaded (alternate) | `datasets/GSE179633/` | MTX sparse | DLE samples | ⚠️ MTX format instead of h5ad |
| **GSE266852** | ✅ Downloaded | `datasets/GSE266852/` | h5ad | HC+SLE+RA | Comparative autoimmune |

**Processing needed**:
- Load different formats (h5ad, MTX)
- QC: nGenes, nUMI, %mitochondrial
- Batch correction (Harmony/Seurat)
- Cell type annotation
- Compute senescence per cell
- Stratify by disease status

**Format-specific notes**:
- GSE139358: 2 files - need to check format
- GSE179633: MTX format (sparse matrix) - use scipy.io.mmread()

---

### CATEGORY 3: TISSUE (6 datasets, 12-20 SLE tissue samples)

| Dataset | Status | Location | Format | Tissue | N SLE |
|---------|--------|----------|--------|--------|-------|
| **GSE36700** | ✅ In repo | `datasets/GSE36700/` | Series Matrix TSV | Synovium | 4 |
| **GSE155405** | ✅ Downloaded | `datasets/GSE155405/` | Series Matrix TSV | Kidney (LN) | ~8 |
| **GSE294496** | ✅ Downloaded | `datasets/GSE294496/` | h5ad/MTX | Kidney scRNA | ~5 |
| **GSE182825** | ✅ Downloaded | `datasets/GSE182825/` | Spatial (10X Visium) | Skin | ~3 |
| **GSE200306** | ✅ Downloaded | `datasets/GSE200306/` | Series Matrix TSV | Kidney (LN) | ~4 |
| **GSE174188** | ✅ Downloaded | `datasets/GSE174188/` | Series Matrix TSV | Renal biopsy | ~3 |

**Processing needed**:
- Normalize across tissue types
- Compute senescence scores
- Extract CSPG4, CD44, ICAM1 expression
- Compare SLE vs control tissues

**Tissue-specific notes**:
- GSE182825: Spatial transcriptomics (special handling needed)
- GSE294496: May be scRNA format (single-cell kidney)

---

### CATEGORY 4: SENESCENCE VALIDATION (5 reference datasets)

| Dataset | Status | Location | Format | Organism | Focus |
|---------|--------|----------|--------|----------|-------|
| **GSE101766** | ✅ Downloaded | `datasets/GSE101766/` | Series Matrix TSV | Human (IMR90) | SASP regulation |
| **GSE226598** | ✅ Downloaded | `datasets/GSE226598/` | scRNA | Human PBMC | T cell senescence, IFN disease |
| **GSE262856** | ✅ Downloaded | `datasets/GSE262856/` | Series Matrix TSV | Human cell lines | Senescence types |
| **GSE157007** | ✅ Downloaded | `datasets/GSE157007/` | scRNA | Human PBMC | Age-dependent senescence |
| **GSE297723** | ✅ Downloaded | `datasets/GSE297723/` | Series Matrix TSV | Mouse lung | LAMP1 senescence marker |

**Processing needed**:
- Validate SenMayo 125-gene panel
- Confirm SASP elevation in senescent samples
- GSE226598: IFN-senescence correlation

---

## FILE FORMAT INVENTORY

### Series Matrix TSV (Standard bulk RNA)
**Datasets**: GSE72509, GSE112087, GSE181500, GSE228066, GSE122459, GSE36700, GSE155405, GSE200306, GSE174188, GSE101766, GSE262856, GSE297723

**File extension**: `_series_matrix.txt` or `_series_matrix.txt.gz`

**Loading**:
```python
import pandas as pd
df = pd.read_csv('GSE72509_series_matrix.txt', sep='\t', header=0, skiprows=0)
```

---

### h5ad (Scanpy/AnnData format - scRNA)
**Datasets**: GSE135779, GSE163121, GSE266852, (possibly GSE294496)

**File extension**: `.h5ad`

**Loading**:
```python
import scanpy as sc
adata = sc.read_h5ad('GSE135779.h5ad')
```

---

### MTX (Sparse Matrix - scRNA)
**Datasets**: GSE179633 (alternate files), (possibly GSE294496)

**Files**: `matrix.mtx.gz`, `barcodes.tsv.gz`, `features.tsv.gz`

**Loading**:
```python
from scipy.io import mmread
import gzip
import pandas as pd

# Read MTX
matrix = mmread(gzip.open('matrix.mtx.gz', 'rb')).T.tocsr()

# Read barcodes
barcodes = pd.read_csv(gzip.open('barcodes.tsv.gz', 'rt'), header=None)[0].values

# Read features
features = pd.read_csv(gzip.open('features.tsv.gz', 'rt'), header=None, sep='\t')[1].values

# Create AnnData
import anndata
adata = anndata.AnnData(X=matrix, obs={'barcode': barcodes}, var={'gene_name': features})
```

---

### SOFT/XML (GEO format metadata)
**Datasets**: GSE179633_family.soft.gz, GSE179633_family.xml.tgz

**Purpose**: Metadata extraction (sample info, phenotypes)

**Loading SOFT**:
```bash
gunzip GSE179633_family.soft.gz
# Parse with GEOparse
```

---

### 10X Spatial (Visium)
**Datasets**: GSE182825

**Files**: `.h5ad` with spatial coordinates

**Loading**:
```python
import scanpy as sc
adata = sc.read_h5ad('GSE182825_spatial.h5ad')
# Spatial coordinates in adata.obsm['spatial']
```

---

## METADATA REQUIREMENTS FOR EACH DATASET

**Essential columns** to extract/verify:

```
✓ Sample_ID (unique identifier)
✓ Disease_Status (SLE, HC, OA, RA, etc.)
✓ If available:
  - SLEDAI score (disease activity)
  - C3, C4 (complement levels)
  - Anti-dsDNA (antibody status)
  - Organ involvement (renal, CNS, cutaneous)
  - Disease duration
  - Treatment status
✓ Tissue_Type (PBMC, kidney, skin, synovium, etc.)
✓ Platform (RNA-seq, microarray, 10X, etc.)
```

---

## DATA PROCESSING PIPELINE OVERVIEW

```
Raw Data (downloaded)
        ↓
    [Load] (handle different formats)
        ↓
    [QC] (filter low-quality samples/cells)
        ↓
    [Normalize] (log2 CPM, DESeq2, or log-normalize scRNA)
        ↓
    [Batch Correction] (scRNA: Harmony/Seurat; bulk: ComBat if needed)
        ↓
    [Senescence Scoring] (SenMayo 125-gene panel)
        ↓
    [Target Extraction] (CSPG4, CD44, ICAM1 expression)
        ↓
    [Cross-Dataset Validation] (correlation, fold-change, AUC)
        ↓
    [Outputs] (CSV files for each dataset + integrated table)
```

---

## NEXT STEPS

1. ✅ All datasets downloaded
2. ⏳ **Create comprehensive loading pipeline** (handle all formats)
3. ⏳ **QC and normalization** (bulk vs scRNA)
4. ⏳ **Senescence scoring** (apply to all datasets)
5. ⏳ **Target extraction** (CSPG4, CD44, ICAM1)
6. ⏳ **Cross-validation analysis** (compare across datasets)
7. ⏳ **Generate integrated outputs** (for manuscript)

---

## STORAGE LOCATION

**Base path**: `datasets/`

**Structure**:
```
datasets/
├── GSE72509/          (bulk RNA-seq)
├── GSE112087/         (microarray)
├── GSE181500/         (bulk RNA-seq)
├── GSE228066/         (bulk RNA-seq)
├── GSE122459/         (bulk RNA-seq)
├── GSE135779/         (scRNA-seq)
├── GSE139358/         (scRNA, was GSE139360)
├── GSE162577/         (scRNA - already had)
├── GSE163121/         (scRNA - B cells)
├── GSE179633/         (scRNA - MTX format)
├── GSE266852/         (scRNA - comparative)
├── GSE36700/          (tissue - already had)
├── GSE155405/         (tissue - kidney)
├── GSE294496/         (tissue scRNA - kidney)
├── GSE182825/         (tissue - spatial skin)
├── GSE200306/         (tissue - kidney)
├── GSE174188/         (tissue - kidney)
├── GSE101766/         (senescence ref)
├── GSE226598/         (senescence ref - IFN)
├── GSE262856/         (senescence ref)
├── GSE157007/         (senescence ref - aging)
└── GSE297723/         (senescence ref - mouse)
```

---

## KNOWN ISSUES & SUBSTITUTIONS

| Issue | Original | Replacement | Status | Action |
|-------|----------|-------------|--------|--------|
| GSE139360 unavailable | GSE139360 | GSE139358 (2 files) | ⚠️ Note in pipeline | Verify GSE139358 is valid scRNA cohort |
| GSE179633 format issue | h5ad expected | MTX sparse matrix | ⚠️ Note in pipeline | Create MTX loader in pipeline |

---

## VERIFICATION CHECKLIST

- [ ] All 21 datasets present in datasets/ folder
- [ ] Each dataset has expected files
- [ ] Metadata files readable (SOFT, XML, etc.)
- [ ] No corrupted gzip files
- [ ] Storage space adequate (~180 GB)

**Next: Create unified loading pipeline to handle all formats**

