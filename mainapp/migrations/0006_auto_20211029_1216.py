# Generated by Django 3.2.8 on 2021-10-29 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_auto_20211029_1207'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoesbrand',
            options={'verbose_name': 'Бренд', 'verbose_name_plural': 'Бренды'},
        ),
        migrations.AlterModelOptions(
            name='shoestype',
            options={'verbose_name': 'Вид обуви', 'verbose_name_plural': 'Виды обуви'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AddField(
            model_name='shoes',
            name='sex_type',
            field=models.CharField(choices=[('male', 'Мужские'), ('female', 'Женские'), ('child', 'Детские')], default='male', max_length=100, verbose_name='Пол'),
        ),
    ]