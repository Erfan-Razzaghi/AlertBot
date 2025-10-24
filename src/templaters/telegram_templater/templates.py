
UNKNOWN_SIGN = "❓ "
SIGNS = {
    "critical": "‼️ ",
    "warning": "⚠️ ",
    "resolved": "✅ ",
    "disaster": "🔥 ",
    "info": "📢 "
}

FIRING_HEADERS_TEMPLATES = \
[
"""<b>##ALERTNAME##</b>

<b><i>Cluster:</i> ##CLUSTER## </b>
<b><i>Summary:</i> ##SUMMARY## </b>

"""
]

FIRING_BODY_TEMPLATE = \
[
"""🔴 ##DESCRIPTION## ##RUNBOOK_URL##

"""
]

RESOLVED_HEADERS_TEMPLATES = \
[
"""<s><b>##ALERTNAME##</b></s>

<i>Summary:</i> ##SUMMARY##

"""
]

RESOLVED_BODY_TEMPLATE = \
[
"""🟢 ##DESCRIPTION## ##RUNBOOK_URL##

"""
]