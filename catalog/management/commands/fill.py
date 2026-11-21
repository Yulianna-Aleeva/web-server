from django.core.management.base import BaseCommand
from django.core.management import call_command
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Очищает БД и заполняет её тестовыми данными из фикстуры'

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()

        call_command('loaddata', 'catalog_fixture.json')
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))
