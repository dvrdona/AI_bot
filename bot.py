import telebot
import img_gen as ig
import database as db
from deep_translator import GoogleTranslator

bot = telebot.TeleBot('7999841639:AAElEto-gXVvMKzBseC0s2jrPvHeA3LU9rk')

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    check_reg = db.check_user(user_id)
    if check_reg is False:
        bot.send_message(user_id, 'Начнем регистрацию! Введите свое имя!')
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(user_id, 'Введите запрос и я сгенерирую по нему изображение!')
        bot.register_next_step_handler(message, gen)


@bot.message_handler(content_types=['text'])
def get_name(message):
    user_id = message.from_user.id
    user_name = message.text
    db.register(user_id, user_name)
    bot.send_message(user_id, 'Вы успешно зарегистрированы! '
                              'Напишите запрос и создам по ней картину!')
    bot.register_next_step_handler(message, gen)


def gen(message):
    user_id = message.from_user.id
    user_tokens = db.check_user(user_id)[1]
    if user_tokens <= 5:
        try:
            prompt = GoogleTranslator(source='auto', target='en').translate(message.text)
            image = ig.get_link(prompt)
            bot.send_photo(user_id, photo=image)
            bot.send_message(user_id, 'Готово! Если хотите запросить еще картину, пишите!')
            db.add_token(user_id)
            bot.register_next_step_handler(message, gen)

        except:
            bot.send_message(user_id, 'Видимо, ошибка в запросе, попробуйте еще раз')
            bot.register_next_step_handler(message, gen)
    else:
        bot.send_message(user_id, 'Похоже, что ты истратил все свои токены. '
                                  'Оплати и можешь использовать бот дальше')


bot.polling(non_stop=True)