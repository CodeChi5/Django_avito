from rest_framework import serializers
from .models import Conversation, Message
from ProductsApi.serializers import ProductSerializer
from UserApi.models import User
from django.db.models import Q

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True
    )
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_id', 'content', 'is_read', 'created_at']
        read_only_fields = ['is_read', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'product', 'buyer', 'seller', 'created_at', 'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_last_message(self, obj):
        # Check if obj is a dictionary (during creation) or a model instance
        if isinstance(obj, dict):
            return None
            
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'content': last_message.content,
                'sender_id': last_message.sender.id,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        # Check if obj is a dictionary (during creation) or a model instance
        if isinstance(obj, dict):
            return 0
            
        user = self.context['request'].user
        return obj.messages.filter(~Q(sender=user), is_read=False).count()

class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages'] 