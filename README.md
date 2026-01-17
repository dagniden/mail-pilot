# Mail Pilot - Сервис управления рассылками

**Техническое задание и документация проекта**

---

## Навигация
- [Требования](./Требования.md)
- [Вопросы и ответы](./Вопросы.md)

## 📋 Содержание

1. [Введение](#введение)
2. [Бизнес-процессы и Use Cases](#1-бизнес-процессы-и-use-cases)
3. [Архитектура приложений Django](#2-архитектура-приложений-django)
4. [Модели данных (концептуальная схема)](#3-модели-данных-концептуальная-схема)
5. [Детальные спецификации моделей](#4-детальные-спецификации-моделей)
6. [Пользовательские экраны](#5-пользовательские-экраны)
7. [Views и маршрутизация](#6-views-и-маршрутизация)
8. [Права доступа и роли](#7-права-доступа-и-роли)
9. [Команды управления](#8-команды-управления)
10. [Настройки и конфигурация](#9-настройки-и-конфигурация)
11. [Критерии приемки](#10-критерии-приемки)

---

## Введение

**Mail Pilot** — веб-приложение на Django для управления email-рассылками. Система позволяет пользователям создавать списки получателей, готовить сообщения и планировать отправку рассылок с детальной статистикой и логированием.

### Цели проекта

- Централизованное управление email-рассылками
- Планирование и автоматизация отправки
- Детальная аналитика и логирование
- Разграничение прав доступа (Пользователи и Менеджеры)
- Масштабируемая архитектура

### Технологический стек

- **Backend**: Django 4.x+ / Python 3.13+
- **Database**: PostgreSQL (опционально SQLite для разработки)
- **Task Queue**: Django Management Commands (Celery в будущем)
- **Email**: Django email backend (SMTP)
- **Caching**: Django Cache Framework
- **Dependency Management**: Poetry

---

## 1. Бизнес-процессы и Use Cases

### 1.1 Регистрация и аутентификация

**Процесс:** Новый пользователь регистрируется в системе и получает доступ к функционалу.

**Use Cases:**

#### UC-1.1: Регистрация пользователя
```
Актор: Гость
Предусловия: Пользователь не зарегистрирован
Основной поток:
1. Пользователь переходит на страницу регистрации
2. Заполняет форму (email, пароль, имя, телефон, страна)
3. Система отправляет код подтверждения на email
4. Пользователь вводит код подтверждения
5. Система активирует аккаунт (is_active=True)
Результат: Пользователь зарегистрирован и может войти в систему
```

#### UC-1.2: Вход в систему
```
Актор: Зарегистрированный пользователь
Предусловия: Пользователь имеет активный аккаунт
Основной поток:
1. Пользователь вводит email и пароль
2. Система проверяет учетные данные и статус is_active
3. При успехе - создается сессия, пользователь перенаправляется на главную
Альтернативный поток:
- Если is_active=False → отказ в доступе
- Неверные учетные данные → сообщение об ошибке
```

#### UC-1.3: Восстановление пароля
```
Актор: Зарегистрированный пользователь
Основной поток:
1. Пользователь запрашивает восстановление пароля
2. Система отправляет ссылку на email
3. Пользователь переходит по ссылке и устанавливает новый пароль
4. Система сохраняет новый пароль и подтверждает изменение
```

---

### 1.2 Управление получателями (клиентами)

**Процесс:** Пользователь создает и управляет списком получателей рассылок.

**Use Cases:**

#### UC-2.1: Создание получателя
```
Актор: Авторизованный пользователь
Основной поток:
1. Пользователь открывает страницу "Получатели"
2. Нажимает "Создать получателя"
3. Заполняет форму (email*, ФИО*, комментарий)
4. Система проверяет уникальность email
5. Сохраняет получателя с привязкой к owner (текущий пользователь)
Результат: Новый получатель добавлен в базу
```

#### UC-2.2: Просмотр списка получателей
```
Актор: Авторизованный пользователь
Основной поток:
1. Пользователь открывает страницу "Получатели"
2. Система отображает список получателей, принадлежащих пользователю
3. Для каждого получателя показаны: email, ФИО, комментарий
4. Доступны кнопки редактирования и удаления
```

#### UC-2.3: Редактирование/Удаление получателя
```
Актор: Авторизованный пользователь
Предусловия: Пользователь - владелец получателя
Основной поток:
1. Пользователь выбирает получателя из списка
2. Нажимает "Редактировать" или "Удалить"
3. Система проверяет права (owner == current_user)
4. Выполняет операцию
```

---

### 1.3 Управление сообщениями

**Процесс:** Пользователь создает шаблоны сообщений для рассылок.

**Use Cases:**

#### UC-3.1: Создание сообщения
```
Актор: Авторизованный пользователь
Основной поток:
1. Пользователь открывает страницу "Сообщения"
2. Нажимает "Создать сообщение"
3. Заполняет форму (тема письма*, тело письма*)
4. Система сохраняет сообщение с привязкой к owner
Результат: Новое сообщение создано и доступно для использования в рассылках
```

#### UC-3.2: CRUD операции над сообщениями
```
Аналогично UC-2.2 и UC-2.3 для получателей
```

---

### 1.4 Управление рассылками

**Процесс:** Пользователь создает рассылку, связывая сообщение с получателями и планируя отправку.

**Use Cases:**

#### UC-4.1: Создание рассылки
```
Актор: Авторизованный пользователь
Основной поток:
1. Пользователь открывает страницу "Рассылки"
2. Нажимает "Создать рассылку"
3. Заполняет форму:
   - Выбирает сообщение (из своих)
   - Выбирает получателей (множественный выбор)
   - Указывает start_time (дата/время начала)
   - Указывает end_time (дата/время окончания)
4. Система валидирует:
   - start_time не в прошлом
   - start_time < end_time
5. Сохраняет рассылку со статусом "Создана"
Результат: Рассылка создана и готова к запуску
```

#### UC-4.2: Просмотр детальной информации о рассылке
```
Актор: Авторизованный пользователь
Основной поток:
1. Пользователь открывает детальную страницу рассылки
2. Система обновляет статус (update_status()):
   - Если now < start_time → "Создана"
   - Если start_time <= now <= end_time → "Запущена"
   - Если now > end_time → "Завершена"
3. Отображает:
   - Информацию о рассылке (сообщение, получатели, время, статус)
   - Список попыток отправки (если есть)
   - Кнопку "Запустить рассылку" (если статус = "Запущена")
```

#### UC-4.3: Редактирование рассылки
```
Актор: Авторизованный пользователь
Предусловия: Пользователь - владелец рассылки
Ограничения: Можно редактировать только рассылки со статусом "Создана"
Основной поток:
1. Пользователь открывает форму редактирования
2. Изменяет параметры рассылки
3. Система валидирует и сохраняет изменения
```

---

### 1.5 Отправка рассылки

**Процесс:** Запуск отправки писем получателям с логированием попыток.

**Use Cases:**

#### UC-5.1: Ручной запуск рассылки через интерфейс
```
Актор: Авторизованный пользователь
Предусловия:
- Рассылка принадлежит пользователю
- Статус рассылки = "Запущена"
Основной поток:
1. Пользователь открывает детальную страницу рассылки
2. Нажимает кнопку "Запустить рассылку"
3. Система проверяет временное окно (start_time <= now <= end_time)
4. Для каждого получателя:
   a. Вызывает send_mail()
   b. Создает запись MailingAttempt:
      - При успехе: status='Успешно', server_response='OK'
      - При ошибке: status='Не успешно', server_response=str(error)
5. Система показывает результат отправки
Результат: Письма отправлены, попытки залогированы
```

#### UC-5.2: Запуск рассылки через командную строку
```
Актор: Система/Администратор
Команда: python manage.py send_mailings
Основной поток:
1. Команда находит все рассылки:
   - start_time <= now <= end_time
   - status = "Создана" или "Запущена"
2. Для каждой рассылки выполняет отправку (аналогично UC-5.1)
3. Логирует результаты в stdout
```

---

### 1.6 Просмотр статистики

**Процесс:** Пользователь просматривает аналитику по своим рассылкам.

**Use Cases:**

#### UC-6.1: Главная страница со статистикой
```
Актор: Авторизованный пользователь
Основной поток:
1. Пользователь открывает главную страницу
2. Система отображает (для текущего пользователя):
   - Общее количество рассылок
   - Количество активных рассылок (статус "Запущена")
   - Количество уникальных получателей
3. Для менеджера - статистика по всем пользователям
```

#### UC-6.2: Детальная статистика по рассылке
```
Актор: Авторизованный пользователь
Основной поток:
1. Пользователь открывает детальную страницу рассылки
2. Система отображает:
   - Общее количество попыток отправки
   - Количество успешных попыток
   - Количество неуспешных попыток
   - Список всех попыток с деталями (время, статус, ответ сервера)
```

---

### 1.7 Управление пользователями (для Менеджеров)

**Процесс:** Менеджер управляет пользователями сервиса.

**Use Cases:**

#### UC-7.1: Просмотр списка пользователей
```
Актор: Менеджер
Предусловия: Пользователь входит в группу "Менеджеры"
Основной поток:
1. Менеджер открывает страницу "Пользователи"
2. Система отображает список всех пользователей с информацией:
   - Email, ФИО, дата регистрации, статус (активен/заблокирован)
3. Доступны кнопки "Просмотр" и "Блокировать/Разблокировать"
```

#### UC-7.2: Блокировка пользователя
```
Актор: Менеджер
Основной поток:
1. Менеджер выбирает пользователя из списка
2. Нажимает "Блокировать"
3. Система устанавливает is_active=False
4. Пользователь больше не может войти в систему
```

#### UC-7.3: Отключение рассылки
```
Актор: Менеджер
Основной поток:
1. Менеджер просматривает список всех рассылок
2. Выбирает рассылку и нажимает "Отключить"
3. Система устанавливает статус "Завершена" или помечает как отключенную
4. Рассылка больше не может быть запущена
```

---

## 2. Архитектура приложений Django

### Структура проекта

```
mail-pilot/
├── config/                      # Настройки проекта
│   ├── __init__.py
│   ├── settings.py             # Основные настройки
│   ├── urls.py                 # Главный URL роутер
│   └── wsgi.py
├── users/                       # Приложение: пользователи
│   ├── models.py               # CustomUser
│   ├── views.py                # Регистрация, вход, профиль
│   ├── forms.py                # UserCreationForm, LoginForm
│   ├── urls.py                 # Маршруты пользователей
│   └── management/
│       └── commands/
│           └── create_groups.py  # Создание группы "Менеджеры"
├── mailings/                    # Приложение: рассылки
│   ├── models.py               # Recipient, Message, Mailing, MailingAttempt
│   ├── views.py                # CRUD для всех моделей, запуск рассылок
│   ├── forms.py                # Формы для моделей
│   ├── urls.py                 # Маршруты рассылок
│   ├── services.py             # Бизнес-логика отправки
│   └── management/
│       └── commands/
│           └── send_mailings.py  # Команда запуска рассылок
├── templates/                   # Шаблоны
│   ├── base.html               # Базовый шаблон
│   ├── index.html              # Главная страница
│   ├── users/
│   ├── mailings/
│   └── registration/           # Шаблоны аутентификации
├── static/                      # Статические файлы
├── media/                       # Загружаемые файлы (аватары)
├── .env                         # Переменные окружения (не в Git!)
├── .env.sample                 # Шаблон .env
├── pyproject.toml              # Зависимости Poetry
├── poetry.lock
└── manage.py
```

### Приложения Django

| Приложение | Назначение | Модели |
|------------|------------|---------|
| `users` | Аутентификация и управление пользователями | `CustomUser` |
| `mailings` | Управление рассылками, сообщениями, получателями | `Recipient`, `Message`, `Mailing`, `MailingAttempt` |

---

## 3. Модели данных (концептуальная схема)

### Список моделей

#### Приложение `users`

| Модель | Описание | Ключевые связи |
|--------|----------|----------------|
| `CustomUser` | Пользователь системы (наследуется от AbstractUser) | - |

#### Приложение `mailings`

| Модель | Описание | Ключевые связи |
|--------|----------|----------------|
| `Recipient` | Получатель рассылки (клиент) | `owner` → CustomUser |
| `Message` | Шаблон сообщения для рассылки | `owner` → CustomUser |
| `Mailing` | Рассылка (связывает сообщение и получателей) | `owner` → CustomUser<br>`message` → Message<br>`recipients` → Recipient (M2M) |
| `MailingAttempt` | Попытка отправки письма | `mailing` → Mailing<br>`recipient` → Recipient (опционально) |

### Концептуальная ERD

```
┌─────────────────┐
│   CustomUser    │
│  (users)        │
│─────────────────│
│ id (PK)         │
│ email (unique)  │
│ password        │
│ is_active       │
│ ...             │
└────────┬────────┘
         │ owner (FK)
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│   Recipient     │    │    Message      │
│  (mailings)     │    │  (mailings)     │
│─────────────────│    │─────────────────│
│ id (PK)         │    │ id (PK)         │
│ email (unique)  │    │ subject         │
│ full_name       │    │ body            │
│ comment         │    │ owner (FK)      │
│ owner (FK)      │    └────────┬────────┘
└────────┬────────┘             │
         │                      │ message (FK)
         │                      │
         │            ┌─────────▼────────┐
         │            │    Mailing       │
         │            │  (mailings)      │
         │            │──────────────────│
         │            │ id (PK)          │
         │◄───────────┤ recipients (M2M) │
         │ M2M        │ message (FK)     │
         │            │ start_time       │
         │            │ end_time         │
         │            │ status           │
         │            │ owner (FK)       │
         │            └─────────┬────────┘
         │                      │ mailing (FK)
         │                      ▼
         │            ┌─────────────────┐
         └────────────┤ MailingAttempt  │
          recipient   │  (mailings)     │
          (FK, opt)   │─────────────────│
                      │ id (PK)         │
                      │ mailing (FK)    │
                      │ recipient (FK)  │
                      │ attempt_time    │
                      │ status          │
                      │ server_response │
                      └─────────────────┘
```

---
### Схема таблиц

![Database Schema](docs/mail-pilot-db.png)



## 4. Детальные спецификации моделей

### 4.1 CustomUser (приложение `users`)

**Наследуется от:** `django.contrib.auth.models.AbstractUser`

**Назначение:** Пользователь системы с расширенными полями.

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `email` | EmailField | unique=True, blank=False | Email (используется для входа) |
| `password` | CharField | - | Хэш пароля (AbstractUser) |
| `first_name` | CharField | max_length=150 | Имя |
| `last_name` | CharField | max_length=150 | Фамилия |
| `avatar` | ImageField | upload_to='avatars/', blank=True, null=True | Фото профиля |
| `phone_number` | CharField | max_length=20, blank=True, null=True | Телефон |
| `country` | CharField | max_length=100, blank=True, null=True | Страна |
| `verification_code` | CharField | max_length=6, blank=True, null=True | Код подтверждения email |
| `is_active` | BooleanField | default=False | Активен ли аккаунт |
| `is_staff` | BooleanField | default=False | Доступ к админке (AbstractUser) |
| `date_joined` | DateTimeField | auto_now_add=True | Дата регистрации |

**Методы:**

```python
def __str__(self):
    return self.email

def generate_verification_code(self):
    """Генерирует 6-значный код подтверждения"""
    pass

def send_verification_email(self):
    """Отправляет код подтверждения на email"""
    pass
```

**Meta:**
```python
class Meta:
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'
    ordering = ['-date_joined']
```

**Настройки:**
```python
# settings.py
AUTH_USER_MODEL = 'users.CustomUser'
USERNAME_FIELD = 'email'
REQUIRED_FIELDS = []  # email уже обязателен как USERNAME_FIELD
```

---

### 4.2 Recipient (приложение `mailings`)

**Назначение:** Получатель рассылки (клиент в базе пользователя).

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `email` | EmailField | unique=True, blank=False | Email получателя (уникальный) |
| `full_name` | CharField | max_length=255, blank=False | Ф.И.О. |
| `comment` | TextField | blank=True | Комментарий |
| `owner` | ForeignKey | to=CustomUser, on_delete=CASCADE, related_name='recipients' | Владелец |
| `created_at` | DateTimeField | auto_now_add=True | Дата создания |

**Методы:**
```python
def __str__(self):
    return f"{self.full_name} ({self.email})"
```

**Meta:**
```python
class Meta:
    verbose_name = 'Получатель'
    verbose_name_plural = 'Получатели'
    ordering = ['full_name']
    permissions = [
        ('can_view_all_recipients', 'Can view all recipients'),
    ]
```

---

### 4.3 Message (приложение `mailings`)

**Назначение:** Шаблон сообщения для рассылки.

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `subject` | CharField | max_length=255, blank=False | Тема письма |
| `body` | TextField | blank=False | Тело письма (может содержать HTML) |
| `owner` | ForeignKey | to=CustomUser, on_delete=CASCADE, related_name='messages' | Владелец |
| `created_at` | DateTimeField | auto_now_add=True | Дата создания |
| `updated_at` | DateTimeField | auto_now=True | Дата последнего изменения |

**Методы:**
```python
def __str__(self):
    return self.subject
```

**Meta:**
```python
class Meta:
    verbose_name = 'Сообщение'
    verbose_name_plural = 'Сообщения'
    ordering = ['-created_at']
    permissions = [
        ('can_view_all_messages', 'Can view all messages'),
    ]
```

---

### 4.4 Mailing (приложение `mailings`)

**Назначение:** Рассылка, связывающая сообщение с получателями.

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `message` | ForeignKey | to=Message, on_delete=PROTECT, related_name='mailings' | Сообщение |
| `recipients` | ManyToManyField | to=Recipient | Получатели |
| `start_time` | DateTimeField | blank=False | Дата и время начала |
| `end_time` | DateTimeField | blank=False | Дата и время окончания |
| `status` | CharField | max_length=20, choices=STATUS_CHOICES, default='Создана' | Статус |
| `owner` | ForeignKey | to=CustomUser, on_delete=CASCADE, related_name='mailings' | Владелец |
| `created_at` | DateTimeField | auto_now_add=True | Дата создания |

**Choices:**
```python
STATUS_CHOICES = [
    ('Создана', 'Создана'),
    ('Запущена', 'Запущена'),
    ('Завершена', 'Завершена'),
]
```

**Методы:**
```python
def __str__(self):
    return f"Рассылка #{self.id}: {self.message.subject}"

def update_status(self):
    """Динамически обновляет статус на основе текущего времени"""
    from django.utils import timezone
    now = timezone.now()

    if now < self.start_time:
        new_status = 'Создана'
    elif self.start_time <= now <= self.end_time:
        new_status = 'Запущена'
    else:
        new_status = 'Завершена'

    if self.status != new_status:
        self.status = new_status
        self.save(update_fields=['status'])

def can_be_sent(self):
    """Проверяет, можно ли отправить рассылку сейчас"""
    from django.utils import timezone
    now = timezone.now()
    return self.start_time <= now <= self.end_time

def clean(self):
    """Валидация полей"""
    from django.core.exceptions import ValidationError
    from django.utils import timezone

    if self.start_time and self.start_time < timezone.now():
        raise ValidationError('Дата начала не может быть в прошлом')

    if self.start_time and self.end_time and self.start_time >= self.end_time:
        raise ValidationError('Дата начала должна быть раньше даты окончания')
```

**Meta:**
```python
class Meta:
    verbose_name = 'Рассылка'
    verbose_name_plural = 'Рассылки'
    ordering = ['-created_at']
    permissions = [
        ('can_view_all_mailings', 'Can view all mailings'),
        ('can_disable_mailing', 'Can disable mailing'),
    ]
```

---

### 4.5 MailingAttempt (приложение `mailings`)

**Назначение:** Попытка отправки письма (лог).

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `mailing` | ForeignKey | to=Mailing, on_delete=CASCADE, related_name='attempts' | Рассылка |
| `recipient` | ForeignKey | to=Recipient, on_delete=SET_NULL, null=True, blank=True | Получатель (опционально) |
| `attempt_time` | DateTimeField | auto_now_add=True | Дата и время попытки |
| `status` | CharField | max_length=20, choices=STATUS_CHOICES | Статус ('Успешно'/'Не успешно') |
| `server_response` | TextField | blank=True | Ответ почтового сервера или текст ошибки |

**Choices:**
```python
STATUS_CHOICES = [
    ('Успешно', 'Успешно'),
    ('Не успешно', 'Не успешно'),
]
```

**Методы:**
```python
def __str__(self):
    recipient_info = f" → {self.recipient.email}" if self.recipient else ""
    return f"Попытка #{self.id}{recipient_info}: {self.status}"
```

**Meta:**
```python
class Meta:
    verbose_name = 'Попытка рассылки'
    verbose_name_plural = 'Попытки рассылок'
    ordering = ['-attempt_time']
```

---

### Детальная ERD диаграмма

```
┌──────────────────────────────────────┐
│         CustomUser (users)           │
├──────────────────────────────────────┤
│ PK │ id: BigAutoField                │
│ UK │ email: EmailField               │
│    │ password: CharField             │
│    │ first_name: CharField(150)      │
│    │ last_name: CharField(150)       │
│    │ avatar: ImageField              │
│    │ phone_number: CharField(20)     │
│    │ country: CharField(100)         │
│    │ verification_code: CharField(6) │
│    │ is_active: BooleanField         │
│    │ is_staff: BooleanField          │
│    │ date_joined: DateTimeField      │
└──────────────┬───────────────────────┘
               │ owner (FK, CASCADE)
               ├───────────────────────────────┐
               │                               │
               ▼                               ▼
┌──────────────────────────────────┐ ┌────────────────────────────────┐
│    Recipient (mailings)          │ │     Message (mailings)         │
├──────────────────────────────────┤ ├────────────────────────────────┤
│ PK │ id: BigAutoField            │ │ PK │ id: BigAutoField          │
│ UK │ email: EmailField           │ │    │ subject: CharField(255)   │
│    │ full_name: CharField(255)   │ │    │ body: TextField           │
│    │ comment: TextField          │ │ FK │ owner → CustomUser        │
│ FK │ owner → CustomUser          │ │    │ created_at: DateTimeField │
│    │ created_at: DateTimeField   │ │    │ updated_at: DateTimeField │
└──────────────┬───────────────────┘ └────────────┬───────────────────┘
               │                                  │
               │ recipients (M2M)                 │ message (FK, PROTECT)
               │                                  │
               │                ┌─────────────────▼──────────────────┐
               │                │        Mailing (mailings)          │
               │                ├────────────────────────────────────┤
               │                │ PK │ id: BigAutoField              │
               └────────────────┤ FK │ message → Message             │
                     M2M        │ M2M│ recipients → Recipient        │
                                │    │ start_time: DateTimeField     │
                                │    │ end_time: DateTimeField       │
                                │    │ status: CharField(20)         │
                                │ FK │ owner → CustomUser            │
                                │    │ created_at: DateTimeField     │
                                └────────────┬───────────────────────┘
                                             │ mailing (FK, CASCADE)
                                             ▼
                      ┌────────────────────────────────────────────────┐
                      │        MailingAttempt (mailings)               │
                      ├────────────────────────────────────────────────┤
                      │ PK │ id: BigAutoField                          │
                      │ FK │ mailing → Mailing                         │
                      │ FK │ recipient → Recipient (NULL, SET_NULL)    │
                      │    │ attempt_time: DateTimeField (auto_now_add)│
                      │    │ status: CharField(20)                     │
                      │    │ server_response: TextField                │
                      └────────────────────────────────────────────────┘
```

---

## 5. Пользовательские экраны

### 5.1 Главная страница (`index.html`)

**URL:** `/`
**View:** `IndexView` (TemplateView)
**Доступ:** Публичный

**Элементы интерфейса:**

```
┌─────────────────────────────────────────────────────────┐
│ [Логотип Mail Pilot]        [Вход] [Регистрация]       │ ← Header (для гостей)
│ [Логотип Mail Pilot]  [Имя пользователя] [Выход]       │ ← Header (для авторизованных)
├─────────────────────────────────────────────────────────┤
│              Добро пожаловать в Mail Pilot!             │
│                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │  Всего рассылок     │  │  Активных рассылок  │     │
│  │        42           │  │         12          │     │
│  └─────────────────────┘  └─────────────────────┘     │
│                                                         │
│  ┌─────────────────────┐                               │
│  │  Уникальных         │                               │
│  │  получателей: 156   │                               │
│  └─────────────────────┘                               │
│                                                         │
│  [Перейти к рассылкам] [Мои получатели] [Мои сообщения]│
└─────────────────────────────────────────────────────────┘
```

**Поля и данные:**
- **Всего рассылок:** `Mailing.objects.filter(owner=request.user).count()`
- **Активных рассылок:** `Mailing.objects.filter(owner=request.user, status='Запущена').count()`
- **Уникальных получателей:** `Recipient.objects.filter(owner=request.user).count()`

**Навигация:**
- Header содержит ссылки на основные разделы (только для авторизованных):
  - Рассылки
  - Сообщения
  - Получатели
  - Профиль
  - (Для менеджеров) Пользователи

---

### 5.2 Регистрация (`users/register.html`)

**URL:** `/users/register/`
**View:** `RegisterView` (CreateView)
**Доступ:** Публичный

**Форма:**

| Поле | Тип input | Валидация | Обязательное |
|------|-----------|-----------|--------------|
| Email | email | EmailValidator, unique | ✓ |
| Пароль | password | MinLength(8) | ✓ |
| Подтверждение пароля | password | Должен совпадать с паролем | ✓ |
| Имя | text | MaxLength(150) | ✓ |
| Фамилия | text | MaxLength(150) | ✓ |
| Телефон | tel | - | - |
| Страна | text | MaxLength(100) | - |
| Аватар | file | ImageField | - |

**Кнопки:**
- **[Зарегистрироваться]** → POST → отправка кода на email → редирект на страницу подтверждения
- **[Уже есть аккаунт? Войти]** → ссылка на `/users/login/`

**Поведение:**
1. Пользователь заполняет форму
2. При отправке:
   - Создается пользователь с `is_active=False`
   - Генерируется `verification_code` (6 цифр)
   - Отправляется письмо с кодом
   - Редирект на `/users/verify/`

---

### 5.3 Подтверждение email (`users/verify.html`)

**URL:** `/users/verify/`
**View:** `VerifyEmailView` (FormView)
**Доступ:** Публичный (после регистрации)

**Форма:**

| Поле | Тип input | Описание |
|------|-----------|----------|
| Код подтверждения | text | 6-значный код из письма |

**Кнопки:**
- **[Подтвердить]** → POST → проверка кода → установка `is_active=True` → редирект на логин
- **[Отправить код повторно]** → генерация нового кода и отправка письма

---

### 5.4 Вход (`registration/login.html`)

**URL:** `/users/login/`
**View:** `LoginView` (встроенный Django)
**Доступ:** Публичный

**Форма:**

| Поле | Тип input | Обязательное |
|------|-----------|--------------|
| Email | email | ✓ |
| Пароль | password | ✓ |
| Запомнить меня | checkbox | - |

**Кнопки:**
- **[Войти]** → POST → аутентификация → редирект на `/`
- **[Забыли пароль?]** → ссылка на `/users/password-reset/`
- **[Зарегистрироваться]** → ссылка на `/users/register/`

---

### 5.5 Список получателей (`mailings/recipient_list.html`)

**URL:** `/mailings/recipients/`
**View:** `RecipientListView` (ListView)
**Доступ:** Авторизованные пользователи

**Таблица:**

| Email | Ф.И.О. | Комментарий | Действия |
|-------|--------|-------------|----------|
| user@example.com | Иван Иванов | VIP клиент | [✏️ Редактировать] [🗑️ Удалить] |
| ... | ... | ... | ... |

**Кнопки:**
- **[+ Создать получателя]** → ссылка на `/mailings/recipients/create/`

**Фильтрация:**
- QuerySet ограничен: `Recipient.objects.filter(owner=request.user)`

---

### 5.6 Создание/Редактирование получателя (`mailings/recipient_form.html`)

**URL:**
- Создание: `/mailings/recipients/create/`
- Редактирование: `/mailings/recipients/<pk>/edit/`

**View:** `RecipientCreateView` / `RecipientUpdateView`
**Доступ:** Авторизованные (владельцы для редактирования)

**Форма:**

| Поле | Тип input | Валидация | Обязательное |
|------|-----------|-----------|--------------|
| Email | email | EmailValidator, unique | ✓ |
| Ф.И.О. | text | MaxLength(255) | ✓ |
| Комментарий | textarea | - | - |

**Кнопки:**
- **[Сохранить]** → POST → сохранение с `owner=request.user` → редирект на список
- **[Отмена]** → ссылка на список получателей

---

### 5.7 Список сообщений (`mailings/message_list.html`)

**URL:** `/mailings/messages/`
**View:** `MessageListView` (ListView)
**Доступ:** Авторизованные пользователи

**Карточки сообщений:**

```
┌────────────────────────────────────────┐
│ 📧 Тема: Скидка 50% на все товары     │
│ Текст: Спешите, акция до конца месяца!│
│ Создано: 01.01.2026                    │
│ [✏️ Редактировать] [🗑️ Удалить]       │
└────────────────────────────────────────┘
```

**Кнопки:**
- **[+ Создать сообщение]** → ссылка на `/mailings/messages/create/`

---

### 5.8 Создание/Редактирование сообщения (`mailings/message_form.html`)

**URL:**
- Создание: `/mailings/messages/create/`
- Редактирование: `/mailings/messages/<pk>/edit/`

**View:** `MessageCreateView` / `MessageUpdateView`

**Форма:**

| Поле | Тип input | Обязательное |
|------|-----------|--------------|
| Тема письма | text | ✓ |
| Тело письма | textarea (WYSIWYG опционально) | ✓ |

**Кнопки:**
- **[Сохранить]** → POST → редирект на список
- **[Отмена]** → список сообщений

---

### 5.9 Список рассылок (`mailings/mailing_list.html`)

**URL:** `/mailings/`
**View:** `MailingListView` (ListView)
**Доступ:** Авторизованные пользователи

**Таблица:**

| ID | Сообщение | Получателей | Начало | Окончание | Статус | Действия |
|----|-----------|-------------|--------|-----------|--------|----------|
| 42 | Скидка 50% | 15 | 01.01.2026 10:00 | 05.01.2026 23:59 | 🟢 Запущена | [👁️ Просмотр] [✏️ Редактировать] [🗑️ Удалить] |
| 41 | Новинки | 8 | 20.12.2025 | 31.12.2025 | 🔴 Завершена | [👁️ Просмотр] |

**Кнопки:**
- **[+ Создать рассылку]** → `/mailings/create/`

**Цветовая индикация статусов:**
- 🟡 Создана (серый)
- 🟢 Запущена (зеленый)
- 🔴 Завершена (красный)

---

### 5.10 Создание/Редактирование рассылки (`mailings/mailing_form.html`)

**URL:**
- Создание: `/mailings/create/`
- Редактирование: `/mailings/<pk>/edit/`

**View:** `MailingCreateView` / `MailingUpdateView`

**Форма:**

| Поле | Тип input | Валидация | Обязательное |
|------|-----------|-----------|--------------|
| Сообщение | select | ForeignKey, только свои сообщения | ✓ |
| Получатели | select multiple / checkboxes | ManyToMany, только свои получатели | ✓ |
| Дата и время начала | datetime-local | Не в прошлом, раньше end_time | ✓ |
| Дата и время окончания | datetime-local | Позже start_time | ✓ |

**Кнопки:**
- **[Сохранить]** → POST → валидация → сохранение → редирект на детальную страницу
- **[Отмена]** → список рассылок

**Валидация (client-side + server-side):**
- start_time не может быть в прошлом
- start_time < end_time

---

### 5.11 Детальная информация о рассылке (`mailings/mailing_detail.html`)

**URL:** `/mailings/<pk>/`
**View:** `MailingDetailView` (DetailView)
**Доступ:** Владелец или менеджер

**Структура страницы:**

```
┌─────────────────────────────────────────────────────────┐
│ Рассылка #42: Скидка 50% на все товары                 │
│                                                         │
│ Статус: 🟢 Запущена                                     │
│ Сообщение: Скидка 50%...                               │
│ Получателей: 15                                         │
│ Начало: 01.01.2026 10:00                               │
│ Окончание: 05.01.2026 23:59                            │
│                                                         │
│ [▶️ Запустить рассылку]  [✏️ Редактировать]  [🗑️ Удалить]│
│                                                         │
│ ────────────────────────────────────────────────────── │
│                                                         │
│ Попытки отправки:                                       │
│                                                         │
│ ✅ 01.01.2026 10:05 → user@example.com: Успешно        │
│ ❌ 01.01.2026 10:05 → test@mail.com: SMTP Error        │
│ ✅ 01.01.2026 10:06 → client@corp.com: Успешно         │
│                                                         │
│ Статистика:                                             │
│ - Всего попыток: 15                                     │
│ - Успешных: 13                                          │
│ - Неуспешных: 2                                         │
└─────────────────────────────────────────────────────────┘
```

**Кнопки:**
- **[▶️ Запустить рассылку]** → POST `/mailings/<pk>/send/` → запуск отправки (видна только если `status='Запущена'`)
- **[✏️ Редактировать]** → `/mailings/<pk>/edit/` (только если владелец)
- **[🗑️ Удалить]** → POST `/mailings/<pk>/delete/` (только если владелец)

**Поведение:**
- При загрузке страницы вызывается `mailing.update_status()` (динамическое обновление статуса)
- Попытки отображаются в обратном хронологическом порядке

---

### 5.12 Страница запуска рассылки (встроена в detail)

**URL:** `/mailings/<pk>/send/` (POST)
**View:** `SendMailingView` (View)
**Доступ:** Владелец рассылки

**Процесс:**
1. Проверка прав (owner == request.user)
2. Проверка временного окна (`can_be_sent()`)
3. Для каждого получателя:
   - Попытка отправки через `send_mail()`
   - Создание `MailingAttempt` с результатом
4. Редирект обратно на детальную страницу с сообщением о результате

---

### 5.13 Список пользователей (для менеджеров) (`users/user_list.html`)

**URL:** `/users/`
**View:** `UserListView` (ListView)
**Доступ:** Группа "Менеджеры"

**Таблица:**

| Email | Ф.И.О. | Дата регистрации | Статус | Действия |
|-------|--------|------------------|--------|----------|
| user@example.com | Иван Иванов | 01.01.2026 | ✅ Активен | [👁️ Просмотр] [🚫 Блокировать] |
| blocked@test.com | Петр Петров | 15.12.2025 | 🚫 Заблокирован | [👁️ Просмотр] [✅ Разблокировать] |

**Кнопки:**
- **[🚫 Блокировать]** → POST → установка `is_active=False`
- **[✅ Разблокировать]** → POST → установка `is_active=True`

---

### 5.14 Детальная информация о пользователе (для менеджеров) (`users/user_detail.html`)

**URL:** `/users/<pk>/`
**View:** `UserDetailView` (DetailView)
**Доступ:** Группа "Менеджеры"

**Информация:**
- Email, Ф.И.О., телефон, страна
- Дата регистрации
- Статус (активен/заблокирован)
- Количество рассылок
- Количество получателей
- Количество сообщений

**Кнопки:**
- **[🚫 Блокировать пользователя]** / **[✅ Разблокировать]**

---

### 5.15 Восстановление пароля (`registration/password_reset_*.html`)

**URLs:**
- `/users/password-reset/` - форма запроса
- `/users/password-reset/done/` - подтверждение отправки
- `/reset/<uidb64>/<token>/` - форма ввода нового пароля
- `/reset/done/` - успех

**Views:** Встроенные Django views

**Последовательность:**
1. Пользователь вводит email
2. Система отправляет письмо со ссылкой
3. Пользователь переходит по ссылке
4. Вводит новый пароль
5. Успех → редирект на логин

---

## 6. Views и маршрутизация

### 6.1 Приложение `users`

**urls.py (`users/urls.py`):**

```python
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView, VerifyEmailView, ProfileView,
    UserListView, UserDetailView, ToggleUserActiveView
)

app_name = 'users'

urlpatterns = [
    # Аутентификация
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyEmailView.as_view(), name='verify'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Восстановление пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    # Профиль
    path('profile/', ProfileView.as_view(), name='profile'),

    # Управление пользователями (для менеджеров)
    path('', UserListView.as_view(), name='user_list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('<int:pk>/toggle-active/', ToggleUserActiveView.as_view(), name='toggle_active'),
]
```

**Views (`users/views.py`):**

| View | Тип | Шаблон | Доступ | Описание |
|------|-----|--------|--------|----------|
| `RegisterView` | CreateView | users/register.html | Публичный | Регистрация |
| `VerifyEmailView` | FormView | users/verify.html | Публичный | Подтверждение email |
| `ProfileView` | UpdateView | users/profile.html | @login_required | Редактирование профиля |
| `UserListView` | ListView | users/user_list.html | @permission_required | Список пользователей |
| `UserDetailView` | DetailView | users/user_detail.html | @permission_required | Детали пользователя |
| `ToggleUserActiveView` | View | - | @permission_required | Блокировка/разблокировка |

---

### 6.2 Приложение `mailings`

**urls.py (`mailings/urls.py`):**

```python
from django.urls import path
from .views import (
    # Получатели
    RecipientListView, RecipientCreateView,
    RecipientUpdateView, RecipientDeleteView,
    # Сообщения
    MessageListView, MessageCreateView,
    MessageUpdateView, MessageDeleteView,
    # Рассылки
    MailingListView, MailingCreateView,
    MailingDetailView, MailingUpdateView, MailingDeleteView,
    SendMailingView,
)

app_name = 'mailings'

urlpatterns = [
    # Получатели
    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/edit/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    # Сообщения
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    # Рассылки
    path('', MailingListView.as_view(), name='mailing_list'),
    path('create/', MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_update'),
    path('<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('<int:pk>/send/', SendMailingView.as_view(), name='mailing_send'),
]
```

**Views (`mailings/views.py`):**

| View | Тип | Миксины | Описание |
|------|-----|---------|----------|
| `RecipientListView` | ListView | LoginRequiredMixin | Фильтрует по owner |
| `RecipientCreateView` | CreateView | LoginRequiredMixin | Устанавливает owner=request.user в form_valid() |
| `RecipientUpdateView` | UpdateView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `RecipientDeleteView` | DeleteView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `MessageListView` | ListView | LoginRequiredMixin | Фильтрует по owner |
| `MessageCreateView` | CreateView | LoginRequiredMixin | Устанавливает owner |
| `MessageUpdateView` | UpdateView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `MessageDeleteView` | DeleteView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `MailingListView` | ListView | LoginRequiredMixin | Фильтрует по owner (или все для менеджеров) |
| `MailingCreateView` | CreateView | LoginRequiredMixin | Устанавливает owner |
| `MailingDetailView` | DetailView | LoginRequiredMixin | Вызывает update_status() |
| `MailingUpdateView` | UpdateView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `MailingDeleteView` | DeleteView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `SendMailingView` | View | LoginRequiredMixin, UserPassesTestMixin | Запускает отправку |

---

### 6.3 Главный маршрутизатор

**urls.py (`config/urls.py`):**

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mailings.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('users/', include('users.urls')),
    path('mailings/', include('mailings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 7. Права доступа и роли

### 7.1 Роли пользователей

| Роль | Группа Django | Описание |
|------|---------------|----------|
| **Пользователь** | (по умолчанию) | Обычный пользователь сервиса |
| **Менеджер** | `Менеджеры` | Пользователь с расширенными правами |

### 7.2 Права пользователей

**Пользователь может:**
- ✅ Создавать, просматривать, редактировать и удалять своих получателей
- ✅ Создавать, просматривать, редактировать и удалять свои сообщения
- ✅ Создавать, просматривать, редактировать и удалять свои рассылки
- ✅ Запускать свои рассылки
- ✅ Просматривать статистику по своим рассылкам
- ❌ Видеть чужие данные
- ❌ Управлять другими пользователями

**Менеджер может:**
- ✅ Всё, что может обычный пользователь
- ✅ Просматривать всех получателей (всех пользователей)
- ✅ Просматривать все сообщения (всех пользователей)
- ✅ Просматривать все рассылки (всех пользователей)
- ✅ Просматривать список пользователей
- ✅ Просматривать детальную информацию о пользователях
- ✅ Блокировать/разблокировать пользователей (is_active)
- ✅ Отключать рассылки
- ❌ Редактировать/удалять чужие получатели, сообщения, рассылки

### 7.3 Кастомные права (permissions)

**В Meta моделей определены:**

```python
# Recipient
permissions = [
    ('can_view_all_recipients', 'Can view all recipients'),
]

# Message
permissions = [
    ('can_view_all_messages', 'Can view all messages'),
]

# Mailing
permissions = [
    ('can_view_all_mailings', 'Can view all mailings'),
    ('can_disable_mailing', 'Can disable mailing'),
]

# CustomUser (в users)
permissions = [
    ('can_block_user', 'Can block user'),
]
```

### 7.4 Реализация проверки прав

**В Views:**

```python
# Фильтрация QuerySet по владельцу
def get_queryset(self):
    if self.request.user.has_perm('mailings.can_view_all_mailings'):
        # Менеджер видит все
        return Mailing.objects.all()
    # Пользователь видит только свои
    return Mailing.objects.filter(owner=self.request.user)

# Проверка владельца при редактировании/удалении
def test_func(self):
    obj = self.get_object()
    return obj.owner == self.request.user
```

**В шаблонах:**

```django
{% if perms.mailings.can_disable_mailing %}
    <a href="{% url 'mailings:mailing_disable' mailing.pk %}">Отключить</a>
{% endif %}

{% if mailing.owner == request.user %}
    <a href="{% url 'mailings:mailing_update' mailing.pk %}">Редактировать</a>
{% endif %}
```

### 7.5 Создание группы "Менеджеры"

**Management команда (`users/management/commands/create_groups.py`):**

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Создание группы Менеджеры с правами'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            permissions = Permission.objects.filter(
                codename__in=[
                    'can_view_all_recipients',
                    'can_view_all_messages',
                    'can_view_all_mailings',
                    'can_disable_mailing',
                    'can_block_user',
                ]
            )
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write('Группа уже существует')
```

**Запуск:**
```bash
python manage.py create_groups
```

---

## 8. Команды управления

### 8.1 Отправка рассылок (`send_mailings`)

**Файл:** `mailings/management/commands/send_mailings.py`

**Назначение:** Запуск отправки рассылок через командную строку (для cron/планировщика).

**Логика:**
1. Находит все рассылки, готовые к отправке:
   - `start_time <= now <= end_time`
   - `status` in ['Создана', 'Запущена']
2. Для каждой рассылки вызывает сервис отправки
3. Логирует результаты

**Пример кода:**

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from mailings.models import Mailing
from mailings.services import send_mailing

class Command(BaseCommand):
    help = 'Отправка рассылок, готовых к отправке'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
        ).exclude(status='Завершена')

        self.stdout.write(f'Найдено рассылок: {mailings.count()}')

        for mailing in mailings:
            try:
                result = send_mailing(mailing)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Рассылка #{mailing.id}: отправлено {result["success"]}/{result["total"]}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка в рассылке #{mailing.id}: {e}')
                )
```

**Запуск:**
```bash
python manage.py send_mailings
```

**Планирование (cron):**
```cron
*/10 * * * * cd /path/to/project && poetry run python manage.py send_mailings
```

---

### 8.2 Создание групп (`create_groups`)

**Описание:** См. раздел 7.5

---

## 9. Настройки и конфигурация

### 9.1 Переменные окружения (`.env`)

**Файл:** `.env` (не добавлять в Git!)

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mailpilot
# Или для SQLite: DATABASE_URL=sqlite:///db.sqlite3

# Email (Yandex example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@yandex.ru
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@yandex.ru

# Для разработки (вывод в консоль):
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Cache (опционально)
CACHE_BACKEND=django.core.cache.backends.dummy.DummyCache
```

**Шаблон (`.env.sample`):** Добавить в Git как образец для других разработчиков.

---

### 9.2 Settings.py

**Ключевые настройки:**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'users',
    'mailings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Email
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Login/Logout redirects
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

# Cache (для production)
CACHES = {
    'default': {
        'BACKEND': os.getenv('CACHE_BACKEND', 'django.core.cache.backends.dummy.DummyCache'),
    }
}
```

---

### 9.3 Зависимости (pyproject.toml)

```toml
[tool.poetry]
name = "mail-pilot"
version = "1.0.0"
description = "Email mailing service"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.13"
django = "^4.2"
python-dotenv = "^1.0.0"
psycopg2-binary = "^2.9"  # Для PostgreSQL
dj-database-url = "^2.1.0"
pillow = "^10.0"  # Для ImageField

[tool.poetry.group.dev.dependencies]
flake8 = "^6.0"
black = "^23.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**Установка:**
```bash
poetry install
```

---

## 10. Критерии приемки

### 10.1 Общие требования

- ✅ Проект выложен на GitHub
- ✅ Есть `.gitignore` (содержит `.env`, `db.sqlite3`, `media/`, `__pycache__/`, и т.д.)
- ✅ Есть файл зависимостей (`pyproject.toml`)
- ✅ При проверке Flake8 не более 5 ошибок
- ✅ Структура соответствует Django-проекту
- ✅ Созданы приложения `users` и `mailings`
- ✅ Настройки в папке `config/`
- ✅ Все секреты в `.env`

### 10.2 Модели

- ✅ `CustomUser` наследуется от `AbstractUser`
- ✅ Поле авторизации - `email`
- ✅ Все модели содержат необходимые поля
- ✅ Связи между моделями корректны (FK, M2M)
- ✅ Миграции запушены в репозиторий
- ✅ В Meta классах определены `permissions` для менеджеров

### 10.3 Views и URLs

- ✅ Реализованы контроллеры регистрации, входа, выхода, профиля
- ✅ Реализованы CRUD для получателей, сообщений, рассылок
- ✅ Все views зарегистрированы в `urls.py`
- ✅ В `CreateView` переопределен `form_valid()` для установки `owner`
- ✅ В `ListView`/`DetailView` переопределен `get_queryset()` для фильтрации по владельцу
- ✅ В `UpdateView`/`DeleteView` используется `UserPassesTestMixin` для проверки прав

### 10.4 Шаблоны

- ✅ Есть базовый шаблон `base.html`
- ✅ Все шаблоны наследуются от базового
- ✅ В хедере кнопки "Вход", "Выход", "Регистрация" (динамически)
- ✅ В хедере меню навигации (только для авторизованных)
- ✅ На главной странице выводится статистика
- ✅ Выделены отдельные страницы для получателей, сообщений, рассылок
- ✅ Кнопки CRUD ведут на корректные URL
- ✅ В шаблонах реализованы проверки прав (`{% if perms.app.permission %}`)

### 10.5 Права доступа

- ✅ Создана группа "Менеджеры"
- ✅ Создана команда `create_groups`
- ✅ Пользователи видят только свои данные
- ✅ Менеджеры видят все данные (read-only для чужих)
- ✅ Менеджеры могут блокировать пользователей
- ✅ Менеджеры могут отключать рассылки

### 10.6 Функциональность рассылок

- ✅ Статус рассылки обновляется динамически (`update_status()`)
- ✅ Валидация: `start_time` не в прошлом, `start_time < end_time`
- ✅ Реализована отправка через интерфейс
- ✅ Реализована отправка через команду `send_mailings`
- ✅ Для каждой попытки создается запись `MailingAttempt`
- ✅ Логируются успешные и неуспешные попытки

### 10.7 Кеширование

- ✅ Настроено серверное кеширование (в settings.py)

---

## 📚 Дополнительные ресурсы

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Email](https://docs.djangoproject.com/en/stable/topics/email/)
- [Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Django Permissions](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions-and-authorization)
- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)

---

## 🚀 Быстрый старт

```bash
# Клонирование и установка зависимостей
git clone <repo-url>
cd mail-pilot
poetry install

# Настройка окружения
cp .env.sample .env
# Отредактируйте .env

# Миграции
poetry run python manage.py migrate

# Создание суперпользователя
poetry run python manage.py createsuperuser

# Создание группы Менеджеры
poetry run python manage.py create_groups

# Запуск сервера
poetry run python manage.py runserver
```

---

**Версия:** 1.0
**Дата последнего обновления:** 2026-01-12
