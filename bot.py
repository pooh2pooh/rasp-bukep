import vk, requests
from datetime import datetime, timedelta
from urllib import request
from bs4 import BeautifulSoup as bs
import re
import threading
from pyrogram import Client, idle
from os import environ
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


app = Client("BUKEP NOTIFIER", api_id=environ.get('API_ID'), api_hash=environ.get('API_HASH'), bot_token=environ.get('TOKENTG'))


URL_TEMPLATE = "http://rasp.bukep.ru/Default.aspx?idFil=1000&tr=gweek&f=10084&s=%d0%98%d0%bd%d1%84%d0%be%d1%80%d0%bc%d0%b0%d1%86%d0%b8%d0%be%d0%bd%d0%bd%d1%8b%d0%b5%20%d1%81%d0%b8%d1%81%d1%82%d0%b5%d0%bc%d1%8b%20(%d0%bf%d0%be%20%d0%be%d1%82%d1%80%d0%b0%d1%81%d0%bb%d1%8f%d0%bc)1&k=3&g=6293"

rasp_time_other = ['', '08:30', '10:15', '12:25', '14:35', '16:20', '18:05', '19:50']
rasp_time_saturday = ['', '08:30', '10:15', '12:00', '14:10', '15:55', '17:40', '19:25']
weekday_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


def main():
    now = datetime.now()
    weekday = datetime.weekday(now)
    if weekday_name[weekday] == 'Суббота':
        rasp_time = rasp_time_saturday
    else:
        rasp_time = rasp_time_other

    cur_time = now.strftime("%H:%M:%S")
    next_notify = "\033[1m" + weekday_name[weekday] + "\033[0m, на сегодня расписания нет :)"

    for today in soup.find_all("td", class_="day_in_table"):

        first_word = next(m.group() for m in re.finditer(r'\w+', today.get_text()))
        if (weekday_name[weekday] == first_word):
            for cur_para in today.find_all("tr"):
                # Этот костыль пропускает строку таблицы расписания где написан день недели!
                if cur_para.get_text().strip("\n\t ") in weekday_name:
                    # print (cur_para.get_text()) # Вторник
                    continue
                # Этот костыль нужен чтобы перейти сразу к изменённому расписание, с галочкой (временно?)
                if '✓' not in cur_para.get_text():
                    continue
                # Парсим номер пары, название, аудиторию и препода
                cur_para_num = cur_para.find("td", class_="num_para")
                cur_para_name = cur_para.find("td", class_="para").get_text("<br>")
                cur_para_prepod = cur_para.find_all("input")
                prepods = ''
                for prepod in cur_para_prepod:
                    prepods += '`' + prepod.get("value") + '`\n'
                # Преобразуем номер пары с галочкой и пояснением (числитель/знаменатель) в цифру
                cur_para_num = int(''.join(c for c in cur_para_num.get_text() if  c.isdecimal()))
                # Проверяем чтобы номер пары был в диапозоне расписания, бывает что всякую фигню вклинивают (прим. разговоры о важном 9:20)
                if cur_para_num in range(len(rasp_time)):
                    if rasp_time[cur_para_num] > cur_time:
                        time_interval = datetime.strptime(rasp_time[cur_para_num]+':00',"%H:%M:%S") - datetime.strptime(cur_time,"%H:%M:%S")
                        loop_timer = datetime.strptime(rasp_time[cur_para_num]+':00',"%H:%M:%S") - timedelta(minutes=15)
                        next_notify = "Следующая пара \033[1m" + cur_para.get_text() + "\033[0m, начнётся через " + str(time_interval) + " в \033[1m" + rasp_time[cur_para_num] + "\033[0m\n" + "Напоминание будет отправлено в " + loop_timer.strftime("%H:%M:%S")
                        if str(time_interval) >= "1:00:00":
                            threading.Timer(3600.0, main).start()
                        else:
                            threading.Timer(300.0, main).start()
                        # print (str(time_interval)) # 4:04:08
                        # print (str(loop_timer)) # 1900-01-01 14:25:00
                        if str(time_interval) <= "0:15:00":
                            print("\033[0mНапоминание отправлено!\033[1m")
                            app.send_message('pooh2pooh', str(cur_para_num) + '. ' + str(cur_para_name).replace("<br>", "\n") + '\n' + prepods + '\n**начнётся через ' + str(time_interval) + '**')
                        break
                    # print(' ' + str(cur_para_num) + ' ' + cur_para_name)

            current = today.find("table", class_="tbl_day").get_text() # всё расписание на Сегодня
            # print(current) 
            break

    print(next_notify)

    return 0

def getRasp():
    global soup
    now = datetime.now()
    cur_time = now.strftime("%H:%M:%S")
    start_time = datetime.strptime('6:00:00', "%H:%M:%S").strftime("%H:%M:%S")
    end_time = datetime.strptime('6:59:59', "%H:%M:%S").strftime("%H:%M:%S")
    # Парсим расписание в 6-00(59) каждого дня, или если оно ещё небыло спаршено
    try:
        soup
        if cur_time >= start_time and cur_time <= end_time:
            r = requests.get(URL_TEMPLATE)
            soup = bs(r.text, "html.parser")
            print ('Спарсил расписание.')
    except NameError:
        r = requests.get(URL_TEMPLATE)
        soup = bs(r.text, "html.parser")
        print ('Спарсил расписание.')
    threading.Timer(3600.0, getRasp).start()


if __name__ == "__main__":
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(" Бот парсит расписание БУКЭП и уведомляет о начале следующей пары в телеграм, примерно за 10 минут")
    print("")
    print(" Автор: @pooh2pooh")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    app.start()
    # app.send_message('pooh2pooh', 'Бот запущен!')
    getRasp()
    main()
    # idle()
    # app.stop()
