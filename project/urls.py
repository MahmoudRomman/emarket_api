from django.contrib import admin
from django.urls import path, include
from users.views import CustomAuthToken
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('product.urls')),
    path('', include('users.urls')),
    path('user-auth-token/', CustomAuthToken.as_view()),


]


handler404 = 'utils.incorrect_link.handle_404'