# Generated by Django 5.0.7 on 2024-07-25 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_transaction_created_at_wallet_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='txid',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.DecimalField(db_index=True, decimal_places=18, default=0, max_digits=50),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='label',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]