import sqlite3
import random
import datetime
from ZurBotClass import ZurBot
import pathlib

path = ""


class BeerDb:

    def __init__(self):
        self.__db = sqlite3.connect(path + 'bot.db')
        self.__beer_db = self.__db.cursor()
        self.__default_beer_t = 20
        self.__max_beer_t = 40
        self.__min_beer_t = 0

    def beer_reg(self, chat_id, from_id, text, first_name, surname):
        chat_name = self.__update_table(chat_id)
        beer_name = text.replace(ZurBot.get_commands().get('beer_reg') + ' ', '')
        self.__beer_db.execute(
            f'CREATE TABLE IF NOT EXISTS"{chat_name}"(id INT, first_name TEXT, surname TEXT, tem INT, time BIGINT, beer_name TEXT, score FLOAT)')
        if self.__beer_db.execute(f'SELECT id FROM "{chat_name}" WHERE id = "{from_id}"').fetchone() is None:
            info = (
                from_id, first_name, surname, self.__default_beer_t,
                datetime.datetime.toordinal(datetime.datetime.now()),
                beer_name, 0.0)
            self.__beer_db.execute(f'INSERT INTO "{chat_name}" VALUES (?,?,?,?,?,?,?)', info)
            self.__db.commit()
            return 'Теперь у пользователя по имени ' + first_name + ' ' + surname + ' в холодильнике пиво марки ' + beer_name + ' температурой ' + str(
                self.__default_beer_t) + '°'
        else:
            return 'У тебя уже есть пиво в холодильнике'

    def beer_drink(self, chat_id, from_id, first_name, surname):
        if not self.__check_date(chat_id, from_id):
            return self.__beer_time_break()
        chat_name = self.__update_table(chat_id)
        try:
            self.__beer_db.execute(f'SELECT id FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()
        except sqlite3.OperationalError:
            return 'В холодильнике этого чата нет пива'
        if self.__beer_db.execute(f'SELECT id FROM "{chat_name}" WHERE id = "{from_id}"').fetchone() is None:
            return 'У тебя в холодильнике нет пива.'
        else:
            beer_name = \
                self.__beer_db.execute(f'SELECT beer_name FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()[0]
            tem = self.__beer_db.execute(f'SELECT tem FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()[0]
            old_score = self.__beer_db.execute(f'SELECT score FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()[0]
            score = self.__max_beer_t / tem + old_score
            self.__beer_db.execute(
                f'UPDATE "{chat_name}" SET tem = "{self.__default_beer_t}", score = "{score}", time = "{datetime.datetime.toordinal(datetime.datetime.now())}" WHERE id = "{from_id}"')
            self.__db.commit()
            return first_name + ' ' + surname + ' пьет ' + beer_name + '!\n' + 'Теперь пиво пользователя ' + str(
                self.__default_beer_t) + '°\n Рейтинг — ' + str(score)

    def beer_change_t(self, chat_id, from_id, first_name, surname):
        chat_name = self.__update_table(chat_id)
        try:
            self.__beer_db.execute(f'SELECT id FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()
        except sqlite3.OperationalError:
            return 'В холодильнике этого чата нет пива'
        if self.__beer_db.execute(f'SELECT id FROM "{chat_name}" WHERE id = "{from_id}"').fetchone() is None:
            return 'У тебя в холодильнике нет пива.'
        if not self.__check_date(chat_id, from_id):
            return self.__beer_time_break()
        temp_beer = self.__beer_db.execute(f'SELECT tem FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()[0]
        rand_beer = random.randint(-5, 3)
        new_beer = temp_beer + rand_beer
        if new_beer > self.__max_beer_t or rand_beer == 0 or new_beer < self.__min_beer_t:
            return self.__break_beer(chat_id, from_id)
        else:
            beer_name = \
                self.__beer_db.execute(f'SELECT beer_name FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()[0]
            self.__beer_db.execute(
                f'UPDATE "{chat_name}"  SET tem = "{new_beer}", time = "{datetime.datetime.toordinal(datetime.datetime.now())}" WHERE id = "{from_id}";')
            self.__db.commit()
            return 'Пиво пользователя ' + first_name + ' ' + surname + ' сменило температуру на ' + str(
                rand_beer) + '°\n' + 'Теперь его ' + beer_name + ' ' + str(new_beer) + '°!'

    def beer_delete(self, chat_id, from_id):
        chat_name = self.__update_table(chat_id)
        try:
            self.__beer_db.execute(f'SELECT id FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()
        except sqlite3.OperationalError:
            return 'В холодильнике этого чата нет пива'
        self.__beer_db.execute(
            f'DELETE FROM "{chat_name}" WHERE id = "{from_id}";')
        self.__db.commit()
        return 'Ты только что выкинул свое пиво...'

    def __check_date(self, chat_id, from_id):
        chat_name = self.__update_table(chat_id)
        try:
            self.__beer_db.execute(f'SELECT id FROM "{chat_name}" WHERE id = "{from_id}"').fetchone()
        except sqlite3.OperationalError:
            return False
        old_date = datetime.datetime.fromordinal(self.__beer_db.execute(
            f'SELECT time FROM "{chat_name}" WHERE id = "{from_id}";').fetchone()[0])
        if old_date + datetime.timedelta(days=1) < datetime.datetime.now():
            return True
        else:
            return False

    def __beer_time_break(self):
        return 'Ты слишком часто думаешь о пиве!'

    def __break_beer(self, chat_id, from_id):
        chat_name = self.__update_table(chat_id)
        self.__beer_db.execute(
            f'DELETE FROM "{chat_name}" WHERE id = "{from_id}";')
        self.__db.commit()
        return 'Твое пиво разбилось.\n Положи новое.'

    def __update_table(self, chat_id):
        self.__table = "chat" + str(chat_id)
        return self.__table

    def show_all(self, chat_id):
        result_beer = 'Пока ничего не нашел.'
        chat_name = self.__update_table(chat_id)
        try:
            all_results = self.__beer_db.execute(
                f'SELECT * FROM "{chat_name}" ORDER BY score ASC;')
            if all_results is not None:
                result_beer = ''
                all_results = self.__beer_db.fetchall()
                for i in range(0, len(all_results)):
                    result_beer += all_results[i][1] + ' ' + all_results[i][2] + ' — ' + str(
                        all_results[i][5]) + ' — ' + str(all_results[i][3]) + '°. Рейтинг — ' + str(
                        all_results[i][6]) + '\n'
        except sqlite3.OperationalError:
            return result_beer
        return result_beer
