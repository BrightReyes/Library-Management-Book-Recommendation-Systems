from rest_framework import serializers
from .models import Loan, Book
from django.utils import timezone
from datetime import timedelta


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    book_title = serializers.ReadOnlyField(source='book.title')
    book_author = serializers.ReadOnlyField(source='book.author')
    book_category = serializers.ReadOnlyField(source='book.category')
    book_isbn = serializers.ReadOnlyField(source='book.isbn')
    username = serializers.ReadOnlyField(source='user.username')
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['id', 'user', 'username', 'book', 'book_title', 'book_author', 'book_category', 'book_isbn', 'borrow_date', 'due_date', 'return_date', 'status', 'fine', 'days_overdue']
    
    def get_days_overdue(self, obj):
        if obj.status == 'returned' or not obj.due_date:
            return 0
        today = timezone.now()
        if today > obj.due_date:
            return (today.date() - obj.due_date.date()).days
        return 0
    
    def create(self, validated_data):
        # Set default due_date if not provided
        if 'due_date' not in validated_data or validated_data['due_date'] is None:
            validated_data['due_date'] = timezone.now() + timedelta(days=14)
        return super().create(validated_data)
