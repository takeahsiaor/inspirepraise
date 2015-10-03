"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.test import Client
from model_mommy import mommy
from django.test import TestCase, LiveServerTestCase
from songs.functions import transpose, convert_setlist_to_string, make_key_option_html
from songs.views import parse_string_to_verses
from songs.models import Verse, Book, Chapter, Profile, Song, Setlist, SetlistSong, Ministry, MinistryMembership
from songs.models import MinistrySong, MinistrySongDetails, ProfileSong, ProfileSongDetails
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
    def setUp(self):
        pass
        # song = mommy.make(Song)
        # ccli = str(song.ccli)
        
    def test_add_unauth(self):
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
        self.assertEqual(self.client.session.get('setlist'), [(ccli, 'G')])
        
        
#test invite to ministry
        
class PublishSetlistAuth(TestCase):
    #tests push_setlist view
    # def setUp(self):
        # user = User.objects.create_user('temp', 'temp@gmail.com', 'temp')
        # profile = Profile(user=user) 
        # self.client.post('/accounts/login/', {'username':'temp', 'password':'temp'})    

    def test_publish_save_info_send_to_ministry(self):
        user = User.objects.create_user('temp', 'temp@gmail.com', 'temp')
        profile, created = Profile.objects.get_or_create(user=user) 
        self.client.post('/accounts/login/', {'username':'temp', 'password':'temp'})  
        ministry = mommy.make(Ministry)
        membership, created = MinistryMembership.objects.get_or_create(member=profile, ministry=ministry)
        profile2 = mommy.make(Profile)
        membership2, created = MinistryMembership.objects.get_or_create(member=profile2, ministry=ministry)
        #test that there are two members in minsitry
        self.assertEqual(2, len(MinistryMembership.objects.filter(ministry=ministry)))
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
        #COULD ADD ANOTHER UPDATE FOR SETLIST NOTES AND SONG NOTES
        #test that profile2 does not currently have setlist
        profile2_setlist = Setlist.objects.filter(profile=profile2)
        self.assertEqual(False, profile2_setlist.exists())
        #publish setlist to ministry with saving data
        response = self.client.get('/push-setlist/?ministry_id='+str(ministry.id)+'&save_stats=true')
        #test popularity increase of song
        song = Song.objects.get(ccli=ccli)
        self.assertEqual(song.popularity, 2)
        #test saving of profilesong
        profilesong = ProfileSong.objects.get(profile=profile, song=song)
        self.assertEqual(profilesong.times_used, 1)
        #test saving of profilesongdetails
        profilesongdetails = ProfileSongDetails.objects.filter(profilesong=profilesong)
        self.assertEqual(True, profilesongdetails.exists())
        profilesongdetails = profilesongdetails[0]
        self.assertEqual(profilesongdetails.key, 'G')
        self.assertEqual(profilesongdetails.song_context, ccli+'-G')
        #test saving of ministrysong
        ministrysong = MinistrySong.objects.get(song=song, ministry=ministry)
        self.assertEqual(ministrysong.times_used, 1)
        #test saving of ministrysongdetails
        ministrysongdetails = MinistrySongDetails.objects.filter(ministrysong=ministrysong)
        self.assertEqual(True, ministrysongdetails.exists())
        ministrysongdetails = ministrysongdetails[0]
        self.assertEqual(ministrysongdetails.key, 'G')
        self.assertEqual(ministrysongdetails.song_context, ccli+'-G')
        #test that copy of setlist saved to profile2
        profile2_setlist = Setlist.objects.filter(profile=profile2)
        self.assertEqual(True, profile2_setlist.exists())
        #test that setlistsong is also saved
        profile2_setlistsong = SetlistSong.objects.filter(setlist=profile2_setlist)
        self.assertEqual(profile2_setlistsong[0].key, 'G')
        self.assertEqual(True, profile2_setlistsong.exists())
        
    def test_publish_no_save_send_to_ministry(self):
        #test send to ministry with no data save
        #should create new setlist object but should not create profilesong/details, or ministrysong/details
        user = User.objects.create_user('temp', 'temp@gmail.com', 'temp')
        profile, created = Profile.objects.get_or_create(user=user) 
        self.client.post('/accounts/login/', {'username':'temp', 'password':'temp'})          
        ministry = mommy.make(Ministry)
        membership, created = MinistryMembership.objects.get_or_create(member=profile, ministry=ministry)
        profile2 = mommy.make(Profile)
        membership2, created = MinistryMembership.objects.get_or_create(member=profile2, ministry=ministry)
        #test that there are two members in minsitry
        self.assertEqual(2, len(MinistryMembership.objects.filter(ministry=ministry)))
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')   
        #test that profile2 does not currently have setlist
        profile2_setlist = Setlist.objects.filter(profile=profile2)
        self.assertEqual(False, profile2_setlist.exists())
        #publish setlist to ministry with saving data
        response = self.client.get('/push-setlist/?ministry_id='+str(ministry.id)+'&save_stats=true')
        #test popularity increase of song
        song = Song.objects.get(ccli=ccli)
        self.assertEqual(song.popularity, 2)
        #test that copy of setlist saved to profile2
        profile2_setlist = Setlist.objects.filter(profile=profile2)
        self.assertEqual(True, profile2_setlist.exists())
        
    def test_publish_no_send_no_save(self):
        #test publish ot nobody and to not save
        user = User.objects.create_user('temp', 'temp@gmail.com', 'temp')
        profile, created = Profile.objects.get_or_create(user=user) 
        self.client.post('/accounts/login/', {'username':'temp', 'password':'temp'})   
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')  
        response = self.client.get('/push-setlist/?ministry_id=none&save_stats=false')
        #should not save any profile song
        self.assertEqual(False, ProfileSong.objects.filter(profile=profile).exists())
        #by not throwing error, this means no ministrysong was created as well
        
    def test_publish_no_send_but_save(self):
        #test publish ot nobody but save usage data
        user = User.objects.create_user('temp', 'temp@gmail.com', 'temp')
        profile, created = Profile.objects.get_or_create(user=user) 
        self.client.post('/accounts/login/', {'username':'temp', 'password':'temp'})   
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')  
        response = self.client.get('/push-setlist/?ministry_id=none&save_stats=true')
        #should save profile song
        profilesong_qs = ProfileSong.objects.filter(profile=profile)
        self.assertEqual(True, profilesong_qs.exists())
        #should save profilesongdetails
        profilesongdetails_qs = ProfileSongDetails.objects.filter(profilesong=profilesong_qs[0])
        self.assertEqual(True, profilesongdetails_qs.exists())
        #by not throwing error, this means no ministrysong was created as well        
        
        
class UpdateSetlistAuth(TestCase):       
    def setUp(self):
        user = User.objects.create_user('temp', 'temp@gmail.com', 'temp')
        profile = Profile(user=user) 
        self.client.post('/accounts/login/', {'username':'temp', 'password':'temp'})
        
    def test_add_auth(self):
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
        #test proper setlist as list
        self.assertEqual(self.client.session.get('setlist'), [(ccli, 'G')])
        #test that a setlistsong was created
        current_setlist = self.client.session.get('current_setlist')
        setlist_song = SetlistSong.objects.filter(setlist=current_setlist, song=song)
        self.assertEqual(len(setlist_song), 1)
        #test that setlist song order string is correct
        setlist_string_order = ccli+'-G'
        self.assertEqual(setlist_string_order, current_setlist.song_order)
        
    def test_clear_auth(self):
        song = mommy.make(Song)
        current_setlist = self.client.session.get('current_setlist')
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
        old_setlist_id = current_setlist.id
        response = self.client.get('/update-setlist/?ccli=clear')
        new_setlist = self.client.session.get('current_setlist')
        #test if old setlist is deleted
        self.assertEqual(False, Setlist.objects.filter(id=old_setlist_id).exists()) 
        #test if old setlistsong is deleted
        self.assertEqual(False, SetlistSong.objects.filter(setlist__id=old_setlist_id).exists())
        #make sure there is no new SetlistSong created
        setlist_song = SetlistSong.objects.filter(setlist=new_setlist, song=song)
        self.assertEqual(False, setlist_song.exists())
        #make sure session setlist is empty list
        self.assertEqual(self.client.session.get('setlist'), [])
        #test to see if that the new setlist is not archived
        self.assertEqual(False, new_setlist.archived)
        #test that old setlist is not hte same as the new setlist
        self.assertNotEqual(old_setlist_id, new_setlist.id)
        
    def test_remove_auth(self):
        songs = mommy.make(Song, _quantity=3)
        setlist_as_list = []
        for song in songs:
            ccli = str(song.ccli)
            response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
            setlist_as_list.append((ccli, 'G'))
        #remove middle element - songs[1]
        ccli_to_remove = str(songs[1].ccli)
        response = self.client.get('/update-setlist/?remove=true&ccli='+ccli_to_remove) 
        #test that setlist order string is good
        current_setlist = self.client.session.get('current_setlist')
        song_order_string = str(songs[0].ccli)+'-G,'+str(songs[2].ccli)+'-G'
        self.assertEqual(song_order_string, current_setlist.song_order)
        #test that setlistsong object is deleted
        setlistsongs = SetlistSong.objects.filter(setlist=current_setlist)
        self.assertEqual(2, len(setlistsongs))
        #test that setlist_as_list is correct
        setlist_as_list.pop(1)
        self.assertEqual(setlist_as_list, self.client.session.get('setlist'))

    def test_reorder_auth(self):
        #can't rely on mommy to make songs with random ccli. will create negative cclis that interfere with 
        #parsing of ccli_string (split on '-')
        song1 = mommy.make(Song, ccli=1)
        song2 = mommy.make(Song, ccli=2)
        song3 = mommy.make(Song, ccli=3)
        songs = [song1, song2, song3]
        setlist_as_list = []
        for song in songs:
            ccli = str(song.ccli)
            response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
            setlist_as_list.append((ccli, 'G'))
        #swap 2nd and 3rd
        ccli_to_send = str(songs[0].ccli)+'-G,'+str(songs[2].ccli)+'-G,'+str(songs[1].ccli)+'-G,'
        response = self.client.get('/update-setlist/?reorder=true&ccli='+ccli_to_send)
        #test song order in setlist object
        current_setlist = self.client.session.get('current_setlist')
        self.assertEqual(current_setlist.song_order, ccli_to_send[:-1])
        #test setlist as list for order
        new_setlist_as_list = [setlist_as_list[0], setlist_as_list[2], setlist_as_list[1]]
        self.assertEqual(new_setlist_as_list, self.client.session.get('setlist'))
        
    def test_setlist_notes_auth(self):
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')        
        notes = 'here are some notes!'
        #test that notes were saved
        response = self.client.get('/update-setlist/?ccli=1&cancel=false&setlist-notes='+notes)
        current_setlist = self.client.session.get('current_setlist')
        self.assertEqual(current_setlist.notes, notes)
        #test if user presses cancel function
        response = self.client.get('/update-setlist/?ccli=1&cancel=true&setlist-notes=blahblahblah')
        current_setlist = self.client.session.get('current_setlist')
        self.assertEqual(current_setlist.notes, notes)     
        #test if user changes notes
        response = self.client.get('/update-setlist/?ccli=1&cancel=false&setlist-notes=blahblahblah')   
        current_setlist = self.client.session.get('current_setlist')
        self.assertEqual(str(current_setlist.notes), 'blahblahblah')    
        
    def test_song_notes_auth(self):
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')       
        #test that notes were saved
        song_notes = 'here are some notes!'
        response = self.client.get('/update-setlist/?ccli='+ccli+'&song-notes='+song_notes+'&cancel=false')
        current_setlist = self.client.session.get('current_setlist')
        setlist_song = SetlistSong.objects.get(setlist=current_setlist, song=song)
        self.assertEqual(setlist_song.notes, song_notes)
        #test if user presses cancel
        response = self.client.get('/update-setlist/?ccli='+ccli+'&song-notes=blahblahblah&cancel=true')
        current_setlist = self.client.session.get('current_setlist')
        setlist_song = SetlistSong.objects.get(setlist=current_setlist, song=song)
        self.assertEqual(setlist_song.notes, song_notes)        
        #test if user changes notes
        response = self.client.get('/update-setlist/?ccli='+ccli+'&song-notes=blahblahblah&cancel=false')
        current_setlist = self.client.session.get('current_setlist')
        setlist_song = SetlistSong.objects.get(setlist=current_setlist, song=song)
        self.assertEqual(setlist_song.notes, 'blahblahblah')     

    def test_archived_auth(self):
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')     
        current_setlist = self.client.session['current_setlist']
        setlist_id_to_archive = current_setlist.id
        #run archive
        response = self.client.get('/update-setlist/?archive=true')
        #test that archived session variable is set
        archived = self.client.session['archived']
        self.assertEqual(archived, True)
        #test that the current setlist is set to archived
        archived_setlist = Setlist.objects.get(id=setlist_id_to_archive)
        self.assertEqual(True, archived_setlist.archived)
        #test that a new setlist is created and set to session variable current_setlist
        current_setlist = self.client.session['current_setlist']
        self.assertNotEqual(current_setlist.id, setlist_id_to_archive)
        #test that empty list is set as setlist session variable
        self.assertEqual([], self.client.session['setlist'])
        
    def test_delete_setlist_auth(self):
        #for deleting from archive
        song = mommy.make(Song)
        ccli = str(song.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')     
        current_setlist = self.client.session['current_setlist']
        setlist_id = current_setlist.id
        #test that setlist exists and setlist song exists
        self.assertEqual(True, Setlist.objects.filter(id=setlist_id).exists())
        self.assertEqual(True, SetlistSong.objects.filter(setlist=current_setlist).exists())
        response = self.client.get('/update-setlist/?delete='+str(setlist_id))
        #test that setlist is deleted
        self.assertEqual(False, Setlist.objects.filter(id=setlist_id).exists())
        #test that setlist songs are deleted
        self.assertEqual(False, SetlistSong.objects.filter(setlist=current_setlist).exists())
        
    def test_reuse_setlist_auth(self):
        song1 = mommy.make(Song, ccli=1)
        ccli1 = str(song1.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli1+'&key=G')     
        current_setlist = self.client.session['current_setlist']
        setlist1_id = current_setlist.id
        setlist1_tuple = self.client.session['setlist']
        #archive setlist1
        response = self.client.get('/update-setlist/?archive=true')
        #creates setlist2
        song2 = mommy.make(Song, ccli=2)
        ccli2 = str(song2.ccli)
        response = self.client.get('/update-setlist/?add=true&ccli='+ccli2+'&key=G')     
        current_setlist = self.client.session['current_setlist']
        setlist2_id = current_setlist.id
        setlist2_tuple = self.client.session['setlist']
        self.assertNotEqual(setlist1_id, setlist2_id)
        self.assertNotEqual(setlist1_tuple, setlist2_tuple)
        self.assertEqual(setlist2_tuple, [(ccli2, 'G')])
        #reuse setlist1
        response = self.client.get('/update-setlist/?reuse-setlist='+str(setlist1_id))
        #test that setlist1 (originally archived) is in current_setlist
        current_setlist = self.client.session['current_setlist']
        setlist1 = Setlist.objects.get(id=setlist1_id)
        self.assertEqual(current_setlist, setlist1)
        #test that setlist1 is not archived
        self.assertEqual(False, setlist1.archived)        
        #test that setlist session is correct
        self.assertEqual(setlist1_tuple, self.client.session['setlist'])        
        #test that setlist2 (originally active) is archived
        setlist2 = Setlist.objects.get(id=setlist2_id)
        self.assertEqual(setlist2.archived, True)
    
    def test_key_reset_auth(self):
        song1 = mommy.make(Song, ccli=1, chords="{key:A}")
        song2 = mommy.make(Song, ccli=2, chords="{key:B}")
        song3 = mommy.make(Song, ccli=3, chords="{key:C}")
        songs = [song1, song2, song3]
        setlist_as_list = []
        for song in songs:
            ccli = str(song.ccli)
            response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
            setlist_as_list.append((ccli, 'G'))
        #reset key for song2
        ccli_str = str(song1.ccli)+'-G,'+str(song2.ccli)+'-G,'+str(song3.ccli)+'-G,'
        response = self.client.get('/update-setlist/?reset='+str(song2.ccli)+'&ccli='+ccli_str)
        #test that setlist session is good
        setlist_as_list = self.client.session['setlist']
        setlist_should_be = [(str(song1.ccli), 'G'), (str(song2.ccli),'B'), (str(song3.ccli), 'G')]
        self.assertEqual(setlist_should_be, setlist_as_list)
        #test that setlist object song order is good
        current_setlist = self.client.session['current_setlist']
        setlist_song_order = current_setlist.song_order
        song_order_should_be = str(song1.ccli)+'-G,'+str(song2.ccli)+'-B,'+str(song3.ccli)+'-G'
        self.assertEqual(setlist_song_order, song_order_should_be)
        #reset key for song3
        ccli_str = str(song1.ccli)+'-G,'+str(song2.ccli)+'-B,'+str(song3.ccli)+'-G,'
        response = self.client.get('/update-setlist/?reset='+str(song3.ccli)+'&ccli='+ccli_str)
        #test that setlist session is good
        setlist_as_list = self.client.session['setlist']
        setlist_should_be = [(str(song1.ccli), 'G'), (str(song2.ccli),'B'), (str(song3.ccli), 'C')]         
        #test that setlist object song order is good
        current_setlist = self.client.session['current_setlist']
        setlist_song_order = current_setlist.song_order
        song_order_should_be = str(song1.ccli)+'-G,'+str(song2.ccli)+'-B,'+str(song3.ccli)+'-C'
        self.assertEqual(setlist_song_order, song_order_should_be)       
        
    def test_key_change_auth(self):
        song1 = mommy.make(Song, ccli=1)
        song2 = mommy.make(Song, ccli=2)
        song3 = mommy.make(Song, ccli=3)
        songs = [song1, song2, song3]
        setlist_as_list = []
        for song in songs:
            ccli = str(song.ccli)
            response = self.client.get('/update-setlist/?add=true&ccli='+ccli+'&key=G')
            setlist_as_list.append((ccli, 'G'))
        #change key for song2 from G to C     
        ccli_str = str(song1.ccli)+'-G,'+str(song2.ccli)+'-G,'+str(song3.ccli)+'-G,'       
        response = self.client.get('/update-setlist/?ccli-keychange='+str(song2.ccli)+'-C'+'&ccli='+ccli_str)
        #test that setlist session is good
        setlist_as_list = self.client.session['setlist']
        setlist_should_be = [(str(song1.ccli), 'G'), (str(song2.ccli),'C'), (str(song3.ccli), 'G')]  
        self.assertEqual(setlist_should_be, setlist_as_list)        
        #test that setlistobject song order is good
        current_setlist = self.client.session['current_setlist']
        setlist_song_order = current_setlist.song_order
        song_order_should_be = str(song1.ccli)+'-G,'+str(song2.ccli)+'-C,'+str(song3.ccli)+'-G'
        self.assertEqual(setlist_song_order, song_order_should_be)              
        #change key for song3 from G to B
        ccli_str = str(song1.ccli)+'-G,'+str(song2.ccli)+'-C,'+str(song3.ccli)+'-B,'
        response = self.client.get('/update-setlist/?ccli-keychange='+str(song3.ccli)+'-B'+'&ccli='+ccli_str)
        #test that setlist session is good
        setlist_as_list = self.client.session['setlist']
        setlist_should_be = [(str(song1.ccli), 'G'), (str(song2.ccli),'C'), (str(song3.ccli), 'B')]         
        self.assertEqual(setlist_should_be, setlist_as_list)
        #test that setlist object song order is good
        current_setlist = self.client.session['current_setlist']
        setlist_song_order = current_setlist.song_order
        song_order_should_be = str(song1.ccli)+'-G,'+str(song2.ccli)+'-C,'+str(song3.ccli)+'-B'
        self.assertEqual(setlist_song_order, song_order_should_be)  
        
class StringToVerseParseTests(TestCase):
    """
    tests for parsing string to verse

    """
    def setUp(self):
        verses = [22, 23, 18, 22]
        book = Book.objects.create(name='Ruth', num_chapters = len(verses), order_index = 8)
        for chap in range(1, 5):
            chapter = Chapter.objects.create(book=book, number=chap, num_verses=verses[chap-1])
            for ver in range(1, verses[chap-1]+1):
                verse = Verse.objects.create(book=book, chapter=chapter, number=ver)
                
    def test_parse_book_only(self):
        """
        Given a string of a book name, should return all verse ids in the book
        """
        query = 'ruth'
        qs = Verse.objects.filter(book__name__iexact=query)
        verse_id_list = qs.values_list('id', flat=True)
        self.assertEqual(len(parse_string_to_verses(query)), len(verse_id_list))
        
    def test_parse_book_chapters(self):
        """
        Given a string of a book name and chapters
        """
        query = 'ruth 1-2'
        qs = Verse.objects.filter(book__name__iexact='ruth', chapter__number=1)
        qs2 = Verse.objects.filter(book__name__iexact='ruth', chapter__number=2)
        qs = qs | qs2
        verse_ids = qs.values_list('id', flat=True)
        self.assertEqual(len(parse_string_to_verses(query)), len(verse_ids))
        query = 'ruth 1,2'
        self.assertEqual(len(parse_string_to_verses(query)), len(verse_ids))
        