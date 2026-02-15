import requests
import json
from loguru import logger

def send_console_alert(feature,metric,value):
    logger.critical(
        f"DRIFT DETECED : {feature} | Metric: {metric} | Value: {value}"
    )
    
def send_slack_alert(drift_results,webhook_url):
    if not webhook_url or "hooks.slack.com" not in webhook_url:
        logger.warning("Slack webhook URL not configured.")
        return
    
    drifted_features={k: v for k,v in drift_results.items() if v['drift']}

    if not drifted_features:
        return
    
    message={
        "text":"Significant changes detected in production",
        "attachment":[
            {
                "color":"#ff0000",
                "fields":[
                    {
                        "title":f"feature {feature}",
                        "value":f"Metric: {res['metric']} | Value:{res['value']:.4f}",
                        "short":False
                    } for feature, res in drifted_features.items()
                ]
            }
        ]
    }

    try:
        response=requests.post(webhook_url,json=message)
        if response.status_code==200:
            logger.info("slack alert sent successfuly")
        else:
            logger.error(f"Slack API returned error {response.status_code}")
    except Exception as e:
        logger.error(f"failed to send slack alert:{e}")

def trigger_alerts(drift_results,config):
    for feature, res in drift_results.items():
        if res['drift']:
            send_console_alert(feature,res['metric'],res['value'])

    if config.get('slack_webhook'):
        send_slack_alert(drift_results,config['slack_webhook'])