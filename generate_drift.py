import pandas as pd
import numpy as np
import os

df=pd.read_csv('data/bank-direct-marketing-campaigns.csv')

df['age']=df['age']+10

df['euribor3m']=df['euribor3m']*0.5

df['job']='retired'

output_path='data/production_logs/drifted_batch.csv'
df.to_csv(output_path,index=False)
