from django.contrib.auth.models import User
from rest_framework.serializers import (ModelSerializer, 
    HyperlinkedModelSerializer)

from songs.models import Song, Verse

class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

class SongSerializer(ModelSerializer):
    class Meta:
        model = Song
        fields = ('ccli', 'title', 'authors', 'popularity', 'publisher',
            'publication_year', 'verses')

class VerseSerializer(ModelSerializer):
    class Meta:
        model = Verse
        fields = ('id', 'book', 'chapter', 'number')