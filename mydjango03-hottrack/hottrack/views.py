from datetime import datetime
from io import BytesIO
import json
from typing import Literal
import pandas as pd
from urllib.request import urlopen

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.db.models import QuerySet, Q
from hottrack.models import Song

from django.shortcuts import get_object_or_404
from hottrack.utils.cover import make_cover_image


def index(request: HttpRequest, release_date:datetime.date=None) -> HttpResponse:
    query = request.GET.get("query", "").strip()

    song_qs: QuerySet[Song] = Song.objects.all()
    
    if release_date:
        song_qs = song_qs.filter(release_date=release_date)

    if query:
        song_qs = song_qs.filter(
            Q(name__icontains=query)
            | Q(artist_name__icontains=query)
            | Q(album_name__icontains=query)
        )

    return render(
        request=request,
        template_name="hottrack/index.html",
        context={"song_list": song_qs, "query": query},
    )

def cover_png(request, pk):
    # 최대값 512, 기본값 256
    canvas_size = min(512, int(request.GET.get("size", 256)))

    song = get_object_or_404(Song, pk=pk)

    cover_image = make_cover_image(
        song.cover_url, song.artist_name, canvas_size=canvas_size
    )

    # param fp : filename (str), pathlib.Path object or file object
    # image.save("image.png")
    response = HttpResponse(content_type="image/png")
    cover_image.save(response, format="png")

    return response

def export(request: HttpRequest, format:Literal["csv", "xlsx"]) -> HttpResponse:
    song_qs: QuerySet = Song.objects.all()

    # .values() : 지정한 필드로 구성된 사전 리스트를 반환
    song_qs = song_qs.values()
    # 원하는 필드만 지정해서 뽑을 수도 있습니다.
    # song_qs = song_qs.values("rank", "name", "artist_name", "like_count")

    # 사전 리스트를 인자로 받아서, DataFrame을 생성할 수 있습니다.
    df = pd.DataFrame(data=song_qs)

    # 메모리 파일 객체에 CSV 데이터를 저장합니다.
    # CSV를 HttpResponse에 바로 저장할 때 utf-8-sig 인코딩이 적용되지 않아서
    # BytesIO를 사용해서 인코딩을 적용한 후, HttpResponse에 저장합니다.
    export_file = BytesIO()
    
    if format == "csv":
        # df.to_csv("hottrack.csv", index=False)      # 지정 파일로 저장할 수도 있고, 파일 객체를 전달할 수도 있습니다.
        # (한글깨짐방지) 한글 엑셀에서는 CSV 텍스트 파일을 해석하는 기본 인코딩이 cp949이기에
        # utf-8-sig 인코딩을 적용하여 생성되는 CSV 파일에 UTF-8 BOM이 추가합니다.
        content_type = "text/csv"
        filename = "hottract.csv"
        df.to_csv(path_or_buf=export_file, index=False, encoding="utf-8-sig")  # noqa
    
    elif format == "xlsx":
        content_type = "application/vnd.ms-excel"
        filename = "hottract.xlsx"
        df.to_excel(excel_writer=export_file, index=False,)
    
    else:
        return HttpResponse(f"Invaild format : {format}")

    
    # 저장된 파일의 전체 내용을 HttpResponse에 전달합니다.
    response = HttpResponse(content=export_file.getvalue(), content_type=content_type)
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)

    return response