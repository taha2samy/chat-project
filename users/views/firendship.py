# views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from users.models import Friendship, User
from users.serializers import FriendshipSerializer
from django.db.models import Q
from rest_framework import status

class FriendshipAPIView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        """
        Get all friendship relations for the currently logged-in user.
        """
        user = request.user
        
        friendships = Friendship.objects.filter(from_user_id=user.id) | Friendship.objects.filter(to_user_id=user.id)

        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new friendship relationship.
        """
        from_user = request.user  
        to_user_id = request.data.get('to_user')
        from_user_status = request.data.get('status')

        if not to_user_id or not from_user_status:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

                
        if from_user_status not in {"pending","accepted","rejected"}:
            return Response({"detail": "status not found."}, status=status.HTTP_404_NOT_FOUND)
        # Validate the to_user
        try:
            to_user = User.objects.get(pk=to_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the users are not the same
        if from_user.id == to_user.id:
            return Response({"detail": "You cannot send a friendship request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a friendship already exists between the users
        existing_friendship = Friendship.objects.filter(
            Q(from_user=from_user.id, to_user=to_user.id) | Q(from_user=to_user.id, to_user=from_user.id)
        ).exists()

        if existing_friendship:
            return Response({"detail": "Friendship already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new friendship record
        friendship = Friendship.objects.create(
            from_user_id=from_user.id,
            to_user_id=to_user.id,
            status_from_user=from_user_status,  # Initial status for the from_user
            status_to_user='pending'     # Initial status for the to_user
        )

        # Return the created friendship data
        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        """
        Update the status of an existing friendship.
        """
        user = request.user
        status_f = request.data.get('status')
        friendship_id=request.data.get("friendship_id")


        # Validate the provided status
        if status_f not in {'pending', 'accepted', 'rejected'}:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the friendship to update
            friendship = Friendship.objects.get(id=friendship_id)
        except Friendship.DoesNotExist:
            return Response({"detail": "Friendship not found."}, status=status.HTTP_404_NOT_FOUND)

        if str(friendship.from_user.id) == user.id:
            friendship.status_from_user = status_f 
        elif str(friendship.to_user.id) == str(user.id):
            friendship.status_to_user = status_f 
        else:
            return Response({"detail": "You are not authorized to update this friendship."}, status=status.HTTP_403_FORBIDDEN)

        friendship.save()  
        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data)
