from django.urls import path
from . import views

urlpatterns = [
    path('debug-showings/', views.debug_showings, name='debug-showings'),
] 