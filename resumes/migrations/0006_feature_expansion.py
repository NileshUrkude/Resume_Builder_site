import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def populate_resume_meta(apps, schema_editor):
    Resume = apps.get_model('resumes', 'Resume')
    for resume in Resume.objects.all():
        if not resume.slug:
            resume.slug = uuid.uuid4()
        if not resume.resume_name:
            resume.resume_name = 'My Resume'
        resume.save(update_fields=['slug', 'resume_name'])


def set_order_fields(apps, schema_editor):
    for model_name, rel in [
        ('Education', 'educations'),
        ('Experience', 'experiences'),
        ('Project', 'projects'),
        ('Skill', 'skills'),
        ('Certificate', 'certificates'),
        ('Achievement', 'achievements'),
    ]:
        Model = apps.get_model('resumes', model_name)
        for idx, obj in enumerate(Model.objects.order_by('id')):
            obj.order = idx
            obj.save(update_fields=['order'])


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0005_remove_education_year_remove_resume_template_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='slug',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name='resume',
            name='resume_name',
            field=models.CharField(default='My Resume', max_length=100),
        ),
        migrations.AddField(
            model_name='resume',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resume',
            name='share_password',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='resume',
            name='share_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resume',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='photos/'),
        ),
        migrations.AddField(
            model_name='resume',
            name='preferred_template',
            field=models.CharField(choices=[('t1', 'Classic'), ('t2', 'Modern'), ('t3', 'Minimal'), ('t4', 'Sidebar'), ('t5', 'Timeline'), ('t6', 'Compact'), ('t7', 'Academic'), ('t8', 'Creative')], default='t1', max_length=3),
        ),
        migrations.AddField(
            model_name='resume',
            name='accent_color',
            field=models.CharField(default='#4f46e5', max_length=7),
        ),
        migrations.AddField(
            model_name='resume',
            name='font_family',
            field=models.CharField(choices=[('Arial', 'Arial'), ('Georgia', 'Georgia'), ('Inter', 'Inter'), ('Times New Roman', 'Times New Roman')], default='Arial', max_length=50),
        ),
        migrations.AddField(
            model_name='resume',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='resume',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RunPython(populate_resume_meta, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='resume',
            name='slug',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='resume',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='resume',
            name='summary',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='resume',
            name='github',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='resume',
            name='linkedin',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='education',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='education',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='education',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='education',
            name='duration',
            field=models.CharField(blank=True, max_length=50, default=''),
        ),
        migrations.AlterField(
            model_name='education',
            name='location',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='experience',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='experience',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='experience',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='tech_stack',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='skill',
            name='level',
            field=models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')], default='intermediate', max_length=20),
        ),
        migrations.AddField(
            model_name='skill',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='certificate',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='achievement',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('proficiency', models.CharField(choices=[('basic', 'Basic'), ('conversational', 'Conversational'), ('fluent', 'Fluent'), ('native', 'Native')], default='fluent', max_length=20)),
                ('order', models.PositiveIntegerField(default=0)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='languages', to='resumes.resume')),
            ],
            options={'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='Hobby',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('order', models.PositiveIntegerField(default=0)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hobbies', to='resumes.resume')),
            ],
            options={'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='ResumeEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('view', 'Template view'), ('pdf', 'PDF download'), ('docx', 'DOCX download'), ('share', 'Public share view')], max_length=20)),
                ('template', models.CharField(blank=True, max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='resumes.resume')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.RunPython(set_order_fields, migrations.RunPython.noop),
    ]
