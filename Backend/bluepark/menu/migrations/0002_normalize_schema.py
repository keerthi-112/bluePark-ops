from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('display_order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='menu',
            name='category_fk',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='menu_items',
                to='menu.category',
            ),
        ),
        migrations.AddField(
            model_name='menu',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='menu',
            name='price',
            field=models.DecimalField(max_digits=8, decimal_places=2),
        ),
    ]
