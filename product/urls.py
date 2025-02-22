from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products, name="products"),
    path('products/<int:pk>/', views.product_pk, name="get_product"),
    path('create_review/<int:pk>/', views.create_review, name="create_review"),
    path('delete_review/<int:pk>/', views.delete_review, name="delete_review"),

    path('<int:pk>/review/create/', views.create_review, name="create_review"),
    path('<int:pk>/review/delete/', views.delete_review, name="delete_review"),
    path('<int:pk>/get_product_reviews/', views.get_product_reviews, name="get_product_reviews"),


    
]

