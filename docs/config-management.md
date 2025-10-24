# AlertBot Configuration Guide

## ⚠️ IMPORTANT WARNING

**AlertBot has an automatic config reloader that runs every 3 minutes!**

- Configuration changes will be automatically picked up within 3 minutes
- **DO NOT restart the AlertBot pods manually** after making configuration changes
- The config reloader will detect changes and reload the configuration automatically

## 🏗️ Configuration Structure

The configuration file contains a `destinations` array where each destination defines:
- **receiver**: A unique identifier following the naming convention
- **severity**: The alert severity level this destination handles
- **types**: An array of notification methods (telegram, sms, or both)

## 🏷️ Receiver Naming Convention

Receivers must follow this format: `{environment}-{product}-{severity}-{target team}`

### Format Components:
- **environment**: `stage` or `prod`
- **product**: `companyapp4`, `companyapp3`, `companyapp2`, etc.
- **severity**: `info`, `warning`, `critical`, `disaster`
- **target team**: `sre-companyapp2`, `portfo`, `sandogh`, `companyapp2-business`, etc. (sre-companyapp2 is considered default now for sre and you may or may not specify dev keyword. for example companyapp2 or companyapp2-dev is considered the same.)

### Examples:
- `prod-companyapp2-critical-sre`
- `stage-companyapp3-warning-sre`
- `prod-companyapp2-critical-portfo-business`

## 🚨 Severity Levels

The following severity levels are supported:
- `info` - Informational alerts
- `warning` - Warning level alerts
- `critical` - Critical alerts requiring immediate attention
- `disaster` - Disaster level alerts (highest priority)

## 📢 Notification Types

### 1. 📱 Telegram Type

#### Required Keys:
- `type`: Must be `"telegram"`
- `telegram_group_id`: The Telegram group/channel ID (string, usually negative number)

#### Optional Keys:
- `telegram_topic_id`: The topic ID within the group (string, for groups with topics enabled)

#### Examples:

**Basic Telegram notification:**
```json
{
    "type": "telegram",
    "telegram_group_id": "-1002149533880"
}
```

**Telegram notification with topic:**
```json
{
    "type": "telegram",
    "telegram_group_id": "-1002515868145",
    "telegram_topic_id": "13"
}
```

### 2. 📧 SMS Type

#### Required Keys:
- `type`: Must be `"sms"`
- `keycloak_group_name`: The Keycloak group name that defines SMS recipients

#### Optional Keys:
- `sender`: The SMS sender number (string)

#### Examples:

**Basic SMS notification:**
```json
{
    "type": "sms",
    "keycloak_group_name": "sre-team"
}
```

**SMS notification with custom sender:**
```json
{
    "type": "sms",
    "sender": "2000008700",
    "keycloak_group_name": "prod-companyapp2-critical-sandogh"
}
```

## ➕ Adding a New Destination

To add a new destination, follow these steps:

### 1. Determine the Configuration
- Choose the appropriate receiver name following the naming convention
- Select the severity level
- Decide which notification types are needed (telegram, sms, or both)

### 2. Create the Destination Object

```json
{
    "receiver": "your-receiver-name",
    "severity": "your-severity-level",
    "types": [
        {
            "type": "telegram",
            "telegram_group_id": "your-group-id",
            "telegram_topic_id": "your-topic-id"  // optional
        },
        {
            "type": "sms",
            "sender": "your-sender-number",  // optional
            "keycloak_group_name": "your-keycloak-group"
        }
    ]
}
```

### 3. Add to Configuration
Add your new destination object to the `destinations` array in the `alertbot-config.json` file.

## 💡 Complete Example

Here's a complete example adding a new destination for production companyapp2 platform business critical alerts:

```json
{
    "receiver": "prod-companyapp2-critical-business-new",
    "severity": "critical",
    "types": [
        {
            "type": "telegram",
            "telegram_group_id": "-1002515868145",
            "telegram_topic_id": "25"
        },
        {
            "type": "sms",
            "sender": "2000008700",
            "keycloak_group_name": "prod-companyapp2-critical-business-new"
        }
    ]
}
```

## 📝 Important Notes

1. **Receiver names must be unique** across all destinations
2. **Telegram group IDs** are usually negative numbers and should be strings
3. **Topic IDs** are only needed for Telegram groups with topics enabled
4. **SMS sender numbers** are optional but recommended for consistency
5. **Keycloak group names** must match existing groups in your Keycloak instance
6. **JSON syntax** must be valid - pay attention to commas, brackets, and quotes
7. **Test thoroughly** after adding new destinations to ensure alerts are delivered correctly

## ✅ Validation Checklist

Before deploying changes:
- [ ] Receiver name follows the naming convention
- [ ] Severity level is valid (info, warning, critical, disaster)
- [ ] All required keys are present for each notification type
- [ ] JSON syntax is valid
- [ ] Telegram group IDs and topic IDs are correct
- [ ] Keycloak group names exist and are accessible
- [ ] SMS sender number is valid (if specified)
