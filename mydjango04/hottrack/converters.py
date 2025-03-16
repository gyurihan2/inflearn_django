from datetime import date
from django.urls import register_converter


class DateConverter:
    # 러프한 패턴 : 2223/12/32/ 와 같은 요청도 매칭되어 관련 View가 호출되고 데이터베이스를 조회하지만, 관련 데이터가 없습니다.
    # regex = r"\d{4}/\d{1,2}/\d{1,2}"

    # 보다 엄격한 패턴 : 2023/12/32/ 와 같이 불필요한 패턴들은 걸러내어, 불필요하게 View가 호출되어 데이터베이스를 조회하지 않도록 합니다.
    #  - year: 2000 ~ 2099
    #  - month: 1, 2, 3, 4, 5, 6, 7, 8, 9, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12
    #  - day : 1, 2, 3, .. 9, 01, 02, 03, .. 09, 10, 11, 12, .. 30, 31
    regex = r"20\d{2}/([1-9]|0[1-9]|1[0-2]){1,2}/([1-9]|0[1-9]|[12][0-9]|3[01]){1,2}"

    # 뷰 함수에 넘기기 전에 date 객체로 변환
    #  - ex) "2023/12/25" -> date(2023, 12, 25)
    def to_python(self, value: str) -> date:
        year, month, day = map(int, value.split("/"))
        return date(year, month, day)

    def to_url(self, value: date) -> str:
        return f"{value.year}/{value.month:02d}/{value.day:02d}"


# DateConverter를 등록합니다.
register_converter(DateConverter, "date")