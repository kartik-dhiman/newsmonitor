from login.forms import CustomAuthForm
from django.contrib.auth.views import login as auth_login
from django.urls import path
from login import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('', auth_login, name='login', kwargs ={'authentication_form': CustomAuthForm}),
    path('', views.login),
    path('logout/', views.logout_page),
    path('accounts/login/',views.login),
    path('sign_up/', views.register),
    path('register_success/', views.register_success),
    path('home/', views.home),
    path('add_source/', views.add_source),
    path('sources_list/', views.sources_list),
    path('remove_source/', views.remove_source),
    path('search_source/', views.search_source),
    path('edit_source/', views.edit_source),
    path('fetch_story/', views.fetch_story),
    path('stories_list/', views.stories_list),
    path('search_stories/', views.search_stories),
    path('remove_story/', views.remove_story),
    path('add_story/', views.add_story),
    path('edit_story/', views.edit_story)
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
