MSG_QUESTION_TEXT = 'Світло є?'
MSG_SUBSCRIBE_TEXT = 'Підписатись'
MSG_UNSUBSCRIBE_TEXT = 'Відписатись'
MSG_ADMIN_STATS_TEXT = '__!!~~##s_t_a_t_s_4_2'
MSG_ADMIN_MASK_TEXT = '__!!~~##m_a_s_k'
MSG_ADMIN_UNMASK_TEXT = '__!!~~##u_n_m_a_s_k'

KBRD_BTN_SUBSCRIBE_LABEL = f"<font bold size=24 color=\"#000000\">{MSG_SUBSCRIBE_TEXT}</font>"
KBRD_BTN_UNSUBSCRIBE_LABEL = f"<font bold size=24 color=\"#000000\">{MSG_UNSUBSCRIBE_TEXT}</font>"
KBRD_BTN_QUESTION_LABEL = f"<font bold size=24>{MSG_QUESTION_TEXT}</font>"
KBRD_BTN_MASK_LABEL = f"<font bold size=24>🔕Disable notif.</font>"
KBRD_BTN_UNMASK_LABEL = f"<font bold size=24>🔔Enable notif.</font>"
KBRD_BTN_STATS_LABEL = f"<font bold size=24>Stats...</font>"

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
    {},
    {
        "Columns": 3,
        "Rows": 1,
        "Text": f'{KBRD_BTN_STATS_LABEL}',
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "center",
        "ActionType": "reply",
        "ActionBody": f'{MSG_ADMIN_STATS_TEXT}',
    }
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


