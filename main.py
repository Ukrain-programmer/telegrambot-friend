import time
from datetime import datetime

import telebot
from telebot import types

from DbConnect import *
from configpars import config
import logging

TWO_BEER = "🍻"
BEER = "🍺"
FRIEND = "👬"
HELP = "📣"
BLOCK = "🔒"
UNBLOCK = "🔓"
MAIL = "📨"
DOWN = "⬇"
AIRPLANE_ATTACK = "❗️✈️"
ARTILLERY = "❗️💣"

bot = telebot.TeleBot('')  # config("config.ini", "token").get("token")

db = BdService()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s', )
log = logging.getLogger(__name__)


@bot.message_handler(commands=["message"])
def handle_admin_general_mailing(message):
    log.info("Start general mailing user - {}".format(message.chat.id))
    if not message.chat.id in db.get_admin_list():
        log.info("User {} have not permission".format(message.chat.id))
        bot.send_message(message.chat.id, "Таки команды может использовать только  ̶т̶в̶о̶й̶ батя")
        return

    bot.send_message(message.chat.id, "Что вы хотите сказать пользователям" + DOWN)
    bot.register_next_step_handler(message, general_mailing)
    log.info("General mailing by user - {} end".format(message.chat.id))


@bot.message_handler(commands=["offer" + MAIL])
def send_offer(message):
    log.info("Start user - {} offer ".format(message.chat.id))
    bot.send_message(message.chat.id, "Я выслушаю тебя животное, напиши что ты хочешь предложить" + DOWN)
    bot.register_next_step_handler(message, inform_admin_and_save_offer)
    log.info("End user - {} offer ".format(message.chat.id))


@bot.message_handler(commands=["help" + HELP])
def help(message):
    log.info("User {} call help".format(message.chat.id))
    bot.send_message(message.chat.id, """go_all_friend_toBeer🍻 - команда, которая рассылает всем вашим друзьям(👬) приглашение на распитие спертных напитков, в свою очередь друг может принять или отказатся, бот пришлет вам ответ\nall_friends👬 - команда, которая выводит всех пользователей бота. 
    👬 - пользователи с такой отметкой являються вашим другом.
    🔒 - пользователи с таким знаком  ̶п̶и̶д̶о̶р̶ы̶ вы не можете их приглашать в друзья 
block🔒 - команда которая блокирует и разблокирует Вас, если вы заблокированы то вас не могут добавить в друзья
offer📨 - отправить предложение или баг одмэну
artillery_attack❗️💣 - команда которая оповестит друзей об ударе артелерии (только тех пользователей которые у вас в друзьях👬)
airplane_attack❗️✈ - команда которая оповестит о приближении авиации (только тех пользователей которые у вас в друзьях👬)""")


@bot.message_handler(commands=["block" + BLOCK, "block" + UNBLOCK])
def block_user(message):
    if db.is_blocked_user(message.chat.id):
        log.info("User {} is unblocked ".format(message.chat.id))
        db.update_user_block(False, message.chat.id)
        bot.send_message(message.chat.id, UNBLOCK)
    else:
        db.update_user_block(True, message.chat.id)
        bot.send_message(message.chat.id, BLOCK)
        log.info("User {} is blocked ".format(message.chat.id))


@bot.message_handler(commands=["all_people" + FRIEND])
def all_user(message):
    log.info("User {} call all people".format(message.chat.id))
    markups = types.InlineKeyboardMarkup()
    userFriends = db.get_user_frienids(message.chat.id)
    for user in db.get_all_users():
        if user.id == message.chat.id:
            continue
        text = str(user.firstname) + " " + (str(user.lastname) if user.lastname is not None else "")
        if user in userFriends:
            text = text + FRIEND
        elif user.isBlock:
            text = text + BLOCK

        markups.add(types.InlineKeyboardButton(text, callback_data="friendship:" + str(user.id)))
    bot.send_message(message.chat.id, "Нажмите чтобы добавить поьзователя в друзья", reply_markup=markups)


@bot.callback_query_handler(func=lambda call: True)
def controller(call):
    if call.data.split(":")[0] == "friendship":
        friendship(call.message, call.data.split(":")[-1])
    if call.data.split(":")[0] == "+":
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, "Хороший выбор, Сэр")
        bot.send_message(call.data.split(":")[-1],
                         call.from_user.first_name + ": КОНЕЧНО, я что в крастной шапке" + TWO_BEER)
    if call.data.split(":")[0] == "-":
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, "Мда, не ожидал от тебя такого")
        bot.send_message(call.data.split(":")[-1], call.from_user.first_name + ": Я сегодня трезвиник")


@bot.message_handler(commands=["airplane_attack" + AIRPLANE_ATTACK])
def send_all_air_attack(message):
    send_message_to_user_friend(message.chat.id, message.chat.first_name + ": ВНИМАНИЕ ИСТРЕБИТЕЛИ " + AIRPLANE_ATTACK)


@bot.message_handler(commands=["artillery_attack" + ARTILLERY])
def send_all_art_attack(message):
    send_message_to_user_friend(message.chat.id, message.chat.first_name + ": ВНИМАНИЕ БОМБЯТ " + ARTILLERY)


@bot.message_handler(commands=["go_all_friend_toBeer" + BEER])
def send_all_beer(message):
    log.info("User {} call your friends to beer".format(message.chat.id))
    bot.send_message(message.chat.id, text="Пииивооо🚨")
    keyboard = types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton(text="+", callback_data="+:" + str(message.chat.id))) \
        .add(types.InlineKeyboardButton(text="-", callback_data="-:" + str(message.chat.id)))

    for user in db.get_user_frienids(message.chat.id):
        bot.send_message(user.id, "{}: Го пить пиво".format(message.from_user.first_name), reply_markup=keyboard)


@bot.message_handler(commands=["start"])
def start(message):
    down_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True) \
        .add(types.InlineKeyboardButton("/airplane_attack" + AIRPLANE_ATTACK)) \
        .add(types.InlineKeyboardButton("/artillery_attack" + ARTILLERY)) \
        .row(types.InlineKeyboardButton("/offer" + MAIL), types.InlineKeyboardButton("/all_people" + FRIEND)) \
        .row(types.InlineKeyboardButton("/block" + BLOCK), types.InlineKeyboardButton("/help" + HELP))

    flag = db.has_user_in_db(message.chat.id)
    if flag:
        bot.send_message(message.chat.id, "Привет мы с тобой уже виделись, сука")
        log.info("User peek start {}".format(message.chat.id))
    else:
        log.info("New user {}".format(message.chat.id))
        db.add_user(
            [message.chat.id, message.chat.first_name, message.chat.last_name,
             message.chat.username, None, False]
        )
        bot.send_message(message.chat.id, "Приятно познакомится {}".format(message.from_user.first_name))

    bot.send_message(message.chat.id, text="Можешь ознакомится с подсказками" + HELP, reply_markup=down_keyboard)
    # keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Вывести всех людей", callback_data=1))
    # bot.send_message(message.chat.id, text="Выбери таблетку. 'В твоем случае бутылку'", reply_markup=keyboard)


def send_message_to_user_friend(userId, message: str):
    for user in db.get_user_frienids(userId):
        bot.send_message(user.id, message)


def refresh_user_list(message):
    bot.delete_message(message.chat.id, message.id)
    all_user(message)


def get_user_keyboard():
    return types.ReplyKeyboardMarkup(resize_keyboard=True) \
        .add(types.InlineKeyboardButton("/airplane_attack" + AIRPLANE_ATTACK)) \
        .add(types.InlineKeyboardButton("/artillery_attack" + ARTILLERY)) \
        .row(types.InlineKeyboardButton("/offer" + MAIL), types.InlineKeyboardButton("/all_people" + FRIEND)) \
        .row(types.InlineKeyboardButton("/block" + BLOCK), types.InlineKeyboardButton("/help" + HELP))

def inform_admin_and_save_offer(message):
    db.add_offer(message.chat.id, message.text, datetime.fromtimestamp(message.date))
    log.info("Offer was added from user {}".format(message.chat.id))
    for adminId in db.get_admin_list():
        bot.send_message(adminId,
                         "Предложение от: {}({}) - {}".format(message.chat.first_name, message.chat.id, message.text))


def general_mailing(message):
    for user in db.get_all_users():
        bot.send_message(user.id, message.text, reply_markup=get_user_keyboard())


def friendship(message, friendId: int):
    has_friend = db.has_friend(message.chat.id, friendId)
    if db.is_blocked_user(friendId) and not has_friend:
        log.info("User {} try to peek {} but he is a block".format(message.chat.id, friendId))
        bot.send_message(message.chat.id, text="Нахуй иди, да ")
        return

    if has_friend:
        db.delete_friend([message.chat.id, friendId])
        log.info("User {} delete from friend {} ".format(message.chat.id, friendId))
        refresh_user_list(message)
    else:
        db.add_friend([message.chat.id, friendId])
        log.info("User {} add to friend {} ".format(message.chat.id, friendId))
        refresh_user_list(message)


def main():
    while True:
        try:
            log.info("Bot running..")
            bot.polling(none_stop=True, interval=2)
            break
        except Exception as e:
            log.error(e)
            bot.stop_polling()

            time.sleep(15)

            log.info("Running again!")


if __name__ == '__main__':
    main()
