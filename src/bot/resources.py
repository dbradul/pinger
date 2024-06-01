import copy

from telegram import ReplyKeyboardMarkup, KeyboardButton
from typing import Union

from bot import MessengerBot
from common.models import Contact


class Resource:
    MSG_QUESTION_TEXT = 'Світло є?'
    MSG_ADMIN_STATS_TEXT = '__!!~~##s_t_a_t_s_4_2'
    MSG_ADMIN_MASK_TEXT = '__!!~~##m_a_s_k'
    MSG_ADMIN_UNMASK_TEXT = '__!!~~##u_n_m_a_s_k'
    MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_n_l_i_n_e__e_n_a_b_l_e'
    MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_f_f_l_i_n_e__e_n_a_b_l_e'
    MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_n_l_i_n_e__d_i_s_a_b_l_e'
    MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT = '__!!~~##f_o_r_c_e_d__o_f_f_l_i_n_e__d_i_s_a_b_l_e'
    MSG_ADMIN_FORCED_RESEND_TEXT = '__!!~~##f_o_r_c_e_d__r_e_s_e_n_d'
    MSG_ADMIN_ADV_MESSAGE_TEXT = '__!!~~##a_d_v__m_e_s_s_a_g_e'
    MSG_SUBSCRIBE_TEXT = 'Підписатись'
    MSG_UNSUBSCRIBE_TEXT = 'Відписатись'

    def get_keyboard_(self, is_admin, is_subscribed, is_masked, is_forced_state):
        keyboard = self._get_common_keyboard(is_subscribed)
        if is_admin:
            self._add_admin_keyboard(keyboard, is_masked, is_forced_state)
        return keyboard

    def get_keyboard(self, contact: Union[None, Contact], messenger_bot: MessengerBot):
        keyboard = self._get_common_keyboard(contact and contact.active)
        if contact and contact.admin:
            self._add_admin_keyboard(keyboard, messenger_bot.masked, messenger_bot.forced_state)
        return keyboard

    def _get_common_keyboard(self, is_subscribed):
        raise NotImplementedError('_get_common_keyboard method is not implemented')

    def _add_admin_keyboard(self, keyboard, is_masked, is_forced_state):
        raise NotImplementedError('_add_admin_keyboard method is not implemented')


class ViberResource(Resource):
    MSG_QUESTION_TEXT = Resource.MSG_QUESTION_TEXT  #TODO: WTF?
    MSG_ADMIN_STATS_TEXT = Resource.MSG_ADMIN_STATS_TEXT
    MSG_ADMIN_MASK_TEXT = Resource.MSG_ADMIN_MASK_TEXT
    MSG_ADMIN_UNMASK_TEXT = Resource.MSG_ADMIN_UNMASK_TEXT
    MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT = Resource.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
    MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT = Resource.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
    MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT = Resource.MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT
    MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT = Resource.MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT
    MSG_ADMIN_FORCED_RESEND_TEXT = Resource.MSG_ADMIN_FORCED_RESEND_TEXT
    MSG_ADMIN_ADV_MESSAGE_TEXT = Resource.MSG_ADMIN_ADV_MESSAGE_TEXT
    MSG_SUBSCRIBE_TEXT = Resource.MSG_SUBSCRIBE_TEXT
    MSG_UNSUBSCRIBE_TEXT = Resource.MSG_UNSUBSCRIBE_TEXT

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
    KBRD_BTN_ADV_MESSAGE_LABEL = f"<font bold size=24 color=\"#000000\">SEND Adv.</font>"

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
        {
            "Columns": 6,
            "Rows": 1,
            "Text": f'{KBRD_BTN_ADV_MESSAGE_LABEL}',
            "TextSize": "large",
            "TextHAlign": "center",
            "TextVAlign": "center",
            "ActionType": "reply",
            "ActionBody": f'{MSG_ADMIN_ADV_MESSAGE_TEXT}',
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

    def _get_common_keyboard(self, is_subscribed):
        if is_subscribed:
            keyboard = self.KBRD_UNSUBSCRIBE
        else:
            keyboard = self.KBRD_SUBSCRIBE
        return copy.deepcopy(keyboard)

    def _add_admin_keyboard(self, keyboard, is_masked, is_forced_state):
        admin_keyboard = copy.deepcopy(self.KBRD_BTN_ADMIN)
        if is_masked:
            admin_keyboard[0]['Text'] = self.KBRD_BTN_UNMASK_LABEL
            admin_keyboard[0]['ActionBody'] = self.MSG_ADMIN_UNMASK_TEXT
        else:
            admin_keyboard[0]['Text'] = self.KBRD_BTN_MASK_LABEL
            admin_keyboard[0]['ActionBody'] = self.MSG_ADMIN_MASK_TEXT

        if is_forced_state is None:
            admin_keyboard[2]['Text'] = self.KBRD_BTN_FORCED_STATE_ONLINE_LABEL
            admin_keyboard[2]['ActionBody'] = self.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
            admin_keyboard[3]['Text'] = self.KBRD_BTN_FORCED_STATE_OFFLINE_LABEL
            admin_keyboard[3]['ActionBody'] = self.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
        elif is_forced_state is True:
            admin_keyboard[2]['Text'] = self.KBRD_BTN_FORCED_STATE_ONLINE_LABEL_DISABLE
            admin_keyboard[2]['ActionBody'] = self.MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT
            admin_keyboard[3]['Text'] = self.KBRD_BTN_FORCED_STATE_OFFLINE_LABEL
            admin_keyboard[3]['ActionBody'] = self.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT
        elif is_forced_state is False:
            admin_keyboard[2]['Text'] = self.KBRD_BTN_FORCED_STATE_ONLINE_LABEL
            admin_keyboard[2]['ActionBody'] = self.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT
            admin_keyboard[3]['Text'] = self.KBRD_BTN_FORCED_STATE_OFFLINE_LABEL_DISABLE
            admin_keyboard[3]['ActionBody'] = self.MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT

        keyboard['Buttons'].extend(admin_keyboard)
        return keyboard


class TelegramResource(Resource):
    MSG_SUBSCRIBE_TEXT = '🔔 Підписатись'
    MSG_UNSUBSCRIBE_TEXT = '🔕 Відписатись'
    MSG_ADMIN_STATS_TEXT = 'Stats...'
    MSG_ADMIN_MASK_TEXT = '🔕 Disable notif.'
    MSG_ADMIN_UNMASK_TEXT = '🔔 Enable notif.'
    MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT = 'Force ONLINE'
    MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT = 'Force OFFLINE'
    MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT = '❌UNForce ONLINE'
    MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT = '❌UNForce OFFLINE'
    MSG_ADMIN_FORCED_RESEND_TEXT = 'R_E_S_E_N_D'
    # MSG_ADMIN_ADV_MESSAGE_TEXT = 'SEND ADV'

    def _get_common_keyboard(self, is_subscribed):
        if is_subscribed:
            button_subscribe_text = self.MSG_UNSUBSCRIBE_TEXT
        else:
            button_subscribe_text = self.MSG_SUBSCRIBE_TEXT

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(button_subscribe_text),
                    KeyboardButton(self.MSG_QUESTION_TEXT)
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=False,
            is_persistent=True
        )
        return keyboard

    def _add_admin_keyboard(self, keyboard, is_masked, is_forced_state):
        admin_keyboard = [
            [
                KeyboardButton(self.MSG_ADMIN_MASK_TEXT),
                KeyboardButton(self.MSG_ADMIN_STATS_TEXT)
            ],
            [
                KeyboardButton(self.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT),
                KeyboardButton(self.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT)
            ],
            [
                KeyboardButton(self.MSG_ADMIN_FORCED_RESEND_TEXT)
            ],
            # [
            #     KeyboardButton(self.MSG_ADMIN_ADV_MESSAGE_TEXT)
            # ],
        ]
        if is_masked:
            admin_keyboard[0][0] = KeyboardButton(self.MSG_ADMIN_UNMASK_TEXT)
        else:
            admin_keyboard[0][0] = KeyboardButton(self.MSG_ADMIN_MASK_TEXT)

        if is_forced_state is None:
            admin_keyboard[1][0] = KeyboardButton(self.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT)
            admin_keyboard[1][1] = KeyboardButton(self.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT)
        elif is_forced_state is True:
            admin_keyboard[1][0] = KeyboardButton(self.MSG_ADMIN_FORCED_ONLINE_DISABLE_TEXT)
            admin_keyboard[1][1] = KeyboardButton(self.MSG_ADMIN_FORCED_OFFLINE_ENABLE_TEXT)
        elif is_forced_state is False:
            admin_keyboard[1][0] = KeyboardButton(self.MSG_ADMIN_FORCED_ONLINE_ENABLE_TEXT)
            admin_keyboard[1][1] = KeyboardButton(self.MSG_ADMIN_FORCED_OFFLINE_DISABLE_TEXT)

        keyboard.keyboard.extend(admin_keyboard)
        return keyboard
