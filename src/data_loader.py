import pandas as pd
from loguru import logger

def load_data(path):
    df=pd.read_csv(path)
    logger.info(f"successfully loaded {path} with {len(df)} rows")
    return df

def preprocess_for_drift(df):
    df=df.copy()

    if 'pdays' in df.columns:
        df['pdays']=df['pdays'].replace(999,-1)
    
    cat_cols=df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df[col]=df[col].astype(str).str.strip().str.lower()
    return df

def get_reference_and_production_batch(ref_path,prod_path):
    ref_raw=load_data(ref_path)
    prod_raw=load_data(prod_path)

    if ref_raw is not None and prod_raw is not None:
        return preprocess_for_drift(ref_raw),preprocess_for_drift(prod_raw)
    return None,None
