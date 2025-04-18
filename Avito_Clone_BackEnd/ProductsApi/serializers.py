from rest_framework import serializers
from .models import Product, ProductImage
from CategorisApi.models import MainCategory, SubCategory
from CategorisApi.serializers import MainCategorySerializer, SubCategorySerializer

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    main_category = MainCategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    main_category_id = serializers.PrimaryKeyRelatedField(
        queryset=MainCategory.objects.all(),
        source='main_category',
        write_only=True
    )
    sub_category_id = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(),
        source='sub_category',
        write_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 
            'main_category', 'sub_category', 
            'main_category_id', 'sub_category_id',
            'created_at', 'updated_at', 'user', 'images'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user'] 