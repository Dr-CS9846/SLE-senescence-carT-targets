#!/usr/bin/env python3
"""
Comprehensive Data Integration Pipeline for SLE Senescence Study

Integrates 21 external datasets across 4 categories:
1. SLE Bulk RNA-seq (5 datasets, 200+ samples)
2. scRNA-seq (6 cohorts, 40+ SLE patients)
3. Tissue (6 datasets, kidney/skin/synovium)
4. Senescence validation (5 reference datasets)

Output: Senescence scores + target gene expression across all cohorts
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import gzip
import json
from scipy.io import mmread
from scipy.stats import spearmanr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'base_path': 'datasets/',
    'output_path': 'data/external_validation/',
    'senescence_genes': {
        'canonical': ['CDKN2A', 'CDKN1A', 'CDKN2B', 'TP53', 'RB1', 'E2F1'],
        'sasp': ['IL6', 'TNF', 'CXCL8', 'MMP3', 'MMP9', 'SERPINE1', 'IGFBP7'],
    },
    'car_t_targets': ['CSPG4', 'CD44', 'ICAM1', 'VCAM1', 'CD38', 'EGFR'],
}

# Create output directories
for category in ['1_Bulk_Expansion', '2_scRNA_Expansion', '3_Tissue_Expansion', '4_Senescence_Validation']:
    os.makedirs(f"{CONFIG['output_path']}{category}", exist_ok=True)


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_series_matrix(filepath):
    """Load GEO Series Matrix TSV file (gzipped or uncompressed)"""
    logger.info(f"Loading Series Matrix: {filepath}")

    try:
        if filepath.endswith('.gz'):
            df = pd.read_csv(filepath, sep='\t', compression='gzip', skiprows=0, low_memory=False)
        else:
            df = pd.read_csv(filepath, sep='\t', skiprows=0, low_memory=False)

        # Series matrix has metadata rows - filter to expression data
        # Typically starts with "ID_REF" or gene names
        logger.info(f"Loaded {df.shape[0]} genes × {df.shape[1]} samples")
        return df

    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return None


def load_h5ad(filepath):
    """Load h5ad file (AnnData format for scRNA-seq)"""
    logger.info(f"Loading h5ad: {filepath}")

    try:
        import scanpy as sc
        adata = sc.read_h5ad(filepath)
        logger.info(f"Loaded {adata.n_obs} cells × {adata.n_vars} genes")
        return adata

    except ImportError:
        logger.error("scanpy not installed. Install with: pip install scanpy")
        return None
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return None


def load_mtx_sparse(filepath_base):
    """Load sparse MTX matrix (GSE179633 format)

    Expects: matrix.mtx.gz, barcodes.tsv.gz, features.tsv.gz
    """
    logger.info(f"Loading MTX sparse matrix: {filepath_base}")

    try:
        import anndata

        # Extract directory from base path
        directory = os.path.dirname(filepath_base)

        # Find MTX files
        mtx_file = None
        for file in os.listdir(directory):
            if file.endswith('matrix.mtx.gz') or file.endswith('matrix.mtx'):
                mtx_file = os.path.join(directory, file)
                break

        if not mtx_file:
            logger.error(f"No matrix.mtx file found in {directory}")
            return None

        # Load matrix
        if mtx_file.endswith('.gz'):
            matrix = mmread(gzip.open(mtx_file, 'rb')).T.tocsr()
        else:
            matrix = mmread(mtx_file).T.tocsr()

        # Load barcodes
        barcodes_file = None
        for file in os.listdir(directory):
            if 'barcode' in file.lower() and file.endswith('.gz'):
                barcodes_file = os.path.join(directory, file)
                break

        if barcodes_file:
            with gzip.open(barcodes_file, 'rt') as f:
                barcodes = [line.strip() for line in f.readlines()]
        else:
            barcodes = [f"Cell_{i}" for i in range(matrix.shape[0])]

        # Load features
        features_file = None
        for file in os.listdir(directory):
            if 'feature' in file.lower() and file.endswith('.gz'):
                features_file = os.path.join(directory, file)
                break

        if features_file:
            with gzip.open(features_file, 'rt') as f:
                features = [line.split('\t')[1].strip() if '\t' in line else line.strip()
                           for line in f.readlines()]
        else:
            features = [f"Gene_{i}" for i in range(matrix.shape[1])]

        # Create AnnData object
        adata = anndata.AnnData(X=matrix, obs=pd.DataFrame(index=barcodes),
                               var=pd.DataFrame(index=features))

        logger.info(f"Loaded {adata.n_obs} cells × {adata.n_vars} genes")
        return adata

    except Exception as e:
        logger.error(f"Failed to load MTX matrix: {e}")
        return None


def normalize_bulk_expression(df):
    """Normalize bulk RNA-seq expression (log2 CPM)"""
    logger.info(f"Normalizing bulk expression: {df.shape}")

    try:
        # Assume first column is gene names
        if df.columns[0] in ['ID_REF', 'GENE_ID', 'gene', 'Gene']:
            genes = df.iloc[:, 0]
            expr = df.iloc[:, 1:].astype(float)
        else:
            genes = df.index
            expr = df.astype(float)

        # CPM normalization: (counts / total) * 1e6
        expr_cpm = expr.div(expr.sum(axis=0), axis=1) * 1e6

        # Log2 transform (add pseudocount to avoid log(0))
        expr_log = np.log2(expr_cpm + 1)

        # Add gene names back
        expr_log.index = genes

        logger.info(f"Normalized to {expr_log.shape[0]} genes × {expr_log.shape[1]} samples")
        return expr_log

    except Exception as e:
        logger.error(f"Normalization failed: {e}")
        return None


def log_normalize_scrna(adata):
    """Log normalize scRNA-seq data"""
    logger.info(f"Log-normalizing scRNA-seq: {adata.shape}")

    try:
        import scanpy as sc

        # Copy to avoid modifying original
        adata_norm = adata.copy()

        # CPM normalization
        sc.pp.normalize_total(adata_norm, target_sum=1e6)

        # Log transform
        sc.pp.log1p(adata_norm)

        logger.info(f"Normalized {adata_norm.shape[0]} cells × {adata_norm.shape[1]} genes")
        return adata_norm

    except ImportError:
        logger.error("scanpy not installed")
        return None
    except Exception as e:
        logger.error(f"Normalization failed: {e}")
        return None


# ============================================================================
# SENESCENCE SCORING
# ============================================================================

def compute_senescence_score(expr_matrix, gene_list, method='mean'):
    """
    Compute senescence score for samples/cells

    Args:
        expr_matrix: Expression matrix (genes × samples/cells)
        gene_list: List of senescence marker genes
        method: 'mean', 'median', or 'zscore'

    Returns:
        Senescence scores (1D array)
    """
    logger.info(f"Computing senescence score ({method}) for {len(gene_list)} genes")

    try:
        # Find genes in expression matrix
        if isinstance(expr_matrix, pd.DataFrame):
            available_genes = [g for g in gene_list if g in expr_matrix.index]
            expr_subset = expr_matrix.loc[available_genes, :]
        else:
            # AnnData format
            available_genes = [g for g in gene_list if g in expr_matrix.var_names]
            expr_subset = expr_matrix[:, available_genes].X

        if len(available_genes) == 0:
            logger.warning(f"No senescence genes found in expression matrix")
            return None

        logger.info(f"Using {len(available_genes)}/{len(gene_list)} senescence genes")

        # Calculate score
        if isinstance(expr_subset, pd.DataFrame):
            if method == 'mean':
                score = expr_subset.mean(axis=0)
            elif method == 'median':
                score = expr_subset.median(axis=0)
        else:
            # Sparse or dense array
            if method == 'mean':
                score = np.asarray(expr_subset.mean(axis=0)).flatten()
            elif method == 'median':
                score = np.asarray(np.median(expr_subset, axis=0)).flatten()

        # Z-score normalize
        score_zscore = (score - score.mean()) / score.std()

        logger.info(f"Senescence score range: {score_zscore.min():.2f} to {score_zscore.max():.2f}")

        return score_zscore

    except Exception as e:
        logger.error(f"Senescence scoring failed: {e}")
        return None


def extract_target_expression(expr_matrix, targets):
    """Extract CAR-T target gene expression"""
    logger.info(f"Extracting {len(targets)} target genes")

    try:
        if isinstance(expr_matrix, pd.DataFrame):
            available = [t for t in targets if t in expr_matrix.index]
            return expr_matrix.loc[available, :]
        else:
            # AnnData
            available = [t for t in targets if t in expr_matrix.var_names]
            expr_df = pd.DataFrame(
                expr_matrix[:, available].X,
                index=[str(i) for i in range(expr_matrix.n_obs)],
                columns=available
            )
            return expr_df

    except Exception as e:
        logger.error(f"Target extraction failed: {e}")
        return None


# ============================================================================
# DATASET PROCESSING
# ============================================================================

class BulkDataset:
    """Process bulk RNA-seq dataset"""

    def __init__(self, name, filepath, metadata_cols=None):
        self.name = name
        self.filepath = filepath
        self.metadata_cols = metadata_cols or {}
        self.data = None
        self.metadata = None
        self.senescence_scores = None

    def load(self):
        """Load and normalize data"""
        raw = load_series_matrix(self.filepath)
        if raw is None:
            return False

        self.data = normalize_bulk_expression(raw)
        self.extract_metadata(raw)
        return True

    def extract_metadata(self, raw_df):
        """Extract sample metadata from raw GEO file"""
        logger.info(f"Extracting metadata for {self.name}")

        # Series matrix has metadata in first columns
        # Typically: ID_REF, Title, Source.Name, etc.
        try:
            # Get sample names from column headers
            sample_names = self.data.columns
            self.metadata = pd.DataFrame(index=sample_names)
            self.metadata['Sample_ID'] = sample_names
            self.metadata['Dataset'] = self.name

            logger.info(f"Metadata extracted for {len(self.metadata)} samples")
        except Exception as e:
            logger.warning(f"Metadata extraction incomplete: {e}")

    def compute_senescence(self):
        """Compute senescence score"""
        all_genes = CONFIG['senescence_genes']['canonical'] + CONFIG['senescence_genes']['sasp']
        self.senescence_scores = compute_senescence_score(self.data, all_genes)
        return self.senescence_scores

    def save_outputs(self, output_dir):
        """Save processed data and scores"""
        os.makedirs(output_dir, exist_ok=True)

        # Save senescence scores
        if self.senescence_scores is not None:
            scores_df = pd.DataFrame({
                'Sample_ID': self.metadata['Sample_ID'],
                'Senescence_Score': self.senescence_scores
            })
            scores_df.to_csv(f"{output_dir}/{self.name}_senescence_scores.csv", index=False)
            logger.info(f"Saved senescence scores to {output_dir}/{self.name}_senescence_scores.csv")

        # Save target expression
        targets_expr = extract_target_expression(self.data, CONFIG['car_t_targets'])
        if targets_expr is not None:
            targets_expr.to_csv(f"{output_dir}/{self.name}_target_expression.csv")
            logger.info(f"Saved target expression to {output_dir}/{self.name}_target_expression.csv")


class scRNADataset:
    """Process scRNA-seq dataset"""

    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        self.adata = None
        self.senescence_scores = None

    def load(self):
        """Load scRNA data (handles h5ad and MTX formats)"""
        if self.filepath.endswith('.h5ad'):
            self.adata = load_h5ad(self.filepath)
        elif '.mtx' in self.filepath or 'matrix' in self.filepath:
            self.adata = load_mtx_sparse(self.filepath)
        else:
            logger.error(f"Unknown format: {self.filepath}")
            return False

        return self.adata is not None

    def process(self):
        """Normalize and score"""
        if self.adata is None:
            return False

        # Normalize
        self.adata = log_normalize_scrna(self.adata)
        if self.adata is None:
            return False

        # Compute senescence
        all_genes = CONFIG['senescence_genes']['canonical'] + CONFIG['senescence_genes']['sasp']
        scores = compute_senescence_score(self.adata, all_genes)

        if scores is not None:
            self.adata.obs['Senescence_Score'] = scores
            self.senescence_scores = scores
            return True

        return False

    def save_outputs(self, output_dir):
        """Save processed data"""
        if self.adata is None:
            return

        os.makedirs(output_dir, exist_ok=True)

        # Save metadata with senescence scores
        metadata_df = pd.DataFrame(self.adata.obs)
        metadata_df.to_csv(f"{output_dir}/{self.name}_metadata_with_senescence.csv")
        logger.info(f"Saved metadata to {output_dir}/{self.name}_metadata_with_senescence.csv")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def process_category_1_bulk():
    """Process SLE Bulk RNA-seq datasets"""
    logger.info("="*60)
    logger.info("CATEGORY 1: SLE BULK RNA-seq")
    logger.info("="*60)

    datasets = {
        'GSE72509': 'GSE72509_series_matrix.txt.gz',
        'GSE112087': 'GSE112087_series_matrix.txt.gz',
        'GSE181500': 'GSE181500_series_matrix.txt.gz',
        'GSE228066': 'GSE228066_series_matrix.txt.gz',
        'GSE122459': 'GSE122459_series_matrix.txt.gz',
    }

    output_dir = f"{CONFIG['output_path']}1_Bulk_Expansion"
    results = {}

    for name, filename in datasets.items():
        filepath = os.path.join(CONFIG['base_path'], name, filename)

        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            continue

        dataset = BulkDataset(name, filepath)

        if dataset.load():
            if dataset.compute_senescence() is not None:
                dataset.save_outputs(f"{output_dir}/{name}")
                results[name] = 'SUCCESS'
            else:
                results[name] = 'SCORE_FAILED'
        else:
            results[name] = 'LOAD_FAILED'

    return results


def process_category_2_scrna():
    """Process scRNA-seq datasets"""
    logger.info("="*60)
    logger.info("CATEGORY 2: scRNA-seq")
    logger.info("="*60)

    datasets = {
        'GSE135779': f"{CONFIG['base_path']}GSE135779/GSE135779.h5ad",
        'GSE139358': f"{CONFIG['base_path']}GSE139358/",  # Special handling
        'GSE162577': f"{CONFIG['base_path']}GSE162577/GSE162577.h5ad",
        'GSE163121': f"{CONFIG['base_path']}GSE163121/GSE163121.h5ad",
        'GSE179633': f"{CONFIG['base_path']}GSE179633/",  # MTX format
        'GSE266852': f"{CONFIG['base_path']}GSE266852/GSE266852.h5ad",
    }

    output_dir = f"{CONFIG['output_path']}2_scRNA_Expansion"
    results = {}

    for name, filepath in datasets.items():
        if not os.path.exists(filepath):
            logger.warning(f"Path not found: {filepath}")
            results[name] = 'PATH_NOT_FOUND'
            continue

        dataset = scRNADataset(name, filepath)

        if dataset.load() and dataset.process():
            dataset.save_outputs(f"{output_dir}/{name}")
            results[name] = 'SUCCESS'
        else:
            results[name] = 'PROCESS_FAILED'

    return results


def process_category_3_tissue():
    """Process tissue datasets"""
    logger.info("="*60)
    logger.info("CATEGORY 3: TISSUE")
    logger.info("="*60)

    # Mix of bulk and scRNA tissue datasets
    bulk_datasets = {
        'GSE36700': 'GSE36700_series_matrix.txt.gz',
        'GSE155405': 'GSE155405_series_matrix.txt.gz',
        'GSE200306': 'GSE200306_series_matrix.txt.gz',
        'GSE174188': 'GSE174188_series_matrix.txt.gz',
    }

    output_dir = f"{CONFIG['output_path']}3_Tissue_Expansion"
    results = {}

    # Process bulk tissue
    for name, filename in bulk_datasets.items():
        filepath = os.path.join(CONFIG['base_path'], name, filename)

        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            continue

        dataset = BulkDataset(name, filepath)

        if dataset.load() and dataset.compute_senescence() is not None:
            dataset.save_outputs(f"{output_dir}/{name}")
            results[name] = 'SUCCESS'
        else:
            results[name] = 'FAILED'

    # Process scRNA tissue (GSE294496, GSE182825)
    scrna_tissue = {
        'GSE294496': f"{CONFIG['base_path']}GSE294496/",
        'GSE182825': f"{CONFIG['base_path']}GSE182825/GSE182825.h5ad",
    }

    for name, filepath in scrna_tissue.items():
        if not os.path.exists(filepath):
            logger.warning(f"Path not found: {filepath}")
            continue

        dataset = scRNADataset(name, filepath)

        if dataset.load() and dataset.process():
            dataset.save_outputs(f"{output_dir}/{name}")
            results[name] = 'SUCCESS'
        else:
            results[name] = 'FAILED'

    return results


def process_category_4_senescence():
    """Process senescence validation datasets"""
    logger.info("="*60)
    logger.info("CATEGORY 4: SENESCENCE VALIDATION")
    logger.info("="*60)

    bulk_datasets = {
        'GSE101766': 'GSE101766_series_matrix.txt.gz',
        'GSE226598': 'GSE226598_series_matrix.txt.gz',
        'GSE262856': 'GSE262856_series_matrix.txt.gz',
        'GSE297723': 'GSE297723_series_matrix.txt.gz',
    }

    output_dir = f"{CONFIG['output_path']}4_Senescence_Validation"
    results = {}

    # Bulk senescence datasets
    for name, filename in bulk_datasets.items():
        filepath = os.path.join(CONFIG['base_path'], name, filename)

        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            continue

        dataset = BulkDataset(name, filepath)

        if dataset.load() and dataset.compute_senescence() is not None:
            dataset.save_outputs(f"{output_dir}/{name}")
            results[name] = 'SUCCESS'
        else:
            results[name] = 'FAILED'

    # scRNA senescence (GSE157007)
    scrna_senescence = {
        'GSE157007': f"{CONFIG['base_path']}GSE157007/",
    }

    for name, filepath in scrna_senescence.items():
        if not os.path.exists(filepath):
            logger.warning(f"Path not found: {filepath}")
            continue

        dataset = scRNADataset(name, filepath)

        if dataset.load() and dataset.process():
            dataset.save_outputs(f"{output_dir}/{name}")
            results[name] = 'SUCCESS'
        else:
            results[name] = 'FAILED'

    return results


def main():
    """Execute full pipeline"""
    logger.info("START: Multi-Dataset Integration Pipeline")
    logger.info(f"Base path: {CONFIG['base_path']}")
    logger.info(f"Output path: {CONFIG['output_path']}")

    results = {
        'Category_1_Bulk': process_category_1_bulk(),
        'Category_2_scRNA': process_category_2_scrna(),
        'Category_3_Tissue': process_category_3_tissue(),
        'Category_4_Senescence': process_category_4_senescence(),
    }

    # Save results summary
    with open(f"{CONFIG['output_path']}/PIPELINE_RESULTS.json", 'w') as f:
        json.dump(results, f, indent=2)

    logger.info("="*60)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*60)
    for category, status in results.items():
        logger.info(f"{category}: {status}")

    logger.info("COMPLETE: All datasets processed")
    logger.info(f"Results saved to: {CONFIG['output_path']}")


if __name__ == '__main__':
    main()
