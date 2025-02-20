from rest_framework import serializers
from . import models




class ProductSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Customize datetime format
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = models.Product
        fields = ['name', 'description', 'price', 'brand', 'category', 'rating', 'stock', 'created_at', 'updated_at']
        # fields = '__all__'



class ReviewSerializers(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Customize datetime format
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = models.Review
        fields = ['rating', 'comment', 'created_at', 'updated_at']
        # fields = '__all__'