import logging
import os
import requests
import sys
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
    logging.info('Проверка доступности токенов')
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    logging.info('Начата отправка сообщения в телеграм')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение в телеграм отправлено')
    except telegram.TelegramError:
        logger.error('Ошибка отправки сообщения в телеграм')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': timestamp}
    logging.info('Начат запрос к API')
    try:
        homework_verdicts = requests.get(ENDPOINT,
                                         headers=HEADERS,
                                         params=params
                                         )
    except Exception as error:
        message = f'Ошибка запроса к API: {error}'
        return message
    if homework_verdicts.status_code != HTTPStatus.OK:
        status_code = homework_verdicts.status_code
        message = f'Ошибка ответа API {status_code}'
        raise Exception(message)
    response = homework_verdicts.json()
    return response


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не словарь')
    homeworks = response.get('homeworks')
    if 'homeworks' not in response:
        raise KeyError('Не найден ключ homeworks')
    if 'current_date' not in response:
        raise KeyError('Не найден ключ current_date')
    if not isinstance(homeworks, list):
        raise TypeError('Получен не список')
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашке ее статус."""
    if 'status' not in homework:
        raise KeyError('В ответе нет ключа "status"')
    if 'homework_name' not in homework:
        raise KeyError('В ответе нет ключа "homework_name"')
    homework_status = homework['status']
    homework_name = homework['homework_name']
    if homework_status not in HOMEWORK_VERDICTS:
        raise Exception(f'Неизвестный статус работы: {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Необходимая переменная окружения недоступна'
        logger.critical(message)
        sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response((response))
            if len(homeworks) > 0:
                message = parse_status(homeworks[0])
                send_message(bot, message)
                timestamp = response.get('current_date', timestamp)
            else:
                logging.info('Нет новых заданий')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
