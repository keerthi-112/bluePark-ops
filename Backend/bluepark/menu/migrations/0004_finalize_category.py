from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_backfill_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu',
            name='category',
        ),
        migrations.RenameField(
            model_name='menu',
            old_name='category_fk',
            new_name='category',
        ),
        migrations.AlterField(
            model_name='menu',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='menu_items',
                to='menu.category',
            ),
        ),
    ]
