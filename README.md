# Homework Bot - Бот для проверки статуса домашней работы на код ревью в Яндекс.Практикум

### homework_bot - отслеживание статуса код-ревью Яндекс.Практикум.

Бот проверяет API Яндекс.Практикум каждые 10 минут и присылает в телеграм статус проверки домашней работы (результат код-ревью).
Если работа проверена, то будет получено сообщение о ее статусе.

У API Практикум.Домашка есть лишь один эндпоинт: 

https://practicum.yandex.ru/api/user_api/homework_statuses/

и доступ к нему возможен только по токену.

Получить токен можно по [адресу](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a). Копируем его, он нам пригодится чуть позже.

### Принцип работы API
Когда ревьюер проверяет вашу домашнюю работу, он присваивает ей один из статусов:

- работа принята на проверку
- работа возвращена для исправления ошибок
- работа принята

### Запуск на ПК

Клонируем проект:

```bash
git clone
```

Переходим в папку с ботом.

```bash
cd homework_bot
```

Устанавливаем виртуальное окружение.

```bash
python -m venv venv
```

Активируем виртуальное окружение.

```bash
source venv/Scripts/activate
```

Устанавливаем зависимости.

```bash
pip install -r requirements.txt
```

В консоли импортируем токены для Яндекс.Практикум и для Телеграм:

```bash
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID>
```

Запускаем бота.

```bash
python homework.py
```
