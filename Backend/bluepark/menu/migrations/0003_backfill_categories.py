from django.db import migrations
from django.utils.text import slugify


def backfill_categories(apps, schema_editor):
    Category = apps.get_model('menu', 'Category')
    Menu = apps.get_model('menu', 'Menu')
    category_by_name = {}
    for item in Menu.objects.all():
        raw_name = (item.category or 'uncategorized').strip() or 'uncategorized'
        if raw_name not in category_by_name:
            slug = slugify(raw_name)
            category, _ = Category.objects.get_or_create(slug=slug, defaults={'name': raw_name.title()})
            category_by_name[raw_name] = category
        item.category_fk = category_by_name[raw_name]
        item.save(update_fields=['category_fk'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_normalize_schema'),
    ]

    operations = [
        migrations.RunPython(backfill_categories, noop_reverse),
    ]
