from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from .models import User, PhoneVerification
from .serializers import PhoneNumberSerializer, CodeVerificationSerializer
from django.utils import timezone
from rest_framework.permissions import AllowAny

class SendVerificationCodeView(APIView):
    permission_classes = [AllowAny]  
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            # Delete old verification codes
            PhoneVerification.objects.filter(phone_number=phone_number).delete()
            
            # Create new verification code
            verification = PhoneVerification(phone_number=phone_number)
            verification.save()
            
            # Print code to console for testing
            print(f"Verification code for {phone_number}: {verification.code}")
            
            return Response({'status': 'Code sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyCodeView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = CodeVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            
            try:
                verification = PhoneVerification.objects.get(
                    phone_number=phone_number,
                    code=code,
                    expires_at__gt=timezone.now()
                )
            except PhoneVerification.DoesNotExist:
                return Response({'error': 'Invalid or expired code'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user
            user, created = User.objects.get_or_create(phone_number=phone_number)
            
            # Mark user as verified and log them in
            user.is_verified = True
            user.save()
            login(request, user)
            
            return Response({
                'status': 'Authenticated',
                'sessionid': request.session.session_key,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)