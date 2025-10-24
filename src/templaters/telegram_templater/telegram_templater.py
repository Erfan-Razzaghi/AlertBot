from alertbot.schemas import AlertRequestPrometheus, \
    AlertPrometheus
from utils.metrics import alertbot_templater_telegram_alert_counter
from .exceptions import TemplateTelegramError
from .templates import SIGNS, UNKNOWN_SIGN, \
    FIRING_HEADERS_TEMPLATES, FIRING_BODY_TEMPLATE, \
    RESOLVED_HEADERS_TEMPLATES, RESOLVED_BODY_TEMPLATE
import logging

logger = logging.getLogger(__name__) 
class TelegramTemplater:
    def __init__(self,
                 alert_group: AlertRequestPrometheus,
                 template: int = 0):
        self.alert_group = alert_group
        self.alerts = self.alert_group.alerts
        self.template = template
        self.severity = self.alert_group.commonLabels["severity"].lower() # without severity we except to face an error!
        self.cluster = self.alert_group.commonLabels.get("cluster", "No Cluster!") # Without cluster we can work!
        self.message = ""

        self.generate_header()
        for alert in self.alerts:
            self.generate_body(alert)
            alertbot_templater_telegram_alert_counter.labels(
                status=self.alert_group.status.lower(), 
                alertname=self.alert_group.commonLabels.get("alertname","unknown").lower(), 
                severity=self.alert_group.commonLabels.get("severity", "unknown").lower(),
                cluster=self.alert_group.commonLabels.get("cluster", "unknown").lower()
            ).inc()
            
    def generate_header(self):
        if "firing" in self.alert_group.status.lower():
            self.message += SIGNS.get(self.severity, UNKNOWN_SIGN)
            self.message += FIRING_HEADERS_TEMPLATES[self.template]

        elif "resolved" in self.alert_group.status.lower():
            self.message += SIGNS.get("resolved", UNKNOWN_SIGN)
            self.message += RESOLVED_HEADERS_TEMPLATES[self.template]
        else:
            logger.error(f"{self.alert_group.status} was not recognized among valid alert status!")
            raise TemplateTelegramError()
        self.message = self.message.replace("##ALERTNAME##", 
                self.alert_group.commonLabels.get("alertname", "No alertname has been added for this alert!"))
        
        self.message = self.message.replace("##CLUSTER##", self.cluster)
        
        self.message = self.message.replace("##SUMMARY##", 
                self.alert_group.commonAnnotations.get("summary", "No summary has been added for this alert!"))
    
    def add_run_book(self,
                     alert: AlertPrometheus):
        runbook_url = alert.annotations.get("runbook_url", None)
        if runbook_url != None:
            self.message = self.message.replace("##RUNBOOK_URL##", \
            f"\n<a href=\"{alert.annotations.get('runbook_url')}\">Document</a>")

        else:
            self.message = self.message.replace("##RUNBOOK_URL##", "")

    def generate_body(self, 
                      alert: AlertPrometheus):
        if "firing" in alert.status.lower():
            self.message += FIRING_BODY_TEMPLATE[self.template]
        elif "resolved" in alert.status.lower():
            self.message += RESOLVED_BODY_TEMPLATE[self.template]
        else:
            logger.error(f"{alert.status} was not recognized among valid alert status!")
            raise TemplateTelegramError()
        
        self.message = self.message.replace("##DESCRIPTION##", 
                alert.annotations.get("description", "NO DESCRIPTION!"))
        
        self.add_run_book(alert)

    def get_message(self):
        return self.message
    
    def get_cluster(self):
        return self.cluster

    def get_severity(self):
        return self.severity