from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import Post

# Create your views here.
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # if post.slug and (slug is None or post.slug != slug):
    #     return redirect("blog:post_detail", pk=pk, slug=post.slug, permanent=True)
    
    return HttpResponse(f"{post.pk}번 글의 {post.slug}")