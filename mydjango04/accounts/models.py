from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.
class User(AbstractUser):
    # 친구 관계 (대칭 관계)
    friend_set = models.ManyToManyField(
        to="self",
        blank=True,
        # to="self"에서 디폴트 True
        symmetrical=True,
        # related_name="friend_set",
        related_query_name="friend_user",
    )

    # 팔로잉 관계 (비대칭 관계)
    follower_set = models.ManyToManyField(
        to="self",
        blank=True,
        # to="self"에서 디폴트 True
        symmetrical=False,
        # symmetrical=False 에서는 related_name을 지원
        related_name="following_set",
        related_query_name="following",
    )

@receiver(post_save, sender=User)
def post_save_on_user(sender, instance:User, created: bool, **kwargs):
    if created:
        print(f"User({instance})의 프로필을 생성합니다.")
        Profile.objects.create(user=instance)

class SuperUserManger(models.Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        return qs.filter(is_superuser=True)

class SuperUser(User):
    objects = SuperUserManger()
    
    class Meta:
        proxy=True
        
    def save(self, *args, **kwargs):
        self.is_superuser = True
        super().save(*args, **kwargs)
        
class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name="profile",
        related_query_name="profile",
        )
    address = models.CharField(max_length=100, blank=True)
    point = models.PositiveIntegerField(default=0)
    
    # pillow 라이브러리가 설치 되어있여야함: makemigration 시에 에러 발생
    photo = models.ImageField(upload_to="profile/photo", blank=True)

@receiver(post_delete, sender=Profile)
def post_delete_on_profile(sender, instance:Profile, **kwargs):
    instance.photo.delete(save=False)