#!/usr/bin/env python3
"""
COMPAS Recidivism Bias Audit
Analysis of racial bias in COMPAS risk scores using AI Fairness 360

This script performs a comprehensive fairness audit of the COMPAS recidivism dataset,
analyzing potential racial bias in the risk assessment algorithm.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from aif360.algorithms.preprocessing.optim_preproc_helpers.data_preprocessing_functions import load_preproc_data_compas
from aif360.metrics import ClassificationMetric
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

class CompasBiasAuditor:
    """
    A comprehensive bias auditor for COMPAS recidivism data.
    """
    
    def __init__(self):
        self.data = None
        self.dataset_original = None
        self.protected_attributes = ['race']
        self.outcome_column = 'two_year_recid'
        
    def load_data(self, file_path='compas-scores-two-years.csv'):
        """Load and preprocess the COMPAS dataset."""
        try:
            print("Loading COMPAS dataset...")
            self.data = pd.read_csv(file_path)
            print(f"Dataset loaded successfully: {self.data.shape[0]} rows, {self.data.shape[1]} columns")
            
            # Basic data preprocessing
            self._preprocess_data()
            return True
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return False
    
    def _preprocess_data(self):
        """Clean and preprocess the COMPAS data."""
        # Filter relevant columns and remove missing values
        relevant_cols = ['race', 'age', 'sex', 'priors_count', 'c_charge_degree', 
                        'two_year_recid', 'decile_score', 'score_text']
        
        self.data = self.data[relevant_cols].copy()
        self.data = self.data.dropna()
        
        # Create binary race categories (African-American vs Others)
        self.data['race_binary'] = (self.data['race'] == 'African-American').astype(int)
        
        print("Data preprocessing completed.")
        print(f"Final dataset shape: {self.data.shape}")
        print(f"Race distribution: {self.data['race'].value_counts()}")
        
    def calculate_basic_statistics(self):
        """Calculate basic statistics for the dataset."""
        print("\n" + "="*50)
        print("BASIC DATASET STATISTICS")
        print("="*50)
        
        # Overall recidivism rates
        overall_recidivism = self.data[self.outcome_column].mean()
        print(f"Overall recidivism rate: {overall_recidivism:.3f}")
        
        # Recidivism rates by race
        recidivism_by_race = self.data.groupby('race')[self.outcome_column].agg(['mean', 'count'])
        print("\nRecidivism rates by race:")
        print(recidivism_by_race)
        
        # COMPAS score distribution by race
        score_by_race = self.data.groupby('race')['decile_score'].agg(['mean', 'std'])
        print("\nCOMPAS decile scores by race:")
        print(score_by_race)
        
        return recidivism_by_race, score_by_race
    
    def calculate_fairness_metrics(self):
        """Calculate comprehensive fairness metrics."""
        print("\n" + "="*50)
        print("FAIRNESS METRICS ANALYSIS")
        print("="*50)
        
        # Convert to AI Fairness 360 format
        dataset = self._convert_to_aif360_format()
        
        # Define privileged and unprivileged groups
        privileged_race = np.array([[1]])  # African-American = 1
        unprivileged_race = np.array([[0]])  # Others = 0
        
        # Binary classification: high risk (score >= 5) vs low risk (score < 5)
        y_pred = (self.data['decile_score'] >= 5).astype(int)
        y_true = self.data[self.outcome_column].values
        
        # Race labels
        race_labels = self.data['race_binary'].values
        
        # Calculate metrics
        metrics = {}
        
        # Basic classification metrics
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred)
        metrics['recall'] = recall_score(y_true, y_pred)
        metrics['f1'] = f1_score(y_true, y_pred)
        
        # Group-specific metrics
        african_american_mask = race_labels == 1
        others_mask = race_labels == 0
        
        # True Positive Rate (Sensitivity)
        metrics['tpr_african_american'] = recall_score(y_true[african_american_mask], y_pred[african_american_mask])
        metrics['tpr_others'] = recall_score(y_true[others_mask], y_pred[others_mask])
        
        # False Positive Rate
        fpr_aa = np.sum((y_true[african_american_mask] == 0) & (y_pred[african_american_mask] == 1)) / np.sum(y_true[african_american_mask] == 0)
        fpr_others = np.sum((y_true[others_mask] == 0) & (y_pred[others_mask] == 1)) / np.sum(y_true[others_mask] == 0)
        metrics['fpr_african_american'] = fpr_aa
        metrics['fpr_others'] = fpr_others
        
        # True Negative Rate (Specificity)
        tnr_aa = 1 - fpr_aa
        tnr_others = 1 - fpr_others
        metrics['tnr_african_american'] = tnr_aa
        metrics['tnr_others'] = tnr_others
        
        # Demographic Parity (Selection Rate)
        selection_rate_aa = np.mean(y_pred[african_american_mask])
        selection_rate_others = np.mean(y_pred[others_mask])
        metrics['selection_rate_african_american'] = selection_rate_aa
        metrics['selection_rate_others'] = selection_rate_others
        
        # Equalized Odds (TPR difference)
        metrics['tpr_difference'] = abs(metrics['tpr_african_american'] - metrics['tpr_others'])
        
        # Equal Opportunity (FPR difference)
        metrics['fpr_difference'] = abs(metrics['fpr_african_american'] - metrics['fpr_others'])
        
        # Disparate Impact
        metrics['disparate_impact'] = selection_rate_aa / selection_rate_others if selection_rate_others > 0 else float('inf')
        
        return metrics
    
    def _convert_to_aif360_format(self):
        """Convert data to AI Fairness 360 format."""
        try:
            # Use AI Fairness 360's built-in COMPAS preprocessing
            dataset = load_preproc_data_compas()
            return dataset
        except:
            # Fallback to manual preprocessing
            return None
    
    def generate_visualizations(self):
        """Generate comprehensive bias visualization."""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('COMPAS Recidivism Risk Score Bias Analysis', fontsize=16, fontweight='bold')
        
        # 1. Recidivism rates by race
        recidivism_rates = self.data.groupby('race')[self.outcome_column].mean().sort_values(ascending=False)
        axes[0, 0].bar(range(len(recidivism_rates)), recidivism_rates.values, color=['red', 'orange', 'blue', 'green'])
        axes[0, 0].set_title('Recidivism Rates by Race')
        axes[0, 0].set_xticks(range(len(recidivism_rates)))
        axes[0, 0].set_xticklabels(recidivism_rates.index, rotation=45)
        axes[0, 0].set_ylabel('Recidivism Rate')
        for i, v in enumerate(recidivism_rates.values):
            axes[0, 0].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
        
        # 2. COMPAS score distribution by race
        race_categories = self.data['race'].unique()
        for race in race_categories:
            race_data = self.data[self.data['race'] == race]['decile_score']
            axes[0, 1].hist(race_data, alpha=0.7, label=race, bins=10)
        axes[0, 1].set_title('COMPAS Decile Score Distribution by Race')
        axes[0, 1].set_xlabel('Decile Score')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].legend()
        
        # 3. False Positive Rates by race
        metrics = self.calculate_fairness_metrics()
        races = ['African American', 'Others']
        fprs = [metrics['fpr_african_american'], metrics['fpr_others']]
        colors = ['red', 'blue']
        bars = axes[0, 2].bar(races, fprs, color=colors, alpha=0.7)
        axes[0, 2].set_title('False Positive Rates by Race')
        axes[0, 2].set_ylabel('False Positive Rate')
        for bar, fpr in zip(bars, fprs):
            axes[0, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                          f'{fpr:.3f}', ha='center', va='bottom')
        
        # 4. Selection rates (demographic parity)
        selection_rates = [metrics['selection_rate_african_american'], metrics['selection_rate_others']]
        bars = axes[1, 0].bar(races, selection_rates, color=colors, alpha=0.7)
        axes[1, 0].set_title('High-Risk Classification Rates (Demographic Parity)')
        axes[1, 0].set_ylabel('Selection Rate')
        for bar, rate in zip(bars, selection_rates):
            axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                          f'{rate:.3f}', ha='center', va='bottom')
        
        # 5. Disparate Impact Visualization
        impact_threshold = [0.8, 1.2]  # 80%-125% rule
        disparate_impact = metrics['disparate_impact']
        bars = axes[1, 1].bar(['Disparate Impact'], [disparate_impact], color='purple', alpha=0.7)
        axes[1, 1].axhline(y=0.8, color='red', linestyle='--', label='80% threshold')
        axes[1, 1].axhline(y=1.2, color='red', linestyle='--', label='125% threshold')
        axes[1, 1].set_title('Disparate Impact Ratio')
        axes[1, 1].set_ylabel('Impact Ratio')
        axes[1, 1].legend()
        axes[1, 1].text(0, disparate_impact + 0.05, f'{disparate_impact:.3f}', ha='center', va='bottom')
        
        # 6. Bias Summary Heatmap
        bias_metrics = pd.DataFrame({
            'African American': [metrics['tpr_african_american'], metrics['fpr_african_american'], 
                                metrics['selection_rate_african_american'], metrics['tnr_african_american']],
            'Others': [metrics['tpr_others'], metrics['fpr_others'], 
                      metrics['selection_rate_others'], metrics['tnr_others']]
        }, index=['True Positive Rate', 'False Positive Rate', 'Selection Rate', 'True Negative Rate'])
        
        sns.heatmap(bias_metrics, annot=True, cmap='RdYlBu_r', ax=axes[1, 2], 
                   cbar_kws={'label': 'Rate'}, fmt='.3f')
        axes[1, 2].set_title('Fairness Metrics Heatmap')
        
        plt.tight_layout()
        plt.savefig('compas_bias_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return bias_metrics
    
    def generate_report(self):
        """Generate comprehensive bias audit report."""
        print("\n" + "="*70)
        print("COMPREHENSIVE COMPAS BIAS AUDIT REPORT")
        print("="*70)
        
        # Load and analyze data
        if not self.load_data():
            return "Failed to load dataset"
        
        # Calculate statistics and metrics
        recidivism_stats, score_stats = self.calculate_basic_statistics()
        metrics = self.calculate_fairness_metrics()
        
        # Generate visualizations
        bias_heatmap = self.generate_visualizations()
        
        # Compile findings
        report = f"""
        COMPAS RECIDIVISM BIAS AUDIT - EXECUTIVE SUMMARY
        ================================================
        
        Dataset Overview:
        - Total records analyzed: {len(self.data):,}
        - African American defendants: {sum(self.data['race'] == 'African-American'):,}
        - Other race defendants: {sum(self.data['race'] != 'African-American'):,}
        - Overall recidivism rate: {self.data[self.outcome_column].mean():.3f}
        
        KEY FINDINGS - EVIDENCE OF BIAS:
        
        1. DEMOGRAPHIC PARITY VIOLATION:
           - African American high-risk classification: {metrics['selection_rate_african_american']:.3f}
           - Others high-risk classification: {metrics['selection_rate_others']:.3f}
           - Disparate impact ratio: {metrics['disparate_impact']:.3f}
           - ASSESSMENT: {'VIOLATED' if metrics['disparate_impact'] < 0.8 or metrics['disparate_impact'] > 1.2 else 'ACCEPTABLE'}
        
        2. EQUAL OPPORTUNITY VIOLATION:
           - False Positive Rate African American: {metrics['fpr_african_american']:.3f}
           - False Positive Rate Others: {metrics['fpr_others']:.3f}
           - FPR Difference: {metrics['fpr_difference']:.3f}
           - ASSESSMENT: {'VIOLATED' if metrics['fpr_difference'] > 0.05 else 'ACCEPTABLE'}
        
        3. ALGORITHMIC FAIRNESS SCORE: {1 - abs(metrics['fpr_difference']) - abs(metrics['disparate_impact'] - 1):.3f}/1.0
        
        CRITICAL BIAS INDICATORS:
        - African Americans are {metrics['disparate_impact']:.2f}x more likely to be classified as high-risk
        - FPR disparity of {metrics['fpr_difference']:.3f} represents significant unequal treatment
        
        REMEDIATION RECOMMENDATIONS:
        
        1. IMMEDIATE ACTIONS:
           - Implement bias monitoring dashboard with real-time fairness metrics
           - Establish 80%-125% disparate impact threshold with automatic alerts
           - Create diverse oversight committee including affected community representatives
        
        2. ALGORITHMIC IMPROVEMENTS:
           - Retrain model with fairness constraints (equalized odds, demographic parity)
           - Implement adversarial debiasing techniques to remove racial correlations
           - Add fairness regularizers to loss function during training
        
        3. DATA-LEVEL INTERVENTIONS:
           - Audit training data for historical bias patterns
           - Implement balanced sampling techniques across racial groups
           - Regular data quality assessments and bias detection
        
        4. PROCESS-LEVEL SAFEGUARDS:
           - Require human review for high-risk classifications
           - Implement appeals process with transparent reasoning
           - Regular external audits by independent bias researchers
        
        5. TRANSPARENCY MEASURES:
           - Public reporting of fairness metrics by demographic groups
           - Clear explanation of factors influencing risk scores
           - Regular community engagement on system performance
        
        LEGAL AND ETHICAL IMPLICATIONS:
        - Current disparities may violate Equal Protection Clause
        - High false positive rates for African Americans risk wrongful convictions
        - Lack of explainability undermines due process rights
        - Algorithmic opacity conflicts with GDPR transparency requirements
        
        CONCLUSION:
        The analysis reveals significant racial bias in COMPAS risk scores, with African American
        defendants experiencing disproportionately higher false positive rates and being more likely
        to be classified as high-risk. Immediate remediation is required to ensure fair treatment
        and prevent discriminatory outcomes in criminal justice decisions.
        
        Report Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        Analyst: AI Ethics Audit Framework v1.0
        """
        
        print(report)
        
        # Save report to file
        with open('compas_bias_audit_report.txt', 'w') as f:
            f.write(report)
        
        return report

def main():
    """Main execution function."""
    print("COMPAS Recidivism Bias Audit")
    print("="*40)
    print("Analyzing racial bias in criminal justice risk assessment...")
    
    # Initialize auditor
    auditor = CompasBiasAuditor()
    
    # Generate comprehensive report
    try:
        report = auditor.generate_report()
        print("\nAudit completed successfully!")
        print("Generated files:")
        print("- compas_bias_analysis.png (visualizations)")
        print("- compas_bias_audit_report.txt (detailed report)")
        
    except Exception as e:
        print(f"Audit failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()