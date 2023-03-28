import vk, requests
from datetime import datetime, timedelta
from urllib import request
from bs4 import BeautifulSoup as bs
import re
import threading
from pyrogram import Client, idle

# Telegram API CONFIG!
tg_api_id = 00000000
tg_api_hash = 'YOUR_API_HASH'
tg_bot_token = 'YOUR_BOT_TOKEN'

app = Client("BUKEP NOTIFIER", api_id=tg_api_id, api_hash=tg_api_hash, bot_token=tg_bot_token)


URL_TEMPLATE = "http://rasp.bukep.ru/Default.aspx?idFil=1000&tr=gweek&f=10084&s=%d0%98%d0%bd%d1%84%d0%be%d1%80%d0%bc%d0%b0%d1%86%d0%b8%d0%be%d0%bd%d0%bd%d1%8b%d0%b5%20%d1%81%d0%b8%d1%81%d1%82%d0%b5%d0%bc%d1%8b%20(%d0%bf%d0%be%20%d0%be%d1%82%d1%80%d0%b0%d1%81%d0%bb%d1%8f%d0%bc)1&k=3&g=6293"
r = requests.get(URL_TEMPLATE)
soup = bs(r.text, "html.parser")

rasp_time_other = ['', '08:30', '10:15', '12:25', '14:35', '16:20', '18:05', '19:50']
rasp_time_saturday = ['', '08:30', '10:15', '12:00', '14:10', '15:55', '17:40', '19:25']
weekday_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

pattern = re.compile(r'\w+') # регулярка для того чтобы вытянуть день недели из таблицы с расписанием и сравнить с сегодняшним

#loop_timer = 0

def main():
    now = datetime.now()
    weekday = datetime.weekday(now)
    if weekday_name[weekday] == 'Суббота':
        rasp_time = rasp_time_saturday
    else:
        rasp_time = rasp_time_other

    cur_time = now.strftime("%H:%M:%S")
    #cur_time = now.strftime('14:35:15')
    next_notify = "\033[1m" + weekday_name[weekday] + "\033[0m, на сегодня расписания нет :)"

    for today in soup.find_all("td", class_="day_in_table"):
        #print(today.get_text())
        first_word = next(m.group() for m in re.finditer(r'\w+', today.get_text()))
        if (weekday_name[weekday] == first_word):
            for cur_para in today.find_all("tr"):
                if cur_para.get_text().strip("\n\t ") in weekday_name:
                    #print (cur_para.get_text()) # Вторник
                    continue
                cur_para_num = cur_para.find("td", class_="num_para")
                cur_para_name = cur_para.find("td", class_="para").get_text("<br>")
                cur_para_prepod = cur_para.find_all("input")
                prepods = ''
                for prepod in cur_para_prepod:
                    prepods += '`' + prepod.get("value") + '`\n'
                cur_para_num = int(''.join(c for c in cur_para_num.get_text() if  c.isdecimal()))
                if rasp_time[cur_para_num] > cur_time:
                    time_interval = datetime.strptime(rasp_time[cur_para_num]+':00',"%H:%M:%S") - datetime.strptime(cur_time,"%H:%M:%S")
                    loop_timer = datetime.strptime(rasp_time[cur_para_num]+':00',"%H:%M:%S") - timedelta(minutes=10)
                    #next_notify = "Следующая пара \033[1m" + cur_para.get_text() + "\033[0m, начнётся через " + str(time_interval) + " в \033[1m" + rasp_time[cur_para_num] + "\033[0m\n" + "Напоминание будет отправлено в " + loop_timer.strftime("%H:%M:%S")
                    #next_notify = "Следующая пара \033[1m" + cur_para.get_text() + "\033[0m, начнётся через " + str(time_interval) + " в \033[1m" + rasp_time[cur_para_num] + "\033[0m"
                    threading.Timer(300.0, main).start()
                    if str(time_interval) >= loop_timer.strftime("%H:%M:%S"):
                        print("\033[0mНапоминание отправлено!\033[1m")
                        app.send_message('pooh2pooh', str(cur_para_num) + '. ' + str(cur_para_name).replace("<br>", "\n") + '\n' + prepods + '\n**начнётся через ' + str(time_interval) + '**')
                    break

            current = today.find("table", class_="tbl_day").get_text() # всё расписание на Сегодня
            #print(current) 
            break

    #print(next_notify)

    return 0

if __name__ == "__main__":
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(" Бот парсит расписание БУКЭП и уведомляет о начале следующей пары в телеграм, примерно за 10 минут")
    print("")
    print(" Автор: @pooh2pooh")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    app.start()
    main()
    idle()
    app.stop()
