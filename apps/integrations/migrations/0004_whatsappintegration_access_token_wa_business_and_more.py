# Generated by Django 5.2.3 on 2025-07-17 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0003_alter_whatsappintegration_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='whatsappintegration',
            name='access_token_wa_business',
            field=models.TextField(blank=True, null=True, verbose_name='Access Token WA Business'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='instance_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='ID da Instância'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='instance_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Nome da Instância'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='integration',
            field=models.CharField(blank=True, max_length=100, verbose_name='Tipo de Integração'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='qrcode_base64',
            field=models.TextField(blank=True, verbose_name='QR Code em Base64'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='qrcode_code',
            field=models.TextField(blank=True, verbose_name='Código QR'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='qrcode_pairing_code',
            field=models.CharField(blank=True, max_length=100, verbose_name='Pairing Code'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='status',
            field=models.CharField(blank=True, max_length=50, verbose_name='Status da Instância'),
        ),
        migrations.AddField(
            model_name='whatsappintegration',
            name='webhook_wa_business',
            field=models.TextField(blank=True, null=True, verbose_name='Webhook WA Business'),
        ),
    ]
