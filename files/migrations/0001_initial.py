# Generated by Django 2.1.5 on 2019-01-31 22:52

from django.db import migrations, models
import files.models
import files.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('source', models.FileField(upload_to=files.models.upload_location, validators=[files.validators.validate_file_extensions])),
                ('slug', models.SlugField(max_length=48)),
            ],
        ),
    ]
