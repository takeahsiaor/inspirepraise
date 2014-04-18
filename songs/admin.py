from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from songs.models import Publisher, Author, Book, Chapter, Verse, Song, SongVerses, Ministry, Profile
from songs.models import Invitation, Setlist, SetlistSong, MinistryMembership

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email')
    search_fields = ('full_name',)
    
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('date', 'email', 'ministry')
    ordering = ('email', 'ministry')

class SetlistAdmin(admin.ModelAdmin):
    list_display = ('profile', 'notes', 'archived')
    ordering = ('profile',)
    fields = ('profile', 'notes', 'created_by', 'song_order')
    
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'ccli', 'popularity', 'publication_year') #customized fields to display
    search_fields = ('title', 'ccli')
    list_filter = ('publication_year',)
    ordering = ('title', 'popularity') # ordering in display
    #customizes editable fields
    fields = ('title', 'authors', 'ccli', 'publisher', 'publication_year', 'popularity') 
    filter_horizontal = ('authors', 'publisher') # side box for many to many fields
    #use raw_id_fields = ('blah',) for foreign keys with a lot of options - gives id and mag glass
    
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_index', 'num_chapters')
    ordering = ('order_index',)

    
class VerseAdmin(admin.ModelAdmin):
    list_display = ('book','chapter','number','id')
    ordering = ('id',)

class SongVerseAdmin(admin.ModelAdmin):
    list_display = ('song', 'verse', 'SV_popularity')

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('book', 'number', 'id','num_verses')
    ordering = ('id',)

class MinistryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'country',)
    # filter_horizontal = ('members',)

#this is to add profile items into admin
class ProfileInline(admin.StackedInline):
    model =  Profile
    filter_horizontal = ('ministries', )
    can_delete = False
    verbose_name_plural = "Profile"
    
class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'num_song_tags', 'num_verse_tags')
    filter_horizontal = ('ministries', )
    
admin.site.unregister(User)
admin.site.register(User,UserAdmin)
admin.site.register(Publisher)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Verse, VerseAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Ministry, MinistryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(SongVerses, SongVerseAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Setlist, SetlistAdmin)
#admin.site.register(SongVerses)