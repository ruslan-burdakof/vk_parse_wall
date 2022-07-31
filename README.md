# vk_parse [![PyPI](https://img.shields.io/pypi/v/vk_api.svg)](https://pypi.org/project/vk_api/) ![Python 3.x](https://img.shields.io/pypi/pyversions/vk_api.svg)![vk_api]()
**vk_parse_wall** – Python модуль для парсинга и очистки стены в ВКонтакте (vk.com API wrapper)

Сохранение всех постов c колличеством лайков не менее 5ти, в папке *mem/* и базе данных SQLite *mem.s3db*
```python
from connect import get_session
from utils import checking_for_nice_OnlyLikes
from parse import iterate_wall_get, save_wall

# Повторный вызов при наличии файла "last_session.pkl"
# не требует логина и пароля
session = get_session("login", "password")
offset = 0 # Смещение выбора первой записи
max_count = 1000 # Максимальное колличество записей
min_likes = 5 # Минимальное колличество лайков
# Функция для проверки колличества лайков
checking = lambda post: checking_for_nice_OnlyLikes(post, min_likes)
wall = iterate_wall_get(session, offset, max_count = max_count)
save_wall(wall, checking)
```
Ещё один вариант для сохранения
```python -m parse.py "login" "password"```
Повторный запуск без логина и пароля

Удаление всех записей со стены
```python
from connect import get_session
from utils import checking_for_nice_OnlyLikes
from parse import iterate_wall_get, save_wall

# Повторный вызов при наличии файла "last_session.pkl"
# не требует логина и пароля
session = get_session("login", "password")
offset = 0 # Смещение выбора первой записи
max_count = 1000 # Максимальное колличество записей
wall = iterate_wall_get(session, offset, max_count = max_count)
data = cleare_wall(session, wall)
```