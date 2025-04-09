from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import MainCategory, SubCategory
from .serializers import MainCategorySerializer, SubCategorySerializer

@api_view(['GET'])
@permission_classes([AllowAny])  # Applying the same permission logic
def list_main_categories(request):
    main_categories = MainCategory.objects.all()
    serializer = MainCategorySerializer(main_categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])  # Applying the same permission logic
def list_subcategories(request, main_category_id):
    try:
        subcategories = SubCategory.objects.filter(main_category_id=main_category_id)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data)
    except MainCategory.DoesNotExist:
        return Response({"error": "Main Category not found"}, status=404)