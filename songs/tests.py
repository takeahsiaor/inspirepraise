"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from model_mommy import mommy
from django.test import TestCase
from songs.functions import transpose, convert_setlist_to_string, make_key_option_html
from songs.views import parse_string_to_verses
from songs.models import Verse, Book, Chapter, Profile, Song, Setlist, SetlistSong

# class MakeKeyOptionHtmlTestCase(TestCase):
    # def test_major_key(self):
        # key = 'G'
        # all_major_keys = ['Ab','A','Bb','B','C', 'C#','Db','D','Eb','E','F','F#','Gb','G','G#']
    # all_minor_keys = ['Abm','Am','Bbm','Bm','Cm', 'C#m','Dm','Ebm','Em','Fm','F#m','Gm','G#m']
        # g_result = '<option>Ab</option><option>A</option><option>Bb</option><option>B</option><option>C</option>\


class TransposeTestCase(TestCase):
    #tranpose(original, semitones, original_key, final_key)
    def test_no_change_major(self):
        original = 'A'
        final = transpose(original, 0, 'C', 'C')
        self.assertEqual(original, final)
        
    def test_slash_chord(self):
        #major key
        self.assertEqual(transpose('G/B', 1, 'G', 'G#'), 'G#/B#')
        self.assertEqual(transpose('G/B', 1, 'G', 'Ab'), 'Ab/C')
        self.assertEqual(transpose('C/E', 1, 'C', 'C#'), 'C#/E#')
        self.assertEqual(transpose('C/E', 1, 'C', 'Db'), 'Db/F')
        #minor key
        self.assertEqual(transpose('G/B', 1, 'Em', 'Fm'), 'Ab/C')
        self.assertEqual(transpose('G/B', 4, 'Em', 'G#m'), 'B/D#')
        self.assertEqual(transpose('G/B', 4, 'Em', 'Abm'), 'Cb/Eb')
        self.assertEqual(transpose('G/B', 7, 'Em', 'Bm'), 'D/F#')
        #minor chord, major key
        self.assertEqual(transpose('Am/C', 1, 'C', 'C#'), 'A#m/C#')
        self.assertEqual(transpose('Am7/C', 1, 'C', 'C#'), 'A#m7/C#')
        self.assertEqual(transpose('Am/C', 1, 'C', 'Db'), 'Bbm/Db')
        self.assertEqual(transpose('Am7/C', 1, 'C', 'Db'), 'Bbm7/Db')
        #G/B to B/D#, must not go to B/B then D#/D#:test
        self.assertEqual(transpose('G/B', 4, 'G', 'B'), 'B/D#')
        self.assertEqual(transpose('C/E', 4, 'C', 'E'), 'E/G#')
        
class SetlistToStringTestCase(TestCase):
    def test_setlist_to_string(self):
        setlist1 = [('4556538', 'G#'), ('3798438', 'G'), ('5677416', 'G'), ('2759753', 'Bm')]
        setlist1_string = convert_setlist_to_string(setlist1)
        self.assertEqual(setlist1_string, '4556538-G#,3798438-G,5677416-G,2759753-Bm')

class SongsViewsTestCase(TestCase):
    def test_home(self):
        resp = self.client.get('/home/')
        self.assertEqual(resp.status_code, 200)

class UpdateSetlistUnauth(TestCase):
    # fixtures = ['songs_views_testdata.json']
    # def test_number_of_songs(self):
        # num = len(Song.objects.all())
        # self.assertEqual(num, 100)
    def setUp(self):
        pass
        # song = mommy.make(Song)
        # ccli = str(song.ccli)
        
    def test_add_unauth(self):
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
        self.assertEqual(self.client.session.get('setlist'), [(ccli, 'G')])
        
class UpdateSetlistAuth(TestCase):       
    def setUp(self):
        user = User.objects.create_user('temp', 'temp@gmail.com', 'temp')
        profile = Profile(user=user) 
        
    def test_add_auth(self):
        song = mommy.make(Song)
        ccli = str(song.ccli)
        user = authenticate(username='temp', password='temp')
        current_setlist = self.client.session.get('current_setlist')
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
        self.assertEqual(self.client.session.get('setlist'), [(ccli, 'G')])
        setlist_song = SetlistSong.objects.filter(setlist=current_setlist, song=song)
        self.assertEqual(len(setlist_song), 1)
        

# class StringToVerseParseTests(TestCase):
    # """
    # tests for parsing string to verse

    # """
    # def setUp(self):
        # verses = [22, 23, 18, 22]
        # book = Book.objects.create(name='Ruth', num_chapters = len(verses), order_index = 8)
        # for chap in range(1, 5):
            # chapter = Chapter.objects.create(book=book, number=chap, num_verses=verses[chap-1])
            # for ver in range(1, verses[chap-1]+1):
                # verse = Verse.objects.create(book=book, chapter=chapter, number=ver)
                
    # def test_parse_book_only(self):
        # """
        # Given a string of a book name, should return all verse ids in the book
        # """
        # query = 'ruth'
        # qs = Verse.objects.filter(book__name__iexact=query)
        # verse_id_list = qs.values_list('id', flat=True)
        # self.assertEqual(len(parse_string_to_verses(query)), len(verse_id_list))
        
    # def test_parse_book_chapters(self):
        # """
        # Given a string of a book name and chapters
        # """
        # query = 'ruth 1-2'
        # qs = Verse.objects.filter(book__name__iexact='ruth', chapter__number=1)
        # qs2 = Verse.objects.filter(book__name__iexact='ruth', chapter__number=2)
        # qs = qs | qs2
        # verse_ids = qs.values_list('id', flat=True)
        # self.assertEqual(len(parse_string_to_verses(query)), len(verse_ids))
        