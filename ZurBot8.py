import ZurBotClass
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import Db
from _thread import start_new_thread
import os
import sys

path = ""
bot = ZurBotClass.ZurBot()
db_bot = Db.BeerDb()
help_text = "Привет!Мне доступны команды:1. @zurbot цитген — делает цитату из вашего сообщения. Можно пересылать " \
            "несколько сообщений. Нельзя пересылать сообщения групп.2. @zurbot положить в холодильник %марка_пива% — " \
            "кладет в холодильник пиво заданной вами марки.3. @zurbot выпить пиво — вы пьете свой напиток. Больше " \
            "рейтинга начисляется за меньшую температуру пива. Доступно не чаще одного раза в день.4. @zurbot пиво — " \
            "охлаждает или нагревает ваше пиво. Доступно не чаще одного раза в день.5. @zurbot пивной рейтинг — " \
            "демонстрирует любителей пива конкретной беседы6. @zurbot выбросить пиво — уничтожает ваше пиво, " \
            "позволяет положить пиво новой марки. "
while True:
    for event in bot.get_longpoll().listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.object.peer_id == event.object.from_id:
                if bot.get_commands().get('citgen') == event.object['message']['text'].lower():
                    start_new_thread(bot.send_first_reply, (event,))
                    try:
                        start_new_thread(bot.make_and_send_quote, (event,))
                    except KeyError:
                        start_new_thread(bot.send_message,(event, 'Не вышло =('))
                elif bot.get_commands().get('beer_reg') in event.object['message']['text'].lower():
                    user = bot.get_user_by_id(event.object['message']['from_id'])
                    start_new_thread(bot.send_message, (event, db_bot.beer_reg(event.object['message']['peer_id'],
                                                                               event.object['message']['from_id'],
                                                                               event.object['message']['text'],
                                                                               user[0]['first_name'],
                                                                               user[0]['last_name'])), )
                elif bot.get_commands().get('beer_drink') == event.object['message']['text'].lower():
                    user = bot.get_user_by_id(event.object['message']['from_id'])
                    start_new_thread(bot.send_message, (event, db_bot.beer_drink(event.object['message']['peer_id'],
                                                                                 event.object['message']['from_id'],
                                                                                 user[0]['first_name'],
                                                                                 user[0]['last_name'])), )
                elif bot.get_commands().get('beer_change_t') == event.object['message']['text'].lower():
                    user = bot.get_user_by_id(event.object['message']['from_id'])
                    start_new_thread(bot.send_message, (event, db_bot.beer_change_t(event.object['message']['peer_id'],
                                                                                    event.object['message']['from_id'],
                                                                                    user[0]['first_name'],
                                                                                    user[0]['last_name'])), )
                elif bot.get_commands().get('beer_rating') == event.object['message']['text'].lower():
                    start_new_thread(bot.send_message, (event, db_bot.show_all(event.object['message']['peer_id']),))
                elif bot.get_commands().get('beer_delete') == event.object['message']['text'].lower():
                    start_new_thread(bot.send_message, (event, db_bot.beer_delete(event.object['message']['peer_id'],
                                                                                  event.object['message']['from_id']),))
                elif bot.get_commands().get('help') == event.object['message']['text'].lower():
                    start_new_thread(bot.send_message, (event, help_text,))
                elif "[club181977084|@zurbot" in event.object['message']['text'].lower():
                    start_new_thread(bot.send_message, (event, 'Я не понял команду. Введи @zurbot помощь',))
