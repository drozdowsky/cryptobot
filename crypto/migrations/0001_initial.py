# Generated by Django 2.1.4 on 2018-12-28 10:25

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=11, unique=True)),
                ('long_name', models.CharField(max_length=32, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CryptoWallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=8, default=0.0, max_digits=19)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.CryptoModel')),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyWallet',
            fields=[
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
            ],
        ),
        migrations.CreateModel(
            name='MarketHistoric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
                ('response_json', django.contrib.postgres.fields.jsonb.JSONField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.CryptoModel')),
            ],
            options={
                'ordering': ('date',),
                'get_latest_by': 'date',
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('type_of_rule', models.CharField(choices=[('BEL', 'below'), ('ABO', 'above'), ('CNG', 'change'), ('CNP', 'change_perc'), ('MVP', 'max_value_perc'), ('MVE', 'max_value'), ('AHS', 'after_hours'), ('MBA', 'market_bot_above'), ('MBB', 'market_bot_below'), ('SBA', 'social_bot_above'), ('SBB', 'social_bot_below')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='RuleSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('type_of_ruleset', models.CharField(choices=[('E', 'email_only'), ('B', 'buy'), ('S', 'sell')], default='E', max_length=1)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.CryptoModel')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SocialHistoric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.CryptoModel')),
            ],
            options={
                'ordering': ('date',),
                'get_latest_by': 'date',
            },
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('type_of_trade', models.CharField(choices=[('E', 'email_only'), ('B', 'buy'), ('S', 'sell')], max_length=1)),
                ('amount', models.DecimalField(decimal_places=8, default=0.0, max_digits=19)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.CryptoModel')),
                ('rule_set', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trades', to='crypto.RuleSet')),
            ],
            options={
                'ordering': ('-date',),
                'get_latest_by': 'date',
            },
        ),
        migrations.AddField(
            model_name='rule',
            name='rule_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rules', to='crypto.RuleSet'),
        ),
        migrations.AddField(
            model_name='cryptowallet',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='rule',
            unique_together={('rule_set', 'value', 'type_of_rule')},
        ),
        migrations.AlterUniqueTogether(
            name='cryptowallet',
            unique_together={('owner', 'crypto')},
        ),
    ]
