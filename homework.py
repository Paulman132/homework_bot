import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions
from settings import ENDPOINT, HOMEWORK_VERDICTS, RETRY_PERIOD

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

GLOBAL_VARIABLE_IS_MISSING = 'Отсутствует глобальная переменная'
GLOBAL_VARIABLE_IS_EMPTY = 'Пустая глобальная переменная'
HOMEWORKS_NAMES = ['homework_name', 'status']

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    level=logging.DEBUG,
    filename='./homework_log.log',
    format='%(asctime)s [%(levelname)s] %(message)s',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.debug(f'Бот отправил сообщение: "{message}"')
        return bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        logger.error(f'Боту не удалось отправить сообщение: "{error}"')
        raise exceptions.SendMessageException(error)


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API сервиса Практикум.Домашка."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        message = f'Эндпоинт {ENDPOINT} недоступен: {error}'
        logger.error(message)
        raise exceptions.GetAPIAnswerException(message)
    if homework_statuses.status_code != HTTPStatus.OK:
        message = f'Код ответа API: {homework_statuses.status_code}'
        logger.error(message)
        raise exceptions.GetAPIAnswerException(message)
    try:
        data = homework_statuses.json()
    except ValueError as error:
        message = f'Ошибка преобразования к формату json: {error}'
        logger.error(message)
        raise exceptions.GetAPIAnswerException(message)
    return data


def check_response(response):
    """Проверяет корректность данных, запрошенных от API Практикум.Домашка."""
    if not isinstance(response, dict):
        message = (
            f'Тип данных в ответе от API не соотвествует ожидаемому.'
            f' Получен: {type(response)}')
        logger.error(message)
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'Ключ homeworks недоступен'
        logger.error(message)
        raise exceptions.CheckResponseException(message)
    homeworks_list = response['homeworks']
    if type(homeworks_list) != list:
        message = (
            f'В ответе от API домашки приходят не в виде списка. '
            f'Получен: {type(homeworks_list)}')
        logger.error(message)
        raise TypeError(message)
    return homeworks_list


def parse_status(homework):
    """Извлекает из информации о конкретной домашке её статус."""
    for key in HOMEWORKS_NAMES:
        if key not in homework:
            message = f'Ключа "{key}" нет в response'
            logger.error(message)
            raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[homework_status]
        return (f'Изменился статус проверки работы '
                f'"{homework_name}". {verdict}')
    message = (
        f'Передан неизвестный статус домашней работы "{homework_status}"')
    logger.error(message)
    raise exceptions.ParseStatusException(message)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    for key in (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ENDPOINT):
        if not key:
            logging.critical(GLOBAL_VARIABLE_IS_EMPTY)
            return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise ValueError('Проверьте переменные окружения')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    current_status = ''
    current_error = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logger.info('Статус не обновлен')
            else:
                homework_status = parse_status(*homeworks[:1])
                if current_status == homework_status:
                    logger.info(homework_status)
                else:
                    current_status = homework_status
                    send_message(bot, homework_status)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if current_error != str(error):
                current_error = str(error)
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
