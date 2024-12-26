# Generated by Django 5.1.3 on 2024-12-26 15:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chat_messages', '0001_initial'),
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='chatgroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.chatgroup'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages_chat', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatmessagestatus',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat_messages.chatmessage'),
        ),
        migrations.AddField(
            model_name='chatmessagestatus',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='media',
            field=models.ManyToManyField(blank=True, related_name='chat_messages', to='chat_messages.media'),
        ),
        migrations.AddField(
            model_name='message',
            name='friendship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='users.friendship'),
        ),
        migrations.AddField(
            model_name='message',
            name='media',
            field=models.ManyToManyField(blank=True, related_name='messages', to='chat_messages.media'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='MessageStatus',
            fields=[
                ('message', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='statuses', serialize=False, to='chat_messages.message')),
                ('is_seen', models.BooleanField(default=False)),
                ('is_received', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
