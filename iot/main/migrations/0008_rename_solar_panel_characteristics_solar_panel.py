# Generated by Django 4.2 on 2023-10-19 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_rename_solar_panel_characteristics_solar_panel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='characteristics',
            old_name='solar_Panel',
            new_name='solar_panel',
        ),
    ]
