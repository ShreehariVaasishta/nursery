from django.contrib import admin
from .models import Plants, Cart, Order

# Register your models here.
admin.site.register(Plants)
admin.site.register(Cart)
admin.site.register(Order)