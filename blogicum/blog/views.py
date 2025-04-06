from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
)

from blog.models import Category, Comment, Post
from .forms import CommentForm, PostForm


class UserProfileView(ListView):
    """A view for displaying the user's profile."""

    paginate_by = 10
    template_name = 'blog/profile.html'

    def get_queryset(self):
        user_profile = get_object_or_404(
            User, username=self.kwargs['username']
        )
        queryset = (
            Post.objects
            .select_related('author')
            .filter(author=user_profile)
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """A view for editing the user's profile."""

    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']

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


class UpdatePostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """A view for editing an existing post."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().id)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.object.id}
        )


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """A view to delete a post."""

    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().id)


class PostDetailView(DetailView):
    """A view to display the details of the post."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=now()
            ) | queryset.filter(author=self.request.user)
        return queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context


class CategoryPostView(ListView):
    """A view for displaying posts in a category."""

    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return get_base_post().filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return context


class IndexView(TemplateView):
    """The view for the main page."""

    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = get_base_post(
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


@login_required
@require_POST
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
    comment = get_object_or_404(
        Comment, id=comment_id,
        post_id=post_id, author=request.user
    )
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
        return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
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


def get_base_post():
    """Returns general data for the user."""
    return Post.objects.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True
    ).select_related('author', 'location', 'category')
