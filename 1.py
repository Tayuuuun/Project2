
import telebot
from handlers import *
from utils import *

API_TOKEN = '8075974197:AAEddxmBUGwPK4IvPo6M0Q-ZfOC9hIA0hEY'
bot = telebot.TeleBot(API_TOKEN)

def main():
    """
    Запускает бота и начинает обработку сообщений.
    """
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()