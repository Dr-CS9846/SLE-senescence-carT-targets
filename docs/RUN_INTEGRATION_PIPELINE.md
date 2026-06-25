# How to Run the Multi-Omics Integration Pipeline

## Quick Start (3 steps)

### Step 1: Open Terminal in VS Code
```
Ctrl + ` (backtick)
```

### Step 2: Install Required Package (if needed)
```bash
pip install openpyxl pandas numpy
```

### Step 3: Run the Script
```bash
python multiomics_integration.py
```

---

## What the Script Does

✅ **Reads all datasets:**
- GSE162577 series matrix → scRNA-seq metadata
- GSE142016 series matrix → scRNA-seq metadata  
- GSE318067 SomaLogic Excel → Proteomics + metadata
- GSE318067 RBM Excel → Proteomics
- GSE36700 series matrix → Tissue metadata

✅ **Harmonizes metadata:**
- Extracts disease activity (Inactive/Mild/Moderate/Severe)
- Maps samples across platforms
- Creates integrated sample table

✅ **Computes senescence:**
- SASP (Senescence-Associated Secretory Phenotype) signatures
- Senescence scores from proteomics
- Z-normalized senescence burden

✅ **Outputs clean data files:**
- `01_METADATA_Integrated_All_Cohorts.csv` → Master sample table
- `03_PROTEOMICS_SomaLogic_Expression.csv` → Protein expression matrix
- `05_SENESCENCE_Scores_GSE318067.csv` → Senescence scores
- `README.md` → Data dictionary
- `00_DATA_QUALITY_REPORT.json` → Integration summary

---

## Expected Output

```
================================================================================
MULTI-OMICS INTEGRATION PIPELINE FOR SLE SENESCENCE STUDY
================================================================================
Start time: 2026-06-25 XX:XX:XX

[1/7] Reading GSE318067 SomaLogic metadata...
   ✓ 75 samples loaded
   ✓ Controls: 34, SLE patients: 34
   ✓ SLE breakdown: Inactive=8, Mild=17, Moderate=8, Severe=1

[2/7] Reading GSE318067 SomaLogic proteomics matrix...
   ✓ 1129 proteins, 68 samples

[3/7] Reading GSE318067 RBM proteomics matrix...
   ✓ 192 proteins, 68 samples

[4/7] Reading scRNA-seq series matrices...
   ✓ 6 scRNA-seq samples loaded
   ✓ GSE162577: 3 samples
   ✓ GSE142016: 3 samples

[5/7] Reading GSE36700 synovial tissue metadata...
   ✓ 25 tissue samples loaded
      SLE: 4 samples
      OA: 5 samples
      RA: 7 samples

[6/7] Computing senescence signatures...
   ✓ SASP signature computed from 7 proteins
   ✓ Senescence scores computed for 68 samples

[7/7] Creating integrated metadata...
   ✓ Integrated metadata: 99 samples
      - GSE318067 (bulk): 68 samples
      - scRNA-seq: 6 samples
      - GSE36700 (tissue): 25 samples

================================================================================
SAVING OUTPUTS
================================================================================
✓ 01_METADATA_Integrated_All_Cohorts.csv
✓ 02_METADATA_GSE318067_PrimaryBulkCohort.csv
✓ 03_PROTEOMICS_SomaLogic_Expression.csv
✓ 04_PROTEOMICS_RBM_Expression.csv
✓ 05_SENESCENCE_Scores_GSE318067.csv
✓ 00_DATA_QUALITY_REPORT.json
✓ README.md

================================================================================
PIPELINE COMPLETE
================================================================================
✓ All data files ready for analysis and GitHub upload
```

---

## Output Files Location

```
D:\New folder\Research\53. Zeshan Gondal\5. Lupus\processed_data\
├── 00_DATA_QUALITY_REPORT.json
├── 01_METADATA_Integrated_All_Cohorts.csv
├── 02_METADATA_GSE318067_PrimaryBulkCohort.csv
├── 03_PROTEOMICS_SomaLogic_Expression.csv
├── 04_PROTEOMICS_RBM_Expression.csv
├── 05_SENESCENCE_Scores_GSE318067.csv
└── README.md
```

---

## Using the Output Files

### Load in Python
```python
import pandas as pd

# Load metadata
metadata = pd.read_csv('processed_data/01_METADATA_Integrated_All_Cohorts.csv')
print(metadata.head())

# Load proteomics
soma = pd.read_csv('processed_data/03_PROTEOMICS_SomaLogic_Expression.csv')
print(f"Proteins: {len(soma)}, Samples: {len(soma.columns)-1}")

# Load senescence scores
senescence = pd.read_csv('processed_data/05_SENESCENCE_Scores_GSE318067.csv')
print(senescence.describe())
```

### Load in R
```r
metadata <- read.csv('processed_data/01_METADATA_Integrated_All_Cohorts.csv')
soma <- read.csv('processed_data/03_PROTEOMICS_SomaLogic_Expression.csv')
senescence <- read.csv('processed_data/05_SENESCENCE_Scores_GSE318067.csv')

# Merge
data <- merge(metadata, senescence, by='Sample_ID')
head(data)
```

---

## Troubleshooting

### Error: "FileNotFoundError: [Errno 2] No such file or directory"
→ Check that all `.xlsx` and `.txt` files exist in `D:\New folder\Research\53. Zeshan Gondal\5. Lupus\datasets\`

### Error: "openpyxl is required but not installed"
```bash
pip install openpyxl
```

### Error: "Permission denied" when writing output
→ Make sure `processed_data\` folder is writable
→ Run VS Code as Administrator if needed

---

## Next Steps

1. ✅ Run the script
2. ✅ Check output files in `processed_data\`
3. ✅ Commit to GitHub:
   ```bash
   git add processed_data/
   git commit -m "Add multi-omics integrated dataset"
   git push
   ```
4. ✅ Use outputs in manuscript Methods section
5. ✅ Reference in data availability statement

---

**Total runtime:** ~15-30 seconds (depending on machine)

**Questions?** Check the console output for detailed logging at each step.
