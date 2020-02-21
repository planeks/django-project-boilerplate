from django.urls import path
from . import views


urlpatterns = [
    path('info/language-choices.json', views.language_choices_view, name='language_choices'),
]