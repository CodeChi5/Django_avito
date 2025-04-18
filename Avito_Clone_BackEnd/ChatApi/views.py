from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationDetailSerializer, MessageSerializer
from ProductsApi.models import Product

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(buyer=user) | Conversation.objects.filter(seller=user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        product_id = self.request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        # Determine buyer and seller
        buyer = self.request.user
        seller = product.user
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            product=product,
            buyer=buyer,
            seller=seller
        ).first()
        
        if existing_conversation:
            return existing_conversation
        
        serializer.save(product=product, buyer=buyer, seller=seller)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'Message content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation's updated_at timestamp
        conversation.save()
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        conversation = self.get_object()
        
        # Mark all messages from the other user as read
        user = request.user
        other_user = conversation.seller if user == conversation.buyer else conversation.buyer
        
        Message.objects.filter(
            conversation=conversation,
            sender=other_user,
            is_read=False
        ).update(is_read=True)
        
        return Response({'status': 'Messages marked as read'})

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            return Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
        return Message.objects.none()
    
    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if the user is part of the conversation
        user = self.request.user
        if user != conversation.buyer and user != conversation.seller:
            raise permissions.PermissionDenied("You are not part of this conversation")
        
        serializer.save(conversation=conversation, sender=user)
        
        # Update conversation's updated_at timestamp
        conversation.save()
