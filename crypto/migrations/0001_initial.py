# Generated by Django 2.1.4 on 2018-12-16 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
            name='MarketHistoric',
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
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(null=True)),
                ('type_of_rule', models.IntegerField()),
                ('crypto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crypto.CryptoModel')),
            ],
        ),
        migrations.CreateModel(
            name='RuleSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
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
                ('type_of_trade', models.CharField(max_length=11)),
                ('amount', models.DecimalField(decimal_places=8, default=0.0, max_digits=12)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
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
    ]
