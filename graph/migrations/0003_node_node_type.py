# Generated by Django 2.0 on 2018-06-14 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0002_node_to_root'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='node_type',
            field=models.IntegerField(choices=[(0, 'ノーマル'), (1, '反論')], default=0),
        ),
    ]
