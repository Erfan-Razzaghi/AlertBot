from dateutil import parser, tz
from datetime import datetime
from alertbot.schemas import AlertRequestPrometheus, AlertPrometheus
from utils.metrics import alertbot_templater_sms_alert_counter
import logging
from .templates import SMS_ALERT_TEMPLATES


class SMSTemplater:
    def __init__(self, alert_group: AlertRequestPrometheus, template: int = 0):
        self.messages = []
        self.template = template
        self.alert_group = alert_group
        self.alert_name = ""
        self.cluster_name = ""
        for alert in alert_group.alerts:
            self._add_alert_to_messages(alert)
            alertbot_templater_sms_alert_counter.labels(
                status=self.alert_group.status, 
                alertname=self.alert_name, 
                severity=self.alert_group.commonLabels.get("severity", "unknown").lower(),
                cluster=self.alert_group.commonLabels.get("cluster", "unknown").lower()
            ).inc()
        
    def _add_alert_to_messages(self, alert: AlertPrometheus):
        message = SMS_ALERT_TEMPLATES[self.template] # self.alert_group.commonLabels.get("cluster", "No Cluster!")
        message = message.replace("##STATUS##", self.alert_group.status.capitalize())

        self.alert_name = alert.labels.get("alertname", "No Alertname")
        message = message.replace("##ALERTNAME##", self.alert_name)

        self.cluster_name = alert.labels.get("cluster", "No Clustername")
        message = message.replace("##CLUSTER##", self.cluster_name)
        
        message = message.replace("##DESCRIPTION##", 
                alert.annotations.get("description", "NO DESCRIPTION!"))
        message = self._add_datetime(message, alert)

        self.messages.append(message)

    def _add_datetime(self, message, alert):
        if "firing" in alert.status.lower():
            UTC = parser.parse(alert.startsAt).strftime("%Y-%m-%d %H:%M:%S")
            correct_date = self._convert_date_time(UTC)
            message = message.replace("##DATETIME##", f"Started: {correct_date}")
        elif "resolved" in alert.status.lower():
            UTC = parser.parse(alert.endsAt).strftime("%Y-%m-%d %H:%M:%S")
            correct_date = self._convert_date_time(UTC)
            message = message.replace("##DATETIME##", f"Resolved: {correct_date}")
        return message

    def _convert_date_time(self, UTC):
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        return datetime.strptime(UTC, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
    
    def get_messages(self):
        return self.messages
    
    def get_alert_name(self):
        return self.alert_name
    
    def get_cluster_name(self):
        return self.cluster_name