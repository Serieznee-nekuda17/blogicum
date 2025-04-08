from django.http import Http404
from django.urls import reverse_lazy
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.models import Category, Comment, Post
from .forms import CommentForm, PostForm
from .mixins import AuthorPermissionMixin
from django.conf import settings


def get_post_queryset(apply_filters=False, apply_annotations=True):
    """A common queryset for working with Post."""
    queryset = Post.objects.select_related('author', 'location', 'category')

    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        )
    if apply_annotations:
        queryset = queryset.annotate(comment_count=Count('comments')
                                     ).order_by('-pub_date')
    return queryset


class UserProfileView(ListView):
    """A view for displaying the user's profile."""

    paginate_by = settings.PAGINATION_SIZE
    template_name = 'blog/profile.html'

    def get_user_profile(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        user_profile = self.get_user_profile()

        queryset = get_post_queryset(
            apply_filters=self.request.user != user_profile,
            apply_annotations=True
        )
        return queryset.filter(author=user_profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_profile()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """A view for editing the user's profile."""

    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class CreatePostView(LoginRequiredMixin, CreateView):
    """A view to create a new post."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class UpdatePostView(LoginRequiredMixin, AuthorPermissionMixin, UpdateView):
    """A view for editing an existing post."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class DeletePostView(LoginRequiredMixin, AuthorPermissionMixin, DeleteView):
    """A view to delete a post."""

    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class PostDetailView(DetailView):
    """A view to display the details of the post."""

    model = Post
    template_name = 'blog/detail.html'
    queryset = get_post_queryset(apply_annotations=False)

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        post = get_object_or_404(
            queryset.select_related('author', 'category', 'location'),
            pk=self.kwargs['post_id']
        )

        user = self.request.user

        is_not_author = post.author != user
        is_unpublished = not post.is_published
        is_category_unpublished = not post.category.is_published
        is_future = post.pub_date > now()

        if is_not_author and (is_unpublished
                              or is_category_unpublished
                              or is_future):
            raise Http404('Пост недоступен')

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author')
        context['form'] = CommentForm()
        return context


class CategoryPostView(ListView):
    """A view for displaying posts in a category."""

    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = settings.PAGINATION_SIZE

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        category = self.get_category()
        return get_post_queryset(
            apply_filters=True, apply_annotations=True
        ).filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class IndexView(ListView):
    """The view for the main page."""

    template_name = 'blog/index.html'
    paginate_by = settings.PAGINATION_SIZE
    queryset = get_post_queryset(apply_filters=True, apply_annotations=True)
    context_object_name = 'page_obj'


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    context = {
        'form': form,
        'comment': comment
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
