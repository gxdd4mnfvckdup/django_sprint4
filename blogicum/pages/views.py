from django.shortcuts import render
from django.views.generic import TemplateView


# def about(request):
#     template_name = 'pages/about.html'
#     return render(request, template_name)
#     pass
#
#
# def rules(request):
#     template_name = 'pages/rules.html'
#     return render(request, template_name)

class AboutView(TemplateView):
    template_name = 'about.html'

class RulesView(TemplateView):
    template_name = 'rules.html'

def handler403(request, exception):
    return render(request, 'pages/403csrf.html', status=403)

def handler404(request, exception):
    return render(request, 'pages/404.html', status=404)

def handler500(request):
    return render(request, 'pages/500.html', status=500)
