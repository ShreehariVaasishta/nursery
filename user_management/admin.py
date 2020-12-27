from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, Buyer, Nursery

# # Register your models here.
admin.site.unregister(Group)
admin.site.register(User)
admin.site.register(Buyer)
admin.site.register(Nursery)