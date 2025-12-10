from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Book, Loan
from .serializers import BookSerializer
from .serializers_user import UserSerializer
from .serializers_loan import LoanSerializer
from django.db import transaction
from rest_framework.exceptions import ValidationError


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-id')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Allow unauthenticated user creation (registration) but require auth for other actions
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
        })


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.select_related('book', 'user').all().order_by('-id')
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by user if requested
        user_id = self.request.query_params.get('user', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        # Filter by status if requested
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        # Create a loan and decrement book availability atomically
        req_user = self.request.user
        book = serializer.validated_data.get('book')
        # allow staff to specify the target user in payload
        target_user = serializer.validated_data.get('user', None)
        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=book.pk)
            if book.available <= 0:
                raise ValidationError('Book is not available')
            book.available = book.available - 1
            book.save()
            if target_user and req_user.is_staff:
                serializer.save(user=target_user)
            else:
                serializer.save(user=req_user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='return')
    def return_(self, request, pk=None):
        # Return a loan and increment availability
        loan = self.get_object()
        if loan.status == 'returned':
            return Response({'detail': 'Loan already returned'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=loan.book.pk)
            book.available = book.available + 1
            book.save()
            loan.status = 'returned'
            loan.return_date = timezone.now()
            loan.save()
        return Response(self.get_serializer(loan).data)
