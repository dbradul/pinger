MSG_QUESTION_TEXT = 'Світло є?'
MSG_SUBSCRIBE_TEXT = 'Підписатись'
MSG_UNSUBSCRIBE_TEXT = 'Відписатись'

KBRD_BTN_SUBSCRIBE_LABEL = f"<font bold size=24>{MSG_SUBSCRIBE_TEXT}</font>"
KBRD_BTN_UNSUBSCRIBE_LABEL = f"<font bold size=24>{MSG_UNSUBSCRIBE_TEXT}</font>"
KBRD_BTN_QUESTION_LABEL = f"<font bold size=24>{MSG_QUESTION_TEXT}</font>"

KBRD_SUBSCRIBE = {
    "Type": "keyboard",
    "InputFieldState": "hidden",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            # "Text": "<font bold size=24 color=\"#494E67\">Світло є?</font>",
            "Text": KBRD_BTN_SUBSCRIBE_LABEL,
            # "Text": "Світло є?",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_SUBSCRIBE_TEXT,
            # "Silent": "true"
            # "BgColor": "#f7bb3f",
            # "Image": "https: //s12.postimg.org/ti4alty19/smoke.png"
        },
        {
            "Columns": 3,
            "Rows": 1,
            # "Text": "<font bold size=24 color=\"#494E67\">Світло є?</font>",
            "Text": KBRD_BTN_QUESTION_LABEL,
            # "Text": "Світло є?",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_QUESTION_TEXT,
            # "Silent": "true"
            # "BgColor": "#f7bb3f",
            # "Image": "https: //s12.postimg.org/ti4alty19/smoke.png"
        },
    ]
}

KBRD_UNSUBSCRIBE = {
    "Type": "keyboard",
    "InputFieldState": "hidden",
    "Buttons": [
        {
            "Columns": 3,
            "Rows": 1,
            # "Text": "<font bold size=24 color=\"#494E67\">Світло є?</font>",
            "Text": KBRD_BTN_UNSUBSCRIBE_LABEL,
            # "Text": "Світло є?",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_UNSUBSCRIBE_TEXT,
            # "Silent": "true"
            # "BgColor": "#f7bb3f",
            # "Image": "https: //s12.postimg.org/ti4alty19/smoke.png"
        },
        {
            "Columns": 3,
            "Rows": 1,
            # "Text": "<font bold size=24 color=\"#494E67\">Світло є?</font>",
            "Text": KBRD_BTN_QUESTION_LABEL,
            # "Text": "Світло є?",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": MSG_QUESTION_TEXT,
            # "Silent": "true"
            # "BgColor": "#f7bb3f",
            # "Image": "https: //s12.postimg.org/ti4alty19/smoke.png"
        },
    ]
}
