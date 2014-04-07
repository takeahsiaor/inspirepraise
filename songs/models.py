from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Publisher(models.Model):
    #does this need to be increased?
    name = models.CharField(max_length=60)
    address = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=60, blank=True)
    state_province = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ('name',)
    
    
class Book(models.Model):
    name = models.CharField(max_length=30)
    num_chapters = models.IntegerField(verbose_name='number of chapters')
    order_index = models.IntegerField(primary_key=True)
    
    def __unicode__(self):
        return self.name
    
class Chapter(models.Model):
    book = models.ForeignKey(Book)
    number = models.IntegerField(verbose_name="chapter")
    num_verses = models.IntegerField(verbose_name="number of verses")
    
    def __unicode__(self):
        return u'%s %s' % (self.book, self.number)
    
class Verse(models.Model):
    book = models.ForeignKey(Book)
    chapter = models.ForeignKey(Chapter)
    number = models.IntegerField()
    #songs = models.ManyToManyField(Song)
    def __unicode__(self):
        return u'%s:%s' % (self.chapter,self.number)
    
#need to revise book chapter and verse model. 
    
class Author(models.Model):

    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, verbose_name='e-mail')
    
    def __unicode__(self):
        return self.full_name    

#need to revise song model for publication year not date.
class Song(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    ccli = models.IntegerField(primary_key=True)
    key_line = models.CharField(max_length=300, blank=True)
    original_key = models.CharField(max_length=5, blank=True)
    recommended_key = models.CharField(max_length=5, blank=True)
    popularity = models.IntegerField(default=1)
    publisher = models.ManyToManyField(Publisher)
    publication_year = models.IntegerField(max_length=4)
    verses = models.ManyToManyField(Verse, through='SongVerses',blank=True)
    chords = models.TextField(default='')
    # SV_pop_temp = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return self.title
        
class SongVerses(models.Model):
    song = models.ForeignKey(Song)
    verse = models.ForeignKey(Verse)
    SV_popularity = models.IntegerField(default=1)
 
    
class Ministry(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state_province = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    # admin = models.ForeignKey(User)
    # members = models.ManyToManyField(User, blank=True)
    def __unicode__(self):
        return self.name
        
class Profile(models.Model):
    user = models.ForeignKey(User, unique = True)
    ministries = models.ManyToManyField(Ministry, through='MinistryMembership', blank=True)
    num_song_tags = models.IntegerField(default=0)
    num_verse_tags = models.IntegerField(default=0)
    
class MinistryMembership(models.Model):
    # to future proof in case i want profile-ministry specific data like instrument played
    member = models.ForeignKey(Profile)
    ministry = models.ForeignKey(Ministry)
    join_date = models.DateField(auto_now_add=True)
    #when admin sends invite, creates membership, when email confirmed, makes active
    active = models.BooleanField(default=False) 
    admin = models.BooleanField(default=False) # this will allow multiple admins
    
class Setlist(models.Model):
    profile = models.ForeignKey(Profile)
    date = models.DateTimeField(auto_now=True)
    notes = models.TextField(default='')
    created_by = models.CharField(max_length=100, blank=True)
    archived = models.BooleanField(default=False)
    songs = models.ManyToManyField(Song, through="SetlistSong")
    #needs a way to keep order of songs
    song_order = models.TextField(default='', max_length=200)
    
class SetlistSong(models.Model):
    setlist = models.ForeignKey(Setlist)
    song = models.ForeignKey(Song)
    notes = models.TextField(default='')
    key = models.CharField(max_length=5)
    capo_key = models.CharField(max_length=5, blank=True)
    order = models.CharField(max_length=100, blank=True)
    