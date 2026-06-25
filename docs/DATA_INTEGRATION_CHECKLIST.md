# Data Integration Checklist: Step-by-Step Actions

**Use this checklist to track progress on each dataset integration.**

---

## CATEGORY 1: SLE BULK RNA-seq EXPANSION

### GSE72509 - PBMC Gene Expression (120 SLE + HC)
- [ ] Download from GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72509
- [ ] Extract metadata: Sample IDs, SLE vs HC status
- [ ] Check: SLEDAI available? (disease activity score)
- [ ] Normalize: Log2(CPM) or DESeq2 VST
- [ ] Compute senescence score (SenMayo 125-gene panel)
- [ ] Analyze: Correlation of senescence vs SLEDAI (if available)
- [ ] Document: N SLE, senescence score range, correlation r-value
- [ ] Save: `data/external_validation/1_Bulk_Expansion/GSE72509/`

**Timeline**: 3-4 hours  
**Expected output**: Senescence correlation r ≈ 0.5-0.7

---

### GSE112087 - Whole Blood, Interferon Pathway
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE112087
- [ ] Extract metadata: SLE vs HC, IFN pathway markers
- [ ] Check: Microarray platform - use same normalization method
- [ ] Compute senescence score
- [ ] Analyze: Senescence vs disease activity (if available)
- [ ] Document findings

**Timeline**: 3-4 hours  
**Note**: Microarray data (not RNA-seq) - normalize to same scale as bulk

---

### GSE181500 - CD4+ T Cell Gene Expression
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE181500
- [ ] Extract: CD4+ T cell subset metadata
- [ ] Key question: Are SLEDAI/disease markers in metadata?
- [ ] Compute senescence score
- [ ] Analysis: Cell-type-specific senescence in SLE CD4+ T cells
- [ ] Document

**Timeline**: 3-4 hours  
**Note**: Cell-type specific - valuable for mapping senescence to CD4+ compartment

---

### GSE228066 - SLE Severity Transcriptomics (2024)
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE228066
- [ ] Extract: SLE disease severity stratification (if available)
- [ ] Check: Does metadata include mild/moderate/severe classification?
- [ ] Compute senescence score
- [ ] Analysis: Senescence vs disease severity (different from SLEDAI)
- [ ] Document: **This is newest dataset (2024) - likely best annotated**

**Timeline**: 4 hours  
**Priority**: HIGH (most recent, likely best metadata)

---

### GSE122459 - PBMC + Proteomics Companion
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE122459
- [ ] Extract: RNA-seq data + associated proteomics samples
- [ ] Check: Do proteomics samples overlap with senescence scores?
- [ ] Compute: Senescence from transcriptomics
- [ ] Cross-validate: Compare senescence score vs proteomics targets (CSPG4, CD44)
- [ ] **This is unique**: Can validate senescence at transcriptomics + protein level

**Timeline**: 5-6 hours  
**Priority**: HIGH (multi-omics validation opportunity)

---

**Category 1 Summary**:
- [ ] All 5 bulk datasets downloaded
- [ ] Metadata extracted for each
- [ ] Senescence scores computed
- [ ] SLEDAI correlations calculated
- [ ] ✅ Success: Senescence-SLEDAI replicated in ≥3 datasets

**Expected Cumulative Timeline**: Week 1, ~20 hours

---

## CATEGORY 2: scRNA-seq EXPANSION (CRITICAL)

### GSE135779 - Large PBMC Cohort (Active/Inactive SLE vs HC)
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779
- [ ] **Large file warning**: Likely 10-20 GB
- [ ] Extract h5ad or 10X format
- [ ] QC: Cells (nGenes, nUMI, %mitochondrial)
- [ ] Cell type annotation (existing or infer from markers: CD4, CD8, CD19, CD14)
- [ ] Stratify: SLE active vs inactive vs HC
- [ ] **Key advantage**: Active/inactive classification = proxy for senescence burden
- [ ] Compute senescence score per cell type
- [ ] Analysis: Senescence differences between active/inactive SLE
- [ ] Document: Cell counts by type, senescence by type

**Timeline**: 6-8 hours (large dataset)  
**Priority**: HIGHEST - Active/inactive SLE is critical

---

### GSE142016 - Extend with Parent GSE139360
- [ ] Check: Already partially in repo
- [ ] **Action**: Download parent dataset GSE139360 for full cohort
- [ ] Merge: GSE139360 (larger) + GSE142016 subset
- [ ] Cell type annotation if not provided
- [ ] Compute senescence scores
- [ ] Integration: Batch-correct with GSE162577 if combining

**Timeline**: 4-5 hours  
**Note**: Check if GSE139360 has additional samples

---

### GSE162577 - Already in Repo
- [ ] ✅ Already integrated
- [ ] Check: Can it be merged/batch-corrected with GSE135779, GSE139360?

**Timeline**: 2 hours (integration only)

---

### GSE163121 - B Cells, CD11c+T-bet+, IFN Signature
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE163121
- [ ] **Focus**: CD11c+T-bet+ B cell subset (rare, disease-relevant)
- [ ] Extract: B cell metadata
- [ ] Check: IFN signature annotation available?
- [ ] Compute senescence score
- [ ] **Key insight**: B cells + senescence + IFN = SLE immunopathology
- [ ] Analysis: Senescence enrichment in SLE B cell subsets
- [ ] Document

**Timeline**: 4-5 hours  
**Insight**: B cells are CAR-T targets; senescent B cells may be priority

---

### GSE179633 - SLE + DLE, Cellular Heterogeneity
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179633
- [ ] Extract: SLE + Discoid Lupus Erythematosus (DLE) data
- [ ] **Note**: DLE is cutaneous lupus (localized) vs SLE (systemic)
- [ ] Compute senescence scores
- [ ] Analysis: Senescence in systemic vs cutaneous lupus
- [ ] Document: Does SLE show more senescence than DLE?

**Timeline**: 4 hours  
**Insight**: Disease subtype differences in senescence

---

### GSE266852 - Comparative PBMC (HC + SLE + RA)
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE266852
- [ ] **High-value**: Direct SLE vs RA comparison in same study
- [ ] Extract: Metadata for all 3 groups
- [ ] Compute senescence scores
- [ ] Analysis: Senescence in SLE > RA > HC?
- [ ] **This validates disease-specificity of senescence**

**Timeline**: 5-6 hours  
**Priority**: HIGH (disease specificity validation)

---

**Category 2 Summary**:
- [ ] All 6 scRNA datasets processed
- [ ] Batch correction across cohorts (Harmony or scVI)
- [ ] Cell type annotation standardized
- [ ] Senescence scores computed per cell
- [ ] ✅ Success: scRNA cohort expanded from N=5 to N=40+ SLE patients
- [ ] ✅ Senescence enrichment confirmed across ≥3 cell types (CD4, CD8, monocytes, B cells)

**Expected Cumulative Timeline**: Week 2, ~35 hours

---

## CATEGORY 3: TISSUE EXPANSION

### GSE36700 - Synovium (CURRENT - N=4 SLE)
- [ ] ✅ Already in repo
- [ ] Use as baseline for comparison

---

### GSE155405 - Kidney, Lupus Nephritis (LN) - Tertiary Lymphoid Structures
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE155405
- [ ] Extract: Kidney biopsy samples, LN status
- [ ] Metadata: Count N SLE with LN
- [ ] Compute senescence score
- [ ] Analysis: Senescence in LN kidney vs normal
- [ ] **Clinical relevance**: LN is where CAR-T is most needed
- [ ] Document

**Timeline**: 4 hours

---

### GSE294496 - Kidney scRNA-seq, Lupus Nephritis (2025)
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE294496
- [ ] **NEW (2025)**: Likely best-annotated kidney dataset
- [ ] Extract h5ad, cell type annotations
- [ ] Cell types in kidney: Endothelial, immune, podocytes, tubular
- [ ] Compute senescence score per cell type
- [ ] Analysis: Which kidney cell types show senescence in LN?
- [ ] **Insight**: Senescence in resident vs infiltrating immune cells

**Timeline**: 6 hours  
**Priority**: HIGH (newest, best annotated)

---

### GSE182825 - Skin, Cutaneous + Systemic SLE (Spatial)
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE182825
- [ ] **Format**: Spatial transcriptomics (10X Visium) - special handling
- [ ] Extract: Spatial coordinates + expression
- [ ] Stratify: Cutaneous-only vs systemic SLE
- [ ] Compute senescence score in spatial context
- [ ] Analysis: Spatial distribution of senescence in lupus skin lesion
- [ ] **Unique insight**: Not just WHAT but WHERE senescence localizes

**Timeline**: 5-6 hours  
**Caveat**: Spatial data requires special processing

---

### GSE200306 - Kidney, Lupus Nephritis Progression
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE200306
- [ ] Extract: LN samples at different disease timepoints (if available)
- [ ] Compute senescence score
- [ ] Analysis: Does senescence correlate with LN class/progression?
- [ ] Document

**Timeline**: 4 hours

---

### GSE174188 - Renal Biopsies, LN Subclass Stratification
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188
- [ ] Extract: LN class I-VI metadata (WHO classification)
- [ ] Compute senescence score
- [ ] Analysis: Senescence vs LN class (I→VI)
- [ ] **Does senescence increase with LN severity?**
- [ ] Document

**Timeline**: 4 hours  
**Insight**: Senescence as marker of LN severity

---

**Category 3 Summary**:
- [ ] All 6 tissue datasets processed
- [ ] Metadata standardized (SLE status, tissue type, disease severity if available)
- [ ] Senescence scores computed
- [ ] CSPG4/CD44/ICAM1 expression extracted from each
- [ ] ✅ Success: Tissue cohort expanded from N=4 SLE (synovium only) to N=12-20 SLE across kidney/skin
- [ ] ✅ **Critical finding**: CSPG4/CD44/ICAM1 still elevated 1.5-2× in SLE vs control tissues

**Expected Cumulative Timeline**: Week 2-3, ~30 hours

---

## CATEGORY 4: SENESCENCE VALIDATION DATASETS

### GSE101766 - IMR90 Fibroblasts, SASP Regulation
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE101766
- [ ] Extract: senescent vs non-senescent samples
- [ ] **Key**: Apply SenMayo 125-gene panel to THIS dataset
- [ ] Validation: Does senescence score separate senescent from control?
- [ ] Extract SASP genes: IL6, TNF, CXCL8, MMP3, etc.
- [ ] Analysis: SASP genes elevated in senescent vs control?
- [ ] **Confirms**: SenMayo scoring works as designed

**Timeline**: 3 hours  
**Purpose**: Methodological validation

---

### GSE226598 - Type-I IFN Disease (SAVI) T Cell Senescence ⭐ CRITICAL
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE226598
- [ ] **HIGH PRIORITY**: Type-I IFN drives senescence — SAME mechanism as SLE
- [ ] Extract: T cells from SAVI patients (type-I IFN hyperactivation)
- [ ] Compute senescence score
- [ ] **Key finding**: Is senescence elevated in IFN-driven disease?
- [ ] Analysis: Senescence score correlates with IFN-I signature?
- [ ] **This is mechanistic bridge**: IFN-I → senescence (common to SLE and SAVI)

**Timeline**: 4 hours  
**Priority**: HIGHEST (mechanistic validation)

---

### GSE262856 - Human Cell Lines, Senescence Types
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE262856
- [ ] Extract: Different senescence induction conditions
- [ ] Compute SenMayo scores across conditions
- [ ] Analysis: Does senescence scoring detect all types equally?
- [ ] **Insight**: Senescence heterogeneity - some types high, some low score?

**Timeline**: 3 hours  
**Purpose**: Robustness of senescence scoring

---

### GSE157007 - Age-Dependent Immune Senescence (scRNA, 114,467 cells)
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE157007
- [ ] **Large**: 114K cells, but high-value
- [ ] Extract: Immune cell types across ages (young, middle, old)
- [ ] Compute senescence score per cell
- [ ] Analysis: Does senescence increase with age as expected?
- [ ] **Cross-validation**: SenMayo panel should work in aging context

**Timeline**: 6 hours  
**Purpose**: Age-related senescence validation

---

### GSE297723 - Mouse Lung, LAMP1 Surface Marker
- [ ] Download: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE297723
- [ ] **Note**: Mouse data (not human) - still relevant
- [ ] Extract: LAMP1 expression as senescence marker
- [ ] **Relevance to CAR-T**: LAMP1 is lysosomal marker upregulated in senescence
- [ ] Analysis: Can LAMP1 be used as CAR-T surface antigen instead of CSPG4/CD44?
- [ ] Document: CSPG4/CD44 vs LAMP1 comparison

**Timeline**: 3 hours  
**Insight**: Alternative CAR-T targets

---

**Category 4 Summary**:
- [ ] All 5 senescence datasets processed
- [ ] SenMayo 125-gene panel validated across multiple contexts
- [ ] SASP genes confirmed elevated in senescent samples
- [ ] ✅ Success: Senescence scoring methodology independently validated
- [ ] ✅ GSE226598 confirms IFN-I → senescence (mechanism in SLE)

**Expected Cumulative Timeline**: Week 3, ~20 hours

---

## CATEGORY 5: CAR-T CLINICAL PAPERS (Literature)

### Müller et al. (2023) - CD19 CAR-T in Refractory SLE
- [ ] Access: https://pubmed.ncbi.nlm.nih.gov/37516082/
- [ ] Read: Full text (Nature Medicine)
- [ ] Extract: N=5 SLE, SLEDAI baseline/post, remission outcomes
- [ ] Document: Killing efficacy, CAR-T persistence, toxicity
- [ ] **Use in manuscript**: "Previous work by Müller et al. demonstrated complete remission in CD19 CAR-T treated SLE (SLEDAI → 0)..."

---

### Taubmann et al. (2023/2024) - Extended Follow-up
- [ ] Access: ASH abstract + full paper when published
- [ ] Extract: 22-month follow-up data, DORIS remission
- [ ] Note: ICANS outcomes (important for safety)

---

### Feng et al. (2023) - Dual-Target CD19/BCMA
- [ ] Access: Blood ASH 2023 abstract
- [ ] Extract: SLEDAI-2K reduction (18.3 → 1.5), LLDAS rate 91.7%
- [ ] **Insight**: Dual-targeting improves efficacy — suggest CSPG4/CD44 dual-target

---

### Wang et al. (2024) - BCMA-CD19 Compound CAR-T
- [ ] Access: NEJM Evidence
- [ ] Extract: 46-month follow-up, renal function improvement
- [ ] **Key**: Long-term renal outcomes — relevant if tissue validation includes kidney

---

### Wang et al. (2025) - Allogeneic CD19 CAR-T (TyU19)
- [ ] Access: Clinical trial results
- [ ] Extract: SRI-4 remission, no GvHD (allogeneic advantage)

---

**Category 5 Summary**:
- [ ] All 5 CAR-T papers accessed and summarized
- [ ] Key efficacy data extracted (SLEDAI reduction, remission rates, toxicity)
- [ ] ✅ Document in manuscript: "Clinical evidence supporting CAR-T in SLE: 5 papers, 37 total SLE patients, >90% remission"

**Expected Timeline**: 1-2 hours

---

## CATEGORY 6: MECHANISTIC PAPERS (Literature)

### Saul et al. (2022) - SenMayo 125-Gene Panel
- [ ] PubMed: Original paper
- [ ] Extract: Gene list, scoring methodology
- [ ] Cite in Methods: "Senescence scored using SenMayo 125-gene panel (Saul et al. 2022)..."

---

### Poli et al. (2021) - Type-I IFN → T Cell Senescence
- [ ] Frontiers in Genetics: IFN-I drives senescence in SLE
- [ ] Extract: Mechanistic evidence
- [ ] Cite in Results: "Consistent with Poli et al., type-I IFN hyperactivation in SLE drives senescence..."

---

### Morel (2023) - Senescence in Autoimmune Disease Review
- [ ] Arthritis & Rheumatology: SASP as flare driver
- [ ] Extract: SASP molecules that could be CAR-T targets
- [ ] Cite in Discussion: "Morel reviews senescence as therapeutic target in autoimmunity..."

---

**Category 6 Summary**:
- [ ] All 3 mechanistic papers read and cited
- [ ] ✅ Methods section: Saul et al. (SenMayo)
- [ ] ✅ Results section: Poli et al. (IFN mechanism)
- [ ] ✅ Discussion section: Morel (therapeutic target)

**Expected Timeline**: 1-2 hours

---

## INTEGRATION COMPLETION CHECKLIST

### By End of Week 1:
- [ ] Category 1: All 5 bulk datasets downloaded + senescence scores computed
- [ ] Begin Category 2: scRNA datasets downloading

### By End of Week 2:
- [ ] Category 2: All 6 scRNA datasets integrated + batch corrected
- [ ] Category 3: All 6 tissue datasets downloaded

### By End of Week 3:
- [ ] Category 3: Tissue analysis complete (N=12-20 SLE)
- [ ] Category 4: Senescence validation datasets complete
- [ ] Category 5-6: All papers read + cited

### Ready for Manuscript (Week 4):
- [ ] ✅ All datasets integrated
- [ ] ✅ docs/EXTERNAL_VALIDATION.md complete
- [ ] ✅ All findings documented
- [ ] ✅ Repository structure updated
- [ ] ✅ Manuscript can reference integrated multi-dataset resource

---

## Storage Notes

**Total anticipated storage**: ~150-200 GB  
**Recommendation**: Download to external drive or institutional cluster

**Directory structure**:
```
data/external_validation/
├── 1_Bulk_Expansion/    (15 GB)
├── 2_scRNA_Expansion/   (80 GB) ← Largest
├── 3_Tissue_Expansion/  (40 GB)
├── 4_Senescence_Datasets/ (5 GB)
└── Integration_results/  (10 GB)
```

