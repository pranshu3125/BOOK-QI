from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiinsights',
            name='sentiment_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]