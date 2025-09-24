from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.models import Comment, Post, PostStatus, Tag


class Command(BaseCommand):
    help = 'Заполняет базу демонстрационными данными для блога (публикации, теги, комментарии).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Предварительно очищает таблицы блога перед заполнением.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Очищаю таблицы блога...'))
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()

        self.stdout.write(self.style.MIGRATE_HEADING('Создаю авторов...'))
        authors_data = [
            {
                'username': 'e.kuznetsova',
                'first_name': 'Екатерина',
                'last_name': 'Кузнецова',
                'email': 'ekaterina@example.com',
            },
            {
                'username': 'd.ivanov',
                'first_name': 'Дмитрий',
                'last_name': 'Иванов',
                'email': 'dmitriy@example.com',
            },
            {
                'username': 'l.nguyen',
                'first_name': 'Лина',
                'last_name': 'Нгуен',
                'email': 'lina@example.com',
            },
        ]
        authors = {}
        for data in authors_data:
            user, created = User.objects.update_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                },
            )
            if created or not user.has_usable_password():
                user.set_password('changeme123')
                user.save(update_fields=['password'])
            authors[data['username']] = user
        self.stdout.write(self.style.SUCCESS(f"Готово. Авторы: {', '.join(authors.keys())}"))

        self.stdout.write(self.style.MIGRATE_LABEL('Создаю теги...'))
        tags_data = [
            ('featured', 'Избранное'),
            ('editor-choice', 'Выбор редакции'),
            ('analytics', 'Аналитика'),
            ('product', 'Продукт'),
            ('ux', 'UX/UI'),
            ('cloud', 'Облако'),
            ('security', 'Безопасность'),
            ('culture', 'Корпоративная культура'),
            ('data-storytelling', 'Data Storytelling'),
            ('automation', 'Автоматизация'),
            ('healthtech', 'HealthTech'),
            ('retail', 'Retail'),
            ('education', 'Образование'),
            ('ai', 'AI'),
            ('supply-chain', 'Supply Chain'),
        ]
        tag_map = {}
        for slug, name in tags_data:
            tag, _ = Tag.objects.update_or_create(slug=slug, defaults={'name': name})
            tag_map[slug] = tag
        self.stdout.write(self.style.SUCCESS(f'Создано тегов: {len(tag_map)}'))

        self.stdout.write(self.style.MIGRATE_LABEL('Создаю публикации...'))
        now = timezone.now()
        posts_data = [
            {
                'slug': 'ai-market-overview',
                'title': 'Как развивается рынок прикладного ИИ',
                'body': 'Разбираемся, какие отрасли быстрее всего внедряют решения на базе искусственного интеллекта, и как компании оценивают ROI пилотных проектов.',
                'author': 'e.kuznetsova',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['ai', 'analytics'],
                'days_ago': 2,
            },
            {
                'slug': 'cloud-security-checklist',
                'title': 'Чек-лист для запуска облачной безопасности',
                'body': 'Пошаговый план для команд, которые переходят в облако: от аудита инфраструктуры до внедрения Zero Trust-подхода.',
                'author': 'd.ivanov',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['cloud', 'security'],
                'days_ago': 5,
            },
            {
                'slug': 'designing-ethical-ai',
                'title': 'Этический дизайн систем искусственного интеллекта',
                'body': 'Какие UX-паттерны помогают объяснять работу алгоритмов и повышать доверие пользователей.',
                'author': 'l.nguyen',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['ai', 'ux'],
                'days_ago': 7,
            },
            {
                'slug': 'digital-wellbeing-guide',
                'title': 'Digital wellbeing: гайд для распределённых команд',
                'body': 'Коллекция практик и инструментов, которые помогают поддерживать продуктивность и mental health в гибридных командах.',
                'author': 'e.kuznetsova',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['culture', 'product'],
                'days_ago': 9,
            },
            {
                'slug': 'remote-work-analytics',
                'title': 'Как аналитика помогает распределённым офисам',
                'body': 'Измеряем эффективность коллаборации, находим узкие места и подсвечиваем лучшие практики.',
                'author': 'd.ivanov',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['analytics', 'culture'],
                'days_ago': 12,
            },
            {
                'slug': 'open-source-trends',
                'title': 'Open-source тренды 2025 года',
                'body': 'Что происходит в сообществах разработчиков, какие проекты набирают популярность и как компании вкладываются в OSS.',
                'author': 'l.nguyen',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['product', 'automation'],
                'days_ago': 16,
            },
            {
                'slug': 'supply-chain-digital',
                'title': 'Цифровизация цепочек поставок',
                'body': 'Какие решения ускоряют доставку и снижают операционные затраты на 15-20% в глобальных сетях.',
                'author': 'e.kuznetsova',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['supply-chain', 'analytics'],
                'days_ago': 18,
            },
            {
                'slug': 'data-storytelling-framework',
                'title': 'Фреймворк Data Storytelling для продуктовых команд',
                'body': 'Учимся переводить массивы данных в понятные истории для руководства и клиентов.',
                'author': 'd.ivanov',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['data-storytelling', 'product'],
                'days_ago': 21,
            },
            {
                'slug': 'healthtech-dashboard',
                'title': 'Как собрать dashboard для HealthTech-продукта',
                'body': 'Показываем, какие метрики важны врачам, пациентам и операционным менеджерам.',
                'author': 'l.nguyen',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['healthtech', 'analytics'],
                'days_ago': 24,
            },
            {
                'slug': 'retail-personalization',
                'title': 'Персонализация в retail: сценарии 2025',
                'body': 'Сегментация, динамическое ценообразование и витрины рекомендаций: кейсы, цифры и эффекты.',
                'author': 'e.kuznetsova',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['retail', 'ai'],
                'days_ago': 27,
            },
            {
                'slug': 'edtech-microlearning',
                'title': 'Микрообучение в корпоративном EdTech',
                'body': 'Как проектировать короткие форматы обучения и измерять их влияние на производительность.',
                'author': 'd.ivanov',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['education', 'product'],
                'days_ago': 31,
            },
            {
                'slug': 'featured-longread',
                'title': 'Большой лонгрид: цифровая трансформация от идеи до масштабирования',
                'body': 'Мы собрали практики лидеров отрасли, инструменты оценки готовности и чек-листы для запуска трансформационных программ.',
                'author': 'l.nguyen',
                'status': PostStatus.PUBLISHED,
                'tag_slugs': ['featured', 'editor-choice', 'automation', 'analytics'],
                'days_ago': 35,
            },
            {
                'slug': 'ai-lab-notes',
                'title': 'AI Lab: заметки о неудачных экспериментах',
                'body': 'Иногда ценнее рассказать, какие подходы не сработали. Делимся инсайтами и выводами.',
                'author': 'e.kuznetsova',
                'status': PostStatus.DRAFT,
                'tag_slugs': ['ai', 'product'],
                'days_ago': 1,
            },
        ]

        published_count = 0
        for item in posts_data:
            publish_dt = now - timedelta(days=item['days_ago'])
            defaults = {
                'title': item['title'],
                'author': authors[item['author']],
                'body': item['body'],
                'status': item['status'],
                'publish': publish_dt,
            }
            post, _ = Post.objects.update_or_create(slug=item['slug'], defaults=defaults)
            tag_objects = [tag_map[slug] for slug in item['tag_slugs']]
            post.tags.set(tag_objects)
            if post.status == PostStatus.PUBLISHED:
                published_count += 1
        self.stdout.write(self.style.SUCCESS(f'Готово: публикаций всего {Post.objects.count()}, опубликовано {published_count}'))

        self.stdout.write(self.style.MIGRATE_LABEL('Добавляю комментарии...'))
        comments_data = [
            ('ai-market-overview', 'Анна Иванова', 'anna@example.com', 'Отличный обзор, особенно блок про ROI.', True),
            ('ai-market-overview', 'Сергей Петров', 'sergey@example.com', 'Хотелось бы больше примеров по retail.', True),
            ('cloud-security-checklist', 'Анна Иванова', 'anna@example.com', 'Чек-лист сохранила, очень полезно!', True),
            ('cloud-security-checklist', 'Виктор Смирнов', 'victor@example.com', 'Добавил бы пункт про обучение сотрудников.', True),
            ('designing-ethical-ai', 'Мария Полянская', 'maria@example.com', 'Тема explainable AI раскрыта классно.', True),
            ('digital-wellbeing-guide', 'Анна Иванова', 'anna@example.com', 'Практики mindfulness работают даже в моей команде.', True),
            ('remote-work-analytics', 'Павел Ершов', 'pavel@example.com', 'Интересно, какие инструменты использовались?', True),
            ('open-source-trends', 'Ирина Ким', 'irina@example.com', 'Open-source развивается не только в ML, классный обзор.', True),
            ('supply-chain-digital', 'Алексей Орлов', 'alexey@example.com', 'Хотелось бы данных по СНГ рынку.', False),
            ('data-storytelling-framework', 'Мария Полянская', 'maria@example.com', 'Уже применяем, очень помогает с презентациями.', True),
            ('healthtech-dashboard', 'Павел Ершов', 'pavel@example.com', 'Показатели врачей и пациентов отлично разведены.', True),
            ('retail-personalization', 'Сергей Петров', 'sergey@example.com', 'Динамическое ценообразование - огонь!', True),
            ('retail-personalization', 'Анна Иванова', 'anna@example.com', 'А как насчёт офлайн магазинов?', True),
            ('edtech-microlearning', 'Ирина Ким', 'irina@example.com', 'Расскажите про кейсы внедрения.', True),
            ('featured-longread', 'Мария Полянская', 'maria@example.com', 'Большой труд, спасибо за подробности.', True),
            ('featured-longread', 'Сергей Петров', 'sergey@example.com', 'Добавьте, пожалуйста, табличку по KPI.', True),
            ('featured-longread', 'Анна Иванова', 'anna@example.com', 'Сохранила себе в закладки.', True),
            ('data-storytelling-framework', 'Павел Ершов', 'pavel@example.com', 'Планирую адаптировать для финансовой команды.', True),
            ('healthtech-dashboard', 'Анна Иванова', 'anna@example.com', 'Было бы классно увидеть примеры интерфейсов.', True),
            ('remote-work-analytics', 'Мария Полянская', 'maria@example.com', 'Замеры вовлеченности - must have.', True),
            ('open-source-trends', 'Анна Иванова', 'anna@example.com', 'Уже отправила коллегам.', True),
            ('designing-ethical-ai', 'Павел Ершов', 'pavel@example.com', 'А как вы тестировали UX-гипотезы?', True),
            ('digital-wellbeing-guide', 'Ирина Ким', 'irina@example.com', 'Подскажите, какие приложения использовали?', True),
            ('ai-market-overview', 'Виктор Смирнов', 'victor@example.com', 'Поддерживаю идею с KPI для ИИ проектов.', True),
            ('supply-chain-digital', 'Мария Полянская', 'maria@example.com', 'Нужны примеры из фармацевтики.', True),
            ('edtech-microlearning', 'Анна Иванова', 'anna@example.com', 'Можем ли мы обменяться шаблонами?', True),
            ('healthtech-dashboard', 'Сергей Петров', 'sergey@example.com', 'Добавьте блок про уведомления.', False),
        ]

        created_comments = 0
        for slug, name, email, body, active in comments_data:
            try:
                post = Post.objects.get(slug=slug)
            except Post.DoesNotExist:
                continue
            comment, created_obj = Comment.objects.get_or_create(
                post=post,
                email=email,
                body=body,
                defaults={
                    'name': name,
                    'active': active,
                },
            )
            if not created_obj:
                comment.name = name
                comment.active = active
                comment.save(update_fields=['name', 'active'])
            created_comments += int(created_obj)
        total_comments = Comment.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Комментариев всего: {total_comments} (новых {created_comments})'))

        self.stdout.write(self.style.SUCCESS('Данные успешно подготовлены.'))
