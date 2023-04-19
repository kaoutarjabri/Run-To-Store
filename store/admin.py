from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(ShippingAddress)
admin.site.register(Wishlist)
admin.site.register(WishedItems)
admin.site.register(Category)
