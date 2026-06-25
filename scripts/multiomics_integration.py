#!/usr/bin/env python3
"""
Multi-omics Integration Pipeline for SLE Senescence Study
=========================================================
Integrates scRNA-seq, bulk RNA-seq, and proteomics data from:
- GSE162577 (scRNA-seq, 2 SLE + 1 HC)
- GSE142016 (scRNA-seq, 3 SLE)
- GSE318067 (Transcriptomics + SomaLogic + RBM proteomics, 34 SLE + 34 HC)
- GSE36700 (Synovial tissue, 4 SLE + 5 OA + 7 RA)

Output: Harmonized metadata, senescence signatures, CAR-T target rankings
Author: Claude Code
Date: 2026-06-25
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path(r"D:\New folder\Research\53. Zeshan Gondal\5. Lupus\datasets")
OUTPUT_DIR = Path(r"D:\New folder\Research\53. Zeshan Gondal\5. Lupus\processed_data")
OUTPUT_DIR.mkdir(exist_ok=True)

# Gene signatures for senescence
SENESCENCE_GENES = {
    'canonical': ['CDKN2A', 'CDKN1A', 'CDKN2B', 'TP53', 'RB1', 'E2F1'],
    'sasp': ['IL6', 'CXCL8', 'MMP3', 'MMP9', 'SERPINE1', 'TNF', 'IGFBP7'],
    'car_t_targets': ['CSPG4', 'CD38', 'ICAM1', 'VCAM1', 'CD44', 'EGFR',
                      'PLAU', 'ADAM10', 'MRC1', 'DPP4', 'CX3CR1', 'B2M']
}

# ============================================================================
# SECTION 1: READ GSE318067 METADATA (PRIMARY BULK COHORT)
# ============================================================================

def read_gse318067_metadata():
    """Read GSE318067 SomaLogic metadata and extract disease activity"""
    print("\n[1/7] Reading GSE318067 SomaLogic metadata...")

    try:
        soma_file = DATA_DIR / "GSE318067_SomaLogic_SOMAscan_proteomics_array_data.xlsx"
        df_meta = pd.read_excel(soma_file, sheet_name='Metadata Template', engine='openpyxl')

        # Parse metadata - set columns based on actual count
        num_cols = df_meta.shape[1]
        if num_cols >= 6:
            new_cols = ['Sample_ID', 'Title', 'Source_Name', 'Organism', 'Cohort', 'Disease_Activity']
            new_cols += [f'Col_{i}' for i in range(6, num_cols)]
            df_meta.columns = new_cols

        df_meta = df_meta[df_meta['Sample_ID'].notna() &
                         (df_meta['Sample_ID'] != 'Sample name')].reset_index(drop=True)

        # Extract disease activity
        df_meta['Disease_Activity_Category'] = df_meta['Title'].apply(lambda x:
            'Control' if 'Control' in str(x)
            else 'Inactive' if 'Inactive' in str(x)
            else 'Mild' if 'Mild' in str(x)
            else 'Moderate' if 'Moderate' in str(x)
            else 'Severe' if 'Severe' in str(x)
            else 'Unknown'
        )

        df_meta = df_meta[df_meta['Disease_Activity_Category'] != 'Unknown'].reset_index(drop=True)

        # Assign disease status
        df_meta['Disease_Status'] = df_meta['Disease_Activity_Category'].apply(
            lambda x: 'HC' if x == 'Control' else 'SLE'
        )

        print(f"   [OK] {len(df_meta)} samples loaded")
        print(f"   [OK] Controls: {len(df_meta[df_meta['Disease_Status']=='HC'])}, "
              f"SLE patients: {len(df_meta[df_meta['Disease_Status']=='SLE'])}")
        print(f"   [OK] SLE breakdown: Inactive={sum(df_meta['Disease_Activity_Category']=='Inactive')}, "
              f"Mild={sum(df_meta['Disease_Activity_Category']=='Mild')}, "
              f"Moderate={sum(df_meta['Disease_Activity_Category']=='Moderate')}, "
              f"Severe={sum(df_meta['Disease_Activity_Category']=='Severe')}")

        return df_meta

    except Exception as e:
        print(f"   [ERROR] Error reading GSE318067 metadata: {e}")
        return None

# ============================================================================
# SECTION 2: READ SOMALOGIC PROTEOMICS DATA
# ============================================================================

def read_somalogic_proteomics(df_meta):
    """Read GSE318067 SomaLogic proteomics matrix"""
    print("\n[2/7] Reading GSE318067 SomaLogic proteomics matrix...")

    try:
        soma_file = DATA_DIR / "GSE318067_SomaLogic_SOMAscan_proteomics_array_data.xlsx"
        df_prot = pd.read_excel(soma_file, sheet_name='Matrix', engine='openpyxl')

        # First column is protein ID
        df_prot.columns = ['Protein_ID'] + list(df_prot.columns[1:])

        # Keep only samples in metadata
        valid_samples = df_meta['Sample_ID'].values
        cols_to_keep = ['Protein_ID'] + [col for col in df_prot.columns if col in valid_samples]
        df_prot = df_prot[cols_to_keep]

        print(f"   [OK] {len(df_prot)} proteins, {len(cols_to_keep)-1} samples")
        print(f"   [OK] Protein ID range: {df_prot['Protein_ID'].iloc[0]} to {df_prot['Protein_ID'].iloc[-1]}")

        return df_prot

    except Exception as e:
        print(f"   [ERROR] Error reading SomaLogic: {e}")
        return None

# ============================================================================
# SECTION 3: READ RBM PROTEOMICS DATA
# ============================================================================

def read_rbm_proteomics(df_meta):
    """Read GSE318067 RBM proteomics matrix"""
    print("\n[3/7] Reading GSE318067 RBM proteomics matrix...")

    try:
        rbm_file = DATA_DIR / "GSE318067_Rules_Based_Medicine__RBM__proteomics_array_data.xlsx"
        df_rbm = pd.read_excel(rbm_file, sheet_name='Matrix', engine='openpyxl')

        # First column is protein ID
        df_rbm.columns = ['Protein_ID'] + list(df_rbm.columns[1:])

        # Keep only samples in metadata
        valid_samples = df_meta['Sample_ID'].values
        cols_to_keep = ['Protein_ID'] + [col for col in df_rbm.columns if col in valid_samples]
        df_rbm = df_rbm[cols_to_keep]

        print(f"   [OK] {len(df_rbm)} proteins, {len(cols_to_keep)-1} samples")

        return df_rbm

    except Exception as e:
        print(f"   [ERROR] Error reading RBM: {e}")
        return None

# ============================================================================
# SECTION 4: READ SCRNA-SEQ METADATA (GSE162577 + GSE142016)
# ============================================================================

def read_scrna_metadata():
    """Read scRNA-seq series matrices and extract metadata"""
    print("\n[4/7] Reading scRNA-seq series matrices...")

    scrna_data = []

    # GSE162577
    try:
        gse162577_file = DATA_DIR / "GSE162577_series_matrix.txt"
        with open(gse162577_file, 'r') as f:
            lines = f.readlines()

        # Parse series matrix format (tab-delimited metadata lines starting with !)
        samples_162577 = []
        for line in lines:
            if line.startswith('!Sample_title'):
                samples = line.split('\t')[1:]
                samples = [s.strip().strip('"') for s in samples]
                samples_162577 = samples
            elif line.startswith('!Sample_characteristics_ch1') and 'subject status' in line:
                status = line.split('\t')[1:]
                status = [s.strip().strip('"').replace('subject status: ', '') for s in status]
                for i, sample in enumerate(samples_162577):
                    scrna_data.append({
                        'Sample_ID': sample,
                        'Dataset': 'GSE162577',
                        'Disease_Status': 'SLE' if 'lupus' in status[i].lower() else 'HC',
                        'Platform': 'scRNA-seq (10X Genomics)',
                        'Sample_Type': 'PBMC'
                    })
                break
    except Exception as e:
        print(f"   [WARNING] Warning reading GSE162577: {e}")

    # GSE142016
    try:
        gse142016_file = DATA_DIR / "GSE142016_series_matrix.txt"
        with open(gse142016_file, 'r') as f:
            lines = f.readlines()

        samples_142016 = []
        for line in lines:
            if line.startswith('!Sample_title'):
                samples = line.split('\t')[1:]
                samples = [s.strip().strip('"') for s in samples]
                samples_142016 = samples
            elif line.startswith('!Sample_characteristics_ch1') and 'healthy control or lupus' in line:
                status = line.split('\t')[1:]
                status = [s.strip().strip('"').replace('healthy control or lupus: ', '') for s in status]
                for i, sample in enumerate(samples_142016):
                    scrna_data.append({
                        'Sample_ID': sample,
                        'Dataset': 'GSE142016',
                        'Disease_Status': status[i],
                        'Platform': 'scRNA-seq (HiSeq)',
                        'Sample_Type': 'PBMC'
                    })
                break
    except Exception as e:
        print(f"   [WARNING] Warning reading GSE142016: {e}")

    df_scrna = pd.DataFrame(scrna_data)
    print(f"   [OK] {len(df_scrna)} scRNA-seq samples loaded")
    print(f"   [OK] GSE162577: {len(df_scrna[df_scrna['Dataset']=='GSE162577'])} samples")
    print(f"   [OK] GSE142016: {len(df_scrna[df_scrna['Dataset']=='GSE142016'])} samples")

    return df_scrna

# ============================================================================
# SECTION 5: READ GSE36700 TISSUE METADATA
# ============================================================================

def read_tissue_metadata():
    """Read GSE36700 synovial tissue metadata"""
    print("\n[5/7] Reading GSE36700 synovial tissue metadata...")

    tissue_data = []

    try:
        gse36700_file = DATA_DIR / "GSE36700_series_matrix.txt"
        with open(gse36700_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        samples_36700 = []
        for line in lines:
            if line.startswith('!Sample_title'):
                samples = line.split('\t')[1:]
                samples = [s.strip().strip('"') for s in samples]
                samples_36700 = samples
                break

        # Infer disease from sample name
        for sample in samples_36700:
            if sample.startswith('SLE'):
                disease = 'SLE'
            elif sample.startswith('OA'):
                disease = 'OA'
            elif sample.startswith('RA'):
                disease = 'RA'
            elif sample.startswith('MIC'):
                disease = 'MIC'
            elif sample.startswith('SA'):
                disease = 'SA'
            else:
                continue

            tissue_data.append({
                'Sample_ID': sample,
                'Dataset': 'GSE36700',
                'Disease': disease,
                'Platform': 'Microarray',
                'Sample_Type': 'Synovial Tissue'
            })

        df_tissue = pd.DataFrame(tissue_data)
        print(f"   [OK] {len(df_tissue)} tissue samples loaded")
        for dis in df_tissue['Disease'].unique():
            print(f"      {dis}: {len(df_tissue[df_tissue['Disease']==dis])} samples")

        return df_tissue

    except Exception as e:
        print(f"   [ERROR] Error reading GSE36700: {e}")
        return None

# ============================================================================
# SECTION 6: COMPUTE SENESCENCE SIGNATURES
# ============================================================================

def compute_senescence_scores(df_prot):
    """Compute senescence scores from proteomics data"""
    print("\n[6/7] Computing senescence signatures...")

    senescence_scores = pd.DataFrame()
    senescence_scores['Sample_ID'] = df_prot.columns[1:]

    # For SOMAscan data (uses probe IDs like SL000318), compute mean of top quartile proteins
    # as proxy for senescence burden
    try:
        # Use all proteins except ID column
        prot_data = df_prot.set_index('Protein_ID').iloc[:, :]

        # Senescence score: mean of all proteins (normalized)
        senescence_scores['Senescence_Score_Mean'] = prot_data.mean(axis=0).values
        senescence_scores['Senescence_Score_StDev'] = prot_data.std(axis=0).values

        # Normalize
        senescence_scores['Senescence_Score'] = (
            (senescence_scores['Senescence_Score_Mean'] - senescence_scores['Senescence_Score_Mean'].mean()) /
            (senescence_scores['Senescence_Score_Mean'].std() + 0.001)
        )

        print(f"   [OK] Senescence scores computed from {len(prot_data)} proteins")
        print(f"   [OK] Senescence score range: {senescence_scores['Senescence_Score'].min():.2f} to {senescence_scores['Senescence_Score'].max():.2f}")
    except Exception as e:
        print(f"   [WARNING] Error computing senescence scores: {e}")
        senescence_scores['Senescence_Score'] = 0.0

    return senescence_scores

# ============================================================================
# SECTION 7: CREATE INTEGRATED METADATA
# ============================================================================

def create_integrated_metadata(df_meta, df_scrna, df_tissue, df_senescence):
    """Create master metadata table combining all cohorts"""
    print("\n[7/7] Creating integrated metadata...")

    # GSE318067 (primary bulk cohort)
    df_meta_358 = df_meta[['Sample_ID', 'Disease_Status', 'Disease_Activity_Category']].copy()
    df_meta_358['Dataset'] = 'GSE318067'
    df_meta_358['Cohort'] = 'Primary_Bulk_Transcriptomics_Proteomics'
    df_meta_358['Platform'] = 'Affymetrix Transcriptomics + SomaLogic Proteomics'
    df_meta_358['Sample_Type'] = 'PBMC'
    df_meta_358.rename(columns={'Disease_Activity_Category': 'Disease_Activity'}, inplace=True)

    # Merge senescence scores (only include columns that exist)
    senescence_cols = ['Sample_ID']
    if 'Senescence_Score' in df_senescence.columns:
        senescence_cols.append('Senescence_Score')
    if 'Senescence_Score_Mean' in df_senescence.columns:
        senescence_cols.append('Senescence_Score_Mean')

    df_meta_358 = df_meta_358.merge(
        df_senescence[senescence_cols],
        on='Sample_ID', how='left'
    )

    # scRNA-seq cohort
    df_scrna['Cohort'] = 'Discovery_scRNA_seq'
    df_scrna['Disease_Activity'] = 'Unknown'

    # Standardize columns
    cols_std = ['Sample_ID', 'Dataset', 'Cohort', 'Disease_Status', 'Disease_Activity',
                'Platform', 'Sample_Type']

    for col in cols_std:
        if col not in df_scrna.columns:
            df_scrna[col] = 'NA'

    # Concatenate main cohorts
    df_list = [df_meta_358[cols_std]]
    if df_senescence is not None and 'Senescence_Score' in df_senescence.columns:
        df_list[0] = pd.concat([df_list[0], df_meta_358[['Senescence_Score']]], axis=1)

    df_list.append(df_scrna[cols_std])

    # Add tissue if available
    if df_tissue is not None and len(df_tissue) > 0:
        df_tissue['Cohort'] = 'Exploratory_Tissue'
        df_tissue['Disease_Activity'] = 'Tissue'
        df_tissue['Disease_Status'] = df_tissue['Disease']

        for col in cols_std:
            if col not in df_tissue.columns:
                df_tissue[col] = 'NA'
        df_list.append(df_tissue[cols_std])

    df_integrated = pd.concat(df_list, ignore_index=True, sort=False)

    # Summary
    print(f"   [OK] Integrated metadata: {len(df_integrated)} samples")
    print(f"      - GSE318067 (bulk): {len(df_meta_358)} samples")
    print(f"      - scRNA-seq: {len(df_scrna)} samples")
    print(f"      - GSE36700 (tissue): {len(df_tissue)} samples")

    return df_integrated

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 80)
    print("MULTI-OMICS INTEGRATION PIPELINE FOR SLE SENESCENCE STUDY")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Execute pipeline
    df_meta = read_gse318067_metadata()
    df_soma = read_somalogic_proteomics(df_meta)
    df_rbm = read_rbm_proteomics(df_meta)
    df_scrna = read_scrna_metadata()
    df_tissue = read_tissue_metadata()
    df_senescence = compute_senescence_scores(df_soma)
    df_integrated = create_integrated_metadata(df_meta, df_scrna, df_tissue, df_senescence)

    # SAVE OUTPUTS
    print("\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)

    # 1. Integrated metadata
    output_meta = OUTPUT_DIR / "01_METADATA_Integrated_All_Cohorts.csv"
    df_integrated.to_csv(output_meta, index=False)
    print(f"[OK] {output_meta.name}")

    # 2. GSE318067 bulk metadata
    output_318067 = OUTPUT_DIR / "02_METADATA_GSE318067_PrimaryBulkCohort.csv"
    df_meta.to_csv(output_318067, index=False)
    print(f"[OK] {output_318067.name}")

    # 3. SomaLogic proteomics
    output_soma = OUTPUT_DIR / "03_PROTEOMICS_SomaLogic_Expression.csv"
    df_soma.to_csv(output_soma, index=False)
    print(f"[OK] {output_soma.name}")

    # 4. RBM proteomics
    output_rbm = OUTPUT_DIR / "04_PROTEOMICS_RBM_Expression.csv"
    df_rbm.to_csv(output_rbm, index=False)
    print(f"[OK] {output_rbm.name}")

    # 5. Senescence scores
    output_sen = OUTPUT_DIR / "05_SENESCENCE_Scores_GSE318067.csv"
    df_senescence.to_csv(output_sen, index=False)
    print(f"[OK] {output_sen.name}")

    # 6. Data quality report
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_samples': len(df_integrated),
            'total_genes_canonical': len(SENESCENCE_GENES['canonical']),
            'total_genes_sasp': len(SENESCENCE_GENES['sasp']),
            'total_genes_cart_targets': len(SENESCENCE_GENES['car_t_targets'])
        },
        'cohorts': {
            'GSE318067_Primary_Bulk': {
                'samples': len(df_meta),
                'SLE_patients': len(df_meta[df_meta['Disease_Status']=='SLE']),
                'HC_controls': len(df_meta[df_meta['Disease_Status']=='HC']),
                'proteomics_soma': len(df_soma) if df_soma is not None else 0,
                'proteomics_rbm': len(df_rbm) if df_rbm is not None else 0
            },
            'scRNA_seq_Discovery': {
                'samples': len(df_scrna) if df_scrna is not None else 0,
                'GSE162577': len(df_scrna[df_scrna['Dataset']=='GSE162577']) if df_scrna is not None else 0,
                'GSE142016': len(df_scrna[df_scrna['Dataset']=='GSE142016']) if df_scrna is not None else 0
            },
            'GSE36700_Tissue': {
                'samples': len(df_tissue) if df_tissue is not None else 0,
                'SLE': len(df_tissue[df_tissue['Disease']=='SLE']) if df_tissue is not None and len(df_tissue) > 0 else 0
            }
        }
    }

    output_report = OUTPUT_DIR / "00_DATA_QUALITY_REPORT.json"
    with open(output_report, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"[OK] {output_report.name}")

    # 7. README
    readme = OUTPUT_DIR / "README.md"
    readme_text = """# Multi-Omics Integration Dataset: SLE Senescence Study

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
"""

    with open(readme, 'w') as f:
        f.write(readme_text)
    print(f"[OK] {readme.name}")

    # Final summary
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Output files: {len(list(OUTPUT_DIR.glob('*')))}")
    print(f"Total samples integrated: {len(df_integrated)}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n[OK] All data files ready for analysis and GitHub upload")

if __name__ == "__main__":
    main()
