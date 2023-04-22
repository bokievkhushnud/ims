
from rest_framework import serializers
from .models import Item, Profile
from .models import Profile, ItemAssignment
from django.contrib.auth.models import User

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'item_name', 'image', 'quantity', 'price']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Profile
        fields = ['owner', 'profile_pic']

class ItemAssignmentSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.item_name')

    class Meta:
        model = ItemAssignment
        fields = ['item', 'item_name', 'quantity', 'action', 'department', 'location', 'requestor', 'done_by', 'date', 'due_date', 'notes', 'status']
