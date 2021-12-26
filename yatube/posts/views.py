from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:index')
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': is_edit, 'post': post})


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': is_edit})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.VAR_LIMITER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@cache_page(20)
def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(posts, settings.VAR_LIMITER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if (not request.user.is_anonymous
            and Follow.objects.filter(user=request.user, author=author)):
        following = True
    else:
        following = False
    request_user = request.user
    author_posts = Post.objects.filter(author=author)
    author_posts_count = author_posts.count()
    paginator = Paginator(author_posts, settings.VAR_LIMITER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'request_user': request_user,
        'author_posts_count': author_posts_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    author_posts = author.posts.all()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    author_posts_count = author_posts.count()
    context = {
        'post': post,
        'author_posts_count': author_posts_count,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context,)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.VAR_LIMITER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    post_author = get_object_or_404(User, username=username)
    follow_exists = Follow.objects.filter(user=request.user,
                                          author=post_author).exists()
    if request.user != post_author and not follow_exists:
        Follow.objects.create(user=request.user, author=post_author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    post_author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=post_author)
    if follow:
        follow.delete()
    return redirect('posts:profile', username=username)
