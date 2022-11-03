from aiogram import executor, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold, hlink
from rss_parser import Parser
from requests import get
import requests

TOKEN = ""
api_key = ""
# api_key = ""
MSG = "Когда сотку вернешь {} ?"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_name = message.from_user.first_name
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="Верну", callback_data="button_id_1")
    button2 = InlineKeyboardButton(text="Не верну, сорри", callback_data="button_id_2")
    markup.add(button1, button2)
    await bot.send_message(message.chat.id, MSG.format(user_name), reply_markup=markup)

@dp.message_handler(commands=['news'])
async def start_handler(message: types.Message):
    habr_title = []
    for i in range(20):
        if len(habr_title) >= 20:
            habr_title = []
        rss_url = "https://habr.com/ru/rss/news/?fl=ru"
        xml = get(rss_url)

        parser = Parser(xml=xml.content, limit=3)
        feed = parser.parse()

        # пробегаемся по каждой новости в цикле
        for item in reversed(feed.feed):
            # проверяем есть ли заголовок новости в списке
            if not item.title in habr_title:
                habr_title.append(item.title)
                # отправляем сообщение
                # await message.answer(f'{hbold(item.publish_date)}\n\n{hlink(item.title, item.link)}\n\n')
                await bot.send_message(message.chat.id, f'{hbold(item.publish_date)}\n\n{hlink(item.title, item.link)}\n\n')

@dp.message_handler()
async def echo_message(msg: types.Message):
    if len(msg.text) == 10:
        try:

            #inn_org = "6312124429"
            inn_org = msg.text

            get_json = requests.get(f"https://api.checko.ru/v2/company?key={api_key}&inn={inn_org}")
            data = get_json.json()

            inn_info = data['data']['ИНН']
            naim_socr_info = data['data']['НаимСокр']
            data_reg_info = data['data']['ДатаРег']
            okved_info = data['data']['ОКВЭД']['Наим']
            ur_adres_info = data['data']['ЮрАдрес']['АдресРФ']
            us_capital_info = data['data']['УстКап']['Сумма']
            data_ruk_spisok_info = data['data']['Руковод']
            data_uch_spisok_info = data['data']['Учред']['ФЛ']
            data_uch_spisok_ro_info = data['data']['Учред']['РосОрг']
            data_uch_spisok_io_info = data['data']['Учред']['ИнОрг']
            data_uch_spisok_pif_info = data['data']['Учред']['ПИФ']
            data_uch_spisok_rf_info = data['data']['Учред']['РФ']

            if len(data_ruk_spisok_info) == 1:
                ruk_info = 'Руководителем является '
                ruk_info = ruk_info + f"{data['data']['Руковод'][0]['ФИО']} (ИНН {data['data']['Руковод'][0]['ИНН']}) "
            else:
                ruk_info = 'Руководителями являются '
                for i in range(len(data_ruk_spisok_info)):
                    ruk_info = ruk_info + f"{data['data']['Руковод'][i]['ФИО']} (ИНН {data['data']['Руковод'][i]['ИНН']}) "

            if len(data_uch_spisok_info) == 0:
                if len(data_uch_spisok_ro_info) == 0:
                    if len(data_uch_spisok_io_info) == 0:
                        if len(data_uch_spisok_pif_info) == 0:
                            if len(data_uch_spisok_rf_info) == 0:
                                uch_info = 'Учредителем является нет сведений'
                            elif len(data_uch_spisok_rf_info) == 1:
                                uch_info = 'Учредителем является '
                                uch_info = uch_info + f"{data['data']['Учред']['РФ'][0]['Тип']}"
                            else:
                                uch_info = 'Учредителями являются '
                                for i in range(len(data_uch_spisok_rf_info)):
                                    uch_info = uch_info + f"ПИФ {data['data']['Учред']['РФ'][i]['Тип']} "

                        elif len(data_uch_spisok_pif_info) == 1:
                            uch_info = 'Учредителем является '
                            uch_info = uch_info + f"ПИФ {data['data']['Учред']['ПИФ'][0]['Наим']} (Управляющая компания {data['data']['Учред']['ИнОрг'][0]['УпрКом']['НаимПолн']} (ИНН {data['data']['Учред']['ИнОрг'][0]['УпрКом']['ИНН']})) "
                        else:
                            uch_info = 'Учредителями являются '
                            for i in range(len(data_uch_spisok_pif_info)):
                                uch_info = uch_info + f"ПИФ {data['data']['Учред']['ПИФ'][i]['Наим']} (Управляющая компания {data['data']['Учред']['ИнОрг'][i]['УпрКом']['НаимПолн']} (ИНН {data['data']['Учред']['ИнОрг'][0]['УпрКом']['ИНН']})) "
                    elif len(data_uch_spisok_io_info) == 1:
                        uch_info = 'Учредителем является '
                        uch_info = uch_info + f"иностранная организация {data['data']['Учред']['ИнОрг'][0]['НаимПолн']} (Страна {data['data']['Учред']['ИнОрг'][0]['Страна']}) "
                    else:
                        uch_info = 'Учредителями являются '
                        for i in range(len(data_uch_spisok_io_info)):
                            uch_info = uch_info + f"иностранная организация {data['data']['Учред']['ИнОрг'][i]['НаимПолн']} (Страна {data['data']['Учред']['ИнОрг'][i]['Страна']}) "
                elif len(data_uch_spisok_ro_info) == 1:
                    uch_info = 'Учредителем является '
                    uch_info = uch_info + f"организация {data['data']['Учред']['РосОрг'][0]['НаимПолн']} (ИНН {data['data']['Учред']['РосОрг'][0]['ИНН']}) "
                else:
                    uch_info = 'Учредителями являются '
                    for i in range(len(data_uch_spisok_ro_info)):
                        uch_info = uch_info + f"организация {data['data']['Учред']['РосОрг'][i]['НаимПолн']} (ИНН {data['data']['Учред']['РосОрг'][i]['ИНН']}) "
            elif len(data_uch_spisok_info) == 1:
                uch_info = 'Учредителем является '
                uch_info = uch_info + f"физическое лицо {data['data']['Учред']['ФЛ'][0]['ФИО']} (ИНН {data['data']['Учред']['ФЛ'][0]['ИНН']}) "
            else:
                uch_info = 'Учредителями являются '
                for i in range(len(data_uch_spisok_info)):
                    uch_info = uch_info + f"физическое лицо {data['data']['Учред']['ФЛ'][i]['ФИО']} (ИНН {data['data']['Учред']['ФЛ'][i]['ИНН']}) "
            otvet = f'{naim_socr_info} (ИНН {inn_info}), дата регистрации {data_reg_info}, основной вид деятельности: {okved_info}. Юридический адрес компании {ur_adres_info}. {ruk_info}. Уставной капитал {us_capital_info} руб. {uch_info}'

            await bot.send_message(msg.from_user.id, otvet)
        except:
            await bot.send_message(msg.from_user.id, 'ошибка')
    else:
        await bot.send_message(msg.from_user.id, 'введите 10 цифр ИНН')


@dp.callback_query_handler(lambda c: c.data == "button_id_1")
async def to_query(call: types.callback_query):
    await bot.answer_callback_query(call.id)
    await bot.send_message(call.message.chat.id, "Спс")


@dp.callback_query_handler(lambda c: c.data == "button_id_2")
async def to_query(call: types.callback_query):
    await bot.answer_callback_query(call.id)
    await bot.send_message(call.message.chat.id, "Блин")


if __name__ == '__main__':
    executor.start_polling(dp)
