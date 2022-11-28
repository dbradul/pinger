MSG_QUESTION_TEXT = 'Світло є?'
KBRD_CHECK_LIGHT = {
    "Type": "keyboard",
    "InputFieldState": "hidden",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        # "Text": "<font bold size=24 color=\"#494E67\">Світло є?</font>",
        "Text": f"<font bold size=24>{MSG_QUESTION_TEXT}</font>",
        # "Text": "Світло є?",
        "TextSize": "medium",
        "TextHAlign": "center",
        "TextVAlign": "center",
        "ActionType": "reply",
        "ActionBody": "Electricity",
        # "Silent": "true"
        # "BgColor": "#f7bb3f",
        # "Image": "https: //s12.postimg.org/ti4alty19/smoke.png"
    }]
}
