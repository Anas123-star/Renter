from django.contrib import admin
from .models import *
from django.forms.widgets import CheckboxSelectMultiple
# Register your models here.

class PlanAdmin(admin.ModelAdmin):
    list_display = ('name','price')
admin.site.register(Plan, PlanAdmin)


class ProfileAdmin(admin.ModelAdmin):
	list_display=('mobile','username')
admin.site.register(Profile, ProfileAdmin)


class AmenitiesAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Amenities, AmenitiesAdmin)


class CategoriesAdmin(admin.ModelAdmin):
     list_display = ('cat_name',)
admin.site.register(Categories, CategoriesAdmin )


class PropertiesAdmin(admin.ModelAdmin):
    list_display = ('property_id','property_title',)
admin.site.register(Properties, PropertiesAdmin )

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('profile',)
admin.site.register(Wishlist, WishlistAdmin )

class PropertyImagesAdmin(admin.ModelAdmin):
    list_display = ('name','property_title','image_tag')
admin.site.register(PropertyImages, PropertyImagesAdmin )


class RoomAdmin(admin.ModelAdmin):
	list_display=('property','user1','user2')
admin.site.register(Room, RoomAdmin)

class MessageAdmin(admin.ModelAdmin):
	list_display=('sender','room','content')
admin.site.register(Message, MessageAdmin)

class TenantAdmin(admin.ModelAdmin):
	list_display=('name','start_date')
admin.site.register(Tenant, TenantAdmin)

class TenantRentRecordAdmin(admin.ModelAdmin):
	list_display=('month','status')
admin.site.register(TenantRentRecord, TenantRentRecordAdmin)


class BannerAdmin(admin.ModelAdmin):
	list_display=('alt_text','image_tag')
admin.site.register(Banners,BannerAdmin)

class PageAdmin(admin.ModelAdmin):
	list_display=('title',)
admin.site.register(Page,PageAdmin)

class FaqAdmin(admin.ModelAdmin):
	list_display=('quest',)
admin.site.register(Faq,FaqAdmin)

class Premium_detailsAdmin(admin.ModelAdmin):
	list_display=('username',)
admin.site.register(Premium_details,Premium_detailsAdmin)



