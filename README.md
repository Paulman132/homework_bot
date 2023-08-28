# Телеграм-бот «Домашка»

Телеграм-бот, который проверит статус сданного на ревью проекта за студента.
* раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
* при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram;
* логирует свою работу и сообщает о важных проблемах сообщением в Telegram.


## Какие технологии и пакеты использовались:
* Python 3.8
* flake8 3.9.2
* flake8-docstrings 1.6.0
* pytest 6.2.5
* python-dotenv 0.19.0
* python-telegram-bot 13.7
* requests 2.26.0

## Функционал проекта
### Функция main() 
Несёт основную логику работы программы. Все остальные функции запускаются из неё. 
Последовательность работы:
* Сделать запрос к API.
* Проверить ответ.
* Если есть обновления — получить статус работы из обновления и отправить сообщение в Telegram.
* Подождать некоторое время и сделать новый запрос.

### Функция check_tokens() 
Проверяет доступность переменных окружения, которые необходимы для работы программы. Если отсутствует хотя бы одна переменная окружения — функция djpdhfoftn False, иначе — True.

### Функция get_api_answer() 
Делает запрос к единственному эндпоинту API-сервиса. В качестве параметра функция получает временную метку. В случае успешного запроса должна вернуть ответ API, преобразовав его из формата JSON к типам данных Python.

### Функция check_response() 
Проверяет ответ API на корректность. В качестве параметра функция получает ответ API, приведенный к типам данных Python. Если ответ API соответствует ожиданиям, то функция должна вернуть список домашних работ (он может быть и пустым), доступный в ответе API по ключу 'homeworks'.

### Функция parse_status() 
Извлекает из информации о конкретной домашней работе статус этой работы. В качестве параметра функция получает только один элемент из списка домашних работ. В случае успеха, функция возвращает подготовленную для отправки в Telegram строку, содержащую один из вердиктов словаря HOMEWORK_STATUSES.

### Функция send_message() 
Отправляет сообщение в Telegram чат, определяемый переменной окружения TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса Bot и строку с текстом сообщения.

---
---

Клонировать репозиторий и перейти в него в командной строке:

<pre><code>git clone git@github.com:Paulman132/homework_bot.git</code>

<code>cd homework_bot</code></pre>

Cоздать и активировать виртуальное окружение:

<pre><code>python3 -m venv venv</code>

<code>source venv/bin/activate</code></pre>

Установить зависимости из файла requirements.txt:

<pre><code>python3 -m pip install --upgrade pip</code>

<code>pip3 install -r requirements.txt</code></pre>