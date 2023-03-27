from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
# from django.core.cache import cache
from django.conf import settings

from .models import Post, Group, User
from .forms import PostForm, CommentForm
from yatube.utils import paginate_posts


@cache_page(settings.CACHE_TIME_IN_SEC, key_prefix='index_page')
def index(request):
    '''Главная страница'''
    template = 'posts/index.html'
    # posts = cache.get('index_page')
    posts = Post.objects.all()
    # if not posts:
    #     posts = Post.objects.all()
    #     cache.set('index_page', posts)
    page_number = request.GET.get('page')
    page_obj = paginate_posts(posts, page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    '''Страница группы'''
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_number = request.GET.get('page')
    page_obj = paginate_posts(posts, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    '''Профиль пользователя.'''
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    page_number = request.GET.get('page')
    page_obj = paginate_posts(posts, page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    '''Страница просмотра поста.'''
    template = 'posts/post_detail.html'
    posts = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    comments = posts.comments.all()
    context = {
        'posts': posts,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    form = PostForm()
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
