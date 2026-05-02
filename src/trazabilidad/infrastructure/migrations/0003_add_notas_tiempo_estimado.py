from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trazabilidad', '0002_alter_eventotrazabilidadmodel_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventotrazabilidadmodel',
            name='notas',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='eventotrazabilidadmodel',
            name='tiempo_estimado_dias',
            field=models.IntegerField(default=0),
        ),
    ]
