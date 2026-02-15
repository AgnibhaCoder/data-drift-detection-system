import numpy as np
import pandas as pd
from scipy import stats
from loguru import logger

def calculate_ks_test(reference_col,production_col):
    ref=reference_col.dropna()
    prod=production_col.dropna()

    statistic,p_value=stats.ks_2samp(ref,prod)
    return statistic,p_value

def calculate_psi(ref_col,prod_col,buckets=10):
    def get_counts(series,all_categories):
        counts=series.value_counts(normalize=True).reindex(all_categories,fill_value=0)
        return counts.replace(0,0.0001)
    all_categories=list(set(ref_col.unique()) | set(prod_col.unique()))
    ref_percents=get_counts(ref_col,all_categories)
    prod_percents=get_counts(prod_col,all_categories)

    psi_values=(prod_percents-ref_percents)*np.log(prod_percents/ref_percents)
    total_psi=np.sum(psi_values)

    return total_psi

def detect_drift(ref_df,prod_df,config):
    results={}

    for feature in config['feature_to_monitor']:
        if feature not in ref_df.columns:
            logger.warning(f"{feature} missing from data")
            continue
        if pd.api.types.is_numeric_dtype(ref_df[feature]):
            stat,p_val=calculate_ks_test(ref_df[feature],prod_df[feature])
            is_drifted=p_val<config['thresholds']['ks_test']
            results[feature]={"metric":"ks_test","value":p_val,"drift":is_drifted}
        else:
            psi_val=calculate_psi(ref_df[feature],prod_df[feature])
            is_drifted=psi_val>config['thresholds']['psi']
            results[feature]={"metric":"PSI","value":psi_val,"drift":is_drifted}
    return results


        