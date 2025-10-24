# Telegram Route Chart Documentation

This document describes the Telegram alert routing flow visualization contained in `telegram-route-chart.html`.


## Overview
The `telegram-route-chart.html` file contains an interactive Mermaid.js flowchart that visualizes how alerts flow from various Kubernetes clusters through Prometheus and AlertManager to the AlertBot v2 system and finally to Telegram notifications.


## System Architecture Diagram

![Telegram Routing Flow](./telegram-chart.png)

## Chart Components

### Source Clusters
The chart shows three production Kubernetes clusters as alert sources:

1. **Prod-companyapp2** - Generates alerts with team: companyapp2, severity: critical
2. **Prod-companyapp1** - Generates alerts with team: companyapp1, severity: critical  
3. **Prod-companyapp3** - Generates alerts with team: companyapp3, severity: warning

### Alert Processing Flow
1. **Incident Detection**: Each cluster detects incidents
2. **Prometheus Monitoring**: Prometheus instances monitor cluster health
3. **Alert Generation**: PromQL alerts are triggered with specific team and severity labels
4. **AlertManager**: Routes alerts to appropriate receivers based on configuration

### AlertBot v2 Processing
The chart shows the AlertBot v2 system in the SourceCluster cluster with two key components:

- **AlertBot v2 API Deployment**: Main application processing incoming webhooks
- **alertbot-config.json**: Configuration file mapping receivers to Telegram groups

### Telegram Delivery
The final step shows delivery to Telegram via:
1. Configuration lookup to find the appropriate Telegram group for each receiver
2. Message delivery using the AlertBot to the Telegram API

## Receivers Shown
- `prod-companyapp2-critical-sre`
- `prod-companyapp1-critical-sre-asset` 
- `prod-companyapp3-warning-sre`
