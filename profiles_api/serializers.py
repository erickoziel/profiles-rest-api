from rest_framework import serializers

from profiles_api import models

class HelloSerializer(serializers.Serializer):
    '''Serializers a name field for testing our APIView'''
    name = serializers.CharField(max_length=10)


class UserProfileSerializer(serializers.ModelSerializer):
    '''Serializes a user profile object'''

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password' : {
                'write_only':True,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        '''Create and return a new user'''
        user = models.UserProfile.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )

        return user

    def update(self, instance, validated_data):
        '''Handle updating user account'''
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        return super().update(instance, validated_data)


class ProfileFeedItemSerializer(serializers.ModelSerializer):
    '''Serializes profile feed items'''

    class Meta:
        model = models.ProfileFeedItem
        fields = ('id', 'user_profile', 'status_text', 'created_on')
        extra_kwargs = {'user_profile': {'read_only' : True}}


class SentimentMessageItemSerializer(serializers.ModelSerializer):
    '''Serializers a message field for testing our APIView'''

    class Meta:
        model = models.SentimentMessageItem
        fields = ('id', 'message', 'created_on')
        extra_kwargs = {'message': {
            'style' :  {'base_template':'textarea.html', 'rows' : 5},
            'max_length' : 1000}}

    # def sentiment_analyzer_score(cls, message):
    #     '''Get sentiment from message'''
    #
    #     if not message:
    #         raise ValueError('Message not found')
    #
    #     # analyser = SentimentIntensityAnalyzer()
    #     # new_words = {
    #     #     'dont': -0.3,
    #     #     "don't": -0.3,
    #     #     "do not": -0.3,
    #     # }
    #     # analyser.lexicon.update(new_words)
    #     # score = analyser.polarity_scores(message)
    #     # return score['compund']
    #     sentiment = 0.1
    #     # translation = 0.1
    #     # item = self.model(message=message, translation=translation)
    #     # item.save(using=self._db)
    #
    #     return sentiment
    #
    # def translation(cls, message):
    #     if not message:
    #         raise ValueError('Message not found')
    #     translatio = message + ' TRANSLATED'
    #     return translation
    #
    # def create(self, validated_data):
    #     '''Create and return a new user'''
    #     sentimentItem = models.SentimentMessageItem.objects.sentiment_analyzer_score(
    #                         message = validated_data['message']
    #                     )
    #
    #     # (
    #     #     email=validated_data['email'],
    #     #     name=validated_data['name'],
    #     #     password=validated_data['password']
    #     # )
    #
    #     return sentimentItem
    #
    # def update(self, instance, validated_data):
    #     '''Handle updating user account'''
    #     if 'password' in validated_data:
    #         password = validated_data.pop('password')
    #         instance.set_password(password)
    #
    #     return super().update(instance, validated_data)
