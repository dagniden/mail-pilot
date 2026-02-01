# Mail Pilot - Сервис управления рассылками

**Техническое задание и документация проекта**

---

## Навигация
- [Требования](./Требования.md)
- [Вопросы и ответы](./Вопросы.md)
- [Чек-лист требований](./Чек-лист.md)

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
   b. Создает запись CampaignAttempt:
      - При успехе: status='Успешно', server_response='OK'
      - При ошибке: status='Не успешно', server_response=str(error)
5. Система показывает результат отправки
Результат: Письма отправлены, попытки залогированы
```

#### UC-5.2: Запуск рассылки через командную строку
```
Актор: Система/Администратор
Команда: python manage.py send_campaigns
Основной поток:
1. Команда находит все рассылки:
   - start_time <= now <= end_time
   - status = "created" или "in_progress"
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
├── campaigns/                    # Приложение: рассылки
│   ├── models.py               # Client, MessageTemplate, Campaign, CampaignAttempt
│   ├── views.py                # CRUD для всех моделей, запуск рассылок
│   ├── forms.py                # Формы для моделей
│   ├── urls.py                 # Маршруты рассылок
│   ├── services.py             # Бизнес-логика отправки
│   └── management/
│       └── commands/
│           └── send_campaigns.py  # Команда запуска рассылок
├── templates/                   # Шаблоны
│   ├── base.html               # Базовый шаблон
│   ├── index.html              # Главная страница
│   ├── users/
│   ├── campaigns/
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
| `campaigns` | Управление рассылками, сообщениями, получателями | `Client`, `MessageTemplate`, `Campaign`, `CampaignAttempt` |

---

## 3. Модели данных (концептуальная схема)

### Список моделей

#### Приложение `users`

| Модель | Описание | Ключевые связи |
|--------|----------|----------------|
| `CustomUser` | Пользователь системы (наследуется от AbstractUser) | - |

#### Приложение `campaigns`

| Модель | Описание | Ключевые связи |
|--------|----------|----------------|
| `Client` | Получатель рассылки (клиент) | `owner` → CustomUser |
| `MessageTemplate` | Шаблон сообщения для рассылки | `owner` → CustomUser |
| `Campaign` | Рассылка (связывает сообщение и получателей) | `owner` → CustomUser<br>`message_template` → MessageTemplate<br>`clients` → Client (M2M) |
| `CampaignAttempt` | Попытка отправки письма | `campaign` → Campaign<br>`client` → Client (опционально) |

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
┌─────────────────┐    ┌─────────────────────┐
│     Client      │    │  MessageTemplate    │
│  (campaigns)    │    │   (campaigns)       │
│─────────────────│    │─────────────────────│
│ id (PK)         │    │ id (PK)             │
│ email (unique)  │    │ subject             │
│ full_name       │    │ body                │
│ comment         │    │ owner (FK)          │
│ owner (FK)      │    └────────┬────────────┘
└────────┬────────┘             │
         │                      │ message_template (FK)
         │                      │
         │            ┌─────────▼──────────┐
         │            │     Campaign       │
         │            │   (campaigns)      │
         │            │────────────────────│
         │            │ id (PK)            │
         │◄───────────┤ clients (M2M)      │
         │ M2M        │ message_template   │
         │            │ start_time         │
         │            │ end_time           │
         │            │ status             │
         │            │ owner (FK)         │
         │            └─────────┬──────────┘
         │                      │ campaign (FK)
         │                      ▼
         │            ┌──────────────────────┐
         └────────────┤  CampaignAttempt     │
          client      │   (campaigns)        │
          (FK, opt)   │──────────────────────│
                      │ id (PK)              │
                      │ campaign (FK)        │
                      │ client (FK)          │
                      │ attempt_time         │
                      │ status               │
                      │ server_response      │
                      └──────────────────────┘
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
| `phone_number` | CharField | max_length=15, blank=True, null=True | Телефон |
| `country` | CharField | max_length=100, blank=True, null=True | Страна |
| `verification_code` | UUIDField | default=uuid.uuid4, editable=False | UUID код подтверждения email |
| `is_email_verified` | BooleanField | default=False | Подтвержден ли email |
| `verification_sent_at` | DateTimeField | null=True, blank=True | Время отправки кода верификации |
| `is_active` | BooleanField | default=True | Активен ли аккаунт (устанавливается в True после верификации email) |
| `is_staff` | BooleanField | default=False | Доступ к админке (AbstractUser) |
| `date_joined` | DateTimeField | auto_now_add=True | Дата регистрации |

**Методы:**

```python
def __str__(self):
    return self.email

def regenerate_verification_code(self):
    """Генерирует новый UUID и обновляет время отправки"""
    self.verification_code = uuid.uuid4()
    self.verification_sent_at = timezone.now()
    self.save(update_fields=["verification_code", "verification_sent_at"])

def is_verification_expired(self):
    """Проверяет, истек ли срок действия кода (24 часа)"""
    if not self.verification_sent_at:
        return True
    return timezone.now() > self.verification_sent_at + timedelta(days=1)
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

### 4.2 Client (приложение `campaigns`)

**Назначение:** Получатель рассылки (клиент в базе пользователя).

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `email` | EmailField | unique=True, blank=False | Email получателя (уникальный) |
| `full_name` | CharField | max_length=255, blank=False | Ф.И.О. |
| `comment` | TextField | blank=True | Комментарий |
| `owner` | ForeignKey | to=CustomUser, on_delete=CASCADE, related_name='clients' | Владелец |
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
        ('can_view_all_recipients', 'Can view all clients'),
    ]
```

---

### 4.3 MessageTemplate (приложение `campaigns`)

**Назначение:** Шаблон сообщения для рассылки.

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `subject` | CharField | max_length=255, blank=False | Тема письма |
| `body` | TextField | blank=False | Тело письма (может содержать HTML) |
| `owner` | ForeignKey | to=CustomUser, on_delete=CASCADE, related_name='templates' | Владелец |
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
        ('can_view_all_messages', 'Can view all message_templates'),
    ]
```

---

### 4.4 Campaign (приложение `campaigns`)

**Назначение:** Рассылка, связывающая сообщение с получателями.

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `message_template` | ForeignKey | to=MessageTemplate, on_delete=PROTECT, related_name='campaigns' | Сообщение |
| `clients` | ManyToManyField | to=Client | Получатели |
| `start_time` | DateTimeField | blank=False | Дата и время начала |
| `end_time` | DateTimeField | blank=False | Дата и время окончания |
| `status` | CharField | max_length=20, choices=STATUS_CHOICES, default='created' | Статус |
| `owner` | ForeignKey | to=CustomUser, on_delete=CASCADE, related_name='campaigns' | Владелец |
| `created_at` | DateTimeField | auto_now_add=True | Дата создания |

**Choices:**
```python
STATUS_CHOICES = [
    ('created', 'Создана'),
    ('in_progress', 'Запущена'),
    ('finished', 'Завершена'),
]
```

**Методы:**
```python
def __str__(self):
    return f"Рассылка #{self.id}: {self.message_template.subject}"

def update_status(self):
    """Динамически обновляет статус на основе текущего времени"""
    from django.utils import timezone
    now = timezone.now()

    if now < self.start_time:
        new_status = 'created'
    elif self.start_time <= now <= self.end_time:
        new_status = 'in_progress'
    else:
        new_status = 'finished'

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
        ('can_view_all_campaigns', 'Can view all campaigns'),
        ('can_disable_campaign', 'Can disable campaign'),
    ]
```

---

### 4.5 CampaignAttempt (приложение `campaigns`)

**Назначение:** Попытка отправки письма (лог).

**Поля:**

| Поле | Тип | Параметры | Описание |
|------|-----|-----------|----------|
| `id` | BigAutoField | primary_key=True | Первичный ключ |
| `campaign` | ForeignKey | to=Campaign, on_delete=CASCADE, related_name='attempts' | Рассылка |
| `client` | ForeignKey | to=Client, on_delete=SET_NULL, null=True, blank=True | Получатель (опционально) |
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
    client_info = f" → {self.client.email}" if self.client else ""
    return f"Попытка #{self.id}{client_info}: {self.status}"
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
│    Client (campaigns)          │ │     MessageTemplate (campaigns)         │
├──────────────────────────────────┤ ├────────────────────────────────┤
│ PK │ id: BigAutoField            │ │ PK │ id: BigAutoField          │
│ UK │ email: EmailField           │ │    │ subject: CharField(255)   │
│    │ full_name: CharField(255)   │ │    │ body: TextField           │
│    │ comment: TextField          │ │ FK │ owner → CustomUser        │
│ FK │ owner → CustomUser          │ │    │ created_at: DateTimeField │
│    │ created_at: DateTimeField   │ │    │ updated_at: DateTimeField │
└──────────────┬───────────────────┘ └────────────┬───────────────────┘
               │                                  │
               │ clients (M2M)                 │ message_template (FK, PROTECT)
               │                                  │
               │                ┌─────────────────▼──────────────────┐
               │                │        Campaign (campaigns)          │
               │                ├────────────────────────────────────┤
               │                │ PK │ id: BigAutoField              │
               └────────────────┤ FK │ message_template → MessageTemplate             │
                     M2M        │ M2M│ clients → Client        │
                                │    │ start_time: DateTimeField     │
                                │    │ end_time: DateTimeField       │
                                │    │ status: CharField(20)         │
                                │ FK │ owner → CustomUser            │
                                │    │ created_at: DateTimeField     │
                                └────────────┬───────────────────────┘
                                             │ campaign (FK, CASCADE)
                                             ▼
                      ┌────────────────────────────────────────────────┐
                      │        CampaignAttempt (campaigns)               │
                      ├────────────────────────────────────────────────┤
                      │ PK │ id: BigAutoField                          │
                      │ FK │ campaign → Campaign                         │
                      │ FK │ client → Client (NULL, SET_NULL)    │
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
- **Всего рассылок:** `Campaign.objects.filter(owner=request.user).count()`
- **Активных рассылок:** `Campaign.objects.filter(owner=request.user, status='in_progress').count()`
- **Уникальных получателей:** `Client.objects.filter(owner=request.user).count()`

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

### 5.5 Список получателей (`campaigns/client_list.html`)

**URL:** `/campaigns/clients/`
**View:** `ClientListView` (ListView)
**Доступ:** Авторизованные пользователи

**Таблица:**

| Email | Ф.И.О. | Комментарий | Действия |
|-------|--------|-------------|----------|
| user@example.com | Иван Иванов | VIP клиент | [✏️ Редактировать] [🗑️ Удалить] |
| ... | ... | ... | ... |

**Кнопки:**
- **[+ Создать получателя]** → ссылка на `/campaigns/clients/create/`

**Фильтрация:**
- QuerySet ограничен: `Client.objects.filter(owner=request.user)`

---

### 5.6 Создание/Редактирование получателя (`campaigns/client_form.html`)

**URL:**
- Создание: `/campaigns/clients/create/`
- Редактирование: `/campaigns/clients/<pk>/edit/`

**View:** `ClientCreateView` / `ClientUpdateView`
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

### 5.7 Список сообщений (`campaigns/message_template_list.html`)

**URL:** `/campaigns/message_templates/`
**View:** `MessageTemplateListView` (ListView)
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
- **[+ Создать сообщение]** → ссылка на `/campaigns/message_templates/create/`

---

### 5.8 Создание/Редактирование сообщения (`campaigns/message_template_form.html`)

**URL:**
- Создание: `/campaigns/message_templates/create/`
- Редактирование: `/campaigns/message_templates/<pk>/edit/`

**View:** `MessageTemplateCreateView` / `MessageTemplateUpdateView`

**Форма:**

| Поле | Тип input | Обязательное |
|------|-----------|--------------|
| Тема письма | text | ✓ |
| Тело письма | textarea (WYSIWYG опционально) | ✓ |

**Кнопки:**
- **[Сохранить]** → POST → редирект на список
- **[Отмена]** → список сообщений

---

### 5.9 Список рассылок (`campaigns/campaign_list.html`)

**URL:** `/campaigns/`
**View:** `CampaignListView` (ListView)
**Доступ:** Авторизованные пользователи

**Таблица:**

| ID | Сообщение | Получателей | Начало | Окончание | Статус | Действия |
|----|-----------|-------------|--------|-----------|--------|----------|
| 42 | Скидка 50% | 15 | 01.01.2026 10:00 | 05.01.2026 23:59 | 🟢 Запущена | [👁️ Просмотр] [✏️ Редактировать] [🗑️ Удалить] |
| 41 | Новинки | 8 | 20.12.2025 | 31.12.2025 | 🔴 Завершена | [👁️ Просмотр] |

**Кнопки:**
- **[+ Создать рассылку]** → `/campaigns/create/`

**Цветовая индикация статусов:**
- 🟡 Создана (серый)
- 🟢 Запущена (зеленый)
- 🔴 Завершена (красный)

---

### 5.10 Создание/Редактирование рассылки (`campaigns/campaign_form.html`)

**URL:**
- Создание: `/campaigns/create/`
- Редактирование: `/campaigns/<pk>/edit/`

**View:** `CampaignCreateView` / `CampaignUpdateView`

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

### 5.11 Детальная информация о рассылке (`campaigns/campaign_detail.html`)

**URL:** `/campaigns/<pk>/`
**View:** `CampaignDetailView` (DetailView)
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
- **[▶️ Запустить рассылку]** → POST `/campaigns/<pk>/send/` → запуск отправки (видна только если `status='in_progress'`)
- **[✏️ Редактировать]** → `/campaigns/<pk>/edit/` (только если владелец)
- **[🗑️ Удалить]** → POST `/campaigns/<pk>/delete/` (только если владелец)

**Поведение:**
- При загрузке страницы вызывается `campaign.update_status()` (динамическое обновление статуса)
- Попытки отображаются в обратном хронологическом порядке

---

### 5.12 Страница запуска рассылки (встроена в detail)

**URL:** `/campaigns/<pk>/send/` (POST)
**View:** `SendCampaignView` (View)
**Доступ:** Владелец рассылки

**Процесс:**
1. Проверка прав (owner == request.user)
2. Проверка временного окна (`can_be_sent()`)
3. Для каждого получателя:
   - Попытка отправки через `send_mail()`
   - Создание `CampaignAttempt` с результатом
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
from .views import (
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
    VerifyEmailView,
    RegistrationCompleteView
)

app_name = 'users'

urlpatterns = [
    # Аутентификация
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-email/<uuid:code>/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('registration-complete/', RegistrationCompleteView.as_view(), name='registration_complete'),
]
```

**Views (`users/views.py`):**

| View | Тип | Шаблон | Доступ | Описание |
|------|-----|--------|--------|----------|
| `UserRegisterView` | CreateView | users/register.html | Публичный | Регистрация с отправкой email верификации |
| `VerifyEmailView` | TemplateView | users/verify_email.html | Публичный | Подтверждение email по UUID коду |
| `UserLoginView` | LoginView | registration/login.html | Публичный | Вход в систему |
| `UserLogoutView` | LogoutView | - | @login_required | Выход из системы |
| `RegistrationCompleteView` | TemplateView | users/registration_complete.html | Публичный | Страница после успешной регистрации |

**Не реализовано (TODO):**
- `ProfileView` - редактирование профиля
- `UserListView` - список пользователей (для менеджеров)
- `UserDetailView` - детали пользователя (для менеджеров)
- `ToggleUserActiveView` - блокировка/разблокировка (для менеджеров)
- Восстановление пароля (Django built-in views)

---

### 6.2 Приложение `campaigns`

**urls.py (`campaigns/urls.py`):**

```python
from django.urls import path
from .views import (
    # Клиенты
    ClientListView, ClientCreateView, ClientDetailView,
    ClientUpdateView, ClientDeleteView,
    # Шаблоны сообщений
    MessageTemplateListView, MessageTemplateCreateView, MessageTemplateDetailView,
    MessageTemplateUpdateView, MessageTemplateDeleteView,
    # Кампании
    CampaignListView, CampaignCreateView, CampaignDetailView,
    CampaignUpdateView, CampaignDeleteView,
    # Попытки отправки
    CampaignAttemptListView, CampaignAttemptDetailView,
)

app_name = 'campaigns'

urlpatterns = [
    # Клиенты
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),

    # Шаблоны сообщений
    path('message_templates/', MessageTemplateListView.as_view(), name='message_templates_list'),
    path('message_templates/create/', MessageTemplateCreateView.as_view(), name='message_template_create'),
    path('message_templates/<int:pk>/', MessageTemplateDetailView.as_view(), name='message_template_detail'),
    path('message_templates/<int:pk>/update/', MessageTemplateUpdateView.as_view(), name='message_template_update'),
    path('message_templates/<int:pk>/delete/', MessageTemplateDeleteView.as_view(), name='message_template_delete'),

    # Кампании
    path('campaigns/', CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/create/', CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/<int:pk>/', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/<int:pk>/update/', CampaignUpdateView.as_view(), name='campaign_update'),
    path('campaigns/<int:pk>/delete/', CampaignDeleteView.as_view(), name='campaign_delete'),

    # Попытки отправки
    path('attempts/', CampaignAttemptListView.as_view(), name='attempt_list'),
    path('attempts/<int:pk>/', CampaignAttemptDetailView.as_view(), name='attempt_detail'),
]
```

**Views (`campaigns/views.py`):**

| View | Тип | Миксины | Описание |
|------|-----|---------|----------|
| `IndexView` | TemplateView | - | Главная страница со статистикой (фильтрация по owner/менеджер) |
| `ClientListView` | ListView | LoginRequiredMixin | Фильтрует по owner |
| `ClientDetailView` | DetailView | LoginRequiredMixin, UserPassesTestMixin | Детали клиента |
| `ClientCreateView` | CreateView | LoginRequiredMixin | Устанавливает owner=request.user в form_valid() |
| `ClientUpdateView` | UpdateView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `ClientDeleteView` | DeleteView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `MessageTemplateListView` | ListView | LoginRequiredMixin | Фильтрует по owner |
| `MessageTemplateDetailView` | DetailView | LoginRequiredMixin, UserPassesTestMixin | Детали шаблона |
| `MessageTemplateCreateView` | CreateView | LoginRequiredMixin | Устанавливает owner |
| `MessageTemplateUpdateView` | UpdateView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `MessageTemplateDeleteView` | DeleteView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `CampaignListView` | ListView | LoginRequiredMixin | Фильтрует по owner (или все для менеджеров) |
| `CampaignCreateView` | CreateView | LoginRequiredMixin | Устанавливает owner |
| `CampaignDetailView` | DetailView | LoginRequiredMixin, UserPassesTestMixin | Вызывает update_status(), POST для отправки |
| `CampaignUpdateView` | UpdateView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `CampaignDeleteView` | DeleteView | LoginRequiredMixin, UserPassesTestMixin | Проверка owner |
| `CampaignAttemptListView` | ListView | LoginRequiredMixin | Фильтрация по campaign_id (GET параметр) |
| `CampaignAttemptDetailView` | DetailView | LoginRequiredMixin | Детали попытки отправки |

---

### 6.3 Главный маршрутизатор

**urls.py (`config/urls.py`):**

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from campaigns.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('users/', include('users.urls')),
    path('campaigns/', include('campaigns.urls')),
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
# Client
permissions = [
    ('can_view_all_recipients', 'Can view all clients'),
]

# MessageTemplate
permissions = [
    ('can_view_all_messages', 'Can view all message_templates'),
]

# Campaign
permissions = [
    ('can_view_all_campaigns', 'Can view all campaigns'),
    ('can_disable_campaign', 'Can disable campaign'),
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
    if self.request.user.has_perm('campaigns.can_view_all_campaigns'):
        # Менеджер видит все
        return Campaign.objects.all()
    # Пользователь видит только свои
    return Campaign.objects.filter(owner=self.request.user)

# Проверка владельца при редактировании/удалении
def test_func(self):
    obj = self.get_object()
    return obj.owner == self.request.user
```

**В шаблонах:**

```django
{% if perms.campaigns.can_disable_campaign %}
    <a href="{% url 'campaigns:campaign_disable' campaign.pk %}">Отключить</a>
{% endif %}

{% if campaign.owner == request.user %}
    <a href="{% url 'campaigns:campaign_update' campaign.pk %}">Редактировать</a>
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
                    'can_view_all_campaigns',
                    'can_disable_campaign',
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

### 8.1 Отправка рассылок (`send_campaigns`)

**Файл:** `campaigns/management/commands/send_campaigns.py`

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
from campaigns.models import Campaign
from campaigns.services import CampaignService

class Command(BaseCommand):
    help = 'Отправляет все активные кампании в пределах временного окна'

    def handle(self, *args, **options):
        campaigns = Campaign.objects.all()
        statistics = {
            'sent': 0,
            'skipped': 0
        }

        for campaign in campaigns:
            if not campaign.can_be_sent():
                continue

            result = CampaignService.send_campaign(campaign)
            statistics['sent' if result else 'skipped'] += 1

        self.stdout.write(self.style.SUCCESS("Command finished"))
        self.stdout.write(self.style.SUCCESS(
            f"Sent {statistics['sent']} campaigns, skipped {statistics['skipped']} campaigns"
        ))
```

**Запуск:**
```bash
python manage.py send_campaigns
```

**Планирование (cron):**
```cron
*/10 * * * * cd /path/to/project && poetry run python manage.py send_campaigns
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
    'campaigns',
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
description = "Email campaign service"
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
- ✅ Созданы приложения `users` и `campaigns`
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
- ✅ Реализована отправка через команду `send_campaigns`
- ✅ Для каждой попытки создается запись `CampaignAttempt`
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
