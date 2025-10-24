from prometheus_client  import Counter, Gauge

alertbot_keycloak_group_members = Gauge(
    name='alertbot_keycloak_group_members',
    documentation='showing the number of member in keycloak groups that alertbot uses',
    labelnames=['group_name'] 
)

alertbot_sent_sms_per_number_counter = Counter(
    name='alertbot_sent_sms_per_number',
    documentation='Number of time alertbot tried to send alert to a number',
    labelnames=['group_name','cluster', 'number']
)

alertbot_sent_sms_per_cluster_counter = Counter(
    name='alertbot_sent_sms_per_cluster',
    documentation='Number of time alertbot tried to send alert to the keycloak group',
    labelnames=['group_name','cluster']
)

alertbot_failed_sent_sms_per_cluster_counter = Counter(
    name='alertbot_failed_sent_sms_per_cluster',
    documentation='Number of time alertbot failed to send alert to the keycloak group',
    labelnames=['group_name','cluster']
)

alertbot_sent_telegram_per_receiver_counter = Counter(
    name='alertbot_sent_telegram_per_receiver',
    documentation='Number of telegram messages sent by Alertbot',
    labelnames=['cluster', 'severity', 'receiver']
)

alertbot_failed_sent_telegram_per_receiver_counter = Counter(
    name='alertbot_failed_sent_telegram_per_receiver',
    documentation='Number of telegram messages sent by Alertbot',
    labelnames=['cluster', 'severity', 'receiver']
)

alertbot_templater_sms_alert_counter = Counter(
    name="alertbot_templater_sms_alert",
    documentation='Number of times each alertname is being used to be sent to sms',
    labelnames=["status", "alertname", "cluster", "severity"]
)


alertbot_templater_telegram_alert_counter = Counter(
    name="alertbot_templater_telegram_alert",
    documentation='Number of times each alertname is being used to be sent to telegram',
    labelnames=["status", "alertname", "cluster", "severity"]
)

api_call_status_count = Counter(name="api_call_status_count",
                                documentation="number of times other apis have been called and the status code received",
                                labelnames=("destination", "status_code", "method"))