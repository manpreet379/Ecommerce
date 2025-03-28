from django.contrib import admin

from.models import AppUser, Address, Seller, Product, Tag
admin.site.register(AppUser)
admin.site.register(Address)
admin.site.register(Seller)
admin.site.register(Product)
admin.site.register(Tag)

# Register your models here.
