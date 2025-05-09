from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.query import Prefetch

from blog.models import Post, Comment

# Create your views here.
@login_required
@permission_required("blog.view_post", raise_exception=False)
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # if post.slug and (slug is None or post.slug != slug):
    #     return redirect("blog:post_detail", pk=pk, slug=post.slug, permanent=True)
    
    return HttpResponse(f"{post.pk}번 글의 {post.slug}")

@login_required
@permission_required("blog.view_premium_post", login_url="blog:premium_user_guide")
def post_premium_detail(request, slug):
    return HttpResponse(f"프리미엄 컨텐츠 페이지: {slug}")

def premium_user_guide(request):
    return HttpResponse("프리미엄 유저 가이드 페이지")

def post_list(request):
    post_qs = Post.objects.all()
    post_qs = post_qs.select_related("author")
    prefetch = Prefetch(lookup="comment_set", queryset=Comment.objects.select_related("author"))
    post_qs = post_qs.prefetch_related("tag_set", prefetch)
    return render(request=request, 
                    template_name="blog/post_list.html",
                    context={"post_list":post_qs},)