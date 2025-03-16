from django.contrib import admin
from django.utils.html import format_html
from .models import Song
from .utils.melon import get_likes_dict
# Register your models here.

#장식자(decorator)
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    # 리스트의 값의 경우 colunm 명
    search_fields =["name", "artist_name"]
    
    list_display = [
        "cover_image",
        "name",
        "artist_name",
        "like_count"
    ]
    
    list_filter = ["genre", "release_date"]
    
    actions = ["update_like_count"]
    
    def update_like_count(self, request, queryset):
        # flat: False(tuple) / Ture(list)
        melon_uid_list = queryset.values_list("melon_uid", flat=True)
        likes_dict = get_likes_dict(melon_uid_list)
        
        changed_count = 0
        for song in queryset:
            song.like_count = likes_dict.get(song.melon_uid)
            
            if song.like_count != likes_dict.get(song.melon_uid):
                song.like_count = likes_dict.get(song.melon_uid)
                changed_count += 1
                
        Song.objects.bulk_update(
            queryset, fields=["like_count"],
        )
        
        self.message_user(request, message=f"{changed_count} 곡의 좋아요 갱신 완료")
        

