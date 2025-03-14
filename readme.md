Бот для записи в визовое агентство
#Описание
Этот проект представляет собой бота, который автоматически записывает пользователя на подачу документов в визовое агентство. Бот взаимодействует с локальным сервером, проводит верификацию пользователя, анализирует доступные слоты и записывает пользователя на ближайшую доступную дату.

Функциональные требования
1. Локальный сервер
Обеспечивает верификацию пользователя (по логину и паролю).
Подключен к базе данных пользователей.
Подключен к базе данных доступных слотов (слоты обновляются в реальном времени).
Предоставляет API для получения слотов и API для записи на подачу.
2. База данных
Хранит информацию о пользователях (логин, пароль, email).
Хранит слоты для записи (дата, время, статус — свободно/занято).
3. Бот (консольное приложение)
Запускается через консоль.
Запрашивает у пользователя логин и пароль для аутентификации.
Подключается к локальному серверу, используя переданные учетные данные.
После успешного входа запрашивает список доступных слотов.
Триггерится на ближайший доступный слот и записывает пользователя.
После успешной записи оповещает пользователя по email.
