from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework import filters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated #IsAuthenticatedOrReadOnly
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

from profiles_api import serializers
from profiles_api import models
from profiles_api import permissions


class HelloApiView(APIView):
    '''Test API View '''
    serializer_class = serializers.HelloSerializer

    def get(self, request, format=None):
        '''Returns a list of APIView features '''
        an_apiview  = [
            'Uses HTTP methods as function (get, post, patch, put, delete)',
            'Is similar to a traditional Django View',
            'Gives you the most control over your application logic',
            'Is mapped manually to URLs',
        ]

        return Response({'message': 'Hello!', 'an_apiview' : an_apiview})

    def post(self, request):
        '''Create a hello message with our name '''
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            message = f'Hello {name}'
            return Response({'message': message})
        else:
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
                )

    def put(self, request, pk=None):
        '''Handle updating an object'''
        return Response({'method': 'PUT'})

    def patch(self, request, pk=None):
        '''Handle a partial update of an object'''
        return Response({'method': 'PATCH'})

    def delete(self, request, pk=None):
        '''Delete an object'''
        return Response({'method':'DELETE'})


# class SentimentViewSet(viewsets.ViewSet):
class SentimentViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    '''Create entry with sentiment and translation'''
    serializer_class = serializers.SentimentMessageItemSerializer

    # @classmethod
    # def sentiment_analyzer_scores(message):
    #     analyser = SentimentIntensityAnalyzer()
    #     new_words = {
    #         'dont': -0.3,
    #         "don't": -0.3,
    #         "do not": -0.3,
    #     }
    #     analyser.lexicon.update(new_words)
    #     # New words and values
    #     score = analyser.polarity_scores(message)
    #     return score['compound']

    def text_analysis(cls, message):
        output = {}
        if not message:
            raise ValueError('Message not found')
        blob = TextBlob(message)
        original_language = blob.detect_language()
        if original_language != "es":
            translation_spanish = blob.translate(to="es")
        else:
            translation_spanish = blob
        if original_language == "en":
            text = blob
        else:
            text = blob.translate(to="en")

        text = str(text)
        # Sentiment score
        analyser = SentimentIntensityAnalyzer()
        new_words = {
            'dont': -2,
            "don't": -2,
            "do not": -2,
            "don't like" : -3,
            "did not" : -3,
            "didn't" : -3,
            "like" : 1,
        }
        analyser.lexicon.update(new_words)
        # New words and values
        score = analyser.polarity_scores(str(text))
        sentiment_score = round(score['compound'],3)
        sentiment_tag = 'Neutral'
        if (sentiment_score < -0.10):
            sentiment_tag = 'Negative'
        elif (sentiment_score > 0.10):
            sentiment_tag = 'Positive'

        analysis = {
            'original_language': str(original_language).upper(),
            'translation_spanish' : str(translation_spanish),
            'translation_english' : str(text),
            'sentiment_score' : sentiment_score,
            'sentiment_tag' : str(sentiment_tag),
            }
        return analysis


    # def list(self, request):
    #     '''Returns custom message '''
    #     an_apiview = ['Uses HTTP GET method as function']
    #     return Response({'message': 'Simple API', 'an_apiview' : an_apiview})

    def create(self, request):
        '''Create a new hello message '''
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            message = serializer.validated_data.get('message')
            analysis = self.text_analysis(message)
            return Response({
                    'message':message,
                    'original_language': analysis['original_language'],
                    'translation_spanish' : analysis['translation_spanish'],
                    'translation_english' : analysis['translation_english'],
                    'sentiment_score' : analysis['sentiment_score'],
                    'sentiment_tag' : analysis['sentiment_tag'],
                        })
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    # def retrieve(self, request, pk=None):
    #     '''Handle getting an object by its ID '''
    #     return Response({'http_method':'GET'})
    #
    # def update(self, request, pk=None):
    #     '''Handle updating an object'''
    #     return Response({'http_method': 'PUT'})
    #
    # def partial_update(self, request, pk=None):
    #     '''Handle updating part of an object'''
    #     return Response({'http_method': 'PATCH'})
    #
    # def destroy(self, request, pk=None):
    #     '''Handle removing an object'''
    #     return Response({'http_method': 'DELETE'})


class HelloViewSet(viewsets.ViewSet):
    '''Test API ViewSet '''
    serializer_class = serializers.HelloSerializer

    def list(self, request):
        '''Return a hello message'''
        a_viewset = [
            'Uses actions (list, create, retrieve, update, partial_update)',
            'Automatically maps to URLs using Routers',
            'Provides more functionality with less code',
        ]

        return Response({'message':'Hello!', 'a_viewset':a_viewset})

    def create(self, request):
        '''Create a new hello message '''
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            message = f'Hello {name}!'
            return Response({'message':message})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, pk=None):
        '''Handle getting an object by its ID '''
        return Response({'http_method':'GET'})

    def update(self, request, pk=None):
        '''Handle updating an object'''
        return Response({'http_method': 'PUT'})

    def partial_update(self, request, pk=None):
        '''Handle updating part of an object'''
        return Response({'http_method': 'PATCH'})

    def destroy(self, request, pk=None):
        '''Handle removing an object'''
        return Response({'http_method': 'DELETE'})

class UserProfileViewSet(viewsets.ModelViewSet):
    '''Handle creating and updating profiles'''
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email',)


class UserLoginApiView(ObtainAuthToken):
    '''Handle creating user authentication tokens '''
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserProfileFeedViewSet(viewsets.ModelViewSet):
    '''Handles creating, reading and updating profile feed items '''
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.ProfileFeedItemSerializer
    queryset = models.ProfileFeedItem.objects.all()
    permission_classes = (
        permissions.UpdateOwnStatus,
        IsAuthenticated #IsAuthenticatedOrReadOnly
    )

    def perform_create(self, serializer):
        '''Sets the user profile to the logged in user'''
        serializer.save(user_profile=self.request.user)

class SentimentMessageItemViewSet(viewsets.ModelViewSet):
    '''Handles creating, reading and updating profile messages items'''
    serializer_class = serializers.SentimentMessageItemSerializer
    queryset = models.SentimentMessageItem.objects.all()
