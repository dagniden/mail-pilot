from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Создает группу 'Менеджеры' и назначает необходимые разрешения"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            self.stdout.write("Группа 'Менеджеры' создана")
        else:
            self.stdout.write("Группа 'Менеджеры' уже существует")

        try:
            can_view_all_campaigns_permission = Permission.objects.get(codename='can_view_all_campaigns')
            can_view_all_recipients_permission = Permission.objects.get(codename='can_view_all_recipients')
            can_view_all_messages_permission = Permission.objects.get(codename='can_view_all_messages')
            can_disable_campaign_permission = Permission.objects.get(codename='can_disable_campaign')

            group.permissions.add(can_view_all_campaigns_permission,
                                  can_view_all_recipients_permission,
                                  can_view_all_messages_permission,
                                  can_disable_campaign_permission)
            group.save()
            self.stdout.write(self.style.SUCCESS("Команда выполнена, группа с правами настроена"))
        except Permission.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: разрешение не найдено - {e}. Выполните миграции!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Произошла ошибка: {e}"))




