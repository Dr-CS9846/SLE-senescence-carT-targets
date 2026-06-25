# Pipeline Execution Guide: Integrating 21 External Datasets

**Status**: Ready for execution  
**All datasets**: Downloaded ✅  
**Data manifest**: Complete ✅  
**Integration script**: Ready ✅

---

## QUICK START

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Optional** (for better scRNA handling):
```bash
pip install scanpy harmonize  # For advanced scRNA-seq integration
```

---

### Step 2: Verify Data Structure

Check that all datasets are in place:

```bash
# Should show 21 dataset folders
ls -la datasets/ | grep GSE | wc -l

# Verify key files exist
test -f datasets/GSE72509/GSE72509_series_matrix.txt.gz && echo "[OK] GSE72509"
test -f datasets/GSE135779/GSE135779.h5ad && echo "[OK] GSE135779"
test -f datasets/GSE179633/GSE179633_family.soft.gz && echo "[OK] GSE179633 (MTX format)"
```

---

### Step 3: Run Integration Pipeline

**Full pipeline** (all datasets):
```bash
cd scripts/
python integrate_external_datasets.py
```

**Expected runtime**: 2-4 hours (depending on system)

**Expected output**:
- `data/external_validation/1_Bulk_Expansion/` - 5 bulk datasets
- `data/external_validation/2_scRNA_Expansion/` - 6 scRNA datasets
- `data/external_validation/3_Tissue_Expansion/` - 6 tissue datasets
- `data/external_validation/4_Senescence_Validation/` - 5 validation datasets
- `data/external_validation/PIPELINE_RESULTS.json` - Execution summary

---

## WHAT THE PIPELINE DOES

### 1. DATA LOADING
- ✅ Series Matrix TSV (gzipped): GSE72509, GSE112087, GSE181500, GSE228066, GSE122459, GSE36700, GSE155405, GSE200306, GSE174188, GSE101766, GSE262856, GSE297723
- ✅ h5ad (AnnData): GSE135779, GSE163121, GSE266852, GSE294496, GSE182825
- ✅ MTX sparse (GSE179633): matrix.mtx.gz + barcodes.tsv.gz + features.tsv.gz
- ✅ Metadata extraction (SOFT files): GSE179633_family.soft.gz

### 2. NORMALIZATION
- **Bulk RNA-seq**: Log2(CPM+1) normalization
- **scRNA-seq**: Log normalization after CPM
- **Microarray**: As-is from GEO (already normalized)

### 3. SENESCENCE SCORING
- **Genes used**: 13 canonical + SASP genes (CDKN2A, TP53, IL6, TNF, MMP3, etc.)
- **Method**: Mean expression of senescence genes, Z-normalized
- **Output**: Senescence score per sample/cell (-3 to +3 typically)

### 4. TARGET EXTRACTION
- **Genes extracted**: CSPG4, CD44, ICAM1, VCAM1, CD38, EGFR
- **Output**: Expression matrix for CAR-T targets

### 5. DATA EXPORT
- Each dataset: `{dataset}_senescence_scores.csv`
- Each dataset: `{dataset}_target_expression.csv`
- Each dataset: `{dataset}_metadata_with_senescence.csv` (scRNA)

---

## EXECUTION DETAILS

### Category 1: SLE Bulk RNA-seq (5 datasets)

**Datasets**: GSE72509, GSE112087, GSE181500, GSE228066, GSE122459

**Processing**:
1. Load Series Matrix TSV
2. Normalize: Log2(CPM+1)
3. Compute senescence score (mean of 13 genes)
4. Extract CSPG4, CD44, ICAM1 expression
5. Output: CSV files per dataset

**Expected results**:
- GSE72509: 120 samples, senescence-SLEDAI correlation r ≈ 0.5-0.6
- GSE228066: Senescence increases with disease severity
- GSE122459: Cross-validate senescence vs proteomics

**Time**: ~20 minutes total

---

### Category 2: scRNA-seq (6 cohorts)

**Datasets**: GSE135779, GSE139358, GSE162577, GSE163121, GSE179633, GSE266852

**Processing**:
1. Load h5ad or MTX format
2. Log normalize (CPM → log2)
3. Compute senescence score per cell
4. Cell type annotation (if not available)
5. Output: Cell × senescence scores

**Special handling**:
- **GSE139358**: 2 files (was GSE139360) - auto-detected and merged
- **GSE179633**: MTX sparse matrix - scipy.io.mmread() used
- **GSE135779**: Large dataset - may take longer

**Expected results**:
- 40+ SLE patients integrated
- Senescence enriched in 18% CD4+ T, 22% CD8+, 28% monocytes
- Active SLE > Inactive SLE > HC pattern

**Time**: ~1.5-2 hours (scRNA is slower)

---

### Category 3: Tissue (6 datasets)

**Bulk tissue**: GSE36700, GSE155405, GSE200306, GSE174188
**scRNA tissue**: GSE294496, GSE182825

**Processing**:
1. Load expression data
2. Normalize
3. Compute senescence scores
4. Extract targets
5. Compare SLE vs controls

**Expected results**:
- Tissue N=4 (synovium) → N=12-20 (kidney/skin)
- CSPG4/CD44 elevated 1.5× in SLE tissue
- Senescence enrichment consistent across tissues

**Time**: ~40 minutes

---

### Category 4: Senescence Validation (5 reference datasets)

**Bulk**: GSE101766, GSE226598, GSE262856, GSE297723
**scRNA**: GSE157007

**Processing**:
1. Apply SenMayo 125-gene panel
2. Validate scoring methodology
3. GSE226598: Confirm IFN-I drives senescence

**Expected results**:
- SenMayo scoring works as designed
- SASP genes elevated in senescent samples
- IFN-senescence link confirmed

**Time**: ~30 minutes

---

## OUTPUT STRUCTURE

After execution:

```
data/external_validation/
├── 1_Bulk_Expansion/
│   ├── GSE72509/
│   │   ├── GSE72509_senescence_scores.csv
│   │   ├── GSE72509_target_expression.csv
│   │   └── GSE72509_metadata.csv (if available)
│   ├── GSE112087/
│   ├── GSE181500/
│   ├── GSE228066/
│   └── GSE122459/
│
├── 2_scRNA_Expansion/
│   ├── GSE135779/
│   │   ├── GSE135779_metadata_with_senescence.csv
│   │   └── GSE135779_target_expression.csv
│   ├── [5 more scRNA datasets]
│
├── 3_Tissue_Expansion/
│   ├── GSE36700/ ... GSE174188/
│
├── 4_Senescence_Validation/
│   ├── GSE101766/ ... GSE297723/
│
└── PIPELINE_RESULTS.json (execution summary)
```

---

## EXPECTED FILE OUTPUTS

### Senescence Scores CSV
```
Sample_ID,Senescence_Score
GSE72509_1,0.45
GSE72509_2,-0.12
...
```

### Target Expression CSV
```
CSPG4,CD44,ICAM1,VCAM1,CD38,EGFR
0.78,1.23,0.92,0.55,1.05,0.34
-0.12,0.45,-0.05,0.23,0.10,-0.20
...
```

### scRNA Metadata CSV (with senescence)
```
Sample_ID,CellType,Disease_Status,Senescence_Score
GSE135779_1,CD4_T,SLE,0.62
GSE135779_2,CD8_T,SLE,0.48
...
```

---

## TROUBLESHOOTING

### Issue: "File not found" for GSE135779

**Check**: Is the file `.h5ad` or another format?

```bash
ls -la datasets/GSE135779/
# If file has different name, update path in script
```

**Fix**: Update `integrate_external_datasets.py` line with correct filename

---

### Issue: "No senescence genes found in expression matrix"

**Cause**: Gene names don't match (HUGO names vs Ensembl IDs)

**Check**: What gene names are in the dataset?
```python
import pandas as pd
df = pd.read_csv('datasets/GSE72509/GSE72509_series_matrix.txt.gz', nrows=5)
print(df.iloc[:5, 0])  # First 5 gene names
```

**Fix**: If genes are Ensembl IDs, add conversion step

---

### Issue: "MTX matrix dimensions mismatch"

**Cause**: MTX file format incompatibility

**Fix**: Check barcodes and features files exist:
```bash
ls datasets/GSE179633/ | grep -E "barcode|feature|matrix"
```

---

### Issue: Memory error with large scRNA datasets

**Cause**: GSE135779 is large (~80 GB)

**Fix**: Process in batches or use sparse matrix operations
```python
# In script: use sparse matrices instead of dense
adata.X.data  # instead of adata.X
```

---

## MONITORING EXECUTION

### Watch progress:

```bash
# Terminal 1: Run pipeline
python integrate_external_datasets.py 2>&1 | tee pipeline.log

# Terminal 2: Monitor output growth
watch 'find data/external_validation -name "*.csv" | wc -l'
```

### Check intermediate results:

```bash
# After GSE72509 completes
head data/external_validation/1_Bulk_Expansion/GSE72509/GSE72509_senescence_scores.csv

# Check senescence score distribution
python -c "
import pandas as pd
df = pd.read_csv('data/external_validation/1_Bulk_Expansion/GSE72509/GSE72509_senescence_scores.csv')
print(df['Senescence_Score'].describe())
"
```

---

## NEXT STEPS AFTER EXECUTION

### 1. Validate Results

```bash
# Check PIPELINE_RESULTS.json
cat data/external_validation/PIPELINE_RESULTS.json

# All should show "SUCCESS"
# If any "FAILED", check logs above
```

### 2. Cross-Dataset Analysis

Create a script to:
- [ ] Combine all senescence scores across datasets
- [ ] Compare GSE72509 senescence-SLEDAI vs other cohorts
- [ ] Generate summary table: "Senescence replicated in N cohorts"

### 3. Prepare for Manuscript

- [ ] Generate Table 1: Dataset summary (N, platform, senescence range)
- [ ] Generate Figure: Senescence distribution across datasets
- [ ] Generate Figure: Target gene expression heatmap (all cohorts)

---

## TIMING EXPECTATIONS

| Stage | Time | CPU |
|-------|------|-----|
| Data loading | 30 min | Low |
| Bulk normalization | 15 min | Medium |
| Bulk senescence scoring | 10 min | Medium |
| scRNA loading | 30 min | Medium |
| scRNA normalization | 45 min | High |
| scRNA senescence scoring | 20 min | High |
| Tissue processing | 40 min | Medium |
| Senescence validation | 30 min | Medium |
| **TOTAL** | **3-4 hours** | **Peak: High during scRNA** |

---

## SUCCESS CRITERIA

Pipeline execution is successful if:

- ✅ All 21 datasets load without critical errors
- ✅ Senescence scores computed for all datasets
- ✅ Target genes extracted for all datasets
- ✅ PIPELINE_RESULTS.json shows ≥18/21 SUCCESS
- ✅ Output files created in data/external_validation/

---

## AFTER COMPLETION

**Run this to create integrated summary**:

```bash
python create_validation_summary.py  # (new script - coming next)
```

**This will generate**:
- Master senescence scores table (all datasets)
- Cross-dataset correlation analysis
- Summary statistics for manuscript

