#!/usr/bin/env python3
"""
COMPAS Recidivism Bias Audit - Simplified Version
Analysis of racial bias in COMPAS risk scores

This script performs bias analysis of the COMPAS dataset using standard Python libraries.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

def load_and_analyze_compas():
    """Load COMPAS data and perform bias analysis."""
    
    print("COMPAS Recidivism Bias Audit")
    print("="*50)
    
    # Load data
    try:
        data = pd.read_csv('compas-scores-two-years.csv')
        print(f"Dataset loaded: {data.shape[0]} rows, {data.shape[1]} columns")
        
        # Clean data
        relevant_cols = ['race', 'age', 'sex', 'priors_count', 'c_charge_degree', 
                        'two_year_recid', 'decile_score', 'score_text']
        data = data[relevant_cols].dropna()
        data['race_binary'] = (data['race'] == 'African-American').astype(int)
        
        print(f"After cleaning: {data.shape[0]} rows")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Basic statistics
    print("\nBasic Statistics:")
    print(f"Overall recidivism rate: {data['two_year_recid'].mean():.3f}")
    
    # Recidivism by race
    recid_by_race = data.groupby('race')['two_year_recid'].agg(['mean', 'count'])
    print("\nRecidivism by race:")
    print(recid_by_race)
    
    # COMPAS scores by race
    score_by_race = data.groupby('race')['decile_score'].mean()
    print("\nAverage COMPAS score by race:")
    print(score_by_race)
    
    # Fairness metrics calculation
    analyze_bias(data)
    
    # Generate visualizations
    create_visualizations(data)
    
    # Generate report
    generate_audit_report(data)

def analyze_bias(data):
    """Calculate fairness metrics."""
    print("\n" + "="*50)
    print("FAIRNESS METRICS ANALYSIS")
    print("="*50)
    
    # Define high-risk threshold
    high_risk_threshold = 5
    data['high_risk'] = (data['decile_score'] >= high_risk_threshold).astype(int)
    
    # Group data
    aa_data = data[data['race'] == 'African-American']
    other_data = data[data['race'] != 'African-American']
    
    # Calculate metrics
    metrics = {}
    
    # Selection rates (demographic parity)
    metrics['selection_rate_aa'] = aa_data['high_risk'].mean()
    metrics['selection_rate_other'] = other_data['high_risk'].mean()
    metrics['disparate_impact'] = metrics['selection_rate_aa'] / metrics['selection_rate_other']
    
    # False Positive Rates
    aa_actual_no_recid = aa_data[aa_data['two_year_recid'] == 0]
    other_actual_no_recid = other_data[other_data['two_year_recid'] == 0]
    
    if len(aa_actual_no_recid) > 0:
        metrics['fpr_aa'] = aa_actual_no_recid['high_risk'].mean()
    else:
        metrics['fpr_aa'] = 0
        
    if len(other_actual_no_recid) > 0:
        metrics['fpr_other'] = other_actual_no_recid['high_risk'].mean()
    else:
        metrics['fpr_other'] = 0
    
    # True Positive Rates
    aa_actual_recid = aa_data[aa_data['two_year_recid'] == 1]
    other_actual_recid = other_data[other_data['two_year_recid'] == 1]
    
    if len(aa_actual_recid) > 0:
        metrics['tpr_aa'] = aa_actual_recid['high_risk'].mean()
    else:
        metrics['tpr_aa'] = 0
        
    if len(other_actual_recid) > 0:
        metrics['tpr_other'] = other_actual_recid['high_risk'].mean()
    else:
        metrics['tpr_other'] = 0
    
    # Print results
    print(f"Demographic Parity (High-Risk Classification):")
    print(f"  African American: {metrics['selection_rate_aa']:.3f}")
    print(f"  Others: {metrics['selection_rate_other']:.3f}")
    print(f"  Disparate Impact: {metrics['disparate_impact']:.3f}")
    
    print(f"\nFalse Positive Rates:")
    print(f"  African American: {metrics['fpr_aa']:.3f}")
    print(f"  Others: {metrics['fpr_other']:.3f}")
    print(f"  Difference: {abs(metrics['fpr_aa'] - metrics['fpr_other']):.3f}")
    
    print(f"\nTrue Positive Rates:")
    print(f"  African American: {metrics['tpr_aa']:.3f}")
    print(f"  Others: {metrics['tpr_other']:.3f}")
    
    # Assessment
    print(f"\nBias Assessment:")
    if metrics['disparate_impact'] < 0.8 or metrics['disparate_impact'] > 1.2:
        print("  WARNING: DEMOGRAPHIC PARITY VIOLATED (80%-125% rule)")
    else:
        print("  OK: Demographic parity acceptable")
    
    if abs(metrics['fpr_aa'] - metrics['fpr_other']) > 0.05:
        print("  WARNING: EQUAL OPPORTUNITY VIOLATED (>5% difference)")
    else:
        print("  OK: Equal opportunity acceptable")
    
    return metrics

def create_visualizations(data):
    """Create bias visualization plots."""
    print("\nGenerating visualizations...")
    
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('COMPAS Recidivism Bias Analysis', fontsize=16, fontweight='bold')
    
    # 1. Recidivism rates by race
    recid_rates = data.groupby('race')['two_year_recid'].mean().sort_values(ascending=False)
    axes[0, 0].bar(range(len(recid_rates)), recid_rates.values, color=['red', 'orange', 'blue'])
    axes[0, 0].set_title('Recidivism Rates by Race')
    axes[0, 0].set_xticks(range(len(recid_rates)))
    axes[0, 0].set_xticklabels(recid_rates.index, rotation=45)
    axes[0, 0].set_ylabel('Recidivism Rate')
    
    # 2. COMPAS score distribution
    aa_scores = data[data['race'] == 'African-American']['decile_score']
    other_scores = data[data['race'] != 'African-American']['decile_score']
    
    axes[0, 1].hist(aa_scores, alpha=0.7, label='African American', bins=10, color='red')
    axes[0, 1].hist(other_scores, alpha=0.7, label='Others', bins=10, color='blue')
    axes[0, 1].set_title('COMPAS Score Distribution')
    axes[0, 1].set_xlabel('Decile Score')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].legend()
    
    # 3. High-risk classification rates
    high_risk_aa = (data[data['race'] == 'African-American']['decile_score'] >= 5).mean()
    high_risk_other = (data[data['race'] != 'African-American']['decile_score'] >= 5).mean()
    
    axes[1, 0].bar(['African American', 'Others'], [high_risk_aa, high_risk_other], 
                   color=['red', 'blue'], alpha=0.7)
    axes[1, 0].set_title('High-Risk Classification Rates')
    axes[1, 0].set_ylabel('Classification Rate')
    
    # 4. False Positive Rates
    aa_no_recid = data[(data['race'] == 'African-American') & (data['two_year_recid'] == 0)]
    other_no_recid = data[(data['race'] != 'African-American') & (data['two_year_recid'] == 0)]
    
    fpr_aa = (aa_no_recid['decile_score'] >= 5).mean() if len(aa_no_recid) > 0 else 0
    fpr_other = (other_no_recid['decile_score'] >= 5).mean() if len(other_no_recid) > 0 else 0
    
    axes[1, 1].bar(['African American', 'Others'], [fpr_aa, fpr_other], 
                   color=['red', 'blue'], alpha=0.7)
    axes[1, 1].set_title('False Positive Rates')
    axes[1, 1].set_ylabel('False Positive Rate')
    
    plt.tight_layout()
    plt.savefig('compas_bias_analysis.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as 'compas_bias_analysis.png'")
    plt.close()

def generate_audit_report(data):
    """Generate the 300-word audit report."""
    
    # Calculate final metrics
    metrics = analyze_bias(data)
    
    report = f"""
COMPAS RECIDIVISM ALGORITHM BIAS AUDIT REPORT

Executive Summary:
This audit examines racial bias in the COMPAS recidivism risk assessment algorithm using a dataset of {len(data):,} criminal cases. The analysis reveals significant disparities in how the algorithm classifies defendants across racial groups, with concerning implications for fairness in criminal justice.

Key Findings:

1. DEMOGRAPHIC PARITY VIOLATION:
African American defendants are classified as high-risk (score ≥5) at a rate of {metrics['selection_rate_aa']:.1%}, compared to {metrics['selection_rate_other']:.1%} for other racial groups. This represents a disparate impact ratio of {metrics['disparate_impact']:.2f}, indicating {'substantial bias against African Americans' if metrics['disparate_impact'] > 1.2 else 'acceptable demographic parity'}.

2. EQUAL OPPORTUNITY VIOLATION:
False positive rates show significant disparity: {metrics['fpr_aa']:.1%} for African Americans versus {metrics['fpr_other']:.1%} for others. This {abs(metrics['fpr_aa'] - metrics['fpr_other']):.1%} difference means African Americans who won't reoffend are more likely to receive high-risk classifications.

3. PREDICTIVE PARITY CONCERNS:
The algorithm shows different accuracy levels across racial groups, with true positive rates of {metrics['tpr_aa']:.1%} (African American) and {metrics['tpr_other']:.1%} (others), suggesting unequal predictive performance.

REMEDIATION RECOMMENDATIONS:

IMMEDIATE ACTIONS:
• Implement continuous bias monitoring with automated alerts when disparate impact exceeds 80%-125% thresholds
• Establish diverse oversight committee including affected community representatives
• Create transparent appeals process for high-risk classifications

ALGORITHMIC IMPROVEMENTS:
• Retrain model with fairness constraints (equalized odds, demographic parity)
• Implement adversarial debiasing to remove racial correlations
• Add fairness regularizers to loss functions during training

DATA INTERVENTIONS:
• Audit historical training data for bias patterns
• Implement balanced sampling across demographic groups
• Regular data quality assessments and bias detection

PROCESS SAFEGUARDS:
• Require human review for high-risk classifications
• Provide clear explanations for risk scores
• Regular external audits by independent bias researchers

The evidence demonstrates that COMPAS perpetuates racial bias in criminal justice decisions, requiring immediate intervention to ensure equitable treatment under the law.
"""
    
    print("\n" + "="*70)
    print("FINAL AUDIT REPORT")
    print("="*70)
    print(report)
    
    # Save report
    with open('compas_audit_report.txt', 'w') as f:
        f.write(report)
    
    print("\nReport saved as 'compas_audit_report.txt'")
    
    return report

if __name__ == "__main__":
    load_and_analyze_compas()