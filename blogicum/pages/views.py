from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    """The view for the 'About the Project' page."""

    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    """View for the 'Rules' page."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Error handler 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Error handler CSRF (403)."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Error handler 500."""
    return render(request, 'pages/500.html', status=500)
