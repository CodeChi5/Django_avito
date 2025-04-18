from django.contrib import admin

# Register your models here.



from .models import ProductImage, Product

admin.site.register(Product)
admin.site.register(ProductImage)
