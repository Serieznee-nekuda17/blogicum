from django.shortcuts import redirect

from django.contrib.auth.mixins import UserPassesTestMixin


class AuthorPermissionMixin(UserPassesTestMixin):
    """Mixin to check if the user is the author of the post."""

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
