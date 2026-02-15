import yaml
import os
import json
from datetime import datetime
from loguru import logger

from src.data_loader import get_reference_and_production_batch
from src.drift_detectors import detect_drift
from src.alerts import trigger_alerts

def main():
    logger.info("Starting data drift detection system")

    try:
        with open("config.yaml","r") as f:
            config=yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("file not found")
        return

    ref_path=config['paths']['reference_data']

    prod_files=sorted(os.listdir(config['paths']['production_dir']))

    if not prod_files:
        logger.error("No production found")
        return
    prod_path=os.path.join(config['paths']['production_dir'],prod_files[-1])
    ref_df,prod_df=get_reference_and_production_batch(ref_path,prod_path)

    if ref_df is None or prod_df is None:
        logger.error("data loading failed")
        return
    drift_results=detect_drift(ref_df,prod_df,config)
    timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename=f"report_{timestamp}.json"
    report_path=os.path.join(config['paths']['report_output'],report_filename)

    with open(report_path,"w") as f:
        json.dump(drift_results,f,indent=4,default=str)
    
    logger.info(f"report saved to {report_path}")
    trigger_alerts(drift_results,config)
    logger.info("Drift check cycle complete")

if __name__=="__main__":
    main()

