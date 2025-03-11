from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from .models import User

# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        
        # Debug print
        print(f"Generated token for {username}: {token.key}")
        
        return Response({
            'success': True,
            'is_staff_member': user.is_staff_member,
            'username': user.username,
            'token': token.key
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user(request):
    """
    Create a new user (admin only)
    """
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        is_staff_member = request.data.get('is_staff_member', False)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff_member=is_staff_member
        )
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': f'Failed to create user: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    """
    List all users (admin only)
    """
    try:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch users: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    is_staff_member = request.data.get('is_staff_member', False)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff_member=is_staff_member,
            is_staff=is_staff_member  # Set is_staff same as is_staff_member
        )
        
        # Create token for new user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'is_staff_member': user.is_staff_member,
            'username': user.username,
            'token': token.key
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)