# SMS Routing System Documentation

## Overview

This document describes the SMS routing architecture for our alerting system, which provides automated SMS notifications for critical incidents across multiple production environments.

## System Architecture Diagram

![SMS Routing Flow](./sms-chart.png)

## System Architecture

The SMS routing system consists of multiple production clusters that feed into a centralized management platform for alert processing and SMS delivery.

### Production Clusters

Our system monitors many main production environments here with 3 examples:

#### 1. Prod-companyapp2 Cluster
- **Team**: companyapp2
- **Severity**: critical
- **Receiver**: `prod-companyapp2-critical-sre`

#### 2. Prod-companyapp1 Cluster  
- **Team**: companyapp1
- **Severity**: critical
- **Receiver**: `prod-companyapp1-critical-sre-asset`

#### 3. Prod-companyapp3 Cluster 
- **Team**: companyapp3
- **Severity**: critical
- **Receiver**: `prod-companyapp3-critical-sre`

### Alert Flow Process

#### Step 1: Incident Detection
When an incident occurs in any production cluster:
1. The Kubernetes cluster detects the incident
2. Prometheus scrapes metrics and evaluates PromQL alert expressions
3. When alert conditions are met, Prometheus generates alerts

#### Step 2: Alert Management
1. Prometheus sends alerts to AlertManager
2. AlertManager processes the alerts with team-specific configurations
3. AlertManager routes alerts to the appropriate receivers based on team and severity

#### Step 3: SMS Processing Pipeline

The core SMS routing happens in the **SourceCluster** cluster through a series of microservices:

##### 3.1 Alertbot-v2 API Deployment
- **Role**: Central alert processing service
- **Function**: Receives alerts from all AlertManager instances
- **Input**: Alert with receiver information (e.g., `prod-companyapp2-critical-sre`)
- **Action**: Initiates the phone number lookup process

##### 3.2 Phone-Sync API
- **Role**: Phone number management and caching service
- **Primary Functions**:
  - Receives API requests for phone numbers based on receiver groups
  - Manages phone number caching for performance
  - Interfaces with keycloak api

##### 3.3 Keycloak Deployment
- **Role**: Identity and user management service
- **Function**: 
  - Stores user group mappings
  - Provides user credentials and phone numbers for specific groups
  - Returns authorized contact information for alert receivers

##### 3.4 Redis Cache
- **Role**: High-performance caching layer
- **Function**:
  - Stores frequently accessed phone numbers
  - Reduces lookup time for repeated alerts
  - Improves system performance and reduces external API calls

#### Step 4: SMS Delivery

##### SMS Gateway (Kavenegar Integration)
- **Provider**: Kavenegar SMS service
- **Function**: Delivers SMS messages to end users
- **Input**: Phone numbers and alert message content

## Detailed Workflow

### Complete SMS Routing Process

1. **Incident Occurrence**: A critical issue is detected in one of the production clusters

2. **Alert Generation**: Prometheus evaluates PromQL expressions and triggers alerts when thresholds are exceeded

3. **Alert Processing**: AlertManager receives the alert and routes it to Alertbot-v2 with the appropriate receiver identifier

4. **Phone Number Lookup**: 
   - Alertbot-v2 requests phone numbers from Phone-Sync API for the given receiver
   - Phone-Sync first checks Redis cache for cached phone numbers
   - If cache miss occurs, Phone-Sync queries Keycloak for group membership and phone numbers

5. **User Resolution**:
   - Keycloak returns user credentials and phone numbers for the specified group
   - Phone-Sync caches the results in Redis for future use
   - Phone-Sync responds to Alertbot-v2 with the phone numbers

6. **SMS Delivery**: Alertbot-v2 sends SMS messages via Kavenegar SMS Gateway to all resolved phone numbers

## Key Features

### Performance Optimization
- **Redis Caching**: Reduces lookup latency for frequently accessed phone numbers
- **Efficient API Design**: Minimizes external service calls through intelligent caching

### Scalability
- **Multi-Cluster Support**: Handles alerts from multiple production environments
- **Team-Based Routing**: Supports different teams with dedicated alert receivers

### Reliability
- **Centralized Management**: Single point of control in SourceCluster cluster
- **Redundant Systems**: Multiple production clusters ensure high availability

### Security
- **Keycloak Integration**: Secure user authentication and authorization
- **Group-Based Access**: Phone numbers are only accessible to authorized groups

## Configuration

### Receiver Mapping
- `prod-companyapp2-critical-sre` → companyapp2 team critical alerts
- `prod-companyapp1-critical-sre-asset` → companyapp1 team critical alerts  
- `prod-companyapp3-critical-sre` → companyapp3 team critical alerts

### Alert Severity
All SMS notifications are currently configured for **critical** severity alerts only.

### SMS Provider
The system uses **Kavenegar** as the SMS gateway provider for reliable message delivery.
