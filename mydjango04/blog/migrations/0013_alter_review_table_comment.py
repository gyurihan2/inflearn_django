# Generated by Django 4.2.20 on 2025-04-18 04:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_alter_post_options'),
    ]

    operations = [
        migrations.AlterModelTableComment(
            name='review',
            table_comment='사용자 리뷰와 평점을 저장하는 테이블. 평점(rating)은 1-5 사이의 값으로 제한.',
        ),
    ]
