from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver



class Plan(models.Model):
    name = models.CharField(max_length=20, null=True)
    price = models.FloatField(default=0.0)
    def __str__(self):
        return self.name



# Create Extended User.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    mobile = models.CharField(max_length=20 , default= "null")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, default=1)
    otp = models.CharField(max_length=6, default= "null")
    uid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.user.username

    @property
    def username(self):
        return self.user.username
    

class Amenities(models.Model):
    name = models.CharField(max_length= 30, null=True)
    def __str__(self):
        return self.name


class Categories(models.Model):
    cat_name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.cat_name



class Properties(models.Model):
    choices = [
        ("FF", "Fully-Furnished"),
        ("SF", "Semi-Furnished"),
        ("UF", "Un-Furnished")
    ]
    renters = [
        ("OB", "Only Boys"),
        ("OG", "Only Girls"),
        ("FAM", "Family"),
        ("ANY", "Anyone")
    ]
    
    propertytitle = models.CharField(max_length=50, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,null=True)
    address = models.TextField()
    district = models.CharField(max_length=30, null=True)
    state = models.CharField(max_length=30, null=True)
    locality = models.CharField(max_length=30, null=True)
    prefer_renter = models.CharField(max_length=50, choices=renters, null=True, default="ANY")
    pincode = models.IntegerField()
    latitude = models.DecimalField(max_digits=15, decimal_places=10, null=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=10, null = True)
    rent = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    furnishing = models.CharField(max_length=50, choices=choices, null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    amenities = models.ManyToManyField(Amenities)
    phone_no_visibility = models.BooleanField(default=True)
    property_visibility = models.BooleanField(default=True)

    property_id = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return str(self.propertytitle)
    
    def property_title(self):
        return self.propertytitle
   


class Wishlist(models.Model):
    profile =  models.ForeignKey(Profile, on_delete=models.CASCADE,null=True)
    wishlist_property = models.ForeignKey(Properties,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.profile.user.username

class PropertyImages(models.Model):
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, null=True, related_name='images')
    image = models.ImageField(upload_to="property/%Y/%m/%d/",default="",max_length=255)

    def __str__(self):
        return self.property.profile.user.username
    
    def image_tag(self):
	    return mark_safe('<img src="%s" width="80" />' % (self.image.url))

    def property_title(self):
        return self.property.propertytitle
     
    def name(self):
        return self.property.profile.user.username
    



# Chat Room 
class Room(models.Model):
    property = models.ForeignKey(Properties, on_delete=models.CASCADE)
    user1 = models.ForeignKey(User, related_name='rooms_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='rooms_as_user2', on_delete=models.CASCADE)
    room_id =  models.UUIDField(default=uuid.uuid4)

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages',null=True)
    is_read = models.BooleanField(default=False)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ('timestamp',)


# ..............................................Dashboard........................................#
class Tenant(models.Model):
    property = models.ForeignKey(Properties,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    rent = models.IntegerField(default=0)
    advance = models.IntegerField(default=0)
    start_date = models.DateField()
    adhaar_no = models.BigIntegerField(default=0)
    uid = models.UUIDField(default=uuid.uuid4)
    document = models.FileField(upload_to="documents/%Y/%m/%d/",default="",max_length=255)
    photo = models.ImageField(upload_to="documents/%Y/%m/%d/",default="",max_length=255)
    
    def __str__(self):
        return self.name


    
class TenantRentRecord(models.Model):
     choices = [
        ("0", "Pending"),
        ("1", "Collected")
        ]

     tenant = models.ForeignKey(Tenant,on_delete=models.CASCADE)
     month = models.IntegerField(default=0)
     amount_rec = models.IntegerField(default=0)
     received_date = models.DateField()
     status = models.CharField(max_length=20, choices=choices, default="0")

     def __str__(self):
        return self.tenant.name






class Banners(models.Model):
	img=models.ImageField(upload_to="banners/")
	alt_text=models.CharField(max_length=150)

	class Meta:
		verbose_name_plural='Banners'

	def __str__(self):
		return self.alt_text

	def image_tag(self):
		return mark_safe('<img src="%s" width="80" />' % (self.img.url))
	




# Pages
class Page(models.Model):
	title=models.CharField(max_length=200)
	detail=models.TextField()

	def __str__(self):
		return self.title

# FAQ
class Faq(models.Model):
	quest=models.TextField()
	ans=models.TextField()

	def __str__(self):
		return self.quest


#Pricing Premium
class Premium_details(models.Model):
    phone_no = models.CharField(max_length=20, null=True)
    username = models.CharField(max_length=50, null=True)

    def __str__(self):
         return self.username


