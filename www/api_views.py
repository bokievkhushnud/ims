from rest_framework import generics
from .models import Item, User
from .serializers import ItemSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile, ItemAssignment
from .serializers import ProfileSerializer, ItemAssignmentSerializer
from rest_framework import status



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def item_details(request, item_id):
    if request.method == 'GET':
        try:
            item = Item.objects.get(id=item_id)
            serializer = ItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    profile = Profile.objects.get(owner=request.user)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_items(request):
    item_assignments = ItemAssignment.objects.filter(requestor=request.user, status='out')
    serializer = ItemAssignmentSerializer(item_assignments, many=True)
    return Response(serializer.data)

