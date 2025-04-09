from django.db import models

class MainCategory(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    name = models.CharField(max_length=100, unique=True)
    subtitle = models.CharField(max_length=150)
    icon = models.CharField(max_length=150)
    logo_img = models.ImageField(upload_to='logos/')  # Field for logo image upload
    main_img = models.ImageField(upload_to='main_images/')  # Field for main image upload

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=150)
    logo_img = models.ImageField(upload_to='logos/')  # Field for logo image upload
    main_category = models.ForeignKey(
        MainCategory, on_delete=models.CASCADE, related_name="subcategories"
    )  # Foreign key linking to MainCategory

    def __str__(self):
        return f"{self.name} ({self.main_category.name})"