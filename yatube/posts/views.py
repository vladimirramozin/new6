from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow
from django.contrib.auth import get_user_model

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
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


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


@cache_page(2)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.VAR_LIMITER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if not request.user.is_anonymous:
        follow = Follow.objects.filter(user=request.user, author=author)
        if follow:
            following = True
    else:
        following = False
    author_posts = Post.objects.filter(author=author)
    author_posts_count = author_posts.count()
    paginator = Paginator(author_posts, settings.VAR_LIMITER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
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
        'author_posts': author_posts,
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
    user_subscriptions = Follow.objects.filter(user=request.user)
    if user_subscriptions is not None:
        authors = list()
        for user in user_subscriptions:
            authors.append(user.author)
        post = Post.objects.filter(author__in=authors)
        paginator = Paginator(post, settings.VAR_LIMITER)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj
        }
        return render(request, 'posts/follow.html', context)
    return render(request, 'posts:follow_index')


@login_required
def profile_follow(request, username):
    post_author = get_object_or_404(User, username=username)
    follow_exists = Follow.objects.filter(user=request.user,
                                          author=post_author).exists()
    if (request.user != post_author) and not follow_exists:
        Follow.objects.create(user=request.user, author=post_author)
    return redirect('posts:profile', username=username)


