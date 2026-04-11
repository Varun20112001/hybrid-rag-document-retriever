from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("document", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="processingrunmodel",
            name="status",
            field=models.CharField(
                choices=[
                    ("STARTED", "Started"),
                    ("RETRY", "Retry"),
                    ("FAILED", "Failed"),
                    ("FINISHED", "Finished"),
                ],
                default="STARTED",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="processingrunmodel",
            name="chunk_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="processingrunmodel",
            name="embed_seconds",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="processingrunmodel",
            name="total_seconds",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="processingrunmodel",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
