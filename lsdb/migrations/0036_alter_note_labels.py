# Generated by Django 3.2 on 2024-01-31 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lsdb', '0035_alter_note_labels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='labels',
            field=models.ManyToManyField(blank=True, to='lsdb.Label'),
        ),
    ]
