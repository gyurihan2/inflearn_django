import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
import requests

# from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path

# connection 추상화
from django.db import connection

settings.configure(
    ROOT_URLCONF=__name__,
    DEBUG=True,
    SECRET_KEY="secret",
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "melon-20230906.sqlite3",
        },
    },
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["templates"],
        }
    ],
)
django.setup()


def index(request):
    query = request.GET.get("query").strip()

    # json_url = "https://raw.githubusercontent.com/pyhub-kr/dump-data/main/melon/melon-20230906.json"
    # response = requests.get(json_url)
    # response.raise_for_status()

    # if response.ok:
    #     song_list = response.json()
    # else:
    #     song_list = []

    song_list = get_song_list(query)

    if query:
        song_list = filter(lambda song: query in song["가수"], song_list)
    # query = "악뮤"  # 검색어

    # song_list = [
    #     {"곡명": "Seven (feat. Latto) - Clean Ver.", "가수": "정국"},
    #     {"곡명": "Love Lee", "가수": "AKMU (악뮤)"},
    #     {"곡명": "Super Shy", "가수": "NewJeans"},
    #     {"곡명": "후라이의 꿈", "가수": "AKMU (악뮤)"},
    #     {"곡명": "어떻게 이별까지 사랑하겠어, 널 사랑하는 거지", "가수": "AKMU (악뮤)"},
    # ]
    # # 파이썬 빌트인 함수 filter를 활용해서, 곡명에 검색어가 포함된 노래만 필터링
    # song_list = filter(lambda song: query in song["가수"], song_list)

    return render(request, "index.html", {"song_list": song_list, "query": query})


def get_song_list(query: str):

    cursor = connection.cursor()

    param = "%" + query + "%"

    if query:
        sql = "SELECT * FROM songs WHERE 가수 LIKE %s OR 곡명 LIKE %s"
        cursor.execute(sql, [param, param])
    else:
        cursor.execute("SELECT * FROM songs")

    column_names = [desc[0] for desc in cursor.description]

    song_list = [
        dict(zip(column_names, song_tuple)) for song_tuple in cursor.fetchall()
    ]

    return song_list


urlpatterns = [
    path("", index),
]


execute_from_command_line(sys.argv)
