from datetime import datetime

from attr.filters import exclude
from django.contrib.admin.templatetags.admin_list import pagination
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.forms import ModelForm
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from blog.models import Post, Category

from .forms import PostForm, CommentForm
from .models import User, Comment


def index(request):
    template_name = 'blog/index.html'
    posts_list = Post.objects.select_related(
        'category'
    ).filter(
        pub_date__lte=datetime.now(),
        is_published=True,
        category__is_published=True
    ).order_by(
        '-pub_date'
    )

    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts_list': posts_list,
        'page_obj': page_obj,
    }

    return render(request, template_name, context)

# def post_detail(request, id):
#     template_name = 'blog/detail.html'
#     post = get_object_or_404(
#         Post,
#         pk=id,
#         is_published=True,
#         pub_date__lte=datetime.now(),
#         category__is_published=True
#     )
#
#     context = {
#         'post': post,
#     }
#
#     return render(request, template_name, context)

def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    posts_list = Post.objects.select_related(
        'category'
    ).filter(
        category__slug=category_slug,
        is_published=True,
        pub_date__lte=datetime.now(),
    ).order_by(
        '-pub_date'
    )

    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts_list': posts_list,
        'category': category,
        'page_obj': page_obj,
    }

    return render(request, template_name, context)


def profile(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)

    if request.user != profile:
        posts_list = Post.objects.filter(
            author=profile,
            is_published=True,
        ).order_by('-pub_date')
    else:
        posts_list = Post.objects.filter(
            author=profile,
        ).order_by('-pub_date')

    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)

def edit_profile(request, username):
    template_name = 'blog/user.html'
    user = get_object_or_404(User, username=username)
    context = {'user': user}
    return render(request, template_name, context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post.id)

@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=post.id)

    if request.method == 'POST':
        form = CommentForm(request.POST or None, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'post': post,
        'comment': comment,
    }

    return render(request, 'blog/comment.html', context)

@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=post.id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post.id)

    context = {'comment': comment}

    return render(request, 'blog/comment.html', context)


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user != obj.author and not obj.is_published:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'
    context_object_name = 'post'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect('blog:post_detail', id=obj.id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'id': self.object.id})


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse_lazy('blog:index')


