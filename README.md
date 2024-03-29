Проект Рейтинги&Жанры
============

### Описание

Проект собирает **отзывы** пользователей на **произведения**. Сами
произведения в R&G не хранятся, здесь нельзя посмотреть фильм или послушать
музыку.

Произведения делятся на **категории**, такие как «Книги», «Фильмы», «Музыка».
Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все»
и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и
вторая сюита Баха. Список категорий может быть расширен (например, можно
добавить категорию «Изобразительное искусство» или «Ювелирка»).

Произведению может быть присвоен **жанр** из списка предустановленных (например,
«Сказка», «Рок» или «Артхаус»).

Добавлять произведения, категории и жанры может только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые
**отзывы** и ставят произведению оценку в диапазоне от одного до десяти (целое
число); из пользовательских оценок формируется усреднённая оценка произведения —
**рейтинг** (целое число). На одно произведение пользователь может оставить
только один отзыв.

Пользователи могут оставлять **комментарии** к отзывам.

Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные
пользователи.

 

### Запуск проекта:

-   Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/momtheprogram/api_rating_genres.git

cd api_yamdb
```
-   Cоздать и активировать виртуальное окружение.

-   Windows:
```bash
python -m venv venv

. venv/Scripts/activate
```

Linux/macOS:
```bash
python3 -m venv venv

source venv/bin/activate
```

-   Установить зависимости из файла requirements.txt:

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

-   Выполнить миграции:

```bash
python manage.py migrate
```

- При желании можете заргузить тестовые данные из CSV:

```bash
python manage.py importcsv
```

-   Запустить проект:

```bash
python manage.py runserver
```

### Регистрация пользователя

Регистрация нового пользователя:

```
POST /api/v1/auth/signup/
```

 

```js
{
   "email": "newuser@yandex.ru",
   "username": "newuser"
}
```
После чего, на почту пользователя придёт код, который надо будет отправить вместе с username по адресу /api/v1/auth/token/:

```
POST /api/v1/auth/token/
```

```js
{
  "username": "newuser",
  "confirmation_code": "12345"
}
```

После получения JWT-токена пользователь может работать с API проекта, отправляя этот токен при каждом запросе.

### Примеры работы с API для администратора

Добавление категории:

```
POST /api/v1/categories/
```

``` js
{
  "name": "Books",
  "slug": "1"
}
```

Удаление категории:

```
DELETE /api/v1/categories/{slug}/
```

Добавление жанра:

```
POST /api/v1/genres/
```

``` json
{
  "name": "Fantasy",
  "slug": "26"
}
```

Удаление жанра:

```
DELETE /api/v1/genres/{slug}/
```


### Использованные технологии:

-   Gроект написан на Python с использованием веб-фреймворка Django REST Framework
-   Библиотека Simple JWT - работа с JWT-токеном
-   Библиотека django-filter - фильтрация запросов
-   База данных - SQLite
-   Cистема управления версиями - git


 

### Авторы:

1.  [momtheprogram](https://github.com/momtheprogram) (Тимлид - Разработчик 1
    “Auth/Users”)

2.  [Stein-NN](https://github.com/Stein-NN) (Разработчик 2
    “Categories/Genres/Titles”)

3.  [iyenveyg](https://github.com/iyenveyg) (Разработчик 3 “Review/Comments”)
