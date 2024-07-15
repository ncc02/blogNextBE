from django.shortcuts import get_object_or_404, render

# Create your views here.
from app.models import Blog
from app.serializers import BlogSerializer
from rest_framework import viewsets

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators  import authentication_classes, permission_classes
from    rest_framework.authentication import SessionAuthentication,TokenAuthentication
from    rest_framework.permissions import IsAuthenticated
from django.db.models import Q

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()   
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Thiết lập author dựa trên người dùng hiện tại0
    def perform_update(self, serializer):
        serializer.save(author=self.request.user)  # Đảm bảo author không thay đổi khi cập nhật
    
@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Sai mật khẩu!"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})

import logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
def signup(request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return Response({"token": token.key, "user": serializer.data})
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("An error occurred during signup.")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET'])
@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated, IsAuthenticatedOrReadOnly])
def test_token(request):
    return Response("pass for {}".format(request.user.email))

@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])  # Người dùng cần đăng nhập
def my_blogs(request):
    blogs = Blog.objects.filter(author=request.user)  
    serializer = BlogSerializer(blogs, many=True)  
    return Response(serializer.data)

@api_view(['GET'])
def search(request):
    search_term = request.query_params.get('search', '')  # Lấy giá trị 'search' từ query parameters

    if search_term:
        # Tìm kiếm không phân biệt hoa thường và cho phép tìm kiếm theo nhiều từ khóa
        search_terms = search_term.split()  
        query = Q()
        for term in search_terms:
            query |= Q(title__icontains=term) 
        blogs = Blog.objects.filter(query)
    else:
        blogs = Blog.objects.all()

    serializer = BlogSerializer(blogs, many=True)
    return Response(serializer.data)