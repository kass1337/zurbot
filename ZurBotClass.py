import random
import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import Picture
import os
import sys

def __read_bot_token__():
    token_file = open(os.path.join(sys.path[0], 'key.txt'), 'r')
    group_id_file = open(os.path.join(sys.path[0], 'group.txt'), 'r')
    data = [token_file.read(), group_id_file.read()]
    token_file.close()
    group_id_file.close()
    return data


class ZurBot(object):
    obj = None  # единственный экземпляр класса

    def __new__(cls, *args, **kwargs):
        if cls.obj is None:
            cls.obj = object.__new__(cls, *args, **kwargs)
        return cls.obj

    def __api_authorize__(self):
        vk = vk_api.VkApi(token=self.__token)
        vk._auth_token()
        vk.get_api()
        longpoll = VkBotLongPoll(vk, self.__group_id)
        api_data = [vk, longpoll]
        return api_data

    def __init__(self):
        group_data = __read_bot_token__()
        self.__token = group_data[0]
        self.__group_id = group_data[1]
        api_data = self.__api_authorize__()
        self.__vk = api_data[0]
        self.__longpoll = api_data[1]
        del group_data
        del api_data

    @staticmethod
    def get_commands():
        return {'citgen': '[club181977084|@zurbot] цитген',
                'beer_change_t': '[club181977084|@zurbot] пиво',
                'beer_rating': '[club181977084|@zurbot] пивной рейтинг',
                'beer_drink': '[club181977084|@zurbot] выпить пиво',
                'beer_reg': '[club181977084|@zurbot] положить в холодильник',
                'beer_delete': '[club181977084|@zurbot] выбросить пиво',
                'help': '[club181977084|@zurbot] помощь'}

    def get_longpoll(self):
        return self.__longpoll

    def get_user_by_id(self, from_id):
        return self.__vk.method("users.get", {"user_ids": from_id,
                                              "fields": ["first_name", "last_name"],
                                              "name_case": "nom"})

    def send_first_reply(self, event):
        self.__vk.method("messages.send", {"peer_id": event.object['message']['peer_id'], "message": "уно моменто",
                                           "random_id": random.getrandbits(64)})

    def send_message(self, event, text, **kwargs):
        if kwargs:
            self.__vk.method("messages.send", {"peer_id": event.object['message']['peer_id'], "message": text,
                                               "attachment": kwargs.get("attachment"),
                                               "random_id": random.getrandbits(64)})
        else:
            self.__vk.method("messages.send", {"peer_id": event.object['message']['peer_id'], "message": text,
                                               "random_id": random.getrandbits(64)})

    def __send_cit_to_db(self, text, attachment):
        self.__vk.method("messages.send", {"peer_id": 535145600, "message": text,
                                           "attachment": attachment,
                                           "random_id": random.getrandbits(64)})

    def make_and_send_quote(self, event):
        global pic
        default_font_size = 20
        default_height_offset = 100
        text_len = 0
        if event.object['message']['fwd_messages']:
            msg = event.object['message']['fwd_messages']
            temp_id = msg[0]['from_id']
            solo_cit = True
            for i in range(0, len(msg)):
                text_len += len(msg[i]['text'])
                if temp_id != msg[i]['from_id']:
                    solo_cit = False
            if solo_cit:
                pic = Picture.PictureMono(event, self.__vk, default_font_size,
                                          int(default_height_offset + (text_len / 30) * 23),
                                          msg)
            else:
                pic = Picture.PictureDuo(event, self.__vk, default_font_size,
                                         int(default_height_offset + len(msg) * 10),
                                         msg)
        else:
            msg = event.object['message']['reply_message']
            pic = Picture.PictureMono(event, self.__vk, default_font_size,
                                      int(default_height_offset + (len(msg["text"]) / 30) * 23),
                                      msg)

        if isinstance(pic, Picture.PictureMono) or isinstance(pic, Picture.PictureDuo):
            path_to_pic = pic.get_img_path()
            pic_file = open(path_to_pic, "rb")
            upload_server = self.__vk.method("photos.getMessagesUploadServer", {"group_id": self.__group_id})
            uri = requests.post(upload_server["upload_url"], files={"photo": pic_file}).json()
            attachment = self.__vk.method("photos.saveMessagesPhoto",
                                          {"photo": uri["photo"], "server": uri["server"],
                                           "hash": uri["hash"]})
            attachment_vk_url = "photo" + str(attachment[0]["owner_id"]) + "_" + str(attachment[0]["id"])
            self.send_message(event, "на", attachment=attachment_vk_url)
            self.__send_cit_to_db('#chat' + str(event.object['message']['peer_id'] - 2000000000) + '\n',
                                  attachment_vk_url)
