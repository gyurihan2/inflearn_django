from django.urls import path
from blog import views

app_name = "blog"

urlpatterns=[
    path("<int:pk>/", views.post_detail, name= "post_detail"),
    path("<int:pk>/<str:slug>/", views.post_detail, name= "post_detail"),
    
]