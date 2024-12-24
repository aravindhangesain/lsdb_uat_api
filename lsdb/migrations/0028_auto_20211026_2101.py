
from django.apps import apps
from django.db import migrations, models
from django.db.models import F

def populate_visiblename(apps, schema_editor):
    NoteType = apps.get_model('lsdb', 'NoteType')
    NoteType.objects.all().update(visible_name=F('name'))

class Migration(migrations.Migration):

    dependencies = [
        ('lsdb', '0030_auto_20211109_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='notetype',
            name='visible_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.RunPython(populate_visiblename),
    ]
