from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("seguimiento", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="borradorcorreomodel",
            name="dias_sin_respuesta",
            field=models.IntegerField(default=0),
        ),
    ]
