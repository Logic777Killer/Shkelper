import os

import vk_api
import requests
from vk_api import VkApi
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
import json
from threading import Thread
import schedule
import datetime
import time
import sqlite3
import pymorphy2
from vk_api.longpoll import VkLongPoll, VkEventType

KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
main_token = '94203354ca9aea103b2fcb2945e2ffd5d154b45d66a9661413089420e3842f0504c7df2cdee9039e0bc76'
TOKEN = main_token
vk_session = vk_api.VkApi(token=main_token)
api = vk_session.get_api()
db_name = sqlite3.connect('siriusBOT.db')
cur = db_name.cursor()
longpoll = VkLongPoll(vk_session)
idk = 0
delete = 0
v = 0
n = 0
nn = 0
n1 = 0
fact = 0
chet = 0
timing = time.time()
timing_ = time.time()
morph = pymorphy2.MorphAnalyzer()
raznoobrazie = 0


def facts():
    db_name = sqlite3.connect('siriusBOT.db')
    cur = db_name.cursor()
    global n1
    global timing_
    if time.time() - timing_ > 86390.0:
        timing_ = time.time()
        result_ = cur.execute("""SELECT idd FROM siriusBOT""").fetchall()
        result__ = cur.execute("""SELECT Факт FROM Интересные_факты""").fetchall()
        print(n1)
        print(len(result__))
        if n1 < len(result__):
            for i in result_:
                id = int(i[0])
                fakt = cur.execute("""SELECT Факт FROM Интересные_факты""").fetchall()
                #                   print(fakt[n1][0])
                send_some_msg(id, str(fakt[n1][0]))
            timing_ = time.time()
            n1 += 1
        cur.execute("delete from Интересные_факты where Факт = ?", (str(fakt[n1][0]),))
        db_name.commit()


def bot_debt():
    db_name = sqlite3.connect('siriusBOT.db')
    cur = db_name.cursor()
    for i in cur.execute('select Дата_сдачи, Ученик, Долг, Преподаватель, Напомнено from долги').fetchall():
        if (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%Y') == i[0] and i[4] == 0:
            cur.execute('UPDATE долги SET Напомнено = 1 WHERE Ученик = ?', (i[1],))
            user = vk_session.method("users.get", {"user_ids": int(i[3])})
            msgg = f"Завтра последний срок сдачи задания:\n \n {i[2]}\n \n учителю {user[0]['first_name']} {user[0]['last_name']}"
            vk_session.method("messages.send", {"user_id": int(i[1]), "message": msgg, "random_id": 0})
            db_name.commit()
    facts()


def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def send_photo(vk, peer_id, owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(
        random_id=get_random_id(),
        peer_id=peer_id,
        attachment=attachment
    )


def main(id, v):
    global raznoobrazie
    vk_session = VkApi(token=TOKEN)
    vk = vk_session.get_api()
    upload = VkUpload(vk)
    if v == 'idk.jpg':
        v = f'idk{raznoobrazie}.jpg'
        raznoobrazie += 1
        if raznoobrazie == 3:
            raznoobrazie = 0
    send_photo(vk, id, *upload_photo(upload, v))


def send_some_msg(id, some_text):
    db_name = sqlite3.connect('siriusBOT.db')
    cur = db_name.cursor()
    userrol = cur.execute("""select Роль from siriusBOT
                                    where idd = ?""", (str(id),)).fetchone()
    if userrol is not None:
        if userrol[0] == 'учитель':
            vk_session.method("messages.send",
                              {"user_id": id, "message": some_text, "random_id": 0, 'keyboard': keyboard})
        elif userrol[0] == 'ученик':
            vk_session.method("messages.send",
                              {"user_id": id, "message": some_text, "random_id": 0, 'keyboard': keyboardd})
    else:
        vk_session.method("messages.send", {"user_id": id, "message": some_text, "random_id": 0})


def get_but(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


keyboard = {
    "one_time": False,
    "buttons": [
        [get_but('я', 'negative')],
        [get_but('хелп', 'negative')],
        [get_but('список', 'negative')],
        [get_but('должники', 'negative')],
        [get_but('плюсы', 'negative')]
    ]
}

keyboardd = {
    "one_time": False,
    "buttons": [
        [get_but('я', 'positive')],
        [get_but('хелп', 'positive')],
        [get_but('мои долги', 'positive')],
        [get_but('список', 'positive')]
    ]
}

keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

keyboardd = json.dumps(keyboardd, ensure_ascii=False).encode('utf-8')
keyboardd = str(keyboardd.decode('utf-8'))

schedule.every().hour.do(bot_debt)


# schedule.every().second.do(facts)

def f1():
    while True:
        schedule.run_pending()
        time.sleep(10)


def f2():
    global n, v, fact, delete, chet, idk, raznoobrazie, timing
    db_name = sqlite3.connect('siriusBOT.db')
    cur = db_name.cursor()
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                try:
                    id = event.user_id
                    PEER_ID = id
                    if fact == 0:
                        msg = event.text.lower()
                    else:
                        msg = event.text
                    userrol = cur.execute("""select Роль from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                    registr = 0
                    q = [0, 0, 0, 0]
                    if '/' in msg:
                        q = msg.split('/')
                    result = cur.execute("""SELECT idd FROM siriusBOT""").fetchall()
                    v = cur.execute("""SELECT * FROM siriusBOT""").fetchall()
                    if (str(id),) not in result and msg != 'регистрация' and 'ученик' not in q and 'учитель' not in q:
                        send_some_msg(id, 'Вы не зарегистрированы! Напишите слово "регистрация", чтобы мы Вас запомнили')
                        continue
                    elif msg == 'регистрация':
                        send_some_msg(id,
                                      "Чтобы зарегистрироваться, напишите следующее:\n \nрег/Фамилия/Имя/Отчество/кто Вы(ученик или учитель)\n \nБЕЗ ПРОБЕЛОВ")
                        continue
                    elif q[0] == 'рег' and q[4] == 'ученик' and (str(id),) not in result:
                        w = [q[1], q[2], q[3], q[4], id]
                        q = "INSERT INTO siriusBOT ('Фамилия', 'Имя', 'Отчество', 'Роль', 'idd') VALUES(?, ?, ?, ?, ?)"
                        send_some_msg(id,
                                      "Регистрация прошла успешно!")
                        send_some_msg(id,
                                      "Чтобы ты смог контактировать с учителями, тебе нужно их добавить.\nТы это сделать сможешь так:\nдобавить/фамилияучителя1/фамилияучителя2/...")
                        cur.execute(q, w)
                        db_name.commit()
                        continue
                    elif q[0] == 'рег' and q[4] == 'учитель' and (str(id),) not in result:
                        w = [q[1], q[2], q[3], q[4], id]
                        send_some_msg(id, "Регистрация прошла успешно!")
                        q = "INSERT INTO siriusBOT ('Фамилия', 'Имя', 'Отчество', 'Роль', 'idd') VALUES(?, ?, ?, ?, ?)"
                        cur.execute(q, w)
                        db_name.commit()
                        continue
                    elif q[0] == 'рег' and (str(id),) in result:
                        send_some_msg(id,
                                      'Чтобы Вы могли зарегистрироваться снова, Вам нужно удалить свой профиль.\nЭто можно сделать по команде "удалиться"')
                        continue
                    elif q[0] == 'добавить' or q[0] == 'Добавить':
                        result = cur.execute("""SELECT * FROM siriusBOT
                                                        WHERE Роль = 'учитель'""").fetchall()
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        surname = cur.execute("""select Фамилия from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        k = q[1:]
                        p = []
                        re = cur.execute("""SELECT Учитель FROM привязка
                                            where Ученик = ?""", (str(id),)).fetchall()
                        for i in q[1:]:
                            t = cur.execute('select * from siriusBOT where Фамилия = ?', (str(i),)).fetchone()
                            try:
                                if (t[4],) in re:
                                    send_some_msg(id,
                                                  f'Ты уже привязан к такому учителю, как {t[1].capitalize()} {t[2].capitalize()}')
                                    p.append(t[0])
                                    continue
                                for j in result:
                                    if i == j[0]:
                                        cur.execute("INSERT INTO привязка VALUES(?, ?)", (str(id), str(j[4]),))
                                        send_some_msg(int(j[4]),
                                                      f'{surname[0].capitalize()} {name[0].capitalize()} выбрал(а) Вас в качестве учителя.')
                                        db_name.commit()
                                        p.append(j[0])
                                        break
                            except TypeError:
                                send_some_msg(id, f'Учителя по фамилии {i} у меня нет.')
                        if k == p:
                            send_some_msg(id,
                                          'Все учителя были успешно добавлены!\n \nЧтобы написать нужному учителю сообщение, пиши так:\n \n!Иван-Иванович Здравствуйте!')
                        elif k != p and p != []:
                            send_some_msg(id,
                                          f'Всех кого смог - добавил, проверь написание фамилий учителей, которые я написал выше.⬆⬆⬆ \n \nЧтобы написать нужному учителю сообщение, пиши так:\n \n!Иван-Иванович Здравствуйте!')
                        continue
                    elif q[0] == 'фактик':
                        try:
                            print(msg)
                            if msg != '':
                                number = cur.execute("""select Номер_факта from Интересные_факты""").fetchall()
                                cur.execute("""insert into Интересные_факты ('Номер_факта', 'Факт') values(?, ?)""",
                                            (str(int(number[-1][0]) + 1), q[1],))
                                send_some_msg(id, 'Ваш факт добавлен в очередь фактов! Ожидайте!')
                                db_name.commit()
                                fact = 0
                                continue
                            else:
                                send_some_msg(id, 'Воспринимается только текстовый факт.')
                                fact = 0
                                continue
                        except IndexError:
                            send_some_msg(id, 'Воспринимается только текстовый факт.')
                    elif msg[0] == '!' and userrol[0] == 'ученик':
                        r = msg.lower().split(' ', 1)
                        r[0] = r[0].replace('!', '')
                        r[0] = r[0].split('-')
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        surname = cur.execute("""select Фамилия from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        try:
                            teacher = cur.execute("""SELECT * FROM siriusBOT where Имя = ? and Отчество = ?""",
                                                  (r[0][0], r[0][1],)).fetchone()
                            priv = cur.execute("""select * from привязка where Учитель = ? and Ученик = ?""",
                                               (teacher[4], str(id),)).fetchall()

                            if teacher is not None:
                                if priv != []:
                                    send_some_msg(int(teacher[4]),
                                                  f'К Вам поступило сообщение от {surname[0].capitalize()} {name[0].capitalize()}!\n \n{r[1]}')
                                    send_some_msg(int(teacher[4]),
                                                  f'Чтобы написать что-нибудь в ответ, пишите так:\n?Иванов Привет!')
                                    send_some_msg(id, 'Сообщение отправлено!')
                                else:
                                    send_some_msg(id,
                                                  f'Ты не можешь отправить, так как ты не выбрал {r[0][0]} {r[0][1]} в качестве учителя.')
                            else:
                                send_some_msg(id, 'Такой учитель ещё не зарегистрировался здесь.')
                        except TypeError:
                            send_some_msg(id, 'Неправильно введены имя или отчество преподавателя!')
                        continue
                    elif '?всем' in msg and userrol[0] == 'учитель':
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        othcenash = cur.execute("""select Отчество from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        ids = cur.execute("""select Ученик from привязка
                                              where Учитель = ?""", (str(id),))
                        msg = msg.split(' ', 1)
                        for i in ids:
                            send_some_msg(int(i[0]),
                                          f'К Вам поступило сообщение от {name[0].capitalize()} {othcenash[0].capitalize()}!\n \n{msg[1]}')
                        send_some_msg(id, 'Сообщение отправлено!')
                        continue
                    elif msg[0] == '?' and userrol[0] == 'учитель':
                        try:
                            priv = None
                            r = msg.lower().split(' ', 1)
                            r[0] = r[0].replace('?', '')
                            name = cur.execute("""select Имя from siriusBOT
                                                            where idd = ?""", (str(id),)).fetchone()
                            othcenash = cur.execute("""select Отчество from siriusBOT
                                                            where idd = ?""", (str(id),)).fetchone()
                            student = cur.execute("""SELECT * FROM siriusBOT where Фамилия = ?""",
                                                  (r[0],)).fetchone()
                            if student is not None:
                                priv = cur.execute("""select * from привязка where Ученик = ? and Учитель = ?""",
                                                   (student[4], str(id),)).fetchall()
                                if priv != []:
                                    send_some_msg(int(student[4]),
                                                  f'К Вам поступило сообщение от {name[0].capitalize()} {othcenash[0].capitalize()}!\n \n{r[1]}')
                                    send_some_msg(int(student[4]),
                                                  f'Чтобы написать что-нибудь в ответ, пишите так:\n!Иван-Иванович Здравствуйте!')
                                    send_some_msg(id, 'Сообщение отправлено!')
                                else:
                                    send_some_msg(id,
                                                  f'Вы не можете отправить сообщение, так как {student[0].capitalize()} {student[1].capitalize()} не выбрал Вас в качестве учителя.')
                                    send_some_msg(int(student[4]),
                                                  f'Тебе {name[0].capitalize()} {othcenash[0].capitalize()} пытался(-ась) что-то написать,\nно ты не добавил его(её) в качестве учителя ☹')
                            else:
                                send_some_msg(id, 'Такой ученик ещё не зарегистрировался здесь.')
                            continue
                        except IndexError:
                            send_some_msg(id, 'Ошибка!\nПроверьте, правильно ли Вы написали фамилию ученика.\nПроверьте, привязан ли данный ученик к Вам.')
                    elif (msg == 'список' or msg == 'cgbcjr') and userrol[0] == 'учитель':
                        k = ''
                        p = 1
                        exit = 0
                        result = cur.execute("""SELECT Ученик FROM привязка
                                                        WHERE Учитель = ?""", (str(id),)).fetchall()
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        otchenash = cur.execute("""select Отчество from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        for i in result:
                            print(i)
                            namee = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            surname = cur.execute("""select Фамилия from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            k += f'{p}. {surname[0].capitalize()} {namee[0].capitalize()}\n'
                            p += 1
                        if len(k) != 0:
                            send_some_msg(id,
                                          f'Вот список Ваших учеников, {name[0].capitalize()} {otchenash[0].capitalize()}:\n {k}')
                        else:
                            send_some_msg(id, 'У Вас пока нет учеников\nВашим балбесам надо зарегистрироваться 😉')
                        continue
                    elif (msg == 'список' or msg == 'cgbcjr') and userrol[0] == 'ученик':
                        k = ''
                        p = 1
                        exit = 0
                        result = cur.execute("""SELECT Учитель FROM привязка
                                                        WHERE Ученик = ?""", (str(id),)).fetchall()
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        for i in result:
                            namee = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            surname = cur.execute("""select Отчество from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            k += f'{p}. {namee[0].capitalize()} {surname[0].capitalize()}\n'
                            p += 1
                        if len(k) != 0:
                            send_some_msg(id,
                                          f'Вот список твоих учителей, {name[0].capitalize()}:\n {k}')
                        else:
                            send_some_msg(id, 'У Вас пока нет учителей\nдобавьте их и будьте счастливы😉')
                        continue
                    elif msg == 'я' or msg == 'z':
                        name = cur.execute("""select Имя from siriusBOT
                                                            where idd = ?""", (str(id),)).fetchone()
                        otchenash = cur.execute("""select Отчество from siriusBOT
                                                            where idd = ?""", (str(id),)).fetchone()
                        surname = cur.execute("""select Фамилия from siriusBOT
                                                            where idd = ?""", (str(id),)).fetchone()
                        rol = cur.execute("""select Роль from siriusBOT
                                                            where idd = ?""", (str(id),)).fetchone()
                        send_some_msg(id,
                                      f'Вы - {surname[0].capitalize()} {name[0].capitalize()} {otchenash[0].capitalize()}, {rol[0]}')
                        continue
                    elif q[0] == 'долг' and userrol[0] == 'учитель':
                        try:
                            q[1] = q[1].split(',')
                            if len(q[1]) == 1:
                                q[1] = q[1][0]
                                uchenik = cur.execute("""select idd from siriusBOT
                                                                        where Фамилия = ?""",
                                                      (str(q[1]),)).fetchone()
                                priv = cur.execute("""select * from привязка where Ученик = ? and Учитель = ?""",
                                                   (uchenik[0], str(id),)).fetchall()
                                if uchenik is not None and priv is not None:
                                    time_ = f'{"30.12" if datetime.date.today().month > 5 else "31.05"}.{datetime.date.today().year}'
                                    w = [uchenik[0], q[2], id, q[3]] if len(q) == 4 else [uchenik[0], q[2], id, time_]
                                    cur.execute(
                                        "insert into долги ('Ученик', 'Долг', 'Преподаватель', Дата_сдачи) values(?, ?, ?, ?)",
                                        w)
                                    send_some_msg(id, f'Долг успешно повешен на {q[1].capitalize()}!')
                                    db_name.commit()
                                elif uchenik is not None and priv is None:
                                    send_some_msg(id,
                                                  f'Вы не можете повесить на {q[1].capitalize()},так как\nэтот ученик не выбрал Вас в качестве учителя.\n')
                                else:
                                    send_some_msg(id, 'В Вашем списке нет ученика с такой фамилией.')
                                continue
                            else:
                                for i in q[1]:
                                    uchenik = cur.execute("""select idd from siriusBOT
                                                                                            where Фамилия = ?""",
                                                          (str(i),)).fetchone()
                                    priv = cur.execute("""select * from привязка where Ученик = ? and Учитель = ?""",
                                                       (uchenik[0], str(id),)).fetchall()
                                    if uchenik is not None and priv is not None:
                                        time_ = f'{"30.12" if datetime.date.today().month > 5 else "31.05"}.{datetime.date.today().year}'
                                        w = [uchenik[0], q[2], id, q[3]] if len(q) == 4 else [uchenik[0], q[2], id, time_]
                                        cur.execute(
                                            "insert into долги ('Ученик', 'Долг', 'Преподаватель', 'Дата_сдачи') values(?, ?, ?, ?)",
                                            w)
                                        send_some_msg(id, f'Долг успешно повешен на {i.capitalize()}!')
                                        db_name.commit()
                                    elif uchenik is not None and priv is None:
                                        send_some_msg(id,
                                                      f'Вы не можете повесить на {i.capitalize()},так как\nэтот ученик не выбрал Вас в качестве учителя.\n')
                                    else:
                                        send_some_msg(id, f'В Вашем списке нет ученика с фамилией {i.capitalize()}.')
                                continue
                        except TypeError:
                            send_some_msg(id, 'Ошибка! Проверьте правильность написания фамилий или структуру написания команды\n \n(долг/Гайдуков,Копий/сдать домашнюю работу/30.12.2021)')
                    elif msg == 'должники' and userrol[0] == 'учитель':
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        otchenash = cur.execute("""select Отчество from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        res = cur.execute("""select Ученик, Долг, Дата_сдачи from долги
                                                where Преподаватель = ?""", (str(id),)).fetchall()
                        k = ''
                        p = 1
                        for i in res:
                            dlognik_name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            dlognik_sur = cur.execute("""select Фамилия from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            k += f'{p}. {dlognik_sur[0].capitalize()} {dlognik_name[0].capitalize()} ({i[1]}, {i[2]})\n'
                            p += 1
                        if k != '':
                            send_some_msg(id, f'Ваши должники, {name[0].capitalize()} {otchenash[0].capitalize()} 😈:\n{k}')
                        else:
                            send_some_msg(id, 'У Ваших учеников нет долгов!🤯🤯🤯')
                        continue
                    elif q[0] == 'убрать долг' and userrol[0] == 'учитель':
                        try:
                            uchenik = cur.execute("""select idd from siriusBOT
                                                                where Фамилия = ?""", (str(q[1]),)).fetchone()
                            proverka = cur.execute("""select Ученик from долги
                                                                where Долг = ?""", (str(q[2]),)).fetchone()
                            proverka_time = cur.execute("""select Ученик from долги
                                                                where Дата_сдачи = ? and Долг = ?""",
                                                        (str(q[3]), str(q[2]),)).fetchone()
                            kuku = cur.execute("""select Ученик from долги""").fetchall()
                            if proverka_time is None:
                                send_some_msg(id, 'На введённое Вами время у ученика нет такого долга.')
                                continue
                            if proverka is None and proverka_time is None:
                                send_some_msg(id, f'У этого человека нет такого долга...\nВы зря на него наговариваете.')
                                continue
                            if proverka_time is not None and proverka is not None:
                                cur.execute("delete from долги where Ученик = ? and Долг = ? and Дата_сдачи = ?",
                                            (str(uchenik[0]), str(q[2]), str(q[3]),))
                                ku = cur.execute("""select Ученик from долги""").fetchall()
                                if len(ku) < len(kuku):
                                    send_some_msg(id, f'Долг успешно списан с {q[1].capitalize()}!')
                                else:
                                    send_some_msg(id,
                                                  'Не удалось списать долг, проверьте, правильно ли вы ввели долг или дату сдачи!\n \n убрать долг/Гайдуков/сдать домашнюю работу/21.12.2021')
                                db_name.commit()
                            continue
                        except IndexError:
                            send_some_msg(id,
                                          'Воспринимается формат только в виде:\n \nубрать долг/Гайдуков/сдать домашнюю работу/21.12.2021')
                    elif msg == 'удалиться' and delete == 0:
                        send_some_msg(id,
                                      'Вы точно хотите удалить свой профиль? \n Для подтверждения напишите "удалить", для отказа - "передумал".')
                        send_some_msg(id, 'P.S. Если Вы удалитесь, то по возвращению придётся регистрироваться снова.')
                        delete += 1
                        continue
                    elif msg == 'удалить' and delete != 0:
                        cur.execute("delete from долги where Ученик = ?", (str(id),))
                        cur.execute("delete from долги where Преподаватель = ?", (str(id),))
                        cur.execute("delete from siriusBOT where idd = ?", (str(id),))
                        cur.execute("delete from привязка where Ученик = ?", (str(id),))
                        cur.execute("delete from привязка where Учитель = ?", (str(id),))
                        cur.execute("delete from плюсики where ученик = ?", (str(id),))
                        cur.execute("delete from плюсики where учитель = ?", (str(id),))
                        send_some_msg(id, 'До встречи в школе 😉')
                        db_name.commit()
                        delete = 0
                        continue
                    elif msg == 'передумал' and delete != 0:
                        send_some_msg(id, 'Ну и правильно, нечего от нас убегать 🏫')
                        delete = 0
                        continue
                    elif msg == 'хелп' or msg == 'help':
                        if userrol[0] == 'ученик':
                            send_some_msg(id,
                                          'Функции, которые тебе доступны:\n'
                                          '1) добавить учителя(добавить/Иванов/Гайдуков/и тд.\n'
                                          '2) узнать кто ты (я)\n'
                                          '3) написать учителю (!Иван-Иванович сообщение)\n'
                                          '4) увидеть список долгов (мои долги)\n'
                                          '5) добавить какой-нибудь интересный факт, который отправится всем через какое-то время (фактик/Гайдуков не сдал домашнюю работу!)\n'
                                          '6) посчитать свой средний балл (средний балл/5 пятёрок/4 четвёрки/3 тройки)\n'
                                          '7) добавить какой-нибудь адрес (добавить адрес/адрес через запятую и пробел/название объекта по адресу)\n'
                                          '8) посмотреть мои избранные адреса списком (адреса списком)\n'
                                          '9)посмотреть ваши избранный адрес на карте(адрес на карте/адрес/масштаб от 1 до 100)\n'
                                          '10) увидеть список всех доступных команд (help)\n'
                                          '11) удалить свой профиль (удалиться)\n \n'
                                          'Заполнять строго так, как в примерах!')
                            continue
                        if userrol[0] == 'учитель':
                            send_some_msg(id, 'Функции, которые Вам доступны:\n'
                                              '1) увидеть список ваших учеников (список)\n'
                                              '2) узнать кто Вы (я)\n'
                                              '3) написать ученику (?Иванов сообщение)\n'
                                              '3) повесить долг на ученика (долг/Гайдуков/сдать домашнюю работу/30.12.2021)\n или на нескольких учеников (долг/Гайдуков,Копий/сдать домашнюю работу/30.12.2021)\n'
                                              '4) увидеть список Ваших должников (должники)\n'
                                              '5) снять долг с ученика (убрать долг/Гайдуков/сдать домашнюю работу\n'
                                              '6) добавить какой-нибудь интересный факт, который отправится всем через какое-то время (фактик/Гайдуков не сдал домашнюю работу!)\n'
                                              '7) дать ученику плюсик за работу на уроке (плюс/Гайдуков)\n'
                                              '8) увидеть учеников с плюсами (плюсы)\n'
                                              '9) снять плюсы с ученика (убрать плюсы/Гайдуков)\n'
                                              '10) добавить какой-нибудь адрес (добавить адрес/адрес через запятую и пробел/название объекта по адресу)\n'
                                              '11) посмотреть ваши избранные адреса списком (адреса списком)\n'
                                              '12) посмотреть ваши избранный адрес на карте(адрес на карте/адрес/масштаб от 0.01 до 100))\n'
                                              '13) увидеть список всех доступных команд (help или хелп)\n'
                                              '14) удалить свой профиль (удалиться)\n \n'
                                              'Заполнять строго так, как в примерах!')
                            continue
                    elif msg == '':
                        pass
                    elif msg == 'адрес на карте' or q[0] == 'адрес на карте':
                        if q[2]:
                            scale_ = q[2]
                        else:
                            scale_ = 1
                        address = cur.execute("select координаты from addresses where адрес=?", (q[1],)).fetchall()[0][0]
#                        map_request = f"http://static-maps.yandex.ru/1.x/?ll={address.replace(' ', '')}&spn={0.002 * int(scale_)},{0.002 * int(scale_)}&l=map"
                        map_request = f"http://static-maps.yandex.ru/1.x/?ll={address.replace(' ', '')}&spn={0.0002 * int(scale_)},{0.0002 * int(scale_)}&l=map&pt={address.replace(' ', '')}"
                        response = requests.get(map_request)
                        vk = vk_session.get_api()
                        upload = VkUpload(vk)
                        map_file = "map.png"
                        with open(map_file, "wb") as file:
                            file.write(response.content)
                        send_photo(vk, id, *upload_photo(upload, map_file))
                        os.remove(map_file)
                    elif msg == 'адреса списком':
                        c = []
                        for i, j in cur.execute(
                                f"select адрес, объект_по_адресу from addresses where пользователь={id}").fetchall():
                            c.append(f'{i} ({j})')
                        send_some_msg(id, '\n'.join(c))
                    elif q[0] == 'добавить адрес':
                        geocoder_request = f"https://geocode-maps.yandex.ru/1.x/?apikey={KEY}&geocode" \
                                           f"={q[1].replace(', ', '+')}&format=json"
                        response = requests.get(geocoder_request)
                        if response:
                            json_response = response.json()
                            coords = \
                                json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point'][
                                    'pos']
                            cur.execute("""INSERT INTO addresses VALUES(?, ?, ?, ?)""",
                                        (q[1], q[2], id, coords.replace(' ', ', ')))
                            db_name.commit()
                        else:
                            print("Ошибка выполнения запроса:")
                            print(geocoder_request)
                            print("Http статус:", response.status_code, "(", response.reason, ")")
                    elif msg == 'мои долги' and userrol[0] == 'ученик':
                        res = cur.execute("""select Долг, Преподаватель from долги
                                                where Ученик = ?""", (str(id),)).fetchall()
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        k = ''
                        qq = 1
                        for i in res:
                            name1 = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(i[1]),)).fetchone()
                            otchenash = cur.execute("""select Отчество from siriusBOT
                                                        where idd = ?""", (str(i[1]),)).fetchone()
                            k += f'{qq}) {i[0]} ({name1[0].capitalize()} {otchenash[0].capitalize()})\n'
                            qq += 1
                        if k != '':
                            send_some_msg(id, f'Твои долги, {name[0].capitalize()} 😬:\n{k}')
                        else:
                            send_some_msg(id, 'У тебя нет долгов! Красавчик! 💪')
                            main(id, 'molodec.jpg')
                        continue
                    elif q[0] == 'средний балл' and userrol[0] == 'ученик':
                        summ = 0
                        kolvo = 0
                        pyat = 0
                        comment = morph.parse('пятёрка')[0]
                        try:
                            if len(q) != 2:
                                for i in q[1:]:
                                    i = i.split()
                                    if 'пятёр' in i[1] or 'пятер' in i[1]:
                                        summ += 5 * int(i[0])
                                        kolvo += int(i[0])
                                    elif 'четвёр' in i[1] or 'четвер' in i[1] or 'чётвер' in i[1] or 'чётвёр' in i[1]:
                                        summ += 4 * int(i[0])
                                        kolvo += int(i[0])
                                    elif 'трой' in i[1]:
                                        summ += 3 * int(i[0])
                                        kolvo += int(i[0])
                                    elif 'двой' in i[1]:
                                        summ += 2 * int(i[0])
                                        kolvo += int(i[0])
                                    elif 'кол' in i[1]:
                                        summ += 1 * int(msg[0])
                                        kolvo += int(msg[0])
                                sr = round(summ / kolvo, 2)
                                srr = sr
                                if sr < 4.50:
                                    while srr < 4.50:
                                        summ += 5
                                        kolvo += 1
                                        pyat += 1
                                        srr = round(summ / kolvo, 2)

                                    send_some_msg(id,
                                                  f'Твой средний балл на данный момент: {sr}.\nТебе нужно получить ещё {pyat} {comment.make_agree_with_number(pyat).word}, чтобы выйти на 5.')
                                else:
                                    send_some_msg(id,
                                                  f'Твой средний балл на данный момент: {sr}.\n У тебя выходит 5, молодец!')
                                    main(id, 'krasava.jpg')
                                chet = 0
                            else:
                                msg = q[1].split()
                                if 'пятёр' in msg[1] or 'пятер' in msg[1]:
                                    summ += 5 * int(msg[0])
                                    kolvo += int(msg[0])
                                elif 'четвёр' in msg[1] or 'четвер' in msg[1]:
                                    summ += 4 * int(msg[0])
                                    kolvo += int(msg[0])
                                elif 'трой' in msg[1]:
                                    summ += 3 * int(msg[0])
                                    kolvo += int(msg[0])
                                elif 'двой' in msg[1]:
                                    summ += 2 * int(msg[0])
                                    kolvo += int(msg[0])
                                elif 'кол' in msg[1]:
                                    summ += 1 * int(msg[0])
                                    kolvo += int(msg[0])
                                sr = round(summ / kolvo, 2)
                                srr = sr
                                if sr < 4.50:
                                    while srr < 4.50:
                                        summ += 5
                                        kolvo += 1
                                        pyat += 1
                                        srr = round(summ / kolvo, 2)
                                    send_some_msg(id,
                                                  f'Твой средний балл на данный момент: {sr}.\nТебе нужно получить ещё {pyat} {comment.make_agree_with_number(pyat).word}, чтобы выйти на 5.')
                                else:
                                    send_some_msg(id,
                                                  f'Твой средний балл на данный момент: {sr}.\n У тебя выходит 5, молодец!')
                                    main(id, 'krasava.jpg')
                                chet = 0
                            continue
                        except ZeroDivisionError:
                            send_some_msg(id,
                                          'Ошибка! Проверь правильность написания оценок.\nБот пока может считать только 5-бальную систему оценивания,\nТакже оценка "кол" недоступна.')
                            continue
                        except IndexError:
                            send_some_msg(id,
                                          'Ошибка! Проверь правильность написания оценок(средний балл/5 пятёрок/4 четвёрки/3 тройки).\nБот пока может считать только 5-бальную систему оценивания,\nТакже оценка "кол" недоступна.')
                            continue
                    elif q[0] == 'плюс' and userrol[0] == 'учитель':
                        uchenik = cur.execute("""select idd from siriusBOT
                                                        where Фамилия = ?""",
                                              (str(q[1]),)).fetchone()
                        if uchenik is None:
                            send_some_msg(id, 'В Вашем списке нет ученика с такой фамилией.')
                            continue
                        priv = cur.execute("""select * from привязка where Ученик = ? and Учитель = ?""",
                                           (uchenik[0], str(id),)).fetchone()
                        if uchenik is not None and priv is not None:
                            w = [uchenik[0], str(id)]
                            prov = cur.execute('select плюсы from плюсики where ученик = ? and учитель = ?',
                                               (uchenik[0], str(id),)).fetchone()
                            if prov is not None:
                                w.append(str(int(prov[0]) + 1))
                                cur.execute("update плюсики set плюсы = ? where ученик = ? and учитель = ?",
                                            (w[2], w[0], w[1],))
                                db_name.commit()
                                send_some_msg(id, f'Плюс добавлен!')
                                continue
                            else:
                                w.append(1)
                                cur.execute("insert into плюсики ('ученик', 'учитель', 'плюсы') values(?, ?, ?)", w)
                                send_some_msg(id, f'Плюс добавлен!')
                                db_name.commit()
                                continue
                        elif priv is None and uchenik is not None:
                            send_some_msg(id,
                                          f'Вы не можете дать плюс {q[1].capitalize()}, т.к. он(она) не выбрал(-а) Вас в качестве учителя.')
                            continue
                    elif q[0] == 'убрать плюсы' and userrol[0] == 'учитель':
                        uchenik = cur.execute("""select idd from siriusBOT
                                                            where Фамилия = ?""", (str(q[1]),)).fetchone()
                        proverka = cur.execute("""select плюсы from плюсики
                                                                where учитель = ? and ученик = ?""",
                                               (str(id), uchenik[0],)).fetchone()
                        if proverka is None:
                            send_some_msg(id, f'У этого человека нет плюсов.\n')
                        else:
                            cur.execute("delete from плюсики where ученик = ? and учитель = ?", (str(uchenik[0]), str(id),))
                            send_some_msg(id, f'Плюсы успешно списаны с {q[1].capitalize()}!')
                            db_name.commit()
                        continue
                    elif msg == 'плюсы':
                        name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        otchenash = cur.execute("""select Отчество from siriusBOT
                                                        where idd = ?""", (str(id),)).fetchone()
                        res = cur.execute("""select ученик, плюсы from плюсики
                                                where учитель = ?""", (str(id),)).fetchall()

                        k = ''
                        p = 1
                        for i in res:
                            dlognik_name = cur.execute("""select Имя from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            dlognik_sur = cur.execute("""select Фамилия from siriusBOT
                                                        where idd = ?""", (str(i[0]),)).fetchone()
                            comment = morph.parse('плюсы')[0]
                            pyat = int(i[1])
                            k += f'{p}. {dlognik_sur[0].capitalize()} {dlognik_name[0].capitalize()} ({i[1]} {comment.make_agree_with_number(pyat).word})\n'
                            p += 1
                        if k != '':
                            send_some_msg(id,
                                          f'Ваши умники и умницы, {name[0].capitalize()} {otchenash[0].capitalize()} 😇:\n{k}')
                        else:
                            send_some_msg(id, 'У Ваших учеников нет плюсов!😬')
                        continue
                    else:
                        if (str(id),) in result:
                            send_some_msg(id,
                                          'Видимо Вы немного запутались.\nЧтобы увидеть список доступных команд, напишите "хелп"')
                            main(id, 'idk.jpg')
                            idk = 0
                            continue
                except IndexError:
                    send_some_msg(event.user_id, 'Только сообщения, не более!')


th_1, th_2 = Thread(target=f1), Thread(target=f2)
if __name__ == '__main__':
    th_1.start(), th_2.start()
    th_1.join(), th_2.join()
