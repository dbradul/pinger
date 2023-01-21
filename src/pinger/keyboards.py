MSG_QUESTION_TEXT = 'Світло є?'
MSG_SUBSCRIBE_TEXT = 'Підписатись'
MSG_UNSUBSCRIBE_TEXT = 'Відписатись'
MSG_ADMIN_STATS_TEXT = '__!!~~##s_t_a_t_s_4_2'
MSG_ADMIN_MASK_TEXT = '__!!~~##m_a_s_k'
MSG_ADMIN_UNMASK_TEXT = '__!!~~##u_n_m_a_s_k'
MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_n_l_i_n_e__e_n_a_b_l_e'
MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_f_f_l_i_n_e__e_n_a_b_l_e'
MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_n_l_i_n_e__d_i_s_a_b_l_e'
MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_f_f_l_i_n_e__d_i_s_a_b_l_e'

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

KBRD_COLOR_NOT_PRESSED = "#000000"
KBRD_COLOR_PRESSED = "#AAAAAA"

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
        # "BgColor": KBRD_COLOR_NOT_PRESSED,
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
        # "BgColor": KBRD_COLOR_NOT_PRESSED,
        "TextSize": "large",
        "TextHAlign": "center",
        "TextVAlign": "center",
        "ActionType": "reply",
        "ActionBody": f'{MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT}',
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



def get_admin_keyboard(is_masked, forced_state=None):
    label, action = [KBRD_BTN_UNMASK_LABEL, MSG_ADMIN_UNMASK_TEXT] if is_masked \
               else [KBRD_BTN_MASK_LABEL,   MSG_ADMIN_MASK_TEXT]
    KBRD_BTN_MASK_UNMASK['Text'] = label
    KBRD_BTN_MASK_UNMASK['ActionBody'] = action
    KBRD_BTN_ADMIN[0] = KBRD_BTN_MASK_UNMASK

    if forced_state is None:
        KBRD_BTN_ADMIN[2]['Text'] = KBRD_BTN_FORCED_STATE_ONLINE_LABEL
        KBRD_BTN_ADMIN[2]['ActionBody'] = MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
        # KBRD_BTN_ADMIN[2]['BgColor'] = KBRD_COLOR_NOT_PRESSED
        KBRD_BTN_ADMIN[3]['Text'] = KBRD_BTN_FORCED_STATE_OFFLINE_LABEL
        KBRD_BTN_ADMIN[3]['ActionBody'] = MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
        # KBRD_BTN_ADMIN[3]['BgColor'] = KBRD_COLOR_NOT_PRESSED
    elif forced_state == True:
        KBRD_BTN_ADMIN[2]['Text'] = KBRD_BTN_FORCED_STATE_ONLINE_LABEL_DISABLE
        KBRD_BTN_ADMIN[2]['ActionBody'] = MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT
        # KBRD_BTN_ADMIN[2]['BgColor'] = KBRD_COLOR_PRESSED
        KBRD_BTN_ADMIN[3]['Text'] = KBRD_BTN_FORCED_STATE_OFFLINE_LABEL
        KBRD_BTN_ADMIN[3]['ActionBody'] = MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
        # KBRD_BTN_ADMIN[3]['BgColor'] = KBRD_COLOR_NOT_PRESSED
    elif forced_state == False:
        KBRD_BTN_ADMIN[2]['Text'] = KBRD_BTN_FORCED_STATE_ONLINE_LABEL
        KBRD_BTN_ADMIN[2]['ActionBody'] = MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
        # KBRD_BTN_ADMIN[2]['BgColor'] = KBRD_COLOR_NOT_PRESSED
        KBRD_BTN_ADMIN[3]['Text'] = KBRD_BTN_FORCED_STATE_OFFLINE_LABEL_DISABLE
        KBRD_BTN_ADMIN[3]['ActionBody'] = MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT
        # KBRD_BTN_ADMIN[3]['BgColor'] = KBRD_COLOR_PRESSED
    return KBRD_BTN_ADMIN
