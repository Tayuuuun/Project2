import telebot
from utils import calculate_daily_calories

# Словари
dish_recipes = {}  # блюда и рецепты
user_states = {}  # состояния пользователя
user_characteristics = {}  # характеристики пользователей

# Состояния пользователя
WAITING_FOR_DISH_NAME = 'waiting_for_dish_name'
WAITING_FOR_RECIPE = 'waiting_for_recipe'
WAITING_FOR_RECIPE_NAME = 'waiting_for_recipe_name'
WAITING_FOR_CALORIE_INFO = 'waiting_for_calorie_info'
WAITING_FOR_HEIGHT = 'waiting_for_height'
WAITING_FOR_WEIGHT = 'waiting_for_weight'
WAITING_FOR_AGE = 'waiting_for_age'

# Пример калорийности ингредиентов (на 100 г)
calories_per_ingredient = {
    'курица': 239,
    'рис': 130,
    'морковь': 41,
    'лук': 40,
    'картофель': 77,
    'помидор': 18,
    'перец': 20,
}


@bot.message_handler(commands=['start'])
def start(message):
    """
    Обрабатывает команду /start и отправляет приветственное сообщение.

    :param message: Сообщение от пользователя.
    """
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('новенькое блюдо', 'рецептик', 'рассчитать калории', 'характеристики')
    bot.send_message(message.chat.id, 'Здравствуйте, давайте что-нибудь приготовим, запишите рецепт или название блюда',
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'новенькое блюдо')
def new_dish(message):
    """
    Обработка нового блюда.

    :param message: Сообщение от пользователя.
    """
    bot.send_message(message.chat.id, 'Давайте придумаем название будущему шедевру')
    user_states[message.chat.id] = WAITING_FOR_DISH_NAME


@bot.message_handler(func=lambda message: message.text == 'рецептик')
def get_recipe(message):
    """
    Обработка запроса на рецепт.

    :param message: Сообщение от пользователя.
    """
    bot.send_message(message.chat.id, 'Введите название этого шедевра')
    user_states[message.chat.id] = WAITING_FOR_RECIPE_NAME


@bot.message_handler(func=lambda message: message.text == 'характеристики')
def get_characteristics(message):
    """
    Обработка запроса на характеристики пользователя.

    :param message: Сообщение от пользователя.
    """
    bot.send_message(message.chat.id,
                     'Давайте начнем с заполнения ваших характеристик. Введите ваш рост в сантиметрах:')
    user_states[message.chat.id] = WAITING_FOR_HEIGHT


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == WAITING_FOR_HEIGHT)
def handle_height(message):
    """
    Обработка ввода роста пользователя.

    :param message: Сообщение от пользователя.
    """
    try:
        height = float(message.text)
        user_characteristics[message.chat.id] = {'height': height}
        bot.send_message(message.chat.id, 'Введите ваш вес в килограммах:')
        user_states[message.chat.id] = WAITING_FOR_WEIGHT
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число.')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == WAITING_FOR_WEIGHT)
def handle_weight(message):
    """
    Обработка ввода веса пользователя.

    :param message: Сообщение от пользователя.
    """
    try:
        weight = float(message.text)
        user_characteristics[message.chat.id]['weight'] = weight
        bot.send_message(message.chat.id, 'Введите ваш возраст:')
        user_states[message.chat.id] = WAITING_FOR_AGE
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число.')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == WAITING_FOR_AGE)
def handle_age(message):
    """
    Обработка ввода возраста пользователя.

    :param message: Сообщение от пользователя.
    """
    try:
        age = int(message.text)
        user_characteristics[message.chat.id]['age'] = age
        calories = calculate_daily_calories(user_characteristics[message.chat.id])
        bot.send_message(message.chat.id,
                         f"Ваши характеристики сохранены. Вам нужно употреблять примерно {calories:.2f} ккал в день.")
        user_states[message.chat.id] = None
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число.')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == WAITING_FOR_DISH_NAME)
def handle_dish_name(message):
    """
    Обработка названия нового блюда.

    :param message: Сообщение от пользователя.
    """
    dish_name = message.text
    bot.send_message(message.chat.id, f"Оо супер, звучит вкусно, теперь напишите рецепт '{dish_name}':")
    user_states[message.chat.id] = WAITING_FOR_RECIPE
    dish_recipes[dish_name] = None


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == WAITING_FOR_RECIPE)
def handle_recipe(message):
    """
    Обработка рецепта.

    :param message: Сообщение от пользователя.
    """
    recipe = message.text
    dish_name = [key for key, value in dish_recipes.items() if value is None][0]
    dish_recipes[dish_name] = recipe
    bot.send_message(message.chat.id, f"Буду ждать, когда вы захотите приготовить '{dish_name}': {recipe}")
    user_states[message.chat.id] = None


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == WAITING_FOR_RECIPE_NAME)
def handle_recipe_name(message):
    """
    Обработка запроса на получение рецепта по названию блюда.

    :param message: Сообщение от пользователя.
    """
    dish_name = message.text
    if dish_name in dish_recipes:
        recipe = dish_recipes[dish_name]
        bot.send_message(message.chat.id, f"Вот рецепт блюда '{dish_name}' , приятного аппетита🤍: {recipe}")
    else:
        bot.send_message(message.chat.id, f"Блюда '{dish_name}' тут нет(")
    user_states[message.chat.id] = None


@bot.message_handler(func=lambda message: message.text == 'рассчитать калории')
def calculate_calories(message):
    """
    Обработка запроса на расчет калорий.

    :param message: Сообщение от пользователя.
    """
    bot.send_message(message.chat.id, 'Введите ингредиенты и их количество (например: курица 200, рис 100)')
    user_states[message.chat.id] = WAITING_FOR_CALORIE_INFO


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == WAITING_FOR_CALORIE_INFO)
def handle_calorie_info(message):
    """
    Обработка ввода информации о калориях.

    :param message: Сообщение от пользователя.
    """
    ingredients = message.text.split(',')
    total_calories = 0
    for ingredient in ingredients:
        try:
            name, weight = ingredient.strip().split()
            weight = float(weight)
            if name in calories_per_ingredient:
                total_calories += (calories_per_ingredient[name] * weight) / 100
            else:
                bot.send_message(message.chat.id, f"Ингредиент '{name}' не найден.")
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, используйте формат 'ингредиент количество'.")
            return

    bot.send_message(message.chat.id, f"Общее количество калорий: {total_calories:.2f} ккал.")
    user_states[message.chat.id] = None