
- [Front](https://github.com/Tryd0g0lik/truck_driver_front)
- [Django Backend Person](https://github.com/Tryd0g0lik/truck_driver)

Регистрация пользователя в блоке Person

Блок обработки даных карты. 

Пользователь - JWT


Permission & groups

Middleware - добавить статус пользователя (Ананом и прочие)

Базовые настройки: "`project.db.corn.Settings`".\
Стартовый файл: "`main.py`"

csrf-токен строиться из "`< sercret-key_there_replaced_the_intermediate_symbols of app>Bearer< random_URL-safe_text_string_in_Base64_encoding >`".\
Файл: "`project/middlewares.py`"

Создана модель сессий пользователя по маршруту: "`project/db/models.py`"
