from channels.generic.websocket import WebsocketConsumer
import json
from django.contrib.auth.models import User
from .models import *
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async

class ChatConsumer(WebsocketConsumer):          
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_name}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.send(text_data = json.dumps({
            'payload':'connected'
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        room_id = text_data_json.get('room_id')
        sender = text_data_json.get('sender')
        recipient_name = text_data_json.get('recipient_name')
        room = Room.objects.get(room_id=room_id)
        user = User.objects.get(username=sender)
        recipient = User.objects.get(username=recipient_name)
        Message.objects.create(
            room=room,
            sender=user,
            recipient = recipient,
            content=text_data_json.get('message')
        )

        payload = {"message": text_data_json.get('message'), "sender" :text_data_json.get('sender'), "room_id": text_data_json.get('room_id'), "recipient_name":recipient_name}

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_message',
                'value': payload
            }
        )

    def send_message(self, event):
        data = event.get('value')
        self.send(text_data=json.dumps({
            'payload': data
        }))

    def disconnect(self, close_code):
        pass


    # def get_unread_message_count(self, user):
    #     return Message.objects.filter(recipient=user, is_read=False).count()



    # def mark_messages_as_read(self, recipient):

    #     unread_messages = Message.objects.filter(recipient=recipient, is_read=False)
    #     unread_messages.update(is_read=True)

    # def mark_messages_as_read(self,event):
    #     data = json.loads(event.get('value'))
    #     room_id = data['room_id']
    #     recipient_name = data['recipient_name']
    #     room = Room.objects.get(room_id = room_id)
    #     recipient = User.objects.get(username=recipient_name)
    #     unread_messages = Message.objects.filter(room = room, recipient=recipient, is_read=False)
    #     unread_messages.update(is_read=True)



class NotificationsConsumer(WebsocketConsumer):      
    def connect(self):
        self.room_name = "view_messages"
        self.room_group_name = "view_messages_group"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.send(text_data = json.dumps({
                        'payload':'connected'
                        }))
            
    def disconnect(self, close_code):
        # Disconnect logic for ConsumerClass2
        pass

    def receive(self, text_data):
        pass

    def update_unread_count(self,event):
        data = json.loads(event.get('value'))
        self.send(text_data=json.dumps({
            'payload': data
        }))


class TenantsConsumer(WebsocketConsumer):      
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['tenant_uid']
        self.room_group_name = f'tenants_{self.room_name}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.send(text_data = json.dumps({
            'payload':'connected'
        }))


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        tenant_uid = text_data_json.get('tenant_uid')
        rent_collect = text_data_json.get('rent_collect')
        month_no = text_data_json.get('month_no')
        rentAmount = text_data_json.get('rentAmount')
        recDate = text_data_json.get('receivingDate')

        tenant_obj = Tenant.objects.get(uid=tenant_uid)
        tenant_obj.rent_collect = rent_collect
        tenant_obj.save()
        
        if month_no is None or recDate is None or rentAmount is None:
            print("else")
        else:
            tenant_rec_obj = TenantRentRecord(tenant=tenant_obj)
            tenant_rec_obj_month_exist = TenantRentRecord.objects.filter(tenant = tenant_obj, month = month_no).exists()
            if not tenant_rec_obj_month_exist:
                tenant_rec_obj.month = month_no
                tenant_rec_obj.amount_rec = rentAmount
                tenant_rec_obj.received_date = recDate
                tenant_rec_obj.status = 1
                tenant_rec_obj.save()  # Save the object to the database
                print(tenant_rec_obj)
                print("hello")

        print(text_data_json)
        print(month_no,rentAmount,recDate)
        advance = tenant_obj.advance
        due = advance-rent_collect
        print(due)
        print(advance)

        payload = {"due":due}

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_message',
                'value': payload
            }
        )


    def disconnect(self, close_code):
        # Disconnect logic for ConsumerClass2
        pass


    def send_message(self,event):
        print(event)
 
