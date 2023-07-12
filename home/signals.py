from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Room, Message,Profile,Premium_details
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from twilio.rest import Client
from django.conf import settings
import json


def sendTextMessage(to,mssg):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"{mssg}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to
    )
    return message.sid



@receiver(post_save, sender=Message)
def update_unread_message_count(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        recipient = instance.recipient
        prop_obj = Profile.objects.get(user = recipient )
        mobile_no = prop_obj.mobile
        mssg = "You got new message please check it on website"
        # users = User.objects.filter((username=recipient)).distinct()
        channel_layer = get_channel_layer()
        count = Message.objects.filter(room=room, recipient=recipient, is_read=False).count()
        payload = {
                'room_id': str(room.room_id),
                'unread_count': count,
            }
        async_to_sync(channel_layer.group_send)(
                'view_messages_group',
                {
                    'type': 'update_unread_count',
                    'value': json.dumps(payload),
                }
            )
        sendTextMessage(mobile_no,mssg)



@receiver(post_save, sender=Premium_details)
def send_premium_customer_details(sender, instance, created, **kwargs):
    if created:
        phone_no = instance.phone_no
        username = instance.username
        company_no = '+91-8864913708'
        mssg = f"Hello This is from anas side You got a new  premium customer  \n please contact him here is the \n mobile no: {phone_no} \n name: {username}"
        sendTextMessage(company_no,mssg=mssg) 
