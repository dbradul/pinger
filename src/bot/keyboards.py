from . texts import *

KBRD_BTN_SUBSCRIBE_LABEL = f"<font bold size=24 color=\"#000000\">{MSG_SUBSCRIBE_TEXT}</font>"
KBRD_BTN_UNSUBSCRIBE_LABEL = f"<font bold size=24 color=\"#000000\">{MSG_UNSUBSCRIBE_TEXT}</font>"
KBRD_BTN_QUESTION_LABEL = f"<font bold size=24>{MSG_QUESTION_TEXT}</font>"
KBRD_BTN_MASK_LABEL = f"<font bold size=24>🔕Disable notif.</font>"
KBRD_BTN_UNMASK_LABEL = f"<font bold size=24>🔔Enable notif.</font>"
KBRD_BTN_STATS_LABEL = f"<font bold size=24>Stats...</font>"
KBRD_BTN_FORCED_STATE_ONLINE_LABEL = f"<font bold size=24 color=\"#000000\">Force ONLINE</font>"
KBRD_BTN_FORCED_STATE_OFFLINE_LABEL = f"<font bold size=24 color=\"#000000\">Force OFFLINE</font>"
KBRD_BTN_FORCED_STATE_ONLINE_LABEL_DISABLE = f"<font bold size=24 color=\"#000000\">❌UNForce ONLINE</font>"
KBRD_BTN_FORCED_STATE_OFFLINE_LABEL_DISABLE = f"<font bold size=24 color=\"#000000\">❌UNForce OFFLINE</font>"
KBRD_BTN_RESEND_LABEL = f"<font bold size=24 color=\"#000000\">RESEND</font>"

KBRD_BTN_MASK_UNMASK = {
    "Columns": 3,
    "Rows": 1,
    "Text": '',
    "TextSize": "large",
    "TextHAlign": "center",
    "TextVAlign": "center",
    "ActionType": "reply",
    "ActionBody": '',
}
KBRD_BTN_ADMIN = [
    KBRD_BTN_MASK_UNMASK,
    {
        "Columns": 3,
        "Rows": 1,
        "Text": f'{KBRD_BTN_STATS_LABEL}',
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "center",
        "ActionType": "reply",
        "ActionBody": f'{MSG_ADMIN_STATS_TEXT}',
    },
    {
        "Columns": 3,
        "Rows": 1,
        "Text": f'{KBRD_BTN_STATS_LABEL}',
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "center",
        "ActionType": "reply",
        "ActionBody": f'{MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT}',
    },
    {
        "Columns": 3,
        "Rows": 1,
        "Text": f'{KBRD_BTN_STATS_LABEL}',
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "center",
        "ActionType": "reply",
        "ActionBody": f'{MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT}',
    },
    {
        "Columns": 6,
        "Rows": 1,
        "Text": f'{KBRD_BTN_RESEND_LABEL}',
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "center",
        "ActionType": "reply",
        "ActionBody": f'{MSG_ADMIN_FORCED_RESEND_TEXT}',
    },
]


KBRD_SUBSCRIBE = {
    "Type": "keyboard",
    "InputFieldState": "hidden",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "Text": KBRD_BTN_SUBSCRIBE_LABEL,
            "BgColor": "#BCE29E",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_SUBSCRIBE_TEXT
        },
        {
            "Columns": 3,
            "Rows": 1,
            "Text": KBRD_BTN_QUESTION_LABEL,
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_QUESTION_TEXT,
            # "Silent": "true"
            # "BgColor": "#f7bb3f",
            # "Image": "https: //s12.postimg.org/ti4alty19/smoke.png"
        }
    ]
}

KBRD_UNSUBSCRIBE = {
    "Type": "keyboard",
    "InputFieldState": "hidden",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            "Text": KBRD_BTN_UNSUBSCRIBE_LABEL,
            "BgColor": "#F7A4A4",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_UNSUBSCRIBE_TEXT
        },
        {
            "Columns": 3,
            "Rows": 1,
            "Text": KBRD_BTN_QUESTION_LABEL,
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_QUESTION_TEXT
        },
    ]
}


