from django.db import models

# Create your models here.


class Genre(models.Model):
    """Model pentru toate genurile muzicale"""

    genre: str = models.CharField(unique=True, max_length=32)


class Token(models.Model):
    """Model pentru token ul Spotify"""

    userid = models.CharField(unique=True, max_length=60)
    creat_la = models.DateField(auto_now_add=True)
    refresh_token = models.CharField(max_length=150)
    access_token = models.CharField(max_length=150)
    expira_la = models.DateTimeField()
    tip_token = models.CharField(max_length=50)


class User(models.Model):
    """Model pentru utilizatori"""

    spotifyid = models.CharField(unique=True, max_length=50)
    favoriteGenreId = models.IntegerField(null=True)
    averageDuration = models.IntegerField(null=True)
    averageYear = models.IntegerField(null=True)
    explicitRatio = models.FloatField(null=True)


class Track(models.Model):
    """Model pentru melodii"""

    spotifyid = models.CharField(unique=True, max_length=64)
    genreid = models.IntegerField()
    artists = models.CharField(max_length=200)
    releasedate = models.DateField()
    durationms = models.IntegerField()
    popularity = models.IntegerField()
    explicit = models.BooleanField()


class Rating(models.Model):
    """Model pentru rating urile date de utilizatori"""

    userid = models.IntegerField()
    songid = models.IntegerField()
    rating = models.IntegerField(default=0)
