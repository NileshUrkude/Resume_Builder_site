# Generated manually for accent_color cleanup

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0007_alter_achievement_options_alter_certificate_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resume',
            name='accent_color',
        ),
    ]
