# Create your views here.
# ooga booga
import time
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from songs.forms import ContactForm, BookForm, SongForm, AuthorForm, PublisherForm, BookChapterForm, BasicForm
from songs.forms import MinistryForm, ProfileForm, TagVerseForm, SearchInfoForm, SearchVerseForm, InviteForm
from songs.models import Song, Book, Chapter, Verse, SongVerses, Ministry, Profile, Publisher, Author, MinistryMembership
from songs.models import Invitation, Setlist, SetlistSong, MinistrySong, ProfileSong, MinistrySongDetails, ProfileSongDetails
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils.html import escape, strip_tags
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Q
from django.contrib.auth import login, authenticate, logout #these are functions
from django.contrib.auth import views #these are views
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.signals import user_logged_in
from itertools import chain, groupby
from operator import itemgetter
from registration.signals import user_activated
# from registration.views import RegistrationView
from haystack.query import SearchQuerySet, RelatedSearchQuerySet
from difflib import get_close_matches
from songs.functions import parse_string_to_verses, test_parsable, force_int, check_song, transpose
from songs.functions import get_song_info_from_link, save_songs_from_dict, link_song_to_verses
from songs.functions import make_key_option_html, convert_setlist_to_string, get_md5_hexdigest, get_global_key_stats
from bs4 import BeautifulSoup
import urllib2, string, re, pickle, os, json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from string import letters
# from random import choice

#reportlab for pdf generation
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame, Table, SimpleDocTemplate
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import KeepTogether, Spacer, PageBreak

#globals for reportlab
#------------------------------------------------------
styles = getSampleStyleSheet()
style = styles["Normal"]

chord_table_style = [
    ('ALIGN',         (1,1),   (-1,-1),  'LEFT'),
    ('LEFTPADDING',   (0,0),   (-1,-1),  0),
    ('RIGHTPADDING',  (0,0),   (-1,-1),  0),
    ('TOPPADDING',    (0,0),   (-1,-1),  0),
    ('BOTTOMPADDING', (0,0),   (-1,-1),  0),
    ('FONT',          (0,0),   (-1,0),  'Times-Italic',  10),
    ('FONT',          (0,-1),  (-1,-1), 'Times-Roman', 12),
]

container_style = [
    ('ALIGN',         (1,1),   (-1,-1),  'LEFT'),
    ('LEFTPADDING',   (0,0),   (-1,-1),  0),
    ('RIGHTPADDING',  (0,0),   (-1,-1),  0),
    ('TOPPADDING',    (0,0),   (-1,-1),  0),
    ('BOTTOMPADDING', (0,0),   (-1,-1),  0),]

transposable = False
transpose_semitones = 2

#move this into functions later: must remember to import dependencies into functions as well
def make_pdf_table(chords, text, original_key):
    """Take list of chords and text and return pdf table"""
    #
    # Always ensure there is at least one space between chords
    #
    idx = 0
    pairs = zip(chords, text)
    for c, t in pairs:
        if idx < (len(pairs) - 1):
            if len(c) >= len(t): #originally just >
                text[idx] += ' - ' #space before AND after?
            chords[idx] += ' '
            idx += 1
    data = [chords, text]
    t = Table(data, style=chord_table_style, hAlign='LEFT')
    return t
    
#--------------------------------------------------------

def chord_html(request):
    #this is only for pagination html in setlist as it accepts cclilist from session setlist
    indexes = {
        'Ab': 0,
        'A': 1,
        'Bb':2,
        'B':3,
        'Cb':3,
        'C':4,
        'C#':5,
        'Db':5,
        'D': 6,
        'D#': 7,
        'Eb': 7,
        'E':8,
        'F':9,
        'F#':10,
        'Gb':10,
        'G':11,
        'G#':0
        }
    # ccli = int(request.GET.get('ccli'))
    ccli_list = request.session['setlist']
    if len(ccli_list) == 0:
        return
        
    # this stuff was needed to get the transpose values before it was changed so that
    # the desired key was saved with the setlist
    # transpose_str = request.GET.get('transpose_values')[:-1]
    # transpose_list_str = transpose_str.split(',')
    
    # transpose_list_final_key = []
    # for s in transpose_list_str:
        # transpose_list_final_key.append(s)
        
    html_list = []
    
    # for ccli, transpose_final_key in zip(ccli_list, transpose_list_final_key):
    for ccli in ccli_list:
        
        #ccli is a tuple
        song = Song.objects.get(ccli=int(ccli[0]))
        transpose_final_key = ccli[1]
        chord_stream = song.chords
        # if not chord_stream:
            # continue
        lines = chord_stream.split('\n')
        
        # f = open('C:/dropbox/django/songs_chordpro_checkedwguitar/1431.cho', 'r')
        html = ''
        emphasis = False
        for line in lines:

            #handle directives first
            if '{' in line:
                if '{title:' in line:
                    html += '<h3>'+line[7:-1]+'</h3>'
                    continue
                elif '{st:' in line:
                    html += '<h5>'+line[4:-1]+'</h5>'
                    continue
                elif '{key:' in line:
                    original_key = line[5:-1]
                    if request.user.is_authenticated():
                        current_setlist = request.session['current_setlist']
                        setlist_song = SetlistSong.objects.get(setlist=current_setlist, song=song)
                        song_notes_string = setlist_song.notes
                        # print song_notes_string
                        if song_notes_string:
                            song_notes_lines = song_notes_string.split('\n')
                            html += '<br><h5>Song Notes:</h5>'
                            for note_line in song_notes_lines:
                                html += '<h5>'+note_line+'</h5>'
                    continue

            #no directive in line
            else:
                if '[' in line:
                    separations = []
                    separations = line.split('[')
                    chords = []
                    lyrics = []
                    # go through each section and get the chord and lyric pairings
                    for section in separations:
                        if section == '':
                            continue
                        #if no chord, still append nothing to chords
                        elif ']' not in section:
                            lyrics.append(section)
                            chords.append('')
                            continue 
                        chordlyric = section.split(']')
                        chords.append(chordlyric[0])
                        lyrics.append(chordlyric[1])
                    html += '<table>'
                    if emphasis:
                        html += '<tr class="emphasis">'
                    else:
                        html += '<tr>'
                    
                    #transpose here!
                    transposed_chords = []
                    
                    if 'm' in original_key:
                        # minor = True
                        original_root = original_key[:-1]
                        final_root = transpose_final_key[:-1]
                    else:
                        # minor = False
                        original_root = original_key
                        final_root = transpose_final_key
                    original_key_index = indexes[original_root]
                    final_key_index = indexes[final_root]
                    
                    # original_key_index = indexes[original_key]
                    # final_key_index = indexes[transpose_final_key]
                    transpose_step = final_key_index - original_key_index
                        
                    for chord in chords:
                        if chord == '':
                            transposed_chords.append('')
                            continue
                        transposed_chord = transpose(chord, transpose_step, original_key, transpose_final_key)
                        transposed_chords.append(transposed_chord)

                    for chord in transposed_chords:
                        html += '<td>'+chord+'</td>'
                        
                    if emphasis:
                        html += '</tr><tr class="emphasis">'
                    else:
                        html += '</tr><tr>'
                        
                    for lyric in lyrics:
                        html += '<td>'+lyric+'</td>'
                        
                    html += '</tr></table>'

                else:
                    html += '<br>' + line
        #adding another br so last line doesn't get cut off
        html += '<br>'
        
        if not chord_stream: #this is to display "NO CHORDS AVAILABLE" in chord preview in setlist
        #                     primarily to solve "jump" issue when song in setlist without chords
            html = ''
            html += '<h3>'+song.title+'</h3>'
            authors_list = []
            publisher_list = []
            publication_year = song.publication_year
            for author in song.authors.all():
                authors_list.append(author.full_name)
            for publisher in song.publisher.all():
                publisher_list.append(publisher.name)
                
            if publication_year == 1111:
                publisher_line = '<h5>Public Domain</h5>'
            else:
                publisher_line = '<h5>Copyright '+str(song.publication_year)+ ' ' +', '.join(publisher_list)+'</h5>'
            html += '<h5>Words and music by '+', '.join(authors_list)+'</h5>'
            html += publisher_line
            html += '<br><br><br>No chords available<br>Check back later! Chords are being added daily!'
        html_list.append(html)
    if len(html_list) > 3:
        multipage = True
    else:
        multipage = False
    return render(request, 'format_as_option_list.html', {'song_chords':html_list, 'multipage':multipage})
                

def lyrics_to_text(request):
    #add in stuff for dealing with stanzas with no lyrics: handled later
    # do_not_include = ['intro:', 'interlude:']
    single_song = request.GET.get('single_song') #yes no for whether songs in single song or multiple
    if single_song=="yes":
        ccli_str = request.GET.get('ccli')
        ccli_list = [(ccli_str,)] #this needs to be like this to be consistent with setlist structure
    else:
        ccli_list = request.session['setlist']
        if len(ccli_list) == 0:
            return     
    response = HttpResponse(content_type='text/plain')
    for ccli_tuple in ccli_list:
        ccli = ccli_tuple[0]
        song = Song.objects.get(ccli=int(ccli))
        contents = song.chords
        if not contents: #no chords available
            continue
        content_lines = contents.split('\n')
        
        authors_list = []
        for author in song.authors.all():
            authors_list.append(author.full_name)
        publisher_list = []
        publication_date = song.publication_year
        for publisher in song.publisher.all():
            publisher_list.append(publisher.name)
        authors_line = ', '.join(authors_list)
        if publication_date == 1111:
            publishers_line = 'Public Domain'
        else:
            publishers_line = str(song.publication_year)+' '+', '.join(publisher_list)

        stanzas = []
        stanza_elements = ''
        for line in content_lines:
            if '{' in line:
                if '{title:' in line:
                    title = line[7:-1]
                    continue
                if '{end}' in line:
                    stanzas.append(stanza_elements)
                continue
            #no directive in line
            else:
                chords = []
                lyrics = []
                if '[' in line:
                    separations = []
                    separations = line.split('[')
                    # go through each section and get the chord and lyric pairings
                    for section in separations:
                        if section == '':
                            continue
                        #if no chord, still append nothing to chords
                        elif ']' not in section:
                            lyrics.append(section)
                            chords.append('')
                            continue 
                        chordlyric = section.split(']')
                        chords.append(chordlyric[0])
                        if chordlyric[1] == ' ': #added this to not add spaces to lyrics list when it's only chords
                            continue
                        lyrics.append(chordlyric[1])
                else:
                    lyrics.append(line)

                if line == '': #stanza ended
                    stanzas.append(stanza_elements)
                    stanza_elements = ''
                else:
                    stanza_elements += ''.join(lyrics) + '\r\n'
        temp_stanzas = []
        for stanza in stanzas:#attempt to get rid of stanzas without text
            if '\r\n' in stanza.strip(): #strips off end line feed. if only one line, will have none, if 2 lines, will have 1
                temp_stanzas.append(stanza.strip()+'\r\n')#remove extra newlines then put only one
        stanzas = temp_stanzas
        
        result = 'Title:'+title+'\r\nAuthor:'+authors_line+'\r\nCopyright:'+publishers_line+'\r\nCCLI:'+ccli+'\r\n\r\n'
        result += '\r\n'.join(stanzas)
        result += '\r\n' #to separate songs from each other
        # print repr(result)
        response.write(result.encode('utf8'))

    if single_song == 'yes':      
        response['Content-Disposition'] = 'attachment; filename="' + song.title+' - '+ ccli + '.txt"'  
    else:
        response['Content-Disposition'] = 'attachment; filename="InspirePraise_lyrics.txt"' 
    return response
    
            
def chord_pdf(request):
    indexes = {
        'Ab': 0,
        'A': 1,
        'Bb':2,
        'B':3,
        'Cb':3,
        'C':4,
        'C#':5,
        'Db':5,
        'D': 6,
        'D#': 7,
        'Eb': 7,
        'E':8,
        'F':9,
        'F#':10,
        'Gb':10,
        'G':11,
        'G#':0
        }
    single_song = request.GET.get('single_song') #yes no for whether songs in single song or multiple
    if single_song=="yes":
        ccli_str = request.GET.get('ccli')
        ccli_list = [ccli_str]
        
        #still need this for single song since we're not looking at setlist and have no key
        transpose_str = request.GET.get('transpose_values')[:-1]
        transpose_list_str = transpose_str.split(',')
        transpose_list_final_key = []
        for s in transpose_list_str:
            transpose_list_final_key.append(s)
        print transpose_list_final_key[0]
    else:
        ccli_list = request.session['setlist']
        if len(ccli_list) == 0:
            return
    


    response = HttpResponse(content_type='application/pdf')
    if single_song == 'yes':
        ccli = ccli_list[0]
        song = Song.objects.get(ccli=int(ccli))
        response['Content-Disposition'] = 'attachment; filename="' + song.title+' - '+ ccli + '.pdf"'
    else:
        response['Content-Disposition'] = 'attachment; filename="InspirePraise Setlist.pdf"'
    # c = canvas.Canvas('C:/dropbox/django/test/test.pdf', letter)
    c = canvas.Canvas(response, letter)    

    # for ccli, transpose_final_key in zip(ccli_list, transpose_list_final_key):
        # song = Song.objects.get(ccli=int(ccli))    
   
    for ccli in ccli_list:
        #ccli is a tuple for multiple songs, but a string for single song
        if single_song =="yes":
            ccli_string = ccli
            song = Song.objects.get(ccli=int(ccli))
            transpose_final_key = transpose_list_final_key[0]
        else:
            ccli_string = ccli[0]
            song = Song.objects.get(ccli=int(ccli[0]))
            transpose_final_key = ccli[1]
        

        chord_stream = song.chords
        if not chord_stream:
            continue
        lines_in_stream = chord_stream.split('\n')
    
        header = []
        song = []
        styles = getSampleStyleSheet()
        # ccli = int(request.GET.get('ccli'))
        #split things up based on "paragraph" then for each paragraph, parse each line for chord/text

        para_texts = []
        para_text = ''
        
        #to get to this point with a raw string rather than file where you can iterate line by line
        #assuming content is a raw string given after opening file then doing f.read()
        #content = content.split('\n')
        #then paragraph separations are either '' or {end}
        #within this loop, you need to re-add the new lines though
        for line in lines_in_stream:
            if line == '' or '{end}' in line:
                para_texts.append(para_text)
                para_text = ''
                continue
            para_text += line + '\n'

        #deal with header paragraph
        header_lines = para_texts[0].split('\n')[:-1]
        for line in header_lines:
            if '{title:' in line:
                style = styles["Normal"]
                title = line[7:-1]
                t = Paragraph(line[7:-1], style)
                header.append(t)
                continue
            if '{st:' in line:
                style = styles["Normal"]
                t = Paragraph(line[4:-1], style)
                header.append(t)
                continue
            if '{key:' in line:
                original_key = line[5:-1]
                continue
        song_notes_flag = False
        #this is for inclusion of basic notes for a given song
        if request.user.is_authenticated():
            current_setlist = request.session['current_setlist']
            current_song = Song.objects.get(ccli=ccli_string) #ccli_string initialized in for loop to handle string vs tuple
            try: #if song not in setlist yet, still want to be able to get pdfs
                setlist_song = SetlistSong.objects.get(setlist=current_setlist, song=current_song)
                song_notes = setlist_song.notes
            except:
                song_notes = ''
            if song_notes:
                header.append(Spacer(3.75*inch, 0.1*inch))
                t = Paragraph(song_notes,style)
                header.append(t)
                song_notes_flag = True
        
                
        stanzas = [] #a list of lists, each element is a stanza each with table elements for each line

        for para_text in para_texts[1:]:
            stanza_elements = []
            lines = para_text.split('\n')[:-1]
            for line in lines:
                if '[' in line:
                    separations = line.split('[')
                    chords = []
                    lyrics = []
                    # go through each section and get the chord and lyric pairings
                    for section in separations:
                        if section == '':
                            continue
                        #if no chord, still append nothing to chords
                        elif ']' not in section:
                            lyrics.append(section)
                            chords.append('')
                            continue 
                        chordlyric = section.split(']')
                        chords.append(chordlyric[0])
                        lyrics.append(chordlyric[1])
                else:
                    lyrics = []
                    lyrics.append(line)
                    chords = ['']
                
                #transposition stuff here
                transposed_chords = []
                
                if 'm' in original_key:
                    # minor = True
                    original_root = original_key[:-1]
                    final_root = transpose_final_key[:-1]
                else:
                    # minor = False
                    original_root = original_key
                    final_root = transpose_final_key
                original_key_index = indexes[original_root]
                final_key_index = indexes[final_root]
                
                # original_key_index = indexes[original_key]
                # final_key_index = indexes[transpose_final_key]
                transpose_step = final_key_index - original_key_index
                           
                for chord in chords:
                    if chord == '':
                        transposed_chords.append('')
                        continue
                    transposed_chord = transpose(chord, transpose_step, original_key, transpose_final_key)
                    transposed_chords.append(transposed_chord)
                
                # song.append(make_pdf_table(chords, lyrics))  
                line = [make_pdf_table(transposed_chords, lyrics, original_key)] #creates table for each line and chord
                stanza_elements.append(line) #creates list of line tables
                
            #this is a container for each stanza: one column, and rows are each line
            stanza_table = Table(stanza_elements, style=container_style) 
            #add the stanza to the song with a spacer afterwards
            song.append(stanza_table)
            song.append(Spacer(3.75*inch, 0.1*inch))
            
        #add check for how long the notes for a song are. if over a certain length, change next lines to
        # headerframe = Frame(0.5*inch, 9*inch, 7.5*inch, 1.5*inch,  showBoundary=0) 
        # headerframe.addFromList(header, c)
        # frame = Frame(0.5*inch, 0.5*inch, 3.75*inch, 8.5*inch, showBoundary=0)
        # frame.addFromList(song, c)
        # frame2 = Frame(4.25*inch, 0.5*inch, 3.75*inch, 8.5*inch, showBoundary=0)
        
        if not song_notes_flag: #if no notes
            headerframe = Frame(0.5*inch, 9.5*inch, 7.5*inch, 1*inch,  showBoundary=0) 
        else: #if single line of notes:
            headerframe = Frame(0.5*inch, 9.5*inch, 7.5*inch, 1.2*inch,  showBoundary=0) 
        headerframe.addFromList(header, c)
        frame = Frame(0.5*inch, 0.5*inch, 3.75*inch, 9.0*inch, showBoundary=0)
        frame.addFromList(song, c)
        frame2 = Frame(4.25*inch, 0.5*inch, 3.75*inch, 9.0*inch, showBoundary=0)
        frame2.addFromList(song, c)
        c.showPage()
        # c.save()
    c.save()
    return response
    
def display_push_setlist(request, **kwargs):
    """
    after login, look for setlists that are pushed.
    """
    print 'display_push_setlist'
    user = request.user
    profile, profile_created = Profile.objects.get_or_create(user=user)
    pushed_setlist = Setlist.objects.filter(profile=profile, pushed=True)
    if pushed_setlist: #perhaps later this can be tuple containing pushed setlists instead of boolean
        request.session['pushed_setlist'] = pushed_setlist
    else:
        request.session['pushed_setlist'] = None
    return
    
def retrieve_setlist(request, **kwargs):
    """
    after login, this will retrieve the text set list from the database
    parse the text into a list of ccli then populate it into the session
    """
    user = request.user
    #attempt to fix the logging in of created superuser and having no profile
    profile, profile_created = Profile.objects.get_or_create(user=user)
    current_setlist, setlist_created = Setlist.objects.get_or_create(profile=profile, archived=False, pushed=False)
    print setlist_created
    request.session['current_setlist'] = current_setlist
    if setlist_created: #new setlist object therefore no setlist order
        setlist_text =''
        print 'NEW SETLIST'
        request.session['setlist'] = []
        return
    else: #old setlist object so must parse song order and put into session 'setlist'
        print current_setlist
        setlist_text = current_setlist.song_order
        if setlist_text: #if the setlist currently has songs
            ccli_list = setlist_text.split(',')
            temp_list = []
            for tuple_str in ccli_list:
                tuple = tuple_str.split('-')
                ccli = tuple[0]
                key = tuple[1]
                temp_list.append((ccli,key))
            request.session['setlist'] = temp_list
        else:
            request.session['setlist'] = []
        return 
    
def login_on_activation(sender, user, request, **kwargs):
    """Logs in the user after activation"""
    user.backend = 'django.contrib.auth.backends.ModelBackend' 
    login(request, user)

# Registers the function with the django-registration user_activated signal
user_activated.connect(login_on_activation)
# after the logged in signal is sent, will call retreive_setlist
user_logged_in.connect(retrieve_setlist)
user_logged_in.connect(display_push_setlist)

#login url comes here. checks for remember me option then sends off to 
#default django login view
def login_user(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(0)
    return views.login(request, *args, **kwargs)


@login_required
def logout_view(request):
    #save setlist to user
    setlist = []
    try:
        setlist = request.session['setlist']
    except:
        pass   
    setlist_string = convert_setlist_to_string(setlist)    
    logout(request)
    return HttpResponseRedirect(reverse('songs.views.home'))


def forbidden(request):
    return render(request, '403.html')

def home(request):
    #this will update session variable in case of someone sending setlist while you are logged in
    if request.user.is_authenticated():
        display_push_setlist(request) 
    return render(request, 'home.html')
    

    
def is_parsable(request):
    """
    receives as input a query and http request. sends response to format_as_option_list
    if parsable, will send True, if not, will send false
    rather than deal with sessions, will force parsing of each query twice for
    every entry. parse once to test, then parse again when tagging.
    # if parsable, will also append verse ID list to session dictionary
    # where key will be the query and the value will be the id list
    """
    #is this enough to make it safe?
    query = escape(request.GET.get('query'))
    try:
        verse_list = parse_string_to_verses(query)
        if len(verse_list) > 0:
            parsable = True
        else:
            parsable = False
    except:
        parsable = False
    return render(request, 'format_as_option_list.html', {'parse_test':True, 'parsable':parsable})
    
def import_songverse_from_file(request):
    """
    takes a dictionary with key being ccli as string and value being list of verse strings
    tags them with each other.
    """
    # f = open('D:/dropbox/django/worshiptogether_noccli_dict.txt', 'r')
    # f = open('D:/dropbox/django/worshiptogether_unparsable_dict.txt', 'r')
    f = open('C:/dropbox/django/dict_to_import.txt', 'r')
    song_verse_dict = pickle.load(f)
    f.close()
    print 'Number of songs'
    print len(song_verse_dict)
    keep_track = 0
    for ccli in song_verse_dict:
        does_not_exist = check_song(ccli)
        if does_not_exist:
            print 'fail'
            print ccli
            continue
        song = Song.objects.get(ccli=int(ccli))
        for verses in song_verse_dict[ccli]:
            verse_ids = parse_string_to_verses(verses)
            link_song_to_verses(song, verse_ids)
        keep_track = keep_track + 1
    print "number of successful imports"
    print keep_track
    return HttpResponseRedirect(reverse('songs.views.success'))
    
def worshiptogether(request):
    #might need to redo import. weird stuff going on. 5496 song verses, 1598 songs with word to worship
    f = open('C:/dropbox/django/all_worshiptogether_html.txt', 'r')
    all_html = pickle.load(f)
    f.close()
    
    # all_html = all_html[800:]
    no_ccli = []
    no_scripture = []
    not_parsable = []
    for html in all_html:
        soup = BeautifulSoup(html)
        #get ccli number and check if ccli can be found on the page
        cclidiv = soup.select('#_ctl0_content_divCCLI')
        if len(cclidiv) == 0:
            no_ccli.append(html)
            continue
        else:
            cclitext = cclidiv[0].text.split('\r')
            ccli = cclitext[1].strip()
        #checks if song exists in database and/or gets song from ccli. if ccli# DNE, move on to next
        does_not_exist = check_song(ccli)
        if does_not_exist:
            continue
        #get scripture and check if any exists
        scriptdiv = soup.select('#_ctl0_content_divScripture')
        if len(scriptdiv) == 0:
            no_scripture.append(ccli)
            continue
        full_text = scriptdiv[0].text
        text = full_text.split('\r')
        #assumes that there is only one \r...may not be true could be missing some.
        scriptures = text[1]
        scripture_list = []
        edited_scripture_list = []
        if ';' in scriptures:
            scripture_list = scriptures.split(';')
        elif ',' in scriptures:
            scripture_list = scriptures.split(',')
        else:
            scripture_list.append(scriptures)
        #goes through each scripture group and tests if they're parsable and strips them    
        parsing_error = False
        for scripture in scripture_list:
            parsable = test_parsable(scripture.strip())
            if not parsable:
                not_parsable.append(ccli)
                parsing_error = True
                break
            edited_scripture_list.append(scripture.strip())

        #if there's an error in parsing in one of the strings, then move on
        if parsing_error:
            continue
        #handles the actually tagging
        # song = Song.objects.get(ccli=int(ccli))
        # for verses in edited_scripture_list:
            # verse_ids = parse_string_to_verses(verses)
            # link_song_to_verses(song, verse_ids)
        # print ccli, edited_scripture_list
    
    #saves all html for no ccli number songs
    # h = open('C:/dropbox/django/worship/worshiptogether_noccli.txt', 'w')
    # pickle.dump(no_ccli, h)
    # h.close()
    # #saves all ccli numbers of songs that can't be parsed - manual input
    # i = open('C:/dropbox/django/worship/worshiptogether_unparasable.txt', 'w')
    # pickle.dump(not_parsable, i)
    # i.close()
    
    print 'Number with no ccli', len(no_ccli)
    print 'No scripture', no_scripture
    print 'Not parsable', not_parsable
    return HttpResponseRedirect(reverse('songs.views.success'))
        

@login_required
@permission_required('is_staff', raise_exception=True)
def crawl_wordtoworship_letter(request): #CURRENTLY DISABLED WILL THROW ERROR
    """
    currently, looks through a letter for word to worship
    then gets the links for each song
    then goes to each link for scripture information and ccli
    and checks to see if the song is currently in WV database
    finally, links verses to song via link_song_to_verses
    """
    letter_link_ends = 'y' #'abcdefghijklmnopqrstuvwxyz'
    #all done
    #do in the secret manually deuteronomy 29:29 doesn't exist in my database
    #jonah 1:17 does not exist Rainbow manual
    # do What a friend i've found  manually
    # do madly manually

    song_links = []
    song_info = {}
    
    # #goes through each letter in letter_link_ends and gets all the song links on each page
    # for end in letter_link_ends:
        # song_list_url = 'http://www.wordtoworship.com/songs/' + end
        # #this section gets the list of urls from a letter page
        # html = urllib2.urlopen(song_list_url).read()
        # soup = BeautifulSoup(html)
        # content = soup.select('.views-field-title')
        # titles = content[1:]
        # for title in titles:
            # song_link = title.select('a')[0]['href']
            # song_links.append(song_link)
    # # song_links = song_links[39:]
    # #goes through each song_link and gets song_info off of it
    
    # this uses file containing all wordtoworship html 
    f = open('D:/dropbox/django/all_wordtoworship_html.txt', 'r')
    all_html = pickle.load(f)
    f.close()
    
    # for song_link in song_links:
        # url = 'http://www.wordtoworship.com' + song_link
        # song_html = urllib2.urlopen(url).read()
    for song_html in all_html:
        soup = BeautifulSoup(song_html)
        #for songs that inexplicably have no ccli number UGH!
        try:
            ccli_field = soup.select('.field-name-field-ccli')[0]
        except:
            continue
        ccli = ccli_field.text.split()[-1]
        labels = soup.select('.field-label')
        #looks for first scripture label in list of labels
        for i,label in enumerate(labels):
            if 'Scripture' in label.text:
                scripture_index = i
                break
        scripture = labels[scripture_index].next_sibling.text.split(';')
        song_info[ccli] = scripture

    #goes through each ccli in dictionary song_info
    #first makes sure it is in the database with check_song. if ccli number is wrong
    #does_not_exist will be true then should skip entry
    for ccli in song_info:
        print ccli
        does_not_exist = check_song(ccli)
        if does_not_exist:
            continue
        verse_string_list = song_info[ccli]
        #goes through each string, parsing each string to find the verse id list associated with it
        for verse_string in verse_string_list:
            verse_list = parse_string_to_verses(verse_string)
            song = Song.objects.get(ccli = int(ccli))
            #takes song object and list of verse ids
            link_song_to_verses(song, verse_list)
    return HttpResponseRedirect(reverse('songs.views.success'))
        

#a lot of similarities between lookup and crawl. can probably get rid of crawl later.
#add instruction. how many added, how many already in database

def lookup(request):
    #looking up "in your freedom" gives 'cia do louvor \n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\tdeigma marques \n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\tmarty sampson \n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\traymond badham'
    # for author. need to parse it differently
    errors = []
    #handle popup - if popup is present in url params and 1, then use popup template
    if '_popup' in request.GET:
        print 'POPUP!'
        popup = request.GET.get('_popup')
    else:
        print "NO POPUP!"
        popup = '0'
    if popup =='1':
        template = 'pop_lookup.html'
    else:
        template = 'lookup.html'
    #find query parameter
    if 'query' in request.GET:
        query = request.GET['query']
        query_url = query.replace(' ', '+')
        sort = request.GET['sort_type']
        if sort == 'popularity':
            beginning_url = 'https://us.songselect.com/search/results?SearchTerm='
            end_url = '&AllowRedirect=False&SearchWithinTerm=&Sorting=Popularity'
        elif sort == 'relevance':
            beginning_url = 'https://us.songselect.com/search/results?SearchTerm='
            end_url = '&AllowRedirect=False&SearchWithinTerm=&Sorting=Relevance'
        else:
            beginning_url = 'https://us.songselect.com/search/results?SearchTerm='
            end_url = '&AllowRedirect=False&SearchWithinTerm=&Sorting=CCLIRank'
        if not query:
            errors.append('Enter a search term.')
        else:
            #do i need to clean the query first??
            url = beginning_url + query_url + end_url
            html = urllib2.urlopen(beginning_url + query_url + end_url).read()
            soup = BeautifulSoup(html)
            list_portion = soup.find('table', 'song-listing')
            l = list_portion.find_all('a', {'class':'', 'onclick':''})

            song_link_list = []
            #finds all links in search results page
            for a in l:
                song_link_list.append(a['href'])
            song_link_list = song_link_list[:5]

            song_base_url = 'https://us.songselect.com'
            song_information = []
            #goes through each link found in search and gets relevant information from each page
            for link in song_link_list:
                url = song_base_url + link
                song_dict = get_song_info_from_link(url)
                song_information.append(song_dict)

            #saves song information in database
            songs = []
            num_new = 0
            num_old = 0
            for dict in song_information:
                song, new = save_songs_from_dict(dict)
                if new:
                    num_new = num_new + 1
                else:
                    num_old = num_old + 1
                songs.append(song)
            return render(request, template, {'songs':songs, 'url':url, 'num_new':num_new, 'num_old':num_old, 'popup':popup, 'query':query})
    return render(request, template, {'errors':errors, 'popup':popup})


@login_required
@permission_required('is_staff', raise_exception=True)
def crawl_songselect(request):
    top_url1 = 'https://us.songselect.com/search/results?Sorting=Popularity&List=PopularSongs&AllowRedirect=False&PageSize=100'
    top_url2 = 'https://us.songselect.com/search/results?AllowRedirect=False&PageSize=100&Sorting=Popularity&List=PopularSongs&Page=2'
    html_top1 = urllib2.urlopen(top_url1).read()
    soup = BeautifulSoup(html_top1)
    list_portion = soup.find('table', 'song-listing')
    l1 = list_portion.find_all('a', {'class':'', 'onclick':''})

    html_top2 = urllib2.urlopen(top_url2).read()
    soup2 = BeautifulSoup(html_top2)
    list_portion2 = soup2.find('table', 'song-listing')
    l2 = list_portion2.find_all('a', {'class':'', 'onclick':''})

    l = l1+l2
    song_link_list = []

    for a in l:
        song_link_list.append(a['href'])
    song_link_list = song_link_list[100:101]
    base_url = 'https://us.songselect.com'

    song_information = []

    for link in song_link_list:
        url = base_url + link
        song_dict = get_song_info_from_link(url)
        song_information.append(song_dict)

    #saves song information in database
    for dict in song_information:
        save_songs_from_dict(dict)
    return HttpResponseRedirect(reverse('songs.views.success'))
    
    
@login_required
def accept_ministry_complete(request):
   pass
    
   
def accept_ministry_invitation(request):
    """
    Email link sends user here. 
    """
    #potentially send to congratulations screen or welcome screen, rather than profile
    try: #verifies correct code and ministry stuff and makes sure user exists
        username = request.GET.get('code')
        ministry_id = request.GET.get('min')
        ministry = Ministry.objects.get(id=ministry_id)
        user = User.objects.get(username=username)
        invitation = Invitation.objects.filter(email=user.email, ministry=ministry)
    except:#if not, then just send to forbidden
        return HttpResponseRedirect(reverse('songs.views.forbidden'))
    if invitation: #if user and ministry exists, check if there is an invitation present for that person
        msg = "Congrats! You're now a part of the %s ministry group! Jump up and down!" % ministry.name
        messages.success(request, msg)
        if not user.is_active:#this means its user's first time logging in
            messages.success(request, "Remember to change your password when you get a chance!")
            user.is_active = True
            user.save()
        profile, created = Profile.objects.get_or_create(user=user)
        profile.save()
        membership = MinistryMembership(member=profile, ministry=ministry, active=True)
        membership.save()
        invitation.delete()
        return HttpResponseRedirect(reverse('songs.views.profile'))
    else:
        return HttpResponseRedirect(reverse('songs.views.forbidden'))
        
def send_ministry_invitation(recipient, password, from_email, ministry):
    user = recipient
    subject = "Invitation to " + ministry.name + " InspirePraise group"
    to_email = user.email
    context = {'ministry':ministry, 'user':user, 'password':password, 'from_email':from_email}
    message = render_to_string('invitation_email.txt', context)
    
    send_mail(subject, message, 'ron@onelivinghope.com', (to_email,))

    
@login_required
def invite_to_ministry(request, ministry_code):
    #PROTECT AGAINST INVITING EXISTING MEMBERS
    ministry = Ministry.objects.get(id=ministry_code)
    members = Profile.objects.filter(ministries=ministry) #members is queryset of profile objects that are part of ministry
    current_user = request.user
    profile = Profile.objects.get(user=current_user)
    try:
        membership = MinistryMembership.objects.get(member = profile, ministry=ministry)
    except:
        return HttpResponseRedirect(reverse('songs.views.forbidden'))    
    if request.method == "POST":
        form = InviteForm(request.POST)
        if form.is_valid():
            raw_email_string = request.POST['emails']
            email_list = raw_email_string.split(',')
            sent = [] #gather emails that will be sent
            already_invited = [] #gather emails that have already been invited
            for email in email_list:
                email = email.strip()
                #test for invitations already issued
                try:
                    invite = Invitation.objects.get(email=email, ministry=ministry)
                except:
                    invite = None                    
                if invite:
                    already_invited.append(email)
                    continue
                #test if user already exists. if so, then just send invitation no need to create user.
                try:
                    user = User.objects.get(email=email)
                    password = ''
                except:
                    #create new user if none exists
                    username = get_md5_hexdigest(email)
                    password = username[:10]
                    user = User(username=username, email=email, is_active=False)
                    user.set_password(password)
                    user.save()
                #create invitation
                invite = Invitation(email=email, ministry=ministry)
                invite.save()
                sender = current_user.email
                #send email
                send_ministry_invitation(user, password, sender, ministry)
                sent.append(email)
            if sent:
                msg_for_sent = 'Invitations have been sent to the following addresses: ' + ' ,'.join(sent)
                messages.success(request, msg_for_sent)
            if already_invited:
                msg_for_already_invited = 'These people have already been invited: ' + ' ,'.join(already_invited)
                messages.warning(request, msg_for_already_invited)            

            return HttpResponseRedirect(reverse('songs.views.profile'))
    else:
        form = InviteForm()
    return render(request, 'invite_to_ministry.html', {'form':form,'ministry':ministry})
    
@login_required
def ministry_profile(request, ministry_code):
    ministry = Ministry.objects.get(id=ministry_code)
    members_memberships = MinistryMembership.objects.filter(ministry=ministry) #queryset of membership objects
    current_user = request.user
    profile = Profile.objects.get(user=current_user)
    try:
        membership = MinistryMembership.objects.get(member = profile, ministry=ministry)
    except:
        return HttpResponseRedirect(reverse('songs.views.forbidden'))
        
    common_songs = MinistrySong.objects.filter(ministry=ministry).order_by('-times_used')[:10]
    recent_songs = MinistrySong.objects.filter(ministry=ministry).order_by('-last_used')[:5]
    return render(request, 'ministry_profile.html', {'ministry':ministry, 'membership':membership, 
        'members_memberships':members_memberships, 'common_songs':common_songs,'recent_songs':recent_songs})

@login_required
def leave_ministry(request, ministry_code):
    """
    Accessed via AJAX. Will be sent get parameters ministry_id
    Handles deletion of membership of current user in ministry
    If last member of ministry, delete ministry as well.
    If not the last member and has admin, transfer admin rights
    """
    #get number of members in ministry
    ministry = Ministry.objects.get(id=ministry_code)
    number_of_members = MinistryMembership.objects.filter(ministry=ministry).count()
    print number_of_members
    user = request.user
    profile = Profile.objects.get(user=user)
    membership = MinistryMembership.objects.get(member=profile, ministry=ministry)
    admin = membership.admin
    membership.delete()
    messages.success(request, "You've successfully left the "+ministry.name+" ministry!")
    if number_of_members == 1: #you're the last one, 
        print 'deleted ministry here!'
        ministry.delete()
        messages.success(request, "Since you were the last member, the ministry was deleted. Cleanin' house baby!")
    elif admin: #if more than 1 member and you are admin, transfer rights
        print 'transfer admin rights'
        earliest_member = MinistryMembership.objects.filter(ministry=ministry).order_by('join_date')[0]
        earliest_member.admin = True
        earliest_member.save()
        messages.success(request, "Since you were an admin, your rights were transferred to another member.")
    
    return HttpResponseRedirect(reverse('songs.views.profile'))

#a lot of repeated code between details for ministry and details for profile. refactor!
@login_required
def song_usage_details_ministry(request):
    """
    This handles the logic for generation of html to display usage stats for a given ccli
    """
    ministry_id = request.GET.get('ministry_id')
    ccli = request.GET.get('ccli')
    ministry = Ministry.objects.get(id=ministry_id)
    song = Song.objects.get(ccli=int(ccli))
    
    ministrysong = MinistrySong.objects.get(ministry=ministry, song=song)
    
    #get all details for every time song was done for keys
    details = MinistrySongDetails.objects.filter(ministrysong=ministrysong).order_by('-date')
    key_list = details.values_list('key', flat=True).order_by('key') #gets list of all keys done
    key_list = list(key_list) #need to convert it to list otherwise count won't work later
    total = len(key_list)
    distinct_keys = sorted(list(set(key_list)))
    key_percentage_list = [] #will be a list of tuples of form (key, percent as string)
    for distinct_key in distinct_keys:
        number = key_list.count(str(distinct_key))
        percent = number/float(total) * 100
        percent = '%.2f' % percent #convert to string and truncate to two decimal places
        key_percentage_list.append((distinct_key,percent))       
        
    start = time.clock()
    global_key_percentage_list = get_global_key_stats(song)
    elapsed = time.clock() - start
    
    #only get details of only last 5 usage instances
    #gets song context for each of the ministrysongdetails in terms of song titles
    details = details[:5]
    song_contexts = [] #list of elements of form 'songtitle (key), songtitle (key)' 
    for detail in details:
        raw_song_contexts = []
        context_string = detail.song_context
        context_list = context_string.split(',')
        for ccli_key in context_list:
            ccli_key = ccli_key.split('-')
            ccli = ccli_key[0]
            key = ccli_key[1]
            title = Song.objects.get(ccli=int(ccli)).title
            partial_str = title + ' ('+key+')'
            raw_song_contexts.append(partial_str)
        full_str = ', '.join(raw_song_contexts)
        song_contexts.append(full_str)
    
    #zip of Latest 5 ProfileSongDetails and strings of song title and key
    details_contexts = zip(details, song_contexts)
    # print song_contexts
    print elapsed
    return render(request, 'format_as_html.html', {'song':song, 'ministrysong':ministrysong, 
        'details_contexts':details_contexts, 'percentages':key_percentage_list, 
        'global_percentages':global_key_percentage_list, 'song_stats_details_ministry':True})
        
@login_required
def profile(request):
    user = request.user      
    #attempt to fix the logging in of created superuser and having no profile
    profile = Profile.objects.get(user=user)
    common_songs = ProfileSong.objects.filter(profile=profile).order_by('-times_used')[:10]
    recent_songs = ProfileSong.objects.filter(profile=profile).order_by('-last_used')[:5]
    return render(request, 'profile.html', {'profile': profile, 'common_songs':common_songs, 'recent_songs':recent_songs})

@login_required
def song_usage_details_profile(request):
    """
    This handles the logic for generation of html to display usage stats for a given ccli
    """
    user = request.user
    profile = Profile.objects.get(user=user)
    ccli = request.GET.get('ccli')
    song = Song.objects.get(ccli=int(ccli))
    profilesong = ProfileSong.objects.get(profile=profile, song=song)
    
    #get all details for every time song was done for keys
    details = ProfileSongDetails.objects.filter(profilesong=profilesong).order_by('-date')
    key_list = details.values_list('key', flat=True).order_by('key') #gets list of all keys done
    key_list = list(key_list) #need to convert it to list otherwise count won't work later
    total = len(key_list)
    distinct_keys = sorted(list(set(key_list)))
    key_percentage_list = [] #will be a list of tuples of form (key, percent as string)
    for distinct_key in distinct_keys:
        number = key_list.count(str(distinct_key))
        percent = number/float(total) * 100
        percent = '%.2f' % percent #convert to string and truncate to two decimal places
        key_percentage_list.append((distinct_key,percent))       
        
    start = time.clock()
    global_key_percentage_list = get_global_key_stats(song)
    elapsed = time.clock() - start
    
    #only get details of only last 5 usage instances
    #gets song context for each of the profilesongdetails in terms of song titles
    details = details[:5]
    song_contexts = [] #list of elements of form 'songtitle (key), songtitle (key)' 
    for detail in details:
        raw_song_contexts = []
        context_string = detail.song_context
        context_list = context_string.split(',')
        for ccli_key in context_list:
            ccli_key = ccli_key.split('-')
            ccli = ccli_key[0]
            key = ccli_key[1]
            title = Song.objects.get(ccli=int(ccli)).title
            partial_str = title + ' ('+key+')'
            raw_song_contexts.append(partial_str)
        full_str = ', '.join(raw_song_contexts)
        song_contexts.append(full_str)
    
    #zip of Latest 5 ProfileSongDetails and strings of song title and key
    details_contexts = zip(details, song_contexts)
    # print song_contexts
    print elapsed
    return render(request, 'format_as_html.html', {'song':song, 'profilesong':profilesong, 
        'details_contexts':details_contexts, 'percentages':key_percentage_list, 
        'global_percentages':global_key_percentage_list, 'song_stats_details_profile':True})
    
@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile_set.get(user=user)
    if request.method =="POST":
        form = ProfileForm(request.POST)
        # form.add_ministry(request.POST.get('ministry_code'))
        if form.is_valid():
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()
            msg = "Profile update successful!"
            messages.success(request, msg)
            #should this direct back to the edit screen or profile or success page?
            return HttpResponseRedirect(reverse('songs.views.profile'))
    else:
        form = ProfileForm(initial={'first_name': user.first_name, 'last_name': user.last_name})
    return render(request, 'edit_profile.html', {'form':form})

def contact(request):
    if request.method =='POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # print cd['subject']
            # print cd['message']
            # print cd['email']
            # send_mail(
               # cd['subject'],
               # cd['message'],
               # cd['email'],
               # ['rhsiao2@gmail.com'],
            # )
            return HttpResponseRedirect(reverse('songs.views.contact_thanks'))
    else:
        form = ContactForm(initial={'subject': 'I love your site!'})
    return render(request, 'contact_form.html', {'form':form})


def contact_thanks(request):
    return render(request, 'contact_thanks.html')

#can add test for this
def update_num_tags(request, num_songs, num_verses):
    """
    This function updates the number of song and verses tagged by the user
    Accepts the HTTP request, the number of songs, and the number of verses tagged
    """
    #gets the user object
    user = request.user
    profile = user.profile_set.get(user = user)
    num_song_tags = profile.num_song_tags + num_songs
    num_verse_tags = profile.num_verse_tags + num_verses
    user.profile_set.update(num_song_tags = num_song_tags, num_verse_tags = num_verse_tags)
    return HttpResponseRedirect(reverse('songs.views.success'))


#could factor out to be more general for sermon passages to song links
def tag_song(request, ccli):
    """
    handles tagging of individual songs from search
    """
    song = Song.objects.get(ccli=ccli) #expects single song object. get receives single object. filter gets queryset
    if request.method == "POST":
        form = BasicForm(request.POST)
        if form.is_valid():
            verse_list = request.POST.getlist('verses') #gets a list of verse IDs
            link_song_to_verses(song, verse_list)
            #updates number of tags user made.
            update_num_tags(request, 1, len(verse_list))
            return HttpResponseRedirect(reverse('songs.views.success'))
    else:
        form = BasicForm()
    return render(request, 'form.html',
        {'form':form, 'title':'Tag Song', 'header1':'Tag Song with Verses', 'song':song, 'tag_song':True})


def tag_handler(request):
    """
    handles tagging of songs from new tag songs and verses page
    """
    #something isn't going correct with tagging verses.
    if request.method == "GET":
        verse_string = request.GET.get('verses')
        ccli = request.GET.get('ccli')
        verse_groupings = verse_string.split('|')[1:]
        verse_ids = []
        for verse_group in verse_groupings:     
            verse_ids = verse_ids + parse_string_to_verses(verse_group)
        ccli = int(ccli)
        
        song = Song.objects.get(ccli=ccli)
        link_song_to_verses(song, verse_ids)
        return HttpResponseRedirect(reverse('songs.views.success')) 
    return HttpResponseRedirect(reverse('songs.views.profile'))  
        
def tag_verses(request):
    """
    handles display of tag songs and verses page. most of the logic is happening in
    tag_verses.js imported in tag_verses.html
    """
    form = BasicForm()
    return render(request, 'tag_verses.html',
        {'form':form, 'title':'Tag Verses', 'header1':'Tag Songs & Verses', 'tag_verses':True})
     
def tag_verse_song_search(request):
    #returns result of search title to tag_verse page
    # songs = Song.objects.filter(title__icontains=query).order_by('-popularity', 'title')[:5]
    # songs = SearchQuerySet().autocomplete(content_auto=query)[:10]
    if 'query' in request.GET:
        query = request.GET['query']
        songs2 = SearchQuerySet().autocomplete(content_auto=query)
        songs1 = SearchQuerySet().filter(content=query)
        songs = (songs1 | songs2)
        sug = songs.spelling_suggestion(query)
        songs = songs[:10]
        if sug == query:
            sug = None
        return render(request, 'format_as_option_list.html', {'newsongs':songs, 'sug':sug, 'query':query, 'tag_search':True})
    return HttpResponseRedirect(reverse('songs.views.success'))
    

@login_required
def add_ministry(request):
    if request.method == "POST":
        form = MinistryForm(request.POST)
        if form.is_valid():
            ministry = form.save()
            user = request.user
            profile = Profile.objects.get(user=user)
            membership = MinistryMembership(member=profile, ministry=ministry, active=True, admin=True)
            membership.save()
            msg = "%s ministry successfully created! You are the only current admin!" % ministry.name
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('songs.views.profile'))
    else:
        form = MinistryForm()
    return render(request, 'create_ministry_form.html', {'form':form})


def success(request):
    return render(request, 'success.html')
    
# def suggestion(request):
    # query = request.GET.get('query')
    # results = SearchQuerySet().filter(title__contains=query)[:5]
    # response = [r.title for r in results]
    # return HttpResponse(json.dumps(response), content_type="application/json")
    
    
def search_info(request):
    """
    handles the search by song information. takes searchinfoform and form submission by AJAX
    then returns html results as AJAX. Deals with cleaning data and CSRF. Javascript handles
    some client side validation. 
    """
    #NEED SOMETHING LIKE PREFETCH_RELATED TO REDUCE QUERIES
    if 'query' in request.GET:
        # if request.GET.get('query') =='':
            # return 
        form = SearchInfoForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            query = cd['query']
            query = query.strip() #to eliminate any spaces after the end
            #for some reason, having a space at teh end makes elasticsearch freak out
            #searching all content, authors included
            songs2 = SearchQuerySet().filter(content=query)
            songs1 = SearchQuerySet().autocomplete(content_auto=query)
            songs = (songs1 | songs2)
            songs = songs.load_all() #does this do anything?
            # songs = Song.objects.filter(title__icontains=q).order_by('-popularity', 'title')
            #could add other filter conditions here.
            
            paginator = Paginator(songs, 20)
            page = request.GET.get('page')
            try:
                songs = paginator.page(page)
            except PageNotAnInteger:
                songs = paginator.page(1)
            except EmptyPage:
                songs = paginator.page(paginator.num_pages)
            
            keylist = []
            for song in songs:
                key = get_chordpro_key(song)
                # key = song.object.original_key
                keylist.append(key)
            # print keylist
            #make option list for each song
            option_list = []
            for key in keylist:
                option_html = make_key_option_html(key)
                option_list.append(option_html)
            song_and_key_option_list = zip(songs, option_list)
            
            return render(request, 'search_results.html', {'songs': songs,'song_and_key_option_list':song_and_key_option_list, 'form':form, 'query':query, 
                'by_info':True})
        return render(request, 'search_form_title.html', {'form':form})
    form = SearchInfoForm()
    return render(request, 'search_form_title.html', {'form':form})
    

def search_all(request):
    songs = SearchQuerySet().all().order_by('title')
    form = SearchInfoForm()
    
    paginator = Paginator(songs, 20)
    page = request.GET.get('page')
    try:
        songs = paginator.page(page)
    except PageNotAnInteger:
        songs = paginator.page(1)
    except EmptyPage:
        songs = paginator.page(paginator.num_pages)
    keylist = []
    for song in songs:
        key = get_chordpro_key(song)
        # key = song.original_key
        keylist.append(key)
    # print keylist
    #make option list for each song
    
    option_list = []
    for key in keylist:
        option_html = make_key_option_html(key)
        option_list.append(option_html)
    song_and_key_option_list = zip(songs, option_list)
    
    return render(request, 'search_results.html', {'songs':songs,'song_and_key_option_list':song_and_key_option_list,  'query':'All Songs', 'form':form, 'by_title':True})
    
    
def search_verses(request):
    if 'query' in request.GET:
        # if request.GET.get('query') =='':
            # return 
        form = SearchVerseForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            query = cd['query']
            verse_ids = parse_string_to_verses(query)
            verse_ids = list(set(verse_ids))
            #gets queryset of all songs that have a verse tag in the verse search list
            songs = Song.objects.filter(verses__id__in=verse_ids).distinct() #[:2] limits to 2
            songs = songs.annotate(total_pop=Sum('songverses__SV_popularity')).order_by('-total_pop', '-popularity','title')
            songs = songs.prefetch_related('authors', 'publisher')
            
            paginator = Paginator(songs, 20)
            page = request.GET.get('page')
            try:
                songs = paginator.page(page)
            except PageNotAnInteger:
                songs = paginator.page(1)
            except EmptyPage:
                songs = paginator.page(paginator.num_pages)
            
            keylist = []
            for song in songs:
                key = get_chordpro_key(song)
                # key = song.original_key
                keylist.append(key)
            # print keylist
            #make option list for each song
            option_list = []
            for key in keylist:
                option_html = make_key_option_html(key)
                option_list.append(option_html)
            song_and_key_option_list = zip(songs, option_list)
            
            #no longer needs just songs context element
            return render(request, 'search_results_verses.html', {'songs': songs, 'song_and_key_option_list':song_and_key_option_list, 'form':form, 'query':query, 
                'by_verse':True})
        return render(request, 'search_form_verses.html', {'form':form})
    form = SearchVerseForm()
    return render(request, 'search_form_verses.html', {'form':form})

#271ms 4 queries without chord display
#778ms 4 queries with chord display
def search_songs_with_chords(request):
    song_queryset = Song.objects.exclude(chords='').prefetch_related('authors', 'publisher').order_by('-popularity')
    
    paginator = Paginator(song_queryset, 20)
    page = request.GET.get('page')
    try:
        songs = paginator.page(page)
        print 'here'
    except PageNotAnInteger:
        songs = paginator.page(1)
    except EmptyPage:
        songs = paginator.page(paginator.num_pages)

    keylist = []

    for song in songs:
        key = get_chordpro_key(song)
        keylist.append(key)
    #make option list for each song
    option_list = []
    for key in keylist:
        option_html = make_key_option_html(key)
        option_list.append(option_html)
    song_and_key_option_list = zip(songs, option_list)    

    return render(request, 'songs_with_chords.html', {'songs':songs,'song_and_key_option_list':song_and_key_option_list,  })

def song_info_pop(request, ccli):
    """
    given the ccli as a string, displays basic song information page
    no header or nav, just container
    """
    song = Song.objects.get(ccli=int(ccli))
    return render(request, 'song_info_pop.html', {'song':song})
    
#create a temp csv or something to have ccli numbers to load into database
def load_ccli_list(request):
    """
    reads csv file from dropbox containing cclis and puts them in the database
    """
    f = open('C:/dropbox/django/cclis_to_add.csv', 'r')
    contents = f.read()
    f.close()
    ccli_list = contents.split(',')
    print "%s total cclis" % len(ccli_list)
    count = 0
    for ccli in ccli_list:
        does_not_exist = check_song(ccli)
        if does_not_exist:
            print "%s does not exist" % ccli
        else:
            count += 1
    print "%d songs input" % count
    return HttpResponseRedirect(reverse('songs.views.success'))
    
def create_chord_template(request):
    """
    creates the header for the chordpro file for each song
    """
    all_songs = Song.objects.all()
    for song in all_songs:
        if song.chords:
            continue
        ccli = song.ccli
        title = song.title
        f = open('C:/dropbox/django/songs_chordpro/'+str(ccli)+'.cho', 'w')
        title_line = '{title:'+title+'}\n'
        authors_list = []
        for author in song.authors.all():
            authors_list.append(author.full_name)
        publisher_list = []
        publication_date = song.publication_year
        for publisher in song.publisher.all():
            publisher_list.append(publisher.name)
        authors_line = '{st:Words and Music by '+ ', '.join(authors_list)+'}\n'
        if publication_date == 1111:
            publishers_line = '{st:Public Domain}\n'
        else:
            publishers_line = '{st:Copyright '+str(song.publication_year)+' '+', '.join(publisher_list)+'}\n'
        ccli_line = '{st:CCLI ' + str(ccli) + '}'
        f.write(title_line.encode('utf8'))
        if len(authors_list) != 0:
            f.write(authors_line.encode('utf8'))
        f.write(publishers_line)
        f.write(ccli_line)
        f.close()

    return HttpResponseRedirect(reverse('songs.views.success'))

def get_chordpro_key(song):
    try:
        #handle different search results - whether they're querysets or searchquerysets
        if song.chords: #from queryset
            chordpro_str = song.chords
        else: #from searchqueryset
            chordpro_str = song.object.chords
        start = chordpro_str.find('{key:')
        end = chordpro_str.find('}', start)
        key_str = chordpro_str[start:end+1]
        key = key_str[5:-1]
        return key
    except:
        return ''
        
def push_setlist_decision(request):
    """
    This is the view to handle acceptance and rejection of a pushed setlist
    Accepts setlist id. If accept, archive current setlist and change pushed setlist to current
    Then change pushed setlist push to false
    If reject, delete pushed setlist and setlist songs
    """
    user = request.user
    profile = Profile.objects.get(user=user)
    current_setlist = request.session['current_setlist']
    
    if 'accept' in request.GET:
        print 'accept'
        setlist_id = request.GET.get('accept')
        #archive current setlist if there are songs in the setlist
        if current_setlist.song_order:
            current_setlist.archived = True
            current_setlist.save()
        else:#if no songs, then just delete it
            current_setlist.delete()
        accepted_setlist = Setlist.objects.get(id=setlist_id)
        accepted_setlist.pushed = False
        accepted_setlist.save()
        request.session['current_setlist'] = accepted_setlist
        #convert setlist to song-key tuple
        #can factor this out of here and 'retrieve_setlist' later!
        setlist_text = accepted_setlist.song_order
        ccli_list = setlist_text.split(',')
        temp_list = []
        for tuple_str in ccli_list:
            tuple = tuple_str.split('-')
            ccli = tuple[0]
            key = tuple[1]
            temp_list.append((ccli,key))
        request.session['setlist'] = temp_list
        num_of_songs = str(len(temp_list))

    elif 'reject' in request.GET:
        print 'reject'
        setlist_id = request.GET.get('reject')
        rejected_setlist = Setlist.objects.get(id=setlist_id)
        rejected_setlist_songs = SetlistSong.objects.filter(setlist=rejected_setlist)
        rejected_setlist_songs.delete()
        rejected_setlist.delete()
        num_of_songs = ''

    #checks if there are remaining pushed setlists and updates session variable accordingly
    pushed_setlist = Setlist.objects.filter(profile=profile, pushed=True)
    #if there are still pushed setlists, then response will be True to keep the window open
    #if no pushed setlists, then response is false to destroy window
    if pushed_setlist:
        request.session['pushed_setlist'] = pushed_setlist
        return HttpResponse(num_of_songs +'|True')
    else:
        request.session['pushed_setlist'] = None 
        return HttpResponse(num_of_songs + '|False')

        
def push_setlist(request):
    """
    This is the view to handle sharing setlists with other members of ministry
    Should be handled through AJAX i think then display success notification popup
    For now, it immediately saves new setlist and new setlists songs even if it's not accepted.
    Slower to push, faster to accept then. 
    """
    #on login signal, checks if there's a setlist that has push field as true, if so then give a message or
    #new screen asking if they want to accept. session variable??
    start = time.clock()
    current_setlist = request.session['current_setlist']
    user = request.user #CAN GET USER OBJECT DIRECTLY FROM REQUEST!!!
    current_profile = Profile.objects.get(user=user)

    #is it better to iterate through queryset or do initial load to list: list(queryset)
    current_setlist_songs = SetlistSong.objects.filter(setlist=current_setlist)
    
    ministry_id = request.GET.get('ministry_id')
    save_stats = request.GET.get('save_stats')
    #normalize jquery boolean to python boolean
    if save_stats == 'true':
        save_stats = True
    else:
        save_stats = False
        
    if save_stats: #save songs to profile will always save to profile no matter what
        for setlistsong in current_setlist_songs:
            #for each song, test if there exists a profilesong object already
            profilesong, created = ProfileSong.objects.get_or_create(profile=current_profile, song=setlistsong.song)
            profilesong.times_used = profilesong.times_used + 1
            profilesong.save()
            # print profilesong.profile, profilesong.song, profilesong.times_used
            profilesongdetails = ProfileSongDetails(profilesong=profilesong, key=setlistsong.key, 
                song_context=current_setlist.song_order)
            profilesongdetails.save()
            # print profilesongdetails.key, profilesongdetails.from_setlist
            
    if ministry_id == "none" or ministry_id == None: #Not sending to any ministries
        print 'i did not send anything'
        return HttpResponseRedirect(reverse('songs.views.success'))
    
    #only continues here if there is some ministry to send to 
    ministry = Ministry.objects.get(id=ministry_id)
    if save_stats: #sending to ministry, save songs to ministry
        for setlistsong in current_setlist_songs:
            ministrysong, created = MinistrySong.objects.get_or_create(ministry=ministry, song=setlistsong.song)
            ministrysong.times_used = ministrysong.times_used + 1
            ministrysong.save()
            # print ministrysong.ministry, ministrysong.song, ministrysong.times_used
            ministrysongdetails = MinistrySongDetails(ministrysong=ministrysong, key=setlistsong.key, 
                song_context=current_setlist.song_order)
            # print ministrysongdetails.key, ministrysongdetails.from_setlist
            ministrysongdetails.save()
            
    print 'i sent something'
    memberships = MinistryMembership.objects.filter(ministry=ministry)
    for membership in memberships:
        profile = membership.member
        #prevent setlist push to self
        if profile == current_profile:
            continue
        #copy current_setlist
        new_setlist = Setlist(profile=profile, notes=current_setlist.notes, created_by=ministry.name, 
            song_order=current_setlist.song_order, pushed=True)
        new_setlist.save()
        #copy setlist_songs
        for setlist_song in current_setlist_songs:
            new_setlist_song = SetlistSong(setlist=new_setlist, song=setlist_song.song, notes=setlist_song.notes,
                key=setlist_song.key, capo_key=setlist_song.capo_key, order=setlist_song.order)
            new_setlist_song.save()
    elapsed = time.clock() - start
    print elapsed
    return HttpResponseRedirect(reverse('songs.views.success'))
    
def setlist(request):
    """
    handles display of setlist
    """
    #common section
    try: # makes sure structure is in place if no songs are in setlist and not logged in
        setlist_as_list = request.session['setlist'] #just a list of tuples
    except:
        setlist_as_list = []
        request.session['setlist'] = []
    keylist = []
    song_list = [] #list of Song objects
    
    #this provides all basic functionality of setlist - key memory, song information and order (non-persistent)
    for ccli_key_tuple in setlist_as_list:
        song = Song.objects.get(ccli=int(ccli_key_tuple[0]))
        song_list.append(song)
        key = ccli_key_tuple[1]
        keylist.append(key)
    
    option_list = []
    for key in keylist:
        option_html = ''
        if key: # if key is "None" means no chords, means empty option_html
            option_html = make_key_option_html(key)
        option_list.append(option_html)
    
    #authenticated section
    #gets more functionality: notes for setlist, persistent order, created by, archive, order in song, capo key, song notes
    if request.user.is_authenticated():
        user = request.user
        profile = Profile.objects.get(user=user)
        ministries = MinistryMembership.objects.filter(member=profile)
        current_setlist = request.session['current_setlist'] #setlist object
        setlistsong_list = [] #list of SetlistSongs
        profilesong_list = []
        for song in song_list:
            setlistsong = SetlistSong.objects.get(setlist=current_setlist, song=song)
            setlistsong_list.append(setlistsong)
            #get the last time this song was done through profilesong
            try:
                profilesong = ProfileSong.objects.get(profile=profile, song=song)
                profilesong_list.append(profilesong)
            except:
                profilesong_list.append(None)

        print profilesong_list
        #final packaging dependent on logged in or not, logged in will give setlist_song_option_list, not logged in song_option_list
        song_optionlist = []
        song_optionlist_setlistsong = zip(song_list, option_list, setlistsong_list, profilesong_list)
        #get profile and all ministries person is a part of
        
    else:        
        song_optionlist_setlistsong = []
        song_optionlist = zip(song_list, option_list)
        
    #refactor this since i don't need both song_optionlist_setlistsong and song_optionlist    
    if request.user.is_authenticated():
        return render(request, 'setlist.html', {'title':'My Setlist', 
            'song_optionlist_setlistsong':song_optionlist_setlistsong, 'current_setlist':current_setlist,
            'ministries':ministries})
    else:
        return render(request, 'setlist.html', {'title':'My Setlist', 'song_optionlist':song_optionlist})
        

def update_setlist(request):
    """
    updates session variable to include or remove song from setlist
    accepts get parameters 'add' or 'remove' and 'ccli'
    'ccli' can be a single or comma separated strings
    """
    #use ajax get parameter for add or remove
    #check if a setlist exists. if not create empty list
    #can setlist be a list of tuples where first element of tuple is ccli, second is key
    #setlist cannot be dictionary alone since it does not preserve order
    temp_list = request.session.get('setlist', [])
    
    #archived session flag is used to indicate whether a setlist has already been archived
    #to prevent archive button from being active upon page reload
    #need to handle changes to setlist through setlist page with ajax
    request.session['archived'] = False #any change in the setlist will set flag for false

    ccli = request.GET.get('ccli')
    reset_ccli = None #flag for determining whether to return "success" page or send to format as option list
    
    if request.user.is_authenticated(): #get all relevant variables up front?
        user = request.user
        profile = Profile.objects.get(user=user)
        current_setlist = request.session['current_setlist']
        # setlist_as_list = request.session['setlist']
    
    if ccli == 'clear':
        print 'clear'
        if request.user.is_authenticated():
            setlist_as_list = request.session['setlist']
            # order_string = convert_setlist_to_string(setlist_as_list)
            # current_setlist.song_order = order_string #probably don't need to do this 
            # #since it will be saved on all refreshes
            # current_setlist.archived = True
            # current_setlist.save()
                
            current_setlist.delete()
            new_setlist = Setlist(profile=profile, archived=False)       
            new_setlist.save()
            request.session['current_setlist'] = new_setlist
            # new_setlist_id = new_setlist.id
        request.session['setlist'] = []
        
    elif 'add' in request.GET:
        #not logged in: update 'setlist' session variable
        #logged in: update 'setlist' session variable, create setlistsong, update setlist song_order
        
        print 'add'
        #common section
        song = Song.objects.get(ccli=int(ccli))
        key = request.GET.get('key')
        if not key: #if no chords therefore no key
            key = 'A' #just a filler chord that won't be seen or used by anyone
        if ccli not in temp_list:
            temp_list.append((ccli, key))
            request.session['setlist'] = temp_list
            
        #authenticated section
        if request.user.is_authenticated():
            setlist_song = SetlistSong(setlist=current_setlist, song=song, key=key)
            setlist_song.save()
            order_string = convert_setlist_to_string(temp_list)
            current_setlist.song_order = order_string
            current_setlist.save()
            
            
    elif 'remove' in request.GET:
        #not logged in: update 'setlist' session variable
        #logged in: update 'setlist' session, find SetlistSong instance to delete, update setlist song_order
        
        print 'remove'
        #common section
        #gets the index of the list that has tuple with first element being ccli, returns as list
        index_as_list = [index for index, tuple in enumerate(temp_list) if tuple[0]==ccli] 
        if index_as_list:
            temp_list.pop(index_as_list[0])
            request.session['setlist'] = temp_list
                    
        #authenticated section
        if request.user.is_authenticated():
            song = Song.objects.get(ccli=int(ccli))
            SetlistSong.objects.filter(setlist=current_setlist, song=song).delete()
            order_string = convert_setlist_to_string(temp_list)
            current_setlist.song_order = order_string
            current_setlist.save()
 
            
    elif 'reorder' in request.GET: #in the case of reordering
        #not logged in: update setlist session
        #logged in: update setlist session, update song_order in current setlist
        
        print 'reorder'
        #common section
        csv_ccli = ccli[:-1] #sent ccli csv must be in form ccli-key,ccli-key
        ccli_list = csv_ccli.split(',')
        temp_list = []
        for ccli_and_key in ccli_list:
            ccli_and_key = ccli_and_key.split('-')
            ccli = ccli_and_key[0]
            key = ccli_and_key[1]
            temp_list.append((ccli,key))
        request.session['setlist'] = temp_list #saves new setlist
        
        #authenticated section
        if request.user.is_authenticated():
            order_string = convert_setlist_to_string(temp_list)
            current_setlist.song_order = order_string
            current_setlist.save()
      
    elif 'setlist-notes' in request.GET:
        print 'setlist-notes'
        #will only be available for logged in users
        cancel = request.GET.get('cancel')
        if cancel == 'true':
            print 'canceled'
            notes = current_setlist.notes
        else:
            notes = request.GET.get('setlist-notes')
            notes = notes.strip()
        current_setlist.notes = notes
        current_setlist.save()
        return HttpResponse(notes)
    
    elif 'song-notes' in request.GET:
        print 'song-notes'
        cancel = request.GET.get('cancel')
        song = Song.objects.get(ccli=int(ccli))
        setlist_song = SetlistSong.objects.filter(song=song, setlist=current_setlist)
        if cancel == 'true':
            notes = setlist_song[0].notes
            print 'canceled'
        else:
            notes = request.GET.get('song-notes')
            #don't want trailing new lines or spaces. also don't want notes with just spaces
            notes = notes.strip()
        setlist_song.update(notes=notes)
        return HttpResponse(notes)
        
    elif 'archive' in request.GET:
        #only available if logged in
        #OLD- will save copy of current setlist with archive=true and all ssetlistsongs, everything else stays the same
        #CURRENT - will update current setlist to archived and create new empty setlist.
        request.session['archived'] = True
        # notes = current_setlist.notes
        # created_by = current_setlist.created_by
        # song_order = current_setlist.song_order 
        # new_setlist = Setlist(profile=profile, notes=notes, created_by=created_by, 
            # song_order=song_order, archived=True)
        # new_setlist.save()
        
        # setlist_songs = list(SetlistSong.objects.filter(setlist=current_setlist)) #forces evaluation into list
        # for setlist_song in setlist_songs:
            # song = setlist_song.song
            # song_notes = setlist_song.notes
            # song_key = setlist_song.key
            # capo_key = setlist_song.capo_key
            # order = setlist_song.order
            # new_setlistsong = SetlistSong(setlist=new_setlist, song=song, notes=song_notes, key=song_key,
                # capo_key=capo_key, order=order)
            # new_setlistsong.save()
        current_setlist.archived = True
        current_setlist.save()
        new_setlist = Setlist(profile=profile, archived=False)
        new_setlist.save()
        request.session['setlist'] = []
        request.session['current_setlist'] = new_setlist

    elif 'delete' in request.GET:
        #only available if logged in
        setlist_id = request.GET.get('delete')
        setlist_to_delete = Setlist.objects.get(pk=int(setlist_id))
        print 'DELETED'
        setlist_to_delete.delete() #will this delete all related fields? setlistsongs? YES!
    
    elif 'reuse-setlist' in request.GET:
        #only available if logged in
        print 'reused'
        setlist_id = request.GET.get('reuse-setlist')
        if current_setlist.song_order: #if there are songs in setlist, archive it
            current_setlist.archived = True
            current_setlist.save()
        else: #if no songs in setlist, delete it
            current_setlist.delete()

        reuse_setlist = Setlist.objects.get(pk=int(setlist_id))
        reuse_setlist.archived = False
        reuse_setlist.save()
        setlist_text = reuse_setlist.song_order
        if setlist_text: #if the setlist currently has songs
            ccli_list = setlist_text.split(',')
            temp_list = []
            for tuple_str in ccli_list:
                tuple = tuple_str.split('-')
                ccli = tuple[0]
                key = tuple[1]
                temp_list.append((ccli,key))
            request.session['setlist'] = temp_list
        else:
            request.session['setlist'] = []
        request.session['current_setlist'] = reuse_setlist
    
    elif 'ccli-keychange' or 'reset' in request.GET:
        #common section
        reset_flag = False
        if 'reset' in request.GET: #if reset button was pressed to reset key
            reset_flag = True
            keychange_ccli = request.GET.get('reset')
            song = Song.objects.get(ccli=keychange_ccli)
            new_key = get_chordpro_key(song)
            print 'reset'
        elif 'ccli-keychange' in request.GET:
            ccli_key = request.GET.get('ccli-keychange') # string of form ccli-key
            ccli_key = ccli_key.split('-')
            keychange_ccli = ccli_key[0]
            print 'keychange'
            new_key = ccli_key[1]
            song = Song.objects.get(ccli=keychange_ccli)

        csv_ccli = ccli[:-1]
        ccli_list = csv_ccli.split(',')
        temp_list = []
        for ccli_and_key in ccli_list:
            ccli_and_key = ccli_and_key.split('-')
            ccli = ccli_and_key[0]
            key = ccli_and_key[1]
            if ccli == keychange_ccli:
                key = new_key #replaces key passed by js with key found in chordpro
            temp_list.append((ccli,key))
        request.session['setlist'] = temp_list #saves new setlist       
        
        #authenticated section:
        if request.user.is_authenticated():
            SetlistSong.objects.filter(setlist=current_setlist, song=song).update(key=new_key)
            order_string = convert_setlist_to_string(temp_list)
            current_setlist.song_order = order_string
            current_setlist.save()            

        if reset_flag: #this is to update the option list after reset is hit so it reflects new key
            return render(request, 'format_as_option_list.html', {'options':make_key_option_html(new_key), 'key_options':True})
    return HttpResponseRedirect(reverse('songs.views.success'))
    
def modal_archive_setlist(request):
    id = request.GET.get('setlist_id')
    setlist = Setlist.objects.get(pk=int(id))
    ccli_key_list = setlist.song_order.split(',')
    setlist_songs = []
    
    for ccli_key_string in ccli_key_list:
        ccli_key = ccli_key_string.split('-')
        ccli = ccli_key[0]
        song = Song.objects.get(ccli=int(ccli))
        setlist_song = SetlistSong.objects.get(setlist=setlist, song=song)
        setlist_songs.append(setlist_song)
        
    return render(request, 'format_as_option_list.html', {'archive_setlist':setlist, 'setlist_songs':setlist_songs})

        
@login_required
def display_archived_setlist(request):
    """
    Handles the display of archived setlists
    """
    user = request.user
    profile = Profile.objects.get(user=user)
    archived_setlists = Setlist.objects.filter(profile=profile, archived=True).order_by('date')
    
    paginator = Paginator(archived_setlists, 10)
    page = request.GET.get('page')
    
    try:
        archived_setlists = paginator.page(page)
    except PageNotAnInteger:
        archived_setlists = paginator.page(1)
    except EmptyPage:
        archived_setlists = paginator.page(paginator.num_pages)
    
    #setlist_setlistsong_tuples [(setlist,[setlistsong,setlistsong]), (setlist,[setlistsong,setlistsong])]
    # setlist_setlistsong_tuples = []
    setlists = []
    title_values = []
    
    for setlist in archived_setlists:
        ccli_key_list = setlist.song_order.split(',')
        setlist_song_list = []
        setlist_string = ''
        for ccli_key_string in ccli_key_list:
            ccli_key = ccli_key_string.split('-')
            ccli = ccli_key[0]
            key = ccli_key[1]
            song = Song.objects.get(ccli=int(ccli))
            title = song.title
            setlist_string += title+' ('+key+'), '
        title_values.append(setlist_string[:-2])
        
        
    archived_and_titles = zip(archived_setlists, title_values)
    return render(request, 'archived_setlist.html', { 'archived_setlists':archived_setlists, 'archived_and_titles':archived_and_titles})
          
    
def push_chords_to_database(request):
    """
    loads contents of cho files in the dropbox folder songs_chordpro_checkedwguitar 
    into database. 
    """
    #should add function to load song info first if ccli doesn't exist in database
    file_list = os.listdir('D:/dropbox/django/songs_chordpro_checkedwguitar/')
    ccli_list = []
    count = 0
    for file_name in file_list:
        ccli = file_name[:-4]
        # ccli_list.append(ccli)

        song_as_qs = Song.objects.filter(ccli=int(ccli))
        if song_as_qs.count() == 0: #if no song exists in database with that ccli look it up from ccli
            check_song(ccli)
        f = open('D:/dropbox/django/songs_chordpro_checkedwguitar/' + ccli + '.cho', 'r')
        chords_from_cho = f.read()
        song_as_qs.update(chords=chords_from_cho)
        f.close()
        count += 1
    print count
    return HttpResponseRedirect(reverse('songs.views.success'))

    

    
#a lot of repeated code here. implement dry? can one day factor out a lot of the html 
#generation into separate function. Still can have two different functions to handle
#the vastly different requests.        
def modal_chord_html(request):
    """
    This is for sending html version of chords as http response
    Requires that ajax send ccli and transpose_value_str = the final key desired
    Will send html to be put into modal for use in search results pages.
    """
    indexes = {
        'Ab': 0,
        'A': 1,
        'Bb':2,
        'B':3,
        'Cb':3,
        'C':4,
        'C#':5,
        'Db':5,
        'D': 6,
        'D#': 7,
        'Eb': 7,
        'E':8,
        'F':9,
        'F#':10,
        'Gb':10,
        'G':11,
        'G#':0
        }
    ccli = int(request.GET.get('ccli'))
    transpose_final_key = request.GET.get('transpose_value_str')
    song = Song.objects.get(ccli=int(ccli))
    chord_stream = song.chords
    if not chord_stream:
        return
    lines = chord_stream.split('\n')
    
    html = ''
    emphasis = False
    for line in lines:
        #handle directives first
        if '{' in line:
            if '{title:' in line:
                html += '<h3>'+line[7:-1]+'</h3>'
                continue
            elif '{st:' in line:
                html += '<h5>'+line[4:-1]+'</h5>'
                continue
            elif '{key:' in line:
                original_key = line[5:-1]
                continue
            elif '{start_of_chorus}' in line:
                emphasis = True
                continue
            elif '{end_of_chorus}' in line:
                emphasis = False
                continue
        #no directive in line
        else:
            if '[' in line:
                separations = []
                separations = line.split('[')
                chords = []
                lyrics = []
                # go through each section and get the chord and lyric pairings
                for section in separations:
                    if section == '':
                        continue
                    #if no chord, still append nothing to chords
                    elif ']' not in section:
                        lyrics.append(section)
                        chords.append('')
                        continue 
                    chordlyric = section.split(']')
                    chords.append(chordlyric[0])
                    lyrics.append(chordlyric[1])
                html += '<table>'
                if emphasis:
                    html += '<tr class="emphasis">'
                else:
                    html += '<tr>'

                transposed_chords = []
                
                if 'm' in original_key:
                    # minor = True
                    original_root = original_key[:-1]
                    final_root = transpose_final_key[:-1]
                else:
                    # minor = False
                    original_root = original_key
                    final_root = transpose_final_key
                original_key_index = indexes[original_root]
                final_key_index = indexes[final_root]
                
                # original_key_index = indexes[original_key]
                # final_key_index = indexes[transpose_final_key]
                transpose_step = final_key_index - original_key_index
                    
                for chord in chords:
                    if chord == '':
                        transposed_chords.append('')
                        continue
                    transposed_chord = transpose(chord, transpose_step, original_key, transpose_final_key)
                    transposed_chords.append(transposed_chord)

                for chord in transposed_chords:
                    html += '<td>'+chord+'</td>'
                    
                if emphasis:
                    html += '</tr><tr class="emphasis">'
                else:
                    html += '</tr><tr>'
                    
                for lyric in lyrics:
                    html += '<td>'+lyric+'</td>'
                    
                html += '</tr></table>'

            else:
                html += '<br>' + line
    #adding another br so last line doesn't get cut off
    html += '<br>'
    return HttpResponse(html)
    
    
    
    
    
    
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------   
    
#disabled in urls: no need for this anymore since no popup add stuff
def handlePopAdd(request, addForm, field):
    if request.method == "POST":
        form = addForm(request.POST)
        if form.is_valid():
            try:
                newObject = form.save()
            except forms.ValidationError, error:
                newObject = None
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                        (escape(newObject._get_pk_val()), escape(newObject)))
    else:
        form = addForm()
    pageContext = {'form': form, 'field': field}
    return render(request,"pop_up_form.html", pageContext)   
    
#disabled in urls: no need to manually add        
@login_required
def add_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('songs.views.success'))
    else:
        form = AuthorForm()
    return render(request, 'form.html', {'form':form, 'title':'Add Author', 'header1':'Add Author'})
    
#disabled in urls:no need to manually add
@login_required
def add_author_pop(request):
    return handlePopAdd(request, AuthorForm, 'author')

#disabled in urls: no need to manually input publisher
@login_required
def add_publisher(request):
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('songs.views.success'))
    else:
        form = PublisherForm()
    return render(request, 'form.html', {'form':form, 'title':'Add Publisher', 'header1':'Add Publisher'})
#disabled in urls: no longer needed, no manual loading
@login_required
def add_publisher_pop(request):
    return handlePopAdd(request, PublisherForm, 'publisher')    
    
#disabled in urls: one time utility. no need to add more books
@login_required
@permission_required('is_staff', raise_exception=True)
def add_book(request):
    if request.method == "POST":
        if request.POST.get('name'): #if post has name field indicating adding book not chapters
            form = BookForm(request.POST)
            if form.is_valid():
                name = request.POST.get('name', '')
                num_chapters = request.POST.get('num_chapters')
                order_index = request.POST.get('order_index')
                book = Book(name=name, num_chapters=num_chapters, order_index=order_index)
                book.save()
                request.session['book'] = book
                i = 1
                request.session['chapter_list'] = []
                #populate chapters based on num of chaps in book
                while i <= int(num_chapters):
                    chapter_num = i
                    num_verses=10
                    chapter = Chapter(book=book, number=chapter_num, num_verses = num_verses)
                    request.session['chapter_list'].append(chapter)
                    chapter.save()
                    i = i + 1
                formChap = BookChapterForm(chapter_list = request.session['chapter_list'])
                return render(request, 'form.html', {'form':formChap,'book': book})
        #handles chapter list subscreen
        else: #if post is only chapters
            form = BookChapterForm(request.POST, chapter_list=request.session['chapter_list'])
            if form.is_valid():
                for chapter in request.session['chapter_list']:
                    chapter.num_verses = request.POST.get('Verses in chapter %s' % chapter.number)
                    chapter.save()
                    j = 1
                    while j <= int(chapter.num_verses):
                        verse_num = j
                        verse = Verse(book=request.session['book'], chapter=chapter, number=verse_num)
                        verse.save()
                        j = j + 1
            return HttpResponseRedirect(reverse('songs.views.success'))

    else:
        form = BookForm()
    return render(request, 'form.html', {'form':form, 'title':'Add Book', 'header1':'Add Book'})
    
 #disabled in urls: old way of handling tag verses   
@login_required
def chapters_in_book(request, book_id):
    book = Book.objects.filter(order_index=book_id)
    chapters = Chapter.objects.filter(book = book).order_by('id')
    return render(request,"format_as_option_list.html", {'chapters': chapters})
#disabled in urls: old way of handling tag verses
@login_required
def verses_in_chapter(request, chapter_id):
    chapter = Chapter.objects.filter(id=chapter_id)
    verses = Verse.objects.filter(chapter = chapter)
    return render(request,"format_as_option_list.html", {'verses': verses})
    
#disabled in urls: old way of handling tag verses
@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, "format_as_option_list.html", {'books': books})
    
#disabled in urls: populates option pull down list for old way of tagging
@login_required
def alpha(request):
    alphabet = 'ABCDBEFGHIJKLMNOPQRSTUVWXYZ'
    return render(request, "format_as_option_list.html", {'alpha': alphabet})
    
#disabled in urls: this was for getting all songs populated in old way of tagging
def songs_in_alpha(request, alpha):
    # if alpha == "all":
        # songs = Song.objects.all().order_by('title')
    if alpha=="num":
        #pretty bad way to get all songs starting with a number
        songs = Song.objects.filter(
            Q(title__startswith='0')|
            Q(title__startswith='1')|
            Q(title__startswith='2')|
            Q(title__startswith='3')|
            Q(title__startswith='4')|
            Q(title__startswith='5')|
            Q(title__startswith='6')|
            Q(title__startswith='7')|
            Q(title__startswith='8')|
            Q(title__startswith='9')
            ).order_by('title')
    else:
        #should this be alphabetical or by popularity??
        songs = Song.objects.filter(title__istartswith=alpha).order_by('title')
    return render(request, "format_as_option_list.html", {'songs':songs}) 
    
#disabled in urls: old way of doing add songs. manually enter data. bad
@login_required
def add_song(request):
    if request.method == "POST":
        form = SongForm(request.POST)
        if form.is_valid():
            # saves form. verses not included in form
            song = form.save()
            verse_list = request.POST.getlist('verses')
            # must handle verse tagging individually
            link_song_to_verses(song, verse_list)
            #song popularity defaults to 2 for new song with verses. Is this oK??
            #default is 1 but link song to verses function adds 1 to it.
            update_num_tags(request, 1, len(verse_list))
            return HttpResponseRedirect(reverse('songs.views.success'))
    else:
        form = SongForm()
    return render(request, 'form.html', {'form':form, 'title':'Add Song','header1':'Add Song', 'add_song':True})

    
# def new_book(request, query):
    # books = SearchQuerySet().autocomplete(content_auto=query).models(Book)[:1]
    # return render(request, 'format_as_option_list.html', {'newbooks':books, 'query':query})
    
# def search_info(request):
    # #displays search by info page
    # return render(request, 'search_form_title.html')
    
# def search_info_results(request):
    # #could make this ajax. load on single page
    # print 'got here'
    # if 'query' in request.GET:
        # query = request.GET['query']
        # #searching all content, authors included
        # songs2 = SearchQuerySet().filter(content=query)
        # songs1 = SearchQuerySet().autocomplete(content_auto=query)
        # songs = (songs1 | songs2)
        # # songs = Song.objects.filter(title__icontains=q).order_by('-popularity', 'title')
        # #could add other filter conditions here.
        # return render(request, 'format_as_option_list.html', {'songs': songs, 'query':query, 'by_info':True})
    # return HttpResponseRedirect(reverse('songs.views.success')) 
    
# def old_search_title(request):
    # #could make this ajax. load on single page
    # errors = []
    # if 'q' in request.GET:
        # q = request.GET['q']
        # if not q:
            # errors.append('Enter a search term.')
        # if len(q) > 40:
            # errors.append('Please enter at most 40 characters.')
        # else:
            # #searching all content, authors included
            # songs2 = SearchQuerySet().filter(content=q)
            # songs1 = SearchQuerySet().autocomplete(content_auto=q)
            # songs = (songs1 | songs2)
            # # songs = Song.objects.filter(title__icontains=q).order_by('-popularity', 'title')
            # #could add other filter conditions here.
            # return render(request, 'search_results.html', {'songs': songs, 'query':q, 'by_title':True})
    # return render(request, 'search_form_title.html', {'errors':errors,})
    
# def search_verses(request):
    # """
    # displays verse search page
    # """
    # return render(request, 'search_form_verses.html')
        
# def search_verses_results(request):
    # """
    # handles background logic for searching verses
    # """
    # if 'verses' in request.GET:
        # verse_string = request.GET.get('verses')
        # # This is for if you want to "add" multiple groupings of verses
        # # verse_groupings = verse_string.split('|')[1:]
        # # verse_ids = []
        # # for verse_group in verse_groupings:     
            # # verse_ids = verse_ids + parse_string_to_verses(verse_group)
        # #eliminates duplicate verses
        # verse_ids = parse_string_to_verses(verse_string)
        # verse_ids = list(set(verse_ids))
        # #gets queryset of all songs that have a verse tag in the verse search list
        # songs = Song.objects.filter(verses__id__in=verse_ids).distinct() #[:2] limits to 2
        # songs = songs.annotate(total_pop=Sum('songverses__SV_popularity')).order_by('-total_pop', '-popularity','title')


        # return render(request, 'format_as_option_list.html', {'songs':songs, 'query':verse_string, 'by_verse':True})
    # return HttpResponseRedirect(reverse('songs.views.success'))
    
# def search_verses(request):
    # """
    # this adds functionality to search songs based on verse tags
    # finds a list of songs that has at least one versetag corresponding to one that was selected
    # """
    # errors = []
    # if 'verses' in request.GET:
        # verse_ids = request.GET.getlist('verses') #gets a list of verse ids
        # if not verse_ids:
            # errors.append('Select at least one verse.')
        # else:
            # #eliminates duplicate verses
            # verse_ids = list(set(verse_ids))
            # #gets queryset of all songs that have a verse tag in the verse search list
            # songs = Song.objects.filter(verses__id__in=verse_ids).distinct() #[:2] limits to 2
            # songs = songs.annotate(total_pop=Sum('songverses__SV_popularity')).order_by('-total_pop', '-popularity','title')

            # verse_strings = parse_verseids_to_string(verse_ids)

            # return render(request, 'search_results.html', {'songs':songs, 'query':verse_strings, 'by_verse':True})
    # return render(request, 'search_form_verses.html', {'errors':errors,})
       
    
# def old_tag_verses(request):
    # """
    # handles core functionality of selecting group of verses and group of songs and tagging each
    # song with each verse
    # """
    # if request.method == "POST":
        # form = BasicForm(request.POST)
        # if form.is_valid():
            # verse_list = request.POST.getlist('verses')
            # song_list = request.POST.getlist('songs')
            # song_list = set(song_list)
            # for song_id in song_list:
                # song = Song.objects.get(ccli=song_id)
                # link_song_to_verses(song, verse_list)
            # update_num_tags(request, len(song_list), len(verse_list))
            # return HttpResponseRedirect(reverse('songs.views.success'))
    # else:
        # form = BasicForm()
    # return render(request, 'form.html',
        # {'form':form, 'title':'Tag Verses', 'header1':'Tag Songs & Verses', 'tag_verses':True})
        
#this is only needed if i use the current method of verse tagging. select box returning list of ids
#problem if verse ids are not in order. what happens if i add a new verse that was missed. order of ids
#no longer reflects absolute ordering of verses. can't rely on the fact that verses in order have sequential ids
# def parse_verseids_to_string(verse_id_list):
    # """
    # receives a list of verse ids
    # returns a list of strings representing each grouping of verses
    # """
    # #makes surch all verse ids in list are integers
    # verse_id_list = map(int, verse_id_list)
    # verse_id_list.sort()
    # seq_lists = []
    # verse_strings = []
    # #this magic gets sequential lists and appends it to seq_lists (list of lists)
    # for k, g in groupby(enumerate(verse_id_list), lambda (i,x):i-int(x)):
        # seq_lists.append(map(itemgetter(1), g))
        
    # for verse_list in seq_lists:
        # #algorithm: get book, chapter and number of first verse in range
        # #get last book, chapter, and number in range. check to see 
        # #whether book and/or chapters are equal. output string based on results
        # first_verse = Verse.objects.get(id=verse_list[0])
        # start_book = first_verse.book
        # start_chapter = first_verse.chapter
        # start_versenum = first_verse.number
        
        # base_string = str(start_chapter) +':' + str(start_versenum)
        # #single verse case
        # if len(verse_list) == 1:
            # verse_strings.append(base_string)
        # #multiple verse case
        # else:
            # last_verse = Verse.objects.get(id=verse_list[-1])
            # end_book = last_verse.book
            # end_chapter = last_verse.chapter
            # end_versenum = last_verse.number
            # #are all verses within same chapter?
            # if start_chapter == end_chapter:
                # verse_strings.append(base_string + ' - ' + str(end_versenum))
            # #different chapter
            # else:
                # #are all verses in the same book?
                # if start_book == end_book:
                    # verse_strings.append(base_string + ' - ' + str(end_chapter.number) +':'+str(end_versenum))
                # #different book
                # else:
                    # verse_strings.append(base_string + ' - ' + str(end_chapter) +':'+str(end_versenum))
    # return verse_strings
    
    
"""
MOVED TO FUNCTIONS.PY
"""
#add tests for different query conditions to make sure returns correct # of verses
# def parse_string_to_verses(query):
    # """
    # receives as input, a string query in the form (book chapter:verses)
    # or (book chapter:verse-verse).
    # returns a list of verse ids
    # """
    # book_list = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 
        # 'joshua', 'judges', 'ruth', '1 samuel', '2 samuel', '1 kings', '2 kings', 
        # '1 chronicles', '2 chronicles', 'ezra', 'nehemiah', 'esther', 'job', 
        # 'psalm', 'proverbs', 'ecclesiastes', 'song of solomon', 'isaiah', 
        # 'jeremiah', 'lamentations', 'ezekiel', 'daniel', 'hosea', 'joel', 'amos', 
        # 'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk', 'zephaniah', 'haggai', 
        # 'zechariah', 'malachi', 'matthew', 'mark', 'luke', 'john', 'acts', 'romans', 
        # '1 corinthians', '2 corinthians', 'galatians', 'ephesians', 'philippians', 
        # 'colossians', '1 thessalonians', '2 thessalonians', '1 timothy', '2 timothy',
        # 'titus', 'philemon', 'hebrews', 'james', '1 peter', '2 peter', '1 john', 
        # '2 john', '3 john', 'jude', 'revelation']
        
    # query = query.strip().lower()
    # #makes sure query is not empty string (no scripture reference)
    # if query == '':
        # return []
    # #currently doesn't allow commas
    # if ',' in query:
        # print query
        # return []
    # #check if book name has ordinal, find location of first number
    # if query[0] in '123':
        # match = re.search("\d", query[2:])
        # loc_ord = 2
    # else:
        # match = re.search("\d", query)
        # loc_ord = 0
        
    # #if there is no number(just book)
    # #get_close matches takes input query, a list of possible options, number of
    # #results to return and a difference factor and returns a list of close matches.
    # #.42 needed for rev. match
    # if not match:
        # book = get_close_matches(query, book_list, 1, 0.4)[0]
        # chapver = []
    # else:
        # num_loc = match.start() + loc_ord
        # book = get_close_matches(query[0:num_loc].strip(), book_list, 1, 0.4)[0]
        # chapver = query[num_loc:].split(':')
    # #if there is nothing after the book name, get the whole book
    # if not chapver:
        # qs = Verse.objects.filter(book__name__iexact=book)
        # verse_list = qs.values_list('id', flat=True)
        # return list(verse_list)
    # else:
        # chapter = chapver[0].strip()
    # verse_list = []
    # #this checks whether  there is verse designation. if not, get queryset of whole chapter
    # if len(chapver) == 1:
        # #check if this has '-'. if so, get multiple chapters
        # if '-' in chapter:
            # chapter_list = chapter.split('-')
            # start_chapter = int(chapter_list[0])
            # end_chapter = int(chapter_list[1])
            # middle_chapters = range(start_chapter+1, end_chapter)
        
            # begin_chap_verses = Verse.objects.filter(
                # book__name__iexact=book, chapter__number=start_chapter,)
                
            # end_chap_verses = Verse.objects.filter(
                # book__name__iexact=book, chapter__number=end_chapter)
                
            # mid_chap_verses = Verse.objects.none()
            # for mid_chap in middle_chapters:
                # verse_qs = Verse.objects.filter(
                    # book__name__iexact=book, chapter__number=mid_chap)
                # mid_chap_verses = mid_chap_verses | verse_qs
                
            # all_verses_qs = begin_chap_verses | mid_chap_verses | end_chap_verses
            # verse_list = all_verses_qs.values_list('id', flat=True)

        # else:
            # chapter = int(chapter)
            # qs = Verse.objects.filter(book__name__iexact=book, chapter__number=chapter)
            # verse_list = qs.values_list('id', flat=True)
    # #this checks if string spans multiple chapters
    # elif len(chapver) == 3:
        # #example isaiah 52:13-53:12
        # #[52, 13-53, 12]
        # start_chapter = int(chapter)
        # mid = chapver[1].split('-')
        # #deals with a/b designation in verses for example verse 14b, just translate to 14
        # #enough to just take off last char?
        # #see force_int method
        # start_verse = force_int(mid[0])
        # end_chapter = int(mid[1])
        # end_verse = force_int(chapver[2])

        # middle_chapters = range(start_chapter+1, end_chapter)
        
        # begin_chap_verses = Verse.objects.filter(
            # book__name__iexact=book, chapter__number=start_chapter,
            # number__gte=start_verse)
            
        # end_chap_verses = Verse.objects.filter(
            # book__name__iexact=book, chapter__number=end_chapter,
            # number__lte=end_verse)
            
        # mid_chap_verses = Verse.objects.none()
        # for mid_chap in middle_chapters:
            # verse_qs = Verse.objects.filter(
                # book__name__iexact=book, chapter__number=mid_chap)
            # mid_chap_verses = mid_chap_verses | verse_qs
            
        # all_verses_qs = begin_chap_verses | mid_chap_verses | end_chap_verses
        # #to get value of specific field in all elements within queryset use
        # #qs.value() for dict, or qs.values_list('fieldname', flat=True) for list
        # verse_list = all_verses_qs.values_list('id', flat=True)
    # else: #if verse designation, then parse the verse string
        # verses = chapver[1]
        # chapter = int(chapter)
        # #if there's a dash in verses, get beginning and end number then get all verses in between
        # if '-' in verses:
            # startend = verses.split('-')
            # start = force_int(startend[0])
            # end = force_int(startend[1])
            # qs = Verse.objects.filter(book__name__iexact=book,chapter__number=chapter,
                # number__gte=start).filter(number__lte=end)
            # verse_list = qs.values_list('id', flat=True)
        # else:
            # verses = force_int(verses)
            # verse_object = Verse.objects.get(book__name__iexact=book, chapter__number=chapter, number=verses)
            # verse_list.append(verse_object.id)
    # verse_list = list(verse_list)
    # return verse_list
    
# def test_parsable(query):
    # """
    # function that receives as in put a query and returns true if parsable and false if not
    # """
    # try:
        # verse_list = parse_string_to_verses(query)
        # if len(verse_list) > 0:
            # parsable = True
        # else:
            # parsable = False
    # except:
        # parsable = False
    # return parsable
    
# def check_song(ccli):
    # """
    # checks for song with ccli# in database. if not in database, will get song info
    # from songselect in ccli. if song exists, doesn't do anything. 
    # returns does_not_exist as either true or false
    # """
    # does_not_exist = False
    # #checks if song is already in database
    # try:
        # song = Song.objects.get(ccli=int(ccli))
    # except:
        # #if song not in database, try to get song_info from url
        # try:
            # url = 'https://us.songselect.com/songs/' + ccli
            # song_info = get_song_info_from_link(url)
            # save_songs_from_dict(song_info)
        # #if ccli is wrong or something, then return does_not_exist as true
        # except:
            # does_not_exist = True
    # return does_not_exist

# def force_int(entry):
    # """
    # accepts string entry with numbers and/or characters. If entry only contains
    # numbers, will convert it to int then return value.
    # If entry contains characters, will force remove characters then convert remains to int
    # """
    # try:
        # result = int(entry)
    # except:
        # temp = re.sub(r'\D', '', entry)
        # result = int(temp)
    # return result
    
# def get_song_info_from_link(url):
    # """
    # This takes a url as input and returns a dictionary of song information
    # """
    # song_html = urllib2.urlopen(url).read()
    # soup = BeautifulSoup(song_html)
    # title = soup.title.text.lower()
    # ccli = int(soup.find('p', {'class':'media-info-heading'}).text.split()[-1])
    # #sometimes there is no original key
    # try:
        # original_key = soup.find_all('p', {'class':'media-info-heading'})[1].text.split()[-1]
    # except:
        # original_key = ''
    # raw_authors = soup.find('ul', {'class': 'authors'}).text.split('\r')
    # lyrics = soup.select('.lyrics-prev')[0].text
    # lyrics = lyrics.replace('  ', ', ')
    # #populate author list: authors will be a list of lists.
    # authors = []
    # for author in raw_authors:
        # #sometimes author name is foreign so can't use str on foreign characters
        # #if can't use str, omitted. is my inability to form an elegant solution making me racist??
        # try:
            # author = str(author)
        # except:
            # continue
        # #this gets rid of all commas in between authors
        # author = author.replace(',','')
        # authors.append(author.strip().lower())
    # raw_publisher = soup.select('.copyright li')
    # #populate publisher list: publishers will be a list of strings
    # publishers = []
    # public_domain = False
    # for publisher in raw_publisher:
        # #check each publisher for public domain. if present, then get rid of all publishers in place
        # #of public domain
        # text = publisher.text.lower()
        # pd = text.find('public domain')
        # if pd != -1:
            # public_domain = True
            # publishers = []
            # publishers.append('Public Domain')
            # break
        # #this eliminates the majority of the cases where there is the admin in parens
        # paren_index = text.find('(')
        # #if there is no admin though, need to handle that differently so that hte last letter doesn't get cut off
        # if paren_index == -1:
            # pub = text
        # else:
            # pub = text[:paren_index - 1]
        # publishers.append(pub)

    # years = re.findall(r'\d{4}', publishers[0])
    # #some entries don't have freaking publication years. UGH!!!
    # #if there is no publication year or its public domain, add this filler year. will have to handle display this case in view
    # if not years or public_domain:
        # years = ['1111']
    # publication_year = years[-1]
    # pb_loc = publishers[0].find(publication_year)
    # if not public_domain and publication_year!= '1111':
        # publishers[0]= publishers[0][pb_loc+5:]
    # if not public_domain and publication_year == '1111':
        # publishers[0]= publishers[0][2:]
    # #this addresses issue of if copyright info isn't in the strict form C YEAR PUBLISHER
    # #can be C Year "and" Year "publisher" or something like that
    # try:
        # int(publication_year)
    # except:
        # publication_year = 0000
        # publishers = []
        # publishers.append('ERROR: Needs fixing')
    # return {'title':title, 'ccli':ccli, 'original_key':original_key,
        # 'authors':authors, 'publication_year':publication_year, 'publishers':publishers, 'key_line':lyrics}

# def save_songs_from_dict(dict):
    # """
    # Takes as input a dictionary of song information and returns the song object instance
    # """
    # ccli = dict['ccli']
    # publication_year = int(dict['publication_year'])
    # original_key = dict['original_key']
    # key_line = dict['key_line']
    # title = string.capwords(dict['title'])
    # #finds location index of left parens
    # loc = title.find('(')
    # if loc != -1: #if left paren exists
        # title = title[0:loc+1] + title[loc+1].upper() + title[loc+2:]
    # try:
        # song = Song.objects.get(ccli=ccli)
        # new = False
    # except:
        # song = Song(title=title, ccli=ccli, publication_year=publication_year, original_key=original_key, key_line=key_line)
        # song.save()
        # new = True
        # #first check for publishers in database
        # publishers = dict['publishers']
        # for publisher in publishers:
            # pub_name = string.capwords(publisher)
            # pub, new_pub = Publisher.objects.get_or_create(name=pub_name)
            # if pub:
                # song.publisher.add(pub)
            # else:
                # song.publisher.add(new_pub)
        # #then check for authors
        # authors = dict['authors']
        # for author in authors:
        # #THIS AREA NEEDS TO CHANGE TO FULL NAME RATHER THAN FIRST, MIDDLE, LAST
            # # l = author.split()
            # # mn = ''
            # # if len(l)==3:
                # # fn = l[0].title()
                # # mn = l[1].title()
                # # ln = l[2].title()
            # # elif len(l)==2:
                # # fn = l[0].title()
                # # ln = l[1].title()
            # # else: #who the freak doesn't have a first name and last name!
                # # fn = l[0].title()
                # # ln = l[0].title()
            # # author = author.title()
            # aut, new_aut = Author.objects.get_or_create(full_name=author.title())
            # if aut:
                # song.authors.add(aut)
            # else:
                # song.authors.add(new_aut)
    # return (song, new)
    
    
#could factor out verse tagging
#can add test for this
# def link_song_to_verses(song, verse_list):
    # """
    # verse_list accepts result from request.POST.getlist('verses'). It is a list of verse IDs
    # song is a song object.
    # this function will test if the song-verse combination exists. if yes, the SV popularity increases.
    # if no, will create a song-verse combination with SV popularity 1.
    # function will iterate through verse_list to create all song-verse combinations.
    # Each time function is called, the popularity of the song increase by 1.
    # """
    # #gets only unique values
    # verse_list = set(verse_list)
    # #can only perform update on queryset so converted song object into query set
    # song_as_qs = Song.objects.filter(ccli=song.ccli)
    # song_pop = song.popularity
    # #update popularity on queryset
    # song_as_qs.update(popularity= song_pop +1)
    # for verse_id in verse_list:
        # verse = Verse.objects.get(pk=verse_id)
        # if SongVerses.objects.filter(song=song, verse=verse).exists():
            # popularity = SongVerses.objects.filter(song=song, verse=verse)[0].SV_popularity +1
            # SongVerses.objects.filter(song=song, verse=verse).update(SV_popularity=popularity)

        # else:
            # songverse = SongVerses(song=song, verse=verse, SV_popularity=1)
            # songverse.save()
    # return 