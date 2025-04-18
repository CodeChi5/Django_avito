from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer
from CategorisApi.models import MainCategory, SubCategory

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'all_products', 'get_by_id', 'get_by_category', 'get_by_main_category', 'get_by_sub_category']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        return Product.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def all_products(self, request):
        """Get all products with pagination"""
        products = self.get_queryset()
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def get_by_id(self, request, pk=None):
        """Get a specific product by ID"""
        product = get_object_or_404(Product, pk=pk)
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def get_by_main_category(self, request):
        """Get products by main category"""
        main_category_id = request.query_params.get('main_category_id', '')
        if not main_category_id:
            return Response(
                {'error': 'Main category ID parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            main_category = MainCategory.objects.get(id=main_category_id)
            products = Product.objects.filter(main_category=main_category).order_by('-created_at')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except MainCategory.DoesNotExist:
            return Response(
                {'error': 'Main category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def get_by_sub_category(self, request):
        """Get products by sub category"""
        sub_category_id = request.query_params.get('sub_category_id', '')
        if not sub_category_id:
            return Response(
                {'error': 'Sub category ID parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            sub_category = SubCategory.objects.get(id=sub_category_id)
            products = Product.objects.filter(sub_category=sub_category).order_by('-created_at')
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        except SubCategory.DoesNotExist:
            return Response(
                {'error': 'Sub category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            # Handle image uploads
            images = request.FILES.getlist('images', [])
            for image in images:
                ProductImage.objects.create(
                    product=serializer.instance,
                    image=image,
                    is_primary=not ProductImage.objects.filter(product=serializer.instance).exists()
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            # Handle image uploads
            images = request.FILES.getlist('images', [])
            for image in images:
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    is_primary=not ProductImage.objects.filter(product=instance).exists()
                )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
