from django.shortcuts import render,redirect,HttpResponse
from django.db.models import Q
from django.urls import reverse
from .models import *
from django.http import JsonResponse
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import authenticate,login,logout
import json
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.serializers import serialize
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
import random
import requests
import re
import os
import googlemaps
from django.core.mail import send_mail
from math import sin, cos, sqrt, atan2, radians



def calculate_distance(lat1, lon1, lat2, lon2):
    # Approximate radius of the Earth in kilometers
    earth_radius = 6371
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = earth_radius * c
    return distance

def get_address(lat,lng,api_key):
    if lat and lng:
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}'
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK':
            results = data['results']
            if len(results) > 0:
                address = results[0]['formatted_address']
                print(address)
                return JsonResponse({'address': address})
    
    return JsonResponse({'error': 'Invalid coordinates'})


def get_coordinates(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data["status"] == "OK":
        # Extract latitude and longitude
        location = data["results"][0]["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
        return latitude, longitude
    else:
        print("Geocoding API request failed.")









def validate_password(password):
    # if len(password) < 8:
    #     return False
    # if not re.search(r'\d', password):
    #     return False
    # if not re.search(r'[A-Z]', password):
    #     return False
    return True


def send_otp(to, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP: {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to
    )
    return message.sid


def logout_view(request):
    logout(request)
    return redirect('login')



def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password= password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            context = {'message' : 'User not found' , 'class' : 'danger' }
            return render(request,'registration/login.html' , context)
    return render(request,'registration/login.html')


# def change_password(request):
#     return render(request, 'registration/change_password.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to update the session with the new password
            return redirect('home')  # Redirect to the home page or any other desired page after successful password change
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'registration/change_password.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        mobile_no = request.POST.get('mobile_no')
        mobile_no_with_code = '+91-'+ mobile_no
        profile_obj = Profile.objects.filter(mobile = mobile_no_with_code).first()
        if profile_obj is not None:
            user_obj = profile_obj.user
            otp = str(random.randint(1000,9999))
            profile_obj.otp = otp
            profile_obj.save()
            send_otp(mobile_no_with_code, otp)
            return redirect(f'/forgot_password_otp/{profile_obj.uid}')
        else:
            context = {'message': "User does not exist", 'class':'danger'}
            return render(request, 'registration/forgot_password.html', context)

    return render(request, 'registration/forgot_password.html')

def register(request):
    if request.method == 'POST':
         email = request.POST.get('email')
        #  name = request.POST.get('name')
         username = request.POST.get('username')
         pass1 = request.POST.get('password1')
         pass2 = request.POST.get('password2')
         mobile_no_without_code = request.POST.get('mobile')
         mobile = '+91-' + mobile_no_without_code 
         check_user = User.objects.filter(email = email).first()
         check_profile = Profile.objects.filter(mobile = mobile).first()  
         if check_user is not None:
            try:
                profile_of_user = check_user.profile
                if profile_of_user.is_verified:
                    print(profile_of_user)
                else:
                    check_user.delete()
                    context = {'message': "You have not verified the account previously. Please register again.", 'class': 'success'}
                    return render(request, 'registration/register.html', context)
            except ObjectDoesNotExist:
                check_user.delete()
                context = {'message': "Redundant user is deleted successfully. You can now register.", 'class': 'success'}
                return render(request, 'registration/register.html', context)
                
         if check_profile:
            context = {'message': "This mobile number is already in use add different mobile number", 'class':'danger'}
            return render(request, 'registration/register.html', context)
         
         if check_user:
            context = {'message': "Email id already in use OR Username is already in use", 'class':'danger'}
            return render(request, 'registration/register.html', context)
         
         if pass1 != pass2:
            context = {'message': "Both password does not match", 'class':'danger'}
            return render(request, 'registration/register.html', context)
         else:
            user = User(email = email, username= username)
            is_validate_pass = validate_password(pass1)
            if is_validate_pass: 
                user.set_password(pass1)
                user.save()
                otp = str(random.randint(1000,9999))
                profile = Profile(user= user, mobile = mobile, otp = otp)
                profile.save()
                send_otp(mobile, otp)
                return redirect(f'/otp/{profile.uid}')
            else:
                context = {'message': "Password must be greater than 8 digit with atleast one capital letter and one number", 'class':'danger'}
                return render(request, 'registration/register.html', context)
    return render(request, 'registration/register.html')   



def forgot_password_otp(request,uid):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.get(uid=uid)
        user = profile.user
        if otp == profile.otp:    
            return redirect(f'/add_new_password/{profile.uid}')
        
    return render(request,'registration/otp.html' )

def add_new_password(request,uid):
    profile = Profile.objects.get(uid=uid)
    user = profile.user
    if request.method == 'POST':
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        is_validate_pass = validate_password(pass1)
        if pass1 == pass2:
            if is_validate_pass:
                new_password = make_password(pass1)
                user.password = new_password
                user.save()
                return redirect('login')
            else:
                context = {'message': "Password must be greater than 8 digit with atleast one capital letter and one number", 'class':'danger'}
                return render(request, 'registration/new_password.html', context)
        else:
            context = {'message': "Both Passwords must be same ", 'class':'danger'}
            return render(request, 'registration/new_password.html', context)

    return render(request, 'registration/new_password.html', {'username':user.username})


def otp(request, uid):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.get(uid=uid)
        if otp == profile.otp:
            profile.is_verified = True
            profile.save()
            return redirect('login')
        else:
            message = 'Entered OTP is wrong'
            return render(request,'registration/otp.html', {'message':message})
    return render(request,'registration/otp.html' )


def delete_account(request,username):
    user = User.objects.get(username= username)
    user.delete()
    return redirect('register')


def list_property(request):
    user = request.user
    if not isinstance(user, AnonymousUser):
        user_plan =  request.user.profile.plan
        profile_obj = request.user.profile
        no_of_prop = Properties.objects.filter(profile=profile_obj).count()

        #    profile_obj.plan

        renter_choices = Properties.prefer_renter.field.choices
        furnishing_choices = Properties.furnishing.field.choices
        with open('static/state_district.json') as json_file:
                data = json.load(json_file)
                states = data['states']
        district_list = []
        states_list = []
        for i in states:
                states_list.append(i['state'])
                for district in i['districts']:
                    district_list.append(district)
        google_map_api_key = settings.GOOGLE_MAPS_API_KEY
        categorical_choices = Categories.objects.all()
        amenities = Amenities.objects.all()
        params = {'renter_choices':renter_choices,'furnishing_choices':furnishing_choices,'categorical_choices':categorical_choices,'amenities':amenities,'google_map_api_key':google_map_api_key, 'states':states_list, 'districts':district_list}

            
        if request.user.is_authenticated:
                if user_plan.name == "Free":
                    if no_of_prop >= 1 :
                        return redirect('pricing')
                    else:
                        if request.method == "POST":
                            profile = request.user.profile
                            propertytitle = request.POST.get("property_title")
                            address = request.POST.get("address")
                            state = request.POST.get("state")
                            city = request.POST.get("district")
                            area = request.POST.get("area")
                            rent = request.POST.get("rent")
                            prefer_renter = request.POST.get("prefer_renter")
                            phone_no_visibility = request.POST.get("phone_no_visibility")
                            type_of_home = request.POST.get("type_of_home")
                            furnishing = request.POST.get("furnishing")
                            pincode = request.POST.get("pincode")
                            description = request.POST.get("description")
                            selected_amenities =  request.POST.getlist("amenities")
                            lat, lng = get_coordinates(address, google_map_api_key)
                            amenities = Amenities.objects.filter(id__in=selected_amenities)
                            category = Categories.objects.get(id=type_of_home)
                            print(phone_no_visibility)
                            print(city)
                            print(state)
                            print(area)
                            prop_obj = Properties.objects.create(profile=profile, propertytitle = propertytitle, address=address, state=state, district=city, locality=area,
                                                        rent=rent, prefer_renter=prefer_renter,category=category, furnishing=furnishing,pincode=pincode,
                                                        description=description, phone_no_visibility = phone_no_visibility)
                            
                            
                            prop_obj.amenities.set(amenities)
                            prop_obj.latitude = lat
                            prop_obj.longitude = lng
                            prop_obj.save()
                            id = prop_obj.property_id
                            print(prop_obj)
                            return redirect(f'/upload_images/{id}')   
                else:
                    if no_of_prop >= 5 :
                        return HttpResponse("You have fullfilled your limit")
                    else:
                        if request.method == "POST":
                            profile = request.user.profile
                            propertytitle = request.POST.get("property_title")
                            address = request.POST.get("address")
                            state = request.POST.get("state")
                            city = request.POST.get("district")
                            area = request.POST.get("area")
                            rent = request.POST.get("rent")
                            prefer_renter = request.POST.get("prefer_renter")
                            phone_no_visibility = request.POST.get("phone_no_visibility")
                            type_of_home = request.POST.get("type_of_home")
                            furnishing = request.POST.get("furnishing")
                            pincode = request.POST.get("pincode")
                            description = request.POST.get("description")
                            selected_amenities =  request.POST.getlist("amenities")
                            lat, lng = get_coordinates(address, google_map_api_key)
                            amenities = Amenities.objects.filter(id__in=selected_amenities)
                            category = Categories.objects.get(id=type_of_home)
                            print(phone_no_visibility)
                            print(city)
                            print(state)
                            print(area)
                            prop_obj = Properties.objects.create(profile=profile, propertytitle = propertytitle, address=address, state=state, district=city, locality=area,
                                                        rent=rent, prefer_renter=prefer_renter,category=category, furnishing=furnishing,pincode=pincode,
                                                        description=description, phone_no_visibility = phone_no_visibility)
                            
                            
                            prop_obj.amenities.set(amenities)
                            prop_obj.latitude = lat
                            prop_obj.longitude = lng
                            prop_obj.save()
                            id = prop_obj.property_id
                            print(prop_obj)
                            return redirect(f'/upload_images/{id}')               
        else:
                return redirect('login')
        return render(request, 'properties/list_property_form.html', params)
    else:
        return redirect('login')

def upload_images(request,uid):
    if request.method == "POST":
        property_obj = Properties.objects.get(property_id = uid)
        images = request.FILES.getlist('multiple_images')
        # folder_path = os.path.join(settings.MEDIA_ROOT, 'property',str(request.user.username),str(uid))
        # os.makedirs(folder_path, exist_ok=True)
        for image in images:
            # file_path = os.path.join(folder_path, image.name)
            # # Save the image to the folder
            # with open(file_path, 'wb') as file:
            #     for chunk in image.chunks():
            #         file.write(chunk)
            PropertyImages.objects.create(property = property_obj,image=image)
        return redirect('listed_properties')
    return render(request,'properties/add_images.html')


def single_property_view(request,uid):
    prop_obj = Properties.objects.filter(property_id = uid)
    user1 = request.user.username
    renter_choices = Properties.prefer_renter.field.choices
    furnishing_choices = Properties.furnishing.field.choices
    
    property = []
    for prop in prop_obj:
        images = PropertyImages.objects.filter(property= prop)
        amenities = prop.amenities.all()
        user2 = prop.profile.user.username
        wishlist_prop_exist = Wishlist.objects.filter(wishlist_property = prop).exists()

        property.append([prop,images,amenities,wishlist_prop_exist,user1,user2])
    param = {'property':property,'renter_choices':renter_choices, 'furnishing_choices':furnishing_choices}
    return render(request,'properties/single_property_view.html', param)


def show_property_photos(request,uid):
    prop_obj = Properties.objects.get(property_id = uid)
    images = PropertyImages.objects.filter(property=prop_obj)

    return render(request, 'properties/show_property_photos.html' , {'prop_obj':prop_obj,'images':images, 
                                                                     })


def listed_properties(request):
    prop_obj = Properties.objects.filter(profile = request.user.profile)
    property = []
    for prop in prop_obj:
        images = PropertyImages.objects.filter(property= prop)
        property.append([prop,images])
    param = {'property':property}
    return render(request,'properties/listed_properties.html', param)

def property_availability(request,uid):
    prop_obj = Properties.objects.get(property_id = uid)
    if prop_obj.property_visibility:
        prop_obj.property_visibility =  False
    else:
        prop_obj.property_visibility =  True
    prop_obj.save()
    return redirect('listed_properties')

def delete_property(request, uid):
    prop_obj = Properties.objects.get(property_id = uid)
    prop_obj.delete()
    return redirect('listed_properties')

def edit_property(request,uid):
    property = Properties.objects.get(property_id = uid)
    # user_plan = request.user.profile.plan
    # profile_obj = request.user.profile
    # no_of_prop = Properties.objects.filter(profile=profile_obj).count()
    renter_choices = Properties.prefer_renter.field.choices
    furnishing_choices = Properties.furnishing.field.choices
    with open('static/state_district.json') as json_file:
        data = json.load(json_file)
        states = data['states']
    district_list = []
    states_list = []
    for i in states:
        states_list.append(i['state'])
        for district in i['districts']:
            district_list.append(district)
    google_map_api_key = settings.GOOGLE_MAPS_API_KEY
    categorical_choices = Categories.objects.all()
    amenities = Amenities.objects.all()
    prop_amenities_list = []
    for i in property.amenities.all():
        prop_amenities_list.append(i.name)
    print(prop_amenities_list)
    params = {
        'renter_choices': renter_choices,
        'furnishing_choices': furnishing_choices,
        'categorical_choices': categorical_choices,
        'amenities': amenities,
        'google_map_api_key': google_map_api_key,
        'states': states_list,
        'districts': district_list,
        'property': property,
        'prop_amenities_list':prop_amenities_list
    }
    if request.method == "POST":
        property.property_title = request.POST.get("property_title")
        property.address = request.POST.get("address")
        property.state = request.POST.get("state")
        property.district = request.POST.get("district")
        property.locality = request.POST.get("area")
        property.rent = request.POST.get("rent")
        property.prefer_renter = request.POST.get("prefer_renter")
        property.phone_no_visibility = request.POST.get("phone_no_visibility")
        property.type_of_home = request.POST.get("type_of_home")
        property.furnishing = request.POST.get("furnishing")
        property.pincode = request.POST.get("pincode")
        property.description = request.POST.get("description")
        selected_amenities = request.POST.getlist("amenities")
        lat, lng = get_coordinates(property.address, google_map_api_key)
        amenities = Amenities.objects.filter(id__in=selected_amenities)
        property.category = Categories.objects.get(id=property.type_of_home)
        property.amenities.set(amenities)
        property.latitude = lat
        property.longitude = lng
        property.save()
        message = 'Your property details has been updated successfully'
        params = {
        'renter_choices': renter_choices,
        'furnishing_choices': furnishing_choices,
        'categorical_choices': categorical_choices,
        'amenities': amenities,
        'google_map_api_key': google_map_api_key,
        'states': states_list,
        'districts': district_list,
        'property': property,
        'prop_amenities_list':prop_amenities_list,
        'message':message
    }
        
        return render(request, 'properties/edit_property.html', params)
    return render(request, 'properties/edit_property.html',params)


def edit_property_photos(request,uid):
    prop_obj = Properties.objects.get(property_id = uid)
    images = PropertyImages.objects.filter(property=prop_obj)
    print(images)
    return render(request, 'properties/edit_property_photos.html' , {'prop_obj':prop_obj,'images':images})

def delete_property_photo(request,uid,id):
    prop_obj = Properties.objects.get(property_id = uid)
    image_obj = PropertyImages.objects.get(id = id)
    image_obj.delete()
    url = reverse('edit_property_photos', args=[uid])
    return redirect(url)


def add_to_wishlist(request,uid):

    user = request.user
    if not isinstance(user, AnonymousUser):
        profile = request.user.profile
        property = Properties.objects.get(property_id = uid)
        wishlist_prop = Wishlist(profile=profile,wishlist_property=property)
        wishlist_prop_exist = Wishlist.objects.filter(wishlist_property = property).exists()
        if wishlist_prop_exist:
            return redirect(f'/wishlist/')
        else:
            wishlist_prop.save()
        return redirect(f'/property_detailed_view/{uid}')
    else:
        return redirect('login')
def remove_from_wishlist(request,uid):
    prop = Properties.objects.get(property_id = uid)
    wish = Wishlist.objects.filter(wishlist_property = prop)
    wish.delete()
    return redirect(f'/wishlist')

def remove_property_from_wishlist(request,uid):
    prop = Properties.objects.get(property_id = uid)
    wish = Wishlist.objects.filter(wishlist_property = prop)
    wish.delete()
    return redirect(f'/property_detailed_view/{uid}')


def wishlist(request):
    wishlist = list(Wishlist.objects.filter(profile = request.user.profile))
    property = []
    for wish in wishlist:
        prop = wish.wishlist_property 
        images = PropertyImages.objects.filter(property= prop)
        property.append([prop,images])
    param = {'property':property}
    return render(request,'user_profile/wishlist.html', param)



def index(request):  
    banners=Banners.objects.all()
    all_properties = Properties.objects.all()
    renter_choices = Properties.prefer_renter.field.choices
    categories = Categories.objects.all()
    cat_properties = []
    property_images = PropertyImages.objects.all()

    cities = Properties.objects.values_list('district', flat=True).distinct()
    localities = Properties.objects.values_list('district', 'locality').distinct()
    user = request.user
    profile = None
    plan = None
    unread_mssg = 0
    print(user)
    if not isinstance(user, AnonymousUser):
        print("hello")
        profile = Profile.objects.get(user=user)
        plan = profile.plan.name
        unread_mssg = Message.objects.filter(recipient = request.user, is_read = False).count()

    all_property = []

    for i in all_properties:
        prop_image = PropertyImages.objects.filter(property=i)
        all_property.append([i,prop_image.first()])


    for cat in categories:
        prop = Properties.objects.filter(category=cat)
        property = []
        for i in prop:
            prop_image = PropertyImages.objects.filter(property=i)
            property.append([i,prop_image.first()])
            cat_properties.append([property,cat.id,cat.cat_name])
    
    params = {'all_properties': all_property, 'cat_properties':cat_properties,'categories':categories, 'prop_images':property_images,
              'localities':localities,'renter_choices':renter_choices,'cities':cities, 'banners':banners, 'plan':plan,'unread_mssg':unread_mssg}
    return render(request, 'home/index.html', params)
    



def search_properties(request):
    serialise_property = request.session.get('result')
    city = request.session.get('city_result')
    prefer_renter = request.session.get('renter_choices_result')
    prefer_renter_list = [prefer_renter]
    selected_category = request.session.get('selected_category_result')
    selected_amenities = request.session.get('amenities_result')
    selected_location = request.session.get('location_result')
    amenities = Amenities.objects.all()
    renter_choices = Properties.prefer_renter.field.choices
    categories = Categories.objects.all()
    all_properties_obj = Properties.objects.all()
    max = request.session.get('max_price_result')

    if serialise_property is not None:
        property = []
        for i in serialise_property:
            propertyi = json.dumps(i)
            uid = json.loads(propertyi)['fields']['property_id']
            prop_obj = Properties.objects.get(property_id = uid)
            images = PropertyImages.objects.filter(property= prop_obj)
            image = images.first()
            prop_amenities = prop_obj.amenities.all()
            wishlist_prop_exist = Wishlist.objects.filter(wishlist_property = prop_obj).exists()
            property.append([prop_obj,image, prop_amenities,wishlist_prop_exist])
            

    if request.method == "POST":
        city = request.POST.get("city")
        prefer_renter = request.POST.get("prefer_renter")
        prefer_renter_list = []
        prefer_renter_list.append(prefer_renter)
        print(prefer_renter)
        type_of_home = request.POST.get("type_of_home")
        max = 0
        for prop_obj in all_properties_obj:
            if prop_obj.rent > max :
                max = prop_obj.rent
            else:
                max = max

        if type_of_home == str(0):
            selected_category = ["All"]
        else:
            selected_category = [Categories.objects.get(id=type_of_home).cat_name]
        
        if type_of_home == str(0):
            if prefer_renter == 'ANY':
                searched_properties = Properties.objects.filter(district = city)
                result = json.loads(serialize('json', searched_properties))
                request.session['result'] = result
            else:
                searched_properties = Properties.objects.filter(district = city, prefer_renter = prefer_renter)
                result = json.loads(serialize('json', searched_properties))
                request.session['result'] = result

        else:
            if prefer_renter == 'ANY':
                searched_properties = Properties.objects.filter(district = city, category = type_of_home)
                result = json.loads(serialize('json', searched_properties))
                request.session['result'] = result

            else:
                searched_properties = Properties.objects.filter(category = type_of_home, district = city, prefer_renter = prefer_renter) 
                result = json.loads(serialize('json', searched_properties))
                request.session['result'] = result
        property = []
        request.session['city_result'] = city
        request.session['selected_category_result'] = selected_category
        for prop in searched_properties:
            images = PropertyImages.objects.filter(property= prop)
            image = images.first()
            prop_amenities = prop.amenities.all()
            wishlist_prop_exist = Wishlist.objects.filter(wishlist_property = prop).exists()
            property.append([prop,image,prop_amenities,wishlist_prop_exist])

    return render(request, 'properties/all_properties.html',{'searched_properties':property , 'google_map_api_key': settings.GOOGLE_MAPS_API_KEY , 
                                                             'amenities': amenities , 'renter_choices':renter_choices, 'categories':categories, 
                                                             'selected_city':city,'prefer_renter':prefer_renter_list, 'selected_category': selected_category, 
                                                             'selected_amenities':selected_amenities, 'selected_location':selected_location, 'max_price':max})


def apply_filters(request):
    if request.method == "POST":
        categories = Categories.objects.all()
        renter_choices = Properties.prefer_renter.field.choices
        city = request.POST.get("city")
        location = request.POST.get("location")
        max_price = request.POST.get("max_price")
        type_of_home = request.POST.getlist("type_of_home")
        filtered_renter_choices = request.POST.getlist("renter_choices")
        filtered_category = []
        for id in type_of_home:
            x = Categories.objects.get(id = id).cat_name
            filtered_category.append(x)
        
        total_amenities = Amenities.objects.all()

        amenities_name_list = request.POST.getlist("amenities")
        request.session['location_result'] = location
        request.session['amenities_filter_result'] = amenities_name_list
        request.session['city_filter_result'] = city
        request.session['type_of_home_result'] = type_of_home
        request.session['renter_choices_result'] = filtered_renter_choices
        request.session['max_price_result'] = max_price
        print(location)

        filter_amenities = Amenities.objects.filter(name__in = amenities_name_list)
        if not filter_amenities:
            x = Properties.objects.filter(district = city, category__in = type_of_home, prefer_renter__in = filtered_renter_choices).distinct()
        else:
            x = Properties.objects.filter(district = city, category__in = type_of_home, amenities__in = filter_amenities, prefer_renter__in = filtered_renter_choices).distinct()

        print(filter_amenities)
        filtered_properties = []
        filtered_properties_details = []
        if location == 'None' or location in (None, '') or not location.strip():
            for i in x:
                rent = i.rent
                if rent <= int(max_price):
                    filtered_properties.append(i)
        else:
            ref_lat, ref_lng = get_coordinates(location,settings.GOOGLE_MAPS_API_KEY)
            for i in x:
                rent = i.rent
                property_latitude = i.latitude
                property_longitude = i.longitude
                distance = calculate_distance(
                        ref_lat,
                        ref_lng,
                        property_latitude,
                        property_longitude
                )
                if distance <= 100 and rent <= int(max_price) :
                    filtered_properties.append(i)
            
        
        print(filtered_properties)


        for prop in filtered_properties:
            images = PropertyImages.objects.filter(property= prop)
            image = images.first()
            prop_amenities = prop.amenities.all()
            wishlist_prop_exist = Wishlist.objects.filter(wishlist_property = prop).exists()
            filtered_properties_details.append([prop,image,prop_amenities,wishlist_prop_exist])

        return render(request, 'properties/all_properties.html', {'searched_properties':filtered_properties_details,'google_map_api_key': settings.GOOGLE_MAPS_API_KEY, 
                                                             'amenities': total_amenities , 'renter_choices':renter_choices, 'categories':categories,'prefer_renter':filtered_renter_choices, 
                                                             'selected_city':city, 'selected_amenities':amenities_name_list, 'selected_location':location,'selected_category':filtered_category, 'max_price':max_price})
    return HttpResponse("Hello")
  


# Messaging part Start here
def view_messages(request):
    user_login = request.user
    owner_rooms = Room.objects.filter(user2 = user_login)
    tenant_rooms = Room.objects.filter(user1 = user_login)
    unread_mssg = []
    owner_room_detail = []
    tenant_room_detail = []
    for room in owner_rooms:
        count = Message.objects.filter(room = room, recipient = user_login, is_read = False).count()
        unread_mssg.append(count)
        owner_room_detail.append([room,count])
    for room in tenant_rooms:
        count = Message.objects.filter(room = room, recipient = user_login, is_read = False).count()
        unread_mssg.append(count)
        tenant_room_detail.append([room,count])
    return render(request,'messages/view_message.html', {'user':user_login,'owner_room_detail' : owner_room_detail, 'tenant_room_detail':tenant_room_detail})






def create_chat_room(request,uid):
    user = request.user
    if not isinstance(user,AnonymousUser):
        property = Properties.objects.get(property_id = uid)
        user1 = request.user
        user2 = property.profile.user
        room = Room.objects.filter(property=property, user1=user1, user2=user2).first()
        # If no room exists, create a new one
        if not room:
            room = Room(property=property, user1=user1, user2=user2)
            room.save()
        room_code = room.room_id
        return redirect(f'/chat/{room_code}/?user={user1}')
    else:
        return redirect('login')


def chat(request,uid):
    room = Room.objects.get(room_id = uid)
    customer = room.user1
    owner = room.user2
    user = request.GET.get('user')
    if user != owner.username:
        recipient_name = owner.username
    else:
        recipient_name = customer.username
    id = str(room.room_id)
    # payload = {'room_id': id, 'recipient_name':recipient_name}
    property = room.property
    messages = Message.objects.filter(room=room)

    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #      'room_'+uid,{
    #          'type': 'mark_messages_as_read',
    #          'value' : json.dumps(payload)
    #      }
    # )

    
    for message in messages:
        if message.sender.username != user and not message.is_read:
            message.is_read = True
            message.save()
    context = {'room_code': uid , 'room': room, 'messages': messages, 'customer':customer, 'owner' :owner, 'property':property, 'user':user, 'recipient_name' : recipient_name}
    return render(request,'messages/chat.html',context)


def dashboard(request):
    prop_obj = Properties.objects.filter(profile = request.user.profile)
    property = []
    for prop in prop_obj:
        images = PropertyImages.objects.filter(property= prop)
        property.append([prop,images])
    param = {'property':property}
    return render(request, 'dashboard/view_dashboard.html' , param)

def delete_tenant(request,uid):
    tenant_obj = Tenant.objects.get(uid = uid)
    prop_id = tenant_obj.property.property_id
    tenant_obj.delete()
    url = reverse('view_tenants', args=[prop_id])
    return redirect(url)

def view_tenants(request,uid):
    property_id = uid
    prop_obj = Properties.objects.get(property_id=uid)
    tenants = Tenant.objects.filter(property=prop_obj)
    print(tenants)
    return render(request,'dashboard/view_tenants.html', {'property_id':property_id, 'tenants':tenants})

def tenant_details(request,uid):
    tenant_details = Tenant.objects.get(uid=uid)
    current_day = date.today().day
    rent_collect_day = tenant_details.start_date.day
    # print(current_date.day)
    days_left = rent_collect_day - current_day
    if days_left < 0:
        days_left = days_left + 30
    total_days = (date.today()-tenant_details.start_date).days
    total_expected_rent_collected = (total_days//30)*tenant_details.rent
    total_month = (total_days//30)
    tenant_record = TenantRentRecord.objects.filter(tenant = tenant_details).order_by('month')
    record_count = tenant_record.count()

    l = []
    for i in tenant_record:
        l.append(i.month)

    missing_number = 1
    while missing_number in l:
        missing_number += 1
    j = []
    for num in range(missing_number, total_month+ 1):
        if num not in l:
            j.append(num)
    amount = []



    for i in tenant_record:
        amount.append(i.amount_rec)

    total_amount = sum(amount) 
  
    total_amount = total_amount-tenant_details.advance
    due = total_expected_rent_collected-total_amount-tenant_details.advance 
    # days_left = (event_date - current_date).days
    return render(request, 'dashboard/tenant_details.html', {'tenant_details' : tenant_details, 'days_left':days_left, 'total_days':total_days, 'tenant_records' :tenant_record,'record_count':record_count,'total_expected_rent_collected':total_expected_rent_collected, 'total_month':total_month , 'range_for': j, 'total_amount': total_amount, 'due':due})
 
# def rent_calculator(request):
#     if request.method == "POST":
#         uid = request.POST.get("uid")
#         tenant_details = Tenant.objects.get(uid=uid)
#         total_days = (date.today()-tenant_details.start_date).days
#         total_rent_collected = (total_days//30)*tenant_details.rent
#     return redirect()


def add_tenants(request,uid):
    property_obj = Properties.objects.get(property_id = uid)
    
    if request.method == "POST":
        name = request.POST.get("name")
        rent = request.POST.get("rent")
        phone_number = request.POST.get("phone")
        email = request.POST.get("email")
        advance = request.POST.get("advance")
        adhaar_no = request.POST.get("adhaar_no")
        start_date = request.POST.get("start_date")
        address = request.POST.get("address")
        document = request.FILES.get("doc")
        photo = request.FILES.get("photo")
        prop_obj = Properties.objects.get(property_id = uid)
        # folder_path = os.path.join(settings.MEDIA_ROOT, 'documents',str(phone_number))
        # os.makedirs(folder_path, exist_ok=True)
        # document_path = os.path.join(folder_path, document.name)
        # photo_path = os.path.join(folder_path, photo.name)
        # with open(photo_path, 'wb') as file:
        #     for chunk in photo.chunks():
        #         file.write(chunk)
        # Save the image to the folder
        # with open(document_path, 'wb') as file:
        #     for chunk in document.chunks():
        #         file.write(chunk)

        tenant_details = Tenant.objects.create(property=prop_obj,phone = phone_number ,start_date = start_date,advance= advance, adhaar_no=adhaar_no, email=email
                              , rent = rent,address= address,name = name,document=document, photo = photo )
        print(tenant_details)
        adv_month = int(tenant_details.advance)//int(tenant_details.rent)
        print(adv_month)
        for i in range(1,adv_month+1):
            tenant_rec_obj = TenantRentRecord.objects.filter(tenant = tenant_details, month = i).exists()
            if not tenant_rec_obj:
                TenantRentRecord.objects.create(tenant = tenant_details, month = i, amount_rec = tenant_details.rent, received_date = tenant_details.start_date, status = 1)
        return redirect('view_tenants', uid)
    return render(request,'dashboard/add_tenant.html',{'property_obj':property_obj})


























# PageDetail
def page_detail(request,id):
	page=Page.objects.get(id=id)
	return render(request, 'home/page.html',{'page':page})

# FAQ
def faq_list(request):
	faq=Faq.objects.all()
	return render(request, 'home/faqs.html',{'faqs':faq})


def pricing(request):
    return render(request, "home/pricing.html")

def go_premium(request):
    username = request.user.username
    phone_no = Profile.objects.get(user=request.user).mobile
    if not Premium_details.objects.filter(username=username):
        Premium_details.objects.create(username=username,phone_no=phone_no)
    return render(request,"home/go_premium.html")

def all_properties(request):
    return render(request, "home/all_properties.html")

def about(request):
    return render(request,"home/about.html")

def property_view(request):
    return render(request, "home/property_view.html")

def list_prop_1(request):
    return render(request,"home/listing_prop_form_1.html")

def list_prop_2(request):
    return render(request,"home/listing_prop_form_3.html")

