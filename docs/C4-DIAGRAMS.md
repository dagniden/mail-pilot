# C4 Architecture Diagrams - Mail Pilot

Данный документ содержит архитектурные диаграммы проекта Mail Pilot в нотации C4 Model.

**Навигация:**
- [Level 1: System Context](#level-1-system-context)
- [Level 2: Container Diagram](#level-2-container-diagram)
- [Level 3: Component Diagram](#level-3-component-diagram-campaigns-app)
- [Sequence Diagrams](#sequence-diagrams)
  - [Registration & Email Verification Flow](#registration--email-verification-flow)
  - [Campaign Sending Flow](#campaign-sending-flow)

---

## Level 1: System Context

**Цель:** Показать Mail Pilot как единую систему в контексте пользователей и внешних систем.

**Описание:**
- Три типа пользователей: обычные пользователи, менеджеры и администраторы
- Mail Pilot взаимодействует с SMTP сервером для отправки писем
- Получатели получают письма через свои email-клиенты

```mermaid
graph TB
    %% Стили для C4 Context
    classDef person fill:#08427B,stroke:#052E56,color:#fff
    classDef system fill:#1168BD,stroke:#0B4884,color:#fff
    classDef external fill:#999,stroke:#666,color:#fff

    User["👤 User<br/>Creates clients, templates,<br/>and campaigns"]
    Manager["👤 Manager<br/>Views all data,<br/>manages users"]
    Admin["👤 Administrator<br/>Configures system<br/>via Django Admin"]

    MailPilot["📧 Mail Pilot<br/>Email Campaign<br/>Management System"]

    SMTP["📮 SMTP Server<br/>Yandex/Gmail SMTP<br/>Email delivery"]
    Recipients["📬 Recipients<br/>End-user email clients"]

    User -->|Регистрация, CRUD операции| MailPilot
    Manager -->|Просмотр всех данных| MailPilot
    Admin -->|Администрирование| MailPilot

    MailPilot -->|Отправляет письма через SMTP| SMTP
    SMTP -->|Доставляет письма| Recipients
    MailPilot -.->|Отправляет верификационные письма| SMTP

    class User,Manager,Admin person
    class MailPilot system
    class SMTP,Recipients external
```

**Ключевые взаимодействия:**
1. Пользователи создают кампании через веб-интерфейс
2. Менеджеры имеют доступ ко всем данным (read-only для чужих данных)
3. Администраторы настраивают систему через Django Admin
4. Mail Pilot отправляет письма через внешний SMTP сервер
5. Система отправляет верификационные письма при регистрации

---

## Level 2: Container Diagram

**Цель:** Показать основные технологические контейнеры и их взаимодействие.

**Описание:**
- Django Web Application - основное приложение
- PostgreSQL - база данных
- SMTP Server - внешний сервис для отправки email
- (Future) Redis Cache - для кеширования статистики

```mermaid
graph TB
    %% Стили для C4 Container
    classDef person fill:#08427B,stroke:#052E56,color:#fff
    classDef container fill:#438DD5,stroke:#2E6295,color:#fff
    classDef database fill:#6DB33F,stroke:#4D7C2F,color:#fff
    classDef external fill:#999,stroke:#666,color:#fff

    User["👤 User / Manager<br/>Browser"]

    subgraph MailPilotSystem["Mail Pilot System"]
        WebApp["🌐 Django Web Application<br/>Python 3.13 + Django 4.x<br/>HTTP requests, business logic, templates"]
        DB["🗄️ PostgreSQL Database<br/>Users, Clients, Campaigns,<br/>Templates, Attempts"]
        Cache["⚡ Redis Cache<br/>Future: Statistics caching"]
    end

    SMTP["📮 SMTP Server<br/>Yandex/Gmail<br/>Email delivery"]
    Cron["⏰ Cron Scheduler<br/>Runs send_campaigns command"]

    User -->|HTTPS requests| WebApp
    WebApp -->|SQL queries via Django ORM| DB
    WebApp -.->|Cache read/write| Cache
    WebApp -->|send_mail via SMTP protocol| SMTP
    Cron -->|Executes command| WebApp

    class User person
    class WebApp container
    class DB,Cache database
    class SMTP,Cron external
```

**Технологический стек:**
- **Web App**: Django 4.x, Python 3.13, Poetry (dependency management)
- **Database**: PostgreSQL (или SQLite для разработки)
- **SMTP**: Yandex SMTP / Gmail SMTP (настраивается через .env)
- **Cache**: Redis (планируется для кеширования статистики)
- **Deployment**: Gunicorn + Nginx (production), runserver (development)

**Коммуникация:**
- User ↔ Web App: HTTPS (HTML, CSS, JS)
- Web App ↔ Database: PostgreSQL protocol через Django ORM
- Web App ↔ SMTP: SMTP protocol (порт 587 с TLS)
- Cron → Web App: CLI команда `python manage.py send_campaigns`

---

## Level 3: Component Diagram (campaigns app)

**Цель:** Показать внутреннюю структуру Django приложения с фокусом на campaigns app.

**Описание:**
- Компоненты разбиты на слои: Models, Views, Services, Management Commands
- Показаны связи между users и campaigns приложениями

```mermaid
graph TB
    %% Стили для C4 Component
    classDef model fill:#FFB84D,stroke:#CC8800,color:#000
    classDef view fill:#85C1E2,stroke:#5A9BC1,color:#000
    classDef service fill:#A9B7C6,stroke:#7A8A9A,color:#000
    classDef form fill:#B8E986,stroke:#8AB660,color:#000
    classDef command fill:#E699A1,stroke:#C06070,color:#000

    Browser["🌐 Browser"]

    subgraph "Django Web Application"
        subgraph "campaigns app"
            direction TB

            %% Models Layer
            ClientModel["📊 Client Model<br/>email, full_name, owner"]
            TemplateModel["📊 MessageTemplate Model<br/>subject, body, owner"]
            CampaignModel["📊 Campaign Model<br/>time window, status, FK to template"]
            AttemptModel["📊 CampaignAttempt Model<br/>status, response, attempt_number"]

            %% Views Layer
            IndexView["🖼️ IndexView<br/>Statistics dashboard"]
            ClientViews["🖼️ Client CRUD Views<br/>List, Detail, Create, Update, Delete"]
            TemplateViews["🖼️ MessageTemplate Views<br/>CRUD operations"]
            CampaignViews["🖼️ Campaign Views<br/>CRUD + POST for sending"]
            AttemptViews["🖼️ CampaignAttempt Views<br/>List, Detail read-only"]

            %% Forms Layer
            ClientForm["📝 ClientForm"]
            TemplateForm["📝 MessageTemplateForm"]
            CampaignForm["📝 CampaignForm<br/>datetime widgets"]

            %% Service Layer
            CampaignService["⚙️ CampaignService<br/>send_campaign method<br/>Email sending logic"]

            %% Management Commands
            SendCommand["🔧 send_campaigns<br/>Management Command<br/>Auto-send active campaigns"]
        end

        subgraph "users app"
            UserModel["👤 CustomUser Model<br/>email, verification_code, is_email_verified"]
            RegisterView["🖼️ RegisterView"]
            VerifyView["🖼️ VerifyEmailView"]
            EmailService["⚙️ EmailVerificationService<br/>send_verification method"]
        end

        subgraph "Django Framework"
            Auth["🔐 django.contrib.auth<br/>Mixins for access control"]
            ORM["🗄️ Django ORM"]
            Email["📧 django.core.mail<br/>send_mail function"]
        end
    end

    DB[("PostgreSQL<br/>Database")]
    SMTP["📮 SMTP Server"]

    %% Browser interactions
    Browser -->|HTTP GET/POST| IndexView
    Browser -->|HTTP| ClientViews
    Browser -->|HTTP| CampaignViews
    Browser -->|HTTP| RegisterView

    %% Views -> Forms
    ClientViews --> ClientForm
    TemplateViews --> TemplateForm
    CampaignViews --> CampaignForm

    %% Views -> Models
    IndexView --> ClientModel
    IndexView --> CampaignModel
    IndexView --> AttemptModel
    ClientViews --> ClientModel
    TemplateViews --> TemplateModel
    CampaignViews --> CampaignModel
    AttemptViews --> AttemptModel

    %% Views -> Services
    CampaignViews -->|POST /campaigns/pk/| CampaignService
    RegisterView --> EmailService
    VerifyView --> UserModel

    %% Service -> Models
    CampaignService --> CampaignModel
    CampaignService --> ClientModel
    CampaignService --> AttemptModel
    EmailService --> UserModel

    %% Management Command
    SendCommand --> CampaignModel
    SendCommand --> CampaignService

    %% Models -> ORM -> DB
    ClientModel --> ORM
    TemplateModel --> ORM
    CampaignModel --> ORM
    AttemptModel --> ORM
    UserModel --> ORM
    ORM --> DB

    %% Services -> Email -> SMTP
    CampaignService --> Email
    EmailService --> Email
    Email --> SMTP

    %% Auth
    ClientViews --> Auth
    CampaignViews --> Auth

    %% Model relationships
    CampaignModel -.->|FK: owner| UserModel
    ClientModel -.->|FK: owner| UserModel
    TemplateModel -.->|FK: owner| UserModel
    CampaignModel -.->|FK: message_template| TemplateModel
    CampaignModel -.->|M2M: clients| ClientModel
    AttemptModel -.->|FK: campaign| CampaignModel
    AttemptModel -.->|FK: client| ClientModel

    class ClientModel,TemplateModel,CampaignModel,AttemptModel,UserModel model
    class IndexView,ClientViews,TemplateViews,CampaignViews,AttemptViews,RegisterView,VerifyView view
    class CampaignService,EmailService service
    class ClientForm,TemplateForm,CampaignForm form
    class SendCommand command
```

**Ключевые компоненты:**

### Models (Модели данных)
- **Client**: Получатель рассылки (email, full_name, comment, owner)
- **MessageTemplate**: Шаблон письма (subject, body, owner)
- **Campaign**: Кампания (start/end time, status, message_template FK, clients M2M)
- **CampaignAttempt**: Попытка отправки (campaign FK, client FK, status, server_response)
- **CustomUser**: Пользователь (email, verification_code UUID, is_email_verified)

### Views (Представления)
- **CRUD Views**: Стандартные ListView, DetailView, CreateView, UpdateView, DeleteView
- **IndexView**: Главная страница с агрегированной статистикой
- **CampaignDetailView**: Детали кампании + POST endpoint для запуска отправки
- **Access Control**: LoginRequiredMixin + UserPassesTestMixin на всех views

### Services (Бизнес-логика)
- **CampaignService**: Логика отправки кампании (send_campaign method)
  - Проверка временного окна (can_be_sent)
  - Итерация по клиентам
  - Отправка через send_mail()
  - Создание CampaignAttempt для каждого клиента
- **EmailVerificationService**: Отправка верификационных писем

### Management Commands
- **send_campaigns**: Автоматическая отправка всех активных кампаний (для cron)

---

## Sequence Diagrams

### Registration & Email Verification Flow

**Описание:** Процесс регистрации нового пользователя с верификацией email.

```mermaid
sequenceDiagram
    actor User as 👤 Пользователь
    participant Browser as 🌐 Browser
    participant RegisterView as 📝 RegisterView
    participant UserModel as 👤 CustomUser
    participant EmailService as ✉️ EmailVerificationService
    participant SMTP as 📮 SMTP Server
    participant VerifyView as ✅ VerifyEmailView

    User->>Browser: Открывает /users/register/
    Browser->>RegisterView: GET /users/register/
    RegisterView-->>Browser: Форма регистрации

    User->>Browser: Заполняет форму<br/>(email, password, phone, etc.)
    Browser->>RegisterView: POST /users/register/

    RegisterView->>UserModel: Создать CustomUser
    Note over UserModel: is_active = False<br/>verification_code = uuid4()<br/>is_email_verified = False
    UserModel-->>RegisterView: User created

    RegisterView->>EmailService: send_verification(user, request)
    EmailService->>EmailService: Генерирует абсолютный URL:<br/>/users/verify-email/{uuid}/
    EmailService->>SMTP: send_mail(subject, body, to=user.email)
    SMTP-->>EmailService: Email sent
    EmailService->>UserModel: Обновить verification_sent_at
    EmailService-->>RegisterView: OK

    RegisterView-->>Browser: Redirect to /registration-complete/
    Browser-->>User: "Проверьте вашу почту"

    Note over User,SMTP: Пользователь получает письмо

    User->>Browser: Переходит по ссылке из письма<br/>/users/verify-email/{uuid}/
    Browser->>VerifyView: GET /users/verify-email/{uuid}/

    VerifyView->>UserModel: Найти пользователя по verification_code
    UserModel-->>VerifyView: User found

    VerifyView->>VerifyView: Проверить is_verification_expired()
    alt Срок не истек (< 24 часов)
        VerifyView->>UserModel: is_email_verified = True<br/>is_active = True
        UserModel-->>VerifyView: Saved
        VerifyView-->>Browser: Success message + redirect to login
        Browser-->>User: "Email подтвержден!<br/>Войдите в систему"
    else Срок истек (> 24 часов)
        VerifyView-->>Browser: Error message + redirect to register
        Browser-->>User: "Ссылка истекла.<br/>Зарегистрируйтесь заново"
    end
```

**Ключевые моменты:**
1. При регистрации создается пользователь с `is_active=False`
2. Генерируется UUID verification_code (не 6-значный код!)
3. Отправляется письмо со ссылкой вида `/users/verify-email/{uuid}/`
4. Ссылка действительна 24 часа (проверка через verification_sent_at)
5. После верификации устанавливается `is_active=True` и `is_email_verified=True`

---

### Campaign Sending Flow

**Описание:** Процесс отправки email-кампании (manual trigger или automatic via cron).

```mermaid
sequenceDiagram
    actor User as 👤 Пользователь
    participant Browser as 🌐 Browser
    participant DetailView as 📄 CampaignDetailView
    participant CampaignModel as 📊 Campaign
    participant Service as ⚙️ CampaignService
    participant ClientModel as 👥 Client
    participant SMTP as 📮 SMTP Server
    participant AttemptModel as 📝 CampaignAttempt

    Note over User,AttemptModel: Manual Trigger (через UI)

    User->>Browser: Открывает /campaigns/{id}/
    Browser->>DetailView: GET /campaigns/{id}/
    DetailView->>CampaignModel: get_object(pk=id)
    CampaignModel-->>DetailView: campaign
    DetailView->>CampaignModel: campaign.update_status()
    Note over CampaignModel: Обновляет status<br/>на основе текущего времени
    DetailView-->>Browser: Отображает детали + кнопку "Запустить"<br/>(если can_be_sent() == True)

    User->>Browser: Нажимает "Запустить рассылку"
    Browser->>DetailView: POST /campaigns/{id}/ (action=send)

    DetailView->>DetailView: Проверка прав:<br/>campaign.owner == request.user
    DetailView->>Service: send_campaign(campaign)

    Service->>CampaignModel: campaign.can_be_sent()
    CampaignModel-->>Service: True (в временном окне)

    Service->>ClientModel: campaign.clients.all()
    ClientModel-->>Service: [client1, client2, ...]

    loop Для каждого клиента
        Service->>SMTP: send_mail(subject, body, to=client.email)

        alt Email успешно отправлен
            SMTP-->>Service: OK
            Service->>AttemptModel: Создать CampaignAttempt<br/>status=SUCCESS<br/>server_response="Email sent successfully"
        else Ошибка отправки
            SMTP-->>Service: SMTP Error
            Service->>AttemptModel: Создать CampaignAttempt<br/>status=FAILED<br/>server_response="SMTP error: ..."
        end

        AttemptModel->>AttemptModel: Автоинкремент attempt_number
        AttemptModel-->>Service: Attempt saved
    end

    Service-->>DetailView: result=True
    DetailView-->>Browser: Success message + redirect
    Browser-->>User: "Рассылка запущена!<br/>Отправлено: X, Ошибок: Y"

    Note over User,AttemptModel: ====================================
    Note over User,AttemptModel: Automatic Trigger (через cron)

    participant Cron as ⏰ Cron
    participant Command as 🔧 send_campaigns

    Cron->>Command: python manage.py send_campaigns
    Command->>CampaignModel: Campaign.objects.all()
    CampaignModel-->>Command: [campaign1, campaign2, ...]

    loop Для каждой кампании
        Command->>CampaignModel: campaign.can_be_sent()
        alt В временном окне
            CampaignModel-->>Command: True
            Command->>Service: send_campaign(campaign)
            Note over Service,AttemptModel: Тот же процесс отправки<br/>что и выше
            Service-->>Command: result=True
        else Вне временного окна
            CampaignModel-->>Command: False
            Command->>Command: statistics['skipped'] += 1
        end
    end

    Command-->>Cron: Выводит статистику в stdout
```

**Ключевые моменты:**

**Manual Trigger:**
1. Пользователь открывает детали кампании
2. `update_status()` динамически обновляет статус на основе текущего времени
3. Кнопка "Запустить" видна только если `can_be_sent()` возвращает True
4. POST запрос проверяет права доступа (owner)
5. Вызывается `CampaignService.send_campaign()`

**Automatic Trigger (Cron):**
1. Cron запускает `python manage.py send_campaigns`
2. Команда загружает все кампании из БД
3. Для каждой проверяет `can_be_sent()` (временное окно)
4. Вызывает тот же `CampaignService.send_campaign()`

**Отправка:**
1. Сервис итерируется по всем клиентам кампании
2. Для каждого клиента вызывает `send_mail()`
3. Создает `CampaignAttempt` с результатом (SUCCESS/FAILED)
4. `attempt_number` автоматически инкрементируется в `save()` методе модели

**Логирование:**
- Каждая попытка сохраняется в БД (таблица CampaignAttempt)
- Хранится статус, серверный ответ, время попытки
- Позволяет отследить историю отправок и диагностировать проблемы

---

## Дополнительная информация

### Паттерны проектирования

**Repository Pattern (через Django ORM):**
- Все обращения к БД через Django ORM
- Менеджеры моделей (`.objects`) как репозитории

**Service Layer Pattern:**
- `CampaignService` - бизнес-логика отправки
- `EmailVerificationService` - логика верификации
- Отделение бизнес-логики от views

**MVC (MTV в Django):**
- Models: data layer
- Templates: presentation layer
- Views: controller layer

### Безопасность

**Аутентификация:**
- Django session-based auth
- Email как USERNAME_FIELD
- Password hashing (PBKDF2)

**Авторизация:**
- `LoginRequiredMixin` на всех CRUD views
- `UserPassesTestMixin` для проверки owner
- Permissions для менеджеров (`can_view_all_campaigns`)

**Access Control:**
- Фильтрация данных по owner в `get_queryset()`
- Managers видят все данные (read-only для чужих)
- Users видят только свои данные

### Масштабирование (Future)

**Текущие ограничения:**
- Синхронная отправка писем (блокирующая операция)
- Нет retry механизма для failed attempts

**Планируемые улучшения:**
- Celery для асинхронной отправки
- Retry logic с exponential backoff
- Rate limiting для SMTP
- Redis для кеширования статистики

---

## Ссылки

- [C4 Model](https://c4model.com/) - официальная документация C4
- [Mermaid Documentation](https://mermaid.js.org/) - синтаксис диаграмм
- [README.md](../README.md) - техническая документация проекта
- [CLAUDE.md](../CLAUDE.md) - руководство для разработки
