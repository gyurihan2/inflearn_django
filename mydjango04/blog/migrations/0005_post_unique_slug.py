# Generated by Django 4.2.20 on 2025-04-02 01:27

from uuid import uuid4
from django.db import migrations, models
from blog.models import slugify

def update_unique_slug_if_empty(apps, schema_editor):
    Post = apps.get_model("blog.Post")
    post_qs = Post.objects.all()
    
    for post in post_qs:
        # 제목으로 만든 slug 문자열 뒤에 uuid를 넣어 유일성 확보
        post.slug = slugify(post.title, allow_unicode=True)
        post.slug = post.slug[:120]
        post.slug += "-" + uuid4().hex[:8]
    
    Post.objects.bulk_update(post_qs, ["slug"], batch_size=100)

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_managers_post_slug'),
    ]

    operations = [
        migrations.RunPython(update_unique_slug_if_empty, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='post',
            constraint=models.UniqueConstraint(fields=('slug',), name='unique_slug'),
        ),
    ]
