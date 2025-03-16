# 커스텀 믹스인으로 코드의 중복을 줄이고 재사용성 높임


class SearchQueryMixin:
    query = None

    # Query Parameter에서 query 값을 조회하여 인스턴스 변수로 저장합니다.
    def get(self, request, *args, **kwargs):
        self.query = request.GET.get("query", "").strip()
        return super().get(request, *args, **kwargs)

    # Query Parameter "query" 값을 context data로 저장합니다.
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["query"] = self.query
        return context_data
