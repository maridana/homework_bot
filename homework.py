import logging
import os
import requests
import telegram
import time

from dotenv import load_dotenv
from http import HTTPStatus

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/HOMEWORK_VERDICTS/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

def check_tokens():
    """Проверяет доступность переменных окружения."""
    logging.info('Проверка доступности каждого отдельного токена')
    tokens = {
        'practicum_token': PRACTICUM_TOKEN,
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
    }
    
    for name, token in tokens.items():
        if token is None:
            message = f'{name} недоступен'
            logging.critical(message)
            return False
    message = 'Токены доступны'       
    logging.info(message)
    return message

def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение в телеграм отправлено')
    except telegram.TelegramError:
        logger.error('Ошибка отправки сообщения в телеграм')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': timestamp}
    try:
        HOMEWORK_VERDICTS = requests.get(ENDPOINT,
                                         headers=HEADERS,
                                         params=params
                                         )
    except Exception as error:
        message = f'Ошибка запроса к API: {error}'
        logging.error(message)
        return message
    if HOMEWORK_VERDICTS.status_code != HTTPStatus.OK:
        status_code = HOMEWORK_VERDICTS.status_code
        message = f'Ошибка ответа API {status_code}'
        logging.error(message)
        raise
    response = HOMEWORK_VERDICTS.json()
    return response

def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if type(response) is not dict:
        raise TypeError('Ответ API не словарь')
    try:
        list_hworks = response.get('homeworks')
    except KeyError:
        message = 'Ошибка словаря по ключу homeworks'
        logger.error(message)
        return message
    if not isinstance(list_hworks, list):
        raise TypeError('Получен не список')
    try:
        homework = list_hworks[0]
    except IndexError:
        message = 'Нет отправленных на проверку домашек'
        logger.error(message)
        return message
    return homework

def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    if 'status' not in homework:
        raise Exception('В ответе нет ключа "status"')
    if 'homework_name' not in homework:
        raise KeyError('В ответе нет ключа "homework_name"')
    homework_status = homework['status']
    homework_name = homework['homework_name']
    if homework_status not in HOMEWORK_VERDICTS.keys():
        raise Exception(f'Неизвестный статус работы: {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    STATUS = ''
    if not check_tokens():
        raise 
    while True:
        try:
            response = get_api_answer(timestamp)
            message = parse_status(check_response(response))
            if message != STATUS:
                send_message(bot, message)
                STATUS = message
                timestamp = response.get('current_date')
            else:
                logging.info('Нет новых заданий')
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
        time.sleep(RETRY_PERIOD)



if __name__ == '__main__':
    main()
