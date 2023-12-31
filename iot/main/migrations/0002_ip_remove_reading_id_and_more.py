# Generated by Django 4.2.2 on 2023-06-23 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(default='', max_length=15)),
                ('port', models.CharField(default='', max_length=5)),
            ],
        ),
        migrations.RemoveField(
            model_name='reading',
            name='id',
        ),
        migrations.AlterField(
            model_name='reading',
            name='installation_number',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='reading',
            name='ip',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to='main.ip'),
        ),
    ]
