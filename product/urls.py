from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.items, name="products"),
    path('products/<int:pk>/', views.item_pk, name="get_product"),
    path('create_review/<int:pk>/', views.create_review, name="create_review"),
    path('delete_review/<int:pk>/', views.delete_review, name="delete_review"),

    path('<int:pk>/review/create/', views.create_review, name="create_review"),
    path('<int:pk>/review/delete/', views.delete_review, name="delete_review"),
    path('<int:pk>/get_product_reviews/', views.get_item_reviews, name="get_product_reviews"),


    path('<int:pk>/add_to_cart/', views.add_to_cart, name="add_to_cart"),
    path('<int:pk>/remove_single_item_from_cart/', views.remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('<int:pk>/remove_from_cart/', views.remove_from_cart, name="remove_from_cart"),
    path('order_summary/', views.order_summary, name="order_summary"),


    
]

