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
import datetime
from django.utils import timezone



# Create your views here.




@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def items(request):
    if request.method == 'GET':
        items = models.Item.objects.all()
        # Apply filters on items to get presied search
        filter = filters.ItemFilter(request.GET, items.order_by('id'))
        filtered_items_count = filter.qs.count()
        # Apply pagination after filtering my items
        paginator = PageNumberPagination()
        res_per_page = 2
        paginator.page_size = res_per_page # number of items per page
        paginated_items = paginator.paginate_queryset(filter.qs, request)
        # Serialize the paginated queryset
        serializer = serializers.ItemSerializers(paginated_items, many=True)
        num_of_pages = math.ceil(filtered_items_count / res_per_page)
        json = {
            "items: ": serializer.data,
            "num of pages: ": num_of_pages,
            "num of items: ": filtered_items_count,
        }
        return Response(json, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = serializers.ItemSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            json = {
                "Message: " : "Item added successfully!",
                "Data: " : serializer.data,
            }
            return Response(json, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def item_pk(request, pk):
    try:
        # Item = models.Item.objects.get(id=pk)
        item = get_object_or_404(models.Item, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "The Item you try to get is not found!"}, status=status.HTTP_204_NO_CONTENT)
    
    if request.method == 'GET':
        serializer = serializers.ItemSerializers(item, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        if item.user == request.user or request.user.is_superuser:
            serializer = serializers.ItemSerializers(item, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                json = {
                    "Message: " : "Item updated successfully!",
                    "Data: " : serializer.data,
                }
                return Response(json, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Message: " : "You don't have permissions to do this"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    elif request.method == 'DELETE':
        if item.user == request.user or request.user.is_superuser:
            item.delete()
            return Response({"Message: " : "This Item is deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"Message: " : "You don't have permissions to do this"}, status=status.HTTP_403_FORBIDDEN)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def create_review(request, pk):
    try:
        # Item = models.Item.objects.get(pk=pk)
        item = get_object_or_404(models.Item, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "This Item is not found!"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        review = models.Review.objects.filter(item=item, user=request.user)

        if int(request.data['rating']) <=0 or int(request.data['rating']) >5:
            return Response({"Message: " : "Rating must be between 0 and 5"}, status=status.HTTP_400_BAD_REQUEST)
        elif review.exists():
            review.update(rating = request.data['rating'], comment = request.data['comment'])

            ratings = models.Review.objects.filter(item=item).aggregate(avg_ratings = Avg('rating'))
            item.rating = ratings['avg_ratings']
            item.save()

            json = {
                "Message: ": "Your review updated successfully",
            }
            return Response(json, status=status.HTTP_200_OK)
        else:
            serializer = serializers.ReviewSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, item=item)

                ratings = models.Review.objects.filter(item=item).aggregate(avg_ratings = Avg('rating'))
                item.rating = ratings['avg_ratings']
                item.save()

                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def delete_review(request, pk):
    try:
        # Item = models.Item.objects.get(pk=pk)
        item = get_object_or_404(models.Item, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "This Item is not found!"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        try:
            review = models.Review.objects.get(item=item, user=request.user)
            review.delete()

            rating = models.Review.objects.filter(item=item).aggregate(avg_ratings = Avg('rating'))   
            if rating['avg_ratings'] is None:
                item.rating = 0
                item.save()
            return Response({"Message: " : "Your Review about this Item has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"Message: " : "You didn't review this Item before!"}, status=status.HTTP_404_NOT_FOUND)
        



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def get_item_reviews(request, pk):
    try:
        # Item = models.Item.objects.get(pk=pk)
        item = get_object_or_404(models.Item, id=pk)
    except ObjectDoesNotExist:
        return Response({"Message: " : "This Item is not found!"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        try:
            reviews = models.Review.objects.filter(item=item)
            serializer = serializers.ReviewSerializers(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"Message: " : "This Item has no reviews yet!"}, status=status.HTTP_404_NOT_FOUND)
        





@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def add_to_cart(request, pk):
    # get the item
    item = get_object_or_404(models.Item, pk=pk)

    if item.quantity == 0:
        return Response({"Message: " : "This item is out of stock!"}, status=status.HTTP_204_NO_CONTENT)
    else:    
        # create an order item or that order or get it if it exists
        order_item, created = models.OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
            )
        
        order_qs = models.Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the orderitem is in the order
            if order.items.filter(item__pk = item.pk).exists():
                if item.quantity > 0:
                    order_item.quantity += 1
                    order_item.save()

                    # Update the quantity for the item in the cart
                    models.Item.objects.filter(pk=pk).update(quantity = (item.quantity - 1))
                    return Response({"Message: " : "This item quantity has been successfully updated!"}, status=status.HTTP_200_OK)
                    # return redirect("order_summary")
                else:
                    return Response({"Message: " : "This item is out of stock!"}, status=status.HTTP_204_NO_CONTENT)
                    # return redirect("shop")
            else:
                if item.quantity > 0:
                    order.items.add(order_item)
                    # Update the quantity for the item in the cart
                    models.Item.objects.filter(pk=pk).update(quantity = (item.quantity - 1))
                    return Response({"Message: " : "added to cart!"}, status=status.HTTP_200_OK)
                    # return redirect("order_summary")
                else:
                    return Response({"Message: " : "This item is out of stock!"}, status=status.HTTP_204_NO_CONTENT)
                    # return redirect("shop")
        else: 
            # Update the quantity for the item in the cart
            models.Item.objects.filter(pk=pk).update(quantity = (item.quantity - 1))

            ordered_date = timezone.now()
            order = models.Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return Response({"Message: " : "added to cart!"}, status=status.HTTP_200_OK)
            # redirect("shop")




@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def remove_single_item_from_cart(request, pk):
    # get the item
    item = get_object_or_404(models.Item, pk=pk)
    
    order_qs = models.Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__pk = item.pk).exists():
            order_item = models.OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()

                # Update the quantity for the item in the cart
                models.Item.objects.filter(pk=pk).update(quantity = (item.quantity + 1))
                return Response({"Message: " : "This item quantity has been successfully updated!"}, status=status.HTTP_200_OK)
                # return redirect("order_summary")
            else:
                models.Item.objects.filter(pk=pk).update(quantity = (item.quantity + 1))
                order.items.remove(order_item)
                order_item.save()
                return Response({"Message: " : "This item removed from cart!"}, status=status.HTTP_204_NO_CONTENT)
                # return redirect("order_summary")

        else:
            return Response({"Message: " : "This item not found in cart!"}, status=status.HTTP_204_NO_CONTENT)
            # return redirect("shop")
    else:
        return Response({"Message: " : "You don't have an active order!"}, status=status.HTTP_204_NO_CONTENT)
        # return redirect("shop")
    



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def remove_from_cart(request, pk):
    # get the item
    item = get_object_or_404(models.Item, pk=pk)
    
    order_qs = models.Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # check if the orderitem is in the order
        if order.items.filter(item__pk = item.pk).exists():
            order_item = models.OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            # Update the quantity for the item in the cart
            models.Item.objects.filter(pk=pk).update(quantity = (item.quantity + order_item.quantity))
            
            order.items.remove(order_item)
            return Response({"Message: " : "This item removed from cart!", "redirect_url": "/order_summary/"}, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"Message: " : "This item not found in cart!", "redirect_url": "/shop/"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({"Message: " : "You don't have an active order!", "redirect_url": "/shop/"}, status=status.HTTP_204_NO_CONTENT)





@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def order_summary(request):
    try:
        order = models.Order.objects.get(user=request.user, ordered=False)

        json = {}
        for order_item in order.items.all():
            json["item"] = order_item.item.name
            json["item_description"] = order_item.item.description
            json["item_price"] = order_item.item.price
            json["item_discount_price"] = order_item.item.discount_price
            json["quantity"] = order_item.quantity
            json["final_price"] = order_item.item.get_final_item_price()


        return Response({"Message: " : "Your Order...", "Data: " : json}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({"Message: " : "You don't have an active order!", "redirect_url": "/shop/"}, status=status.HTTP_204_NO_CONTENT)

