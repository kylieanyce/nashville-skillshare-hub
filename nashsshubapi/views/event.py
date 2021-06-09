"""View module for handling requests about events"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from nashsshubapi.models import Event, Host, Bookmark, Topic


class EventView(ViewSet):
    """Nashville SkillShare Hub events"""

    def create(self, request):
        """Handle POST operations for events

        Returns:
            Response -- JSON serialized event instance
        """

        event = Event()
        event.title = request.data["title"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        event.cost = request.data["cost"]
        event.location = request.data["location"]
        event.address = request.data["address"]
        event.description = request.data["description"]
        event.hostname = request.data["hostname"]

        try:
            event.save()
            hosts = request.auth.user
            event.hosts.add(hosts)
            topics = Topic.objects.filter(pk__in=request.data["topicId"])
            event.topics.set(topics)
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for an event

        Returns:
            Response -- Empty body with 204 status code
        """
        event = Event.objects.get(pk=pk)
        event.title = request.data["title"]
        event.date = request.data["date"]
        event.time = request.data["time"]
        event.cost = request.data["cost"]
        event.location = request.data["location"]
        event.address = request.data["address"]
        event.description = request.data["description"]
        event.hostname = request.data["hostname"]

        topics = Topic.objects.filter(pk__in=request.data["topics"])
        event.save()
        event.topics.set(topics)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    # def destroy(self, request, pk=None):
    #     """Handle DELETE requests for a single game

    #     Returns:
    #         Response -- 200, 404, or 500 status code
    #     """
    #     try:
    #         event = Event.objects.get(pk=pk)
    #         event.delete()

    #         return Response({}, status=status.HTTP_204_NO_CONTENT)

    #     except Event.DoesNotExist as ex:
    #         return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    #     except Exception as ex:
    #         return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def list(self, request):
    #     """Handle GET requests to events resource

    #     Returns:
    #         Response -- JSON serialized list of events
    #     """
    #     gamer = Gamer.objects.get(user=request.auth.user)
    #     events = Event.objects.all()

    #     # Set the `joined` property on every event
    #     for event in events:
    #         event.joined = None

    #         try:
    #             GamerEvent.objects.get(event=event, gamer=gamer)
    #             event.joined = True
    #         except GamerEvent.DoesNotExist:
    #             event.joined = False

    #     # Support filtering events by game
    #     game = self.request.query_params.get('gameId', None)
    #     if game is not None:
    #         events = events.filter(game__id=game)

    #     serializer = EventSerializer(
    #         events, many=True, context={'request': request})
    #     return Response(serializer.data)


class EventUserSerializer(serializers.ModelSerializer):
    """JSON serializer for event organizer's related Django user"""
    class Meta:
        model = User
        fields = ['username']


class EventTopicSerializer(serializers.ModelSerializer):
    """JSON serializer for event organizer"""
    class Meta:
        model = Topic
        fields = ['label']


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    hosts = EventUserSerializer(many=True)
    topics = EventTopicSerializer(many=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'date', 'time',
                  'description', 'location', 'cost', 'address',
                  'hosts', 'hostname', 'topics', 'bookmarks')
