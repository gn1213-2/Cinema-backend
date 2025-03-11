"""
URL configuration for cinema_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import login_view, list_users, create_user
from movies.views import MovieViewSet, ShowingViewSet, TheaterViewSet, today_showings, book_showing, user_bookings, remove_test_showings
from inventory.views import SnackItemViewSet

router = DefaultRouter()
router.register(r'movies/movies', MovieViewSet)
router.register(r'movies/showings', ShowingViewSet)
router.register(r'movies/theaters', TheaterViewSet)
router.register(r'inventory/snacks', SnackItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users/login/', login_view),
    path('api/movies/today-showings/', today_showings),
    path('api/movies/book/', book_showing),
    path('api/movies/user-bookings/', user_bookings),
    path('api/movies/remove-test-showings/', remove_test_showings),
    path('api/users/', list_users),
    path('api/users/create/', create_user),
]
