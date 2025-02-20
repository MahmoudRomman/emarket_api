from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from . import models
from . import serializers
from . import filters
import math
from django.db.models import Avg

# Create your views here.




@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def products(request):
    if request.method == 'GET':
        products = models.Product.objects.all()
        # Apply filters on products to get presied search
        filter = filters.ProductFilter(request.GET, products.order_by('id'))
        filtered_products_count = filter.qs.count()
        # Apply pagination after filtering my products
        paginator = PageNumberPagination()
        res_per_page = 2
        paginator.page_size = res_per_page # number of products per page
        paginated_products = paginator.paginate_queryset(filter.qs, request)
        # Serialize the paginated queryset
        serializer = serializers.ProductSerializers(paginated_products, many=True)
        num_of_pages = math.ceil(filtered_products_count / res_per_page)
        json = {
            "Products: ": serializer.data,
            "num of pages: ": num_of_pages,
            "num of Products: ": filtered_products_count,
        }
        return Response(json, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = serializers.ProductSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            json = {
                "Message: " : "Product added successfully!",
                "Data: " : serializer.data,
            }
            return Response(json, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def product_pk(request, pk):
    try:
        # product = models.Product.objects.get(id=pk)
        product = get_object_or_404(models.Product, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "The product you try to get is not found!"}, status=status.HTTP_204_NO_CONTENT)
    
    if request.method == 'GET':
        serializer = serializers.ProductSerializers(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        if product.user == request.user or request.user.is_superuser:
            serializer = serializers.ProductSerializers(product, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                json = {
                    "Message: " : "Product updated successfully!",
                    "Data: " : serializer.data,
                }
                return Response(json, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Message: " : "You don't have permissions to do this"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    elif request.method == 'DELETE':
        if product.user == request.user or request.user.is_superuser:
            product.delete()
            return Response({"Message: " : "This product is deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"Message: " : "You don't have permissions to do this"}, status=status.HTTP_403_FORBIDDEN)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def create_review(request, pk):
    try:
        # product = models.Product.objects.get(pk=pk)
        product = get_object_or_404(models.Product, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "This Product is not found!"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        review = models.Review.objects.filter(product=product, user=request.user)

        if int(request.data['rating']) <=0 or int(request.data['rating']) >5:
            return Response({"Message: " : "Rating must be between 0 and 5"}, status=status.HTTP_400_BAD_REQUEST)
        elif review.exists():
            review.update(rating = request.data['rating'], comment = request.data['comment'])

            ratings = models.Review.objects.filter(product=product).aggregate(avg_ratings = Avg('rating'))
            product.rating = ratings['avg_ratings']
            product.save()

            json = {
                "Message: ": "Your review updated successfully",
            }
            return Response(json, status=status.HTTP_200_OK)
        else:
            serializer = serializers.ReviewSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, product=product)

                ratings = models.Review.objects.filter(product=product).aggregate(avg_ratings = Avg('rating'))
                product.rating = ratings['avg_ratings']
                product.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def delete_review(request, pk):
    try:
        # product = models.Product.objects.get(pk=pk)
        product = get_object_or_404(models.Product, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "This Product is not found!"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        try:
            review = models.Review.objects.get(product=product, user=request.user)
            review.delete()
            return Response({"Message: " : "Your Review about this product has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"Message: " : "You didn't review this product before!"}, status=status.HTTP_404_NOT_FOUND)
        



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def get_product_reviews(request, pk):
    try:
        # product = models.Product.objects.get(pk=pk)
        product = get_object_or_404(models.Product, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "This Product is not found!"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        try:
            reviews = models.Review.objects.filter(product=product)
            serializer = serializers.ReviewSerializers(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"Message: " : "This product has no reviews yet!"}, status=status.HTTP_404_NOT_FOUND)
        


