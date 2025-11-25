from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages import success
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import CreateView

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url='/'
        ),
        name='registration',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'pages.views.handler403'
handler404 = 'pages.views.handler404'
handler500 = 'pages.views.handler500'
