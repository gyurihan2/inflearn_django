from uuid import uuid4
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint, Q
from django.db.models.functions import Lower

from core.model_fields import BooleanYNField, IPv4AddressIntegerField
# python .\manage.py startapp blog
# python .\manage.py makemigrations blog
# python .\manage.py migrate blog
# python manage.py shell_plus --print-sql

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class PostQuerySet(models.QuerySet):
    
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED)
    
    def draft(self):
        return self.filter(status=Post.Status.DRAFT)
    
    def search(self, query:str):
        return self.filter(title__contains=query)
    
    def by_author(self, author):
        return self.filter(author=author)
    
    def create(self, **kwargs):
        kwargs.setdefault("status", Post.Status.PUBLISHED)
        return super().create(**kwargs)

# class PublishedPostManager(models.Manager):
    
#     def get_queryset(self):
#         qs = super().get_queryset()
#         qs =  qs.filter(status=Post.Status.PUBLISHED)
#         return qs
    
#     def create(self, **kwargs):
#         kwargs.setdefault("status", Post.Status.PUBLISHED)
#         return super().create(**kwargs)

# Create your models here.
class Post(TimestampedModel):
    class Status(models.TextChoices): # 문자열 선택지
        DRAFT = "D", "초안"            # 상수, 값, 레이블
        PUBLISHED = "P", "발행"

    categoty = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_post_set")
    slug = models.SlugField(max_length=120, allow_unicode=True)
    title = models.CharField(max_length=100)
    status = models.CharField(
        # 선택지 값 크기에 맞춰 최대 길이를 지정
        max_length=1,
        # choices 속성으로 사용할 수 있도록 2중 리스트로 반환
        # choices 속성은 모든 모델 필드에서 지원합니다.
        choices=Status.choices,
        # status 필드에 대한 모든 값 지정에는 상수로 지정하면 쿼리에 값으로 자동 변환
        default=Status.DRAFT,
    )
    content = models.TextField()
    # many2many에서 blank가 false일 경우 생성할때 유효성 검사에서 1개 이상의 Post를 요구하기 때문에 True로 설정하여 
    tag_set = models.ManyToManyField(
        "Tag", blank=True,
        related_name="blog_post_set",
        related_query_name="blog_post",
        )

    objects = PostQuerySet.as_manager()
    

    def __str__(self):
        # choices 속성을 사용한 필드는 get_필드명_display() 함수를 통해 레이블 조회를 지원합니다.
        return f"{self.title} ({self.get_status_display()})"
    
    def slugify(self, force=False):
        if force or not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
            self.slug = self.slug[:120]
            # 제목으로 만든 slug 문자열 뒤에 uuid를 붙여 slug의 유일성을 확보
            self.slug += "-" + uuid4().hex[:8]
    
    def save(self, *args, **kwargs):
        self.slugify()
        super().save(*args, **kwargs)
        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_slug"),
        ]
        verbose_name = "포스팅"
        verbose_name_plural = "포스팅 목록"
        permissions = [
            ("view_premium_post", "프리미엄 컨텐츠를 볼 수 있음"),
        ]

class Comment(TimestampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()

class AccessLog(TimestampedModel):
    
    ip_generic = models.GenericIPAddressField(protocol="IPv4")
    ip_int = IPv4AddressIntegerField()
    
class Article(TimestampedModel):
    title = models.CharField(max_length=100)
    is_public_ch = models.CharField(
        max_length=1,
        choices=[
            ("Y", "예"),
            ("N", "아니오")
        ],
        default= "N"
    )
    is_public_yn = BooleanYNField(default=False)

class Review(TimestampedModel, models.Model):
    message = models.TextField()
    # 평점의 경우 1-5사이의 범위를 가지고 파이썬 코드 레벨에서 점검이 이루어짐(MinValueValidator, MaxValueValidator)
    rating = models.SmallIntegerField(
        # validators=[
        #     MinValueValidator(1),
        #     MaxValueValidator(5),
        # ]
    )
    
    class Meta:
        constraints =[
            models.CheckConstraint(
                check= Q(rating__gte=1, rating__lte=5),
                name="blog_review_rating_gte_1_lte_5",
            )
        ]
        db_table_comment = "사용자 리뷰와 평점을 저장하는 테이블. 평점(rating)은 1-5 사이의 값으로 제한."

class Tag(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                #fields=["name"],
                name="blog_tag_name_unique",
            )
        ]

        indexes = [
            models.Index(
                #  models.Index(fields=["name"])
                
                #(PostgrSQL Only) unique=True와 동일한 인덱스 만들기
                fields=["name"],
                name="blog_tag_name_like",
                opclasses=["varchar_pattern_ops"]
            )
        ]
        
class Student(models.Model):
    name = models.CharField(max_length=100)

class Course(models.Model):
    title = models.CharField(max_length=100)

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                "student", "course", Lower("semester"),      # 다수의 expression 지정
                # fields=["student", "course", "semester"],  # 단순 필드명 나열
                name="blog_enrollment_uniq"),
        ]