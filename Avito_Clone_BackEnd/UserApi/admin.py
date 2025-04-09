from django.contrib import admin




from .models import PhoneVerification, User

admin.site.register(User)
admin.site.register(PhoneVerification)
