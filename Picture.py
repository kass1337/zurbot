import textwrap
import urllib
from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlretrieve
import vk_api

path = ""


class PictureMono(object):
    __width = 640
    __height = 400
    __color_text = "#FFFFFF"
    __font = "arial.ttf"
    __img_path = path + "citgen.png"
    __font_title = ImageFont.truetype(__font, 48, encoding="unic")  # Цитаты великих дюдей
    __title_x = 30
    __title_y = 35
    __avatar_x = 20
    __avatar_y = 150
    __text_x = 240
    __text_y = 200
    __text_offset = 200
    __len_line = 30
    __title_text = "Цитаты великих людей"
    __font_sign = ImageFont.truetype(__font, 22, encoding="unic")  # Авторство

    def __init__(self, event, vk, font_size, height_offset, text):
        self.__event = event
        self.__vk = vk
        self.__height_offset = height_offset
        try:
            self.__author_id = text['from_id']
        except TypeError:
            self.__author_id = text[0]['from_id']
        try:
            self.__author = self.__vk.method("users.get", {"user_ids": self.__author_id,
                                                           "fields": ["first_name", "last_name", "photo_200_orig"],
                                                           "name_case": "nom"})
        except vk_api.exceptions.ApiError:
            return

        self.__font_quote = ImageFont.truetype(self.__font, font_size, encoding="unic")  # Авторство
        img = Image.new("RGBA", [self.__width, self.__height + self.__height_offset], (0, 0, 0))
        img_draw = ImageDraw.Draw(img)
        self.__build__title(img_draw)
        self.__build__avatar(img)
        self.__build__quote(img_draw, text)
        self.__build_author(img_draw)
        img.save(self.__img_path)

    def __build__title(self, img_draw):
        img_draw.text((self.__title_x, self.__title_y), self.__title_text,
                      font=self.__font_title, fill=self.__color_text)

    def __build__avatar(self, img):
        urllib.request.urlretrieve(self.__author[0]["photo_200_orig"],
                                   path + "ava.jpg")
        avatar = Image.open(path + "ava.jpg")
        img.paste(avatar, (self.__avatar_x, self.__avatar_y))

    def set_text_offset(self, offset):
        self.__text_offset = offset

    def __build__quote(self, img_draw, tx):
        if isinstance(tx, dict):
            msg = [tx]
        else:
            msg = tx
            self.__text_offset = 150
        msg[0]["text"] = '"' + msg[0]["text"]
        msg[len(msg) - 1]["text"] = msg[len(msg) - 1]["text"] + '"'
        for i in range(0, len(msg)):
            text = msg[i]["text"]
            if len(text) < self.__len_line:
                img_draw.text((self.__text_x, self.__text_offset), text, font=self.__font_quote, fill="#FFFFFF")
                self.__text_offset += self.__font_quote.getsize(text)[1] + 1
            else:
                for line in textwrap.wrap(text, width=33):
                    img_draw.text((self.__text_x, self.__text_offset), line, font=self.__font_quote, fill="#FFFFFF")
                    self.__text_offset += self.__font_quote.getsize(line)[1] + 4

    def __build_author(self, img_draw):
        name = "(ɔ)" + " " + self.__author[0]["first_name"] + " " + self.__author[0]["last_name"]
        img_draw.text((400 - len(name), self.__height + self.__height_offset - 40), name, font=self.__font_sign,
                      fill="#FFFFFF")

    def get_img_path(self):
        return self.__img_path


class PictureDuo(object):
    __width = 640
    __height = 400
    __color_text = "#FFFFFF"
    __font = "arial.ttf"
    __img_path = path + "citgen.png"
    __font_title = ImageFont.truetype(__font, 48, encoding="unic")  # Цитаты великих дюдей
    __title_x = 30
    __title_y = 35
    __avatar_x = 20
    __avatar_y = 150
    __text_x = 160
    __text_y = 200
    __text_offset = 170
    __len_line = 30
    __title_text = "Цитаты великих людей"
    __font_sign = ImageFont.truetype(__font, 22, encoding="unic")  # Авторство

    def __init__(self, event, vk, font_size, height_offset, text):
        self.__event = event
        self.__vk = vk
        self.__height_offset = height_offset

        self.__font_quote = ImageFont.truetype(self.__font, font_size, encoding="unic")  # Авторство
        img = Image.new("RGBA", [self.__width, self.__height + self.__height_offset], (0, 0, 0))
        img_draw = ImageDraw.Draw(img)
        self.__build__title(img_draw)
        self.__build__quote(img_draw, text, img)
        img.save(self.__img_path)

    def __build__title(self, img_draw):
        img_draw.text((self.__title_x, self.__title_y), self.__title_text,
                      font=self.__font_title, fill=self.__color_text)

    def set_text_offset(self, offset):
        self.__text_offset = offset

    def __build_text(self, text, img_draw):
        if len(text) < self.__len_line:
            img_draw.text((self.__text_x, self.__text_offset), text, font=self.__font_quote, fill="#FFFFFF")
            self.__text_offset += self.__font_quote.getsize(text)[1] + 1
        else:
            for line in textwrap.wrap(text, width=35):
                img_draw.text((self.__text_x, self.__text_offset), line, font=self.__font_quote, fill="#FFFFFF")
                self.__text_offset += self.__font_quote.getsize(line)[1] + 4

    def __build__quote(self, img_draw, tx, img):
        msg = tx
        processing_id = msg[0]['from_id']
        self.__build_author(img_draw, processing_id)
        self.__build__avatar(processing_id, img)
        for i in range(0, len(msg)):
            if processing_id != msg[i]['from_id']:
                self.__text_offset += 70
                processing_id = msg[i]['from_id']
                self.__build_author(img_draw, processing_id)
                self.__build__avatar(processing_id, img)
                self.__build_text(msg[i]["text"], img_draw)
            else:
                self.__build_text(msg[i]["text"], img_draw)

    def __build__avatar(self, processing_id, img):
        author = self.__vk.method("users.get", {"user_ids": processing_id,
                                                "fields": ["first_name", "last_name", "photo_50"],
                                                "name_case": "nom"})
        urllib.request.urlretrieve(author[0]["photo_50"],
                                   path + 'ava.jpg')
        avatar = Image.open(path + 'ava.jpg')
        img.paste(avatar, (self.__text_x - 60, self.__text_offset - 25))

    def __build_author(self, img_draw, processing_id):
        try:
            author = self.__vk.method("users.get", {"user_ids": processing_id,
                                                    "fields": ["first_name", "last_name", "photo_200_orig"],
                                                    "name_case": "nom"})
        except vk_api.exceptions.ApiError:
            return
        name = author[0]["first_name"] + " " + author[0]["last_name"]
        img_draw.text((self.__text_x, self.__text_offset - 25), name, font=self.__font_sign,
                      fill="#FFFFFF")

    def get_img_path(self):
        return self.__img_path
