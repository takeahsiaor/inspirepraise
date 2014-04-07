from songs.models import Song, Book, Chapter, Verse, SongVerses, Ministry, Profile, Publisher, Author
from difflib import get_close_matches
import urllib2, string, re, pickle
from bs4 import BeautifulSoup

# def chord_lines_to_html(lines):



def convert_setlist_to_string(setlist):
    """
    Accepts as input the request setlist variable
    Currnetly setlist = [ (ccli, key), (ccli, key) ]
    and returns a string of 'ccli-key,ccli-key,'
    """
    setlist_string = ''
    for ccli in setlist:
        if len(ccli) < 2: #for some reason the string turned out to be ,592839 so first ccli was empty string
            continue
        setlist_string += str(ccli[0]) + '-' + str(ccli[1]) +','
    setlist_string = setlist_string[:-1]
    return setlist_string

def make_key_option_html(key):
    """
    Given a key as a string, will create option list html with key selected
    """
    all_major_keys = ['Ab','A','Bb','B','C', 'C#','Db','D','Eb','E','F','F#','Gb','G','G#']
    all_minor_keys = ['Abm','Am','Bbm','Bm','Cm', 'C#m','Dm','Ebm','Em','Fm','F#m','Gm','G#m']
    option_html = ''
    if 'm' in key:
        all_keys = all_minor_keys
    else:
        all_keys = all_major_keys
        
    for option in all_keys:
        if option == key:
            option_html += '<option selected>' + option +'</option>'
        else:
            option_html += '<option>'+option+'</option>'
    return option_html


def parse_string_to_verses(query):
    """
    receives as input, a string query in the form (book chapter:verses)
    or (book chapter:verse-verse).
    returns a list of verse ids
    """
    book_list = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 
        'joshua', 'judges', 'ruth', '1 samuel', '2 samuel', '1 kings', '2 kings', 
        '1 chronicles', '2 chronicles', 'ezra', 'nehemiah', 'esther', 'job', 
        'psalm', 'proverbs', 'ecclesiastes', 'song of solomon', 'isaiah', 
        'jeremiah', 'lamentations', 'ezekiel', 'daniel', 'hosea', 'joel', 'amos', 
        'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk', 'zephaniah', 'haggai', 
        'zechariah', 'malachi', 'matthew', 'mark', 'luke', 'john', 'acts', 'romans', 
        '1 corinthians', '2 corinthians', 'galatians', 'ephesians', 'philippians', 
        'colossians', '1 thessalonians', '2 thessalonians', '1 timothy', '2 timothy',
        'titus', 'philemon', 'hebrews', 'james', '1 peter', '2 peter', '1 john', 
        '2 john', '3 john', 'jude', 'revelation']
        
    query = query.strip().lower()
    #makes sure query is not empty string (no scripture reference)
    if query == '':
        return []
    #currently doesn't allow commas
    if ',' in query:
        print query
        return []
    #check if book name has ordinal, find location of first number
    if query[0] in '123':
        match = re.search("\d", query[2:])
        loc_ord = 2
    else:
        match = re.search("\d", query)
        loc_ord = 0
        
    #if there is no number(just book)
    #get_close matches takes input query, a list of possible options, number of
    #results to return and a difference factor and returns a list of close matches.
    #.42 needed for rev. match
    if not match:
        book = get_close_matches(query, book_list, 1, 0.6)[0]
        chapver = []
    else:
        num_loc = match.start() + loc_ord
        book = get_close_matches(query[0:num_loc].strip(), book_list, 1, 0.6)[0]
        chapver = query[num_loc:].split(':')
    #if there is nothing after the book name, get the whole book
    if not chapver:
        qs = Verse.objects.filter(book__name__iexact=book)
        verse_list = qs.values_list('id', flat=True)
        return list(verse_list)
    else:
        chapter = chapver[0].strip()
    verse_list = []
    #this checks whether  there is verse designation. if not, get queryset of whole chapter
    if len(chapver) == 1:
        #check if this has '-'. if so, get multiple chapters
        if '-' in chapter:
            chapter_list = chapter.split('-')
            start_chapter = int(chapter_list[0])
            end_chapter = int(chapter_list[1])
            middle_chapters = range(start_chapter+1, end_chapter)
        
            begin_chap_verses = Verse.objects.filter(
                book__name__iexact=book, chapter__number=start_chapter,)
                
            end_chap_verses = Verse.objects.filter(
                book__name__iexact=book, chapter__number=end_chapter)
                
            mid_chap_verses = Verse.objects.none()
            for mid_chap in middle_chapters:
                verse_qs = Verse.objects.filter(
                    book__name__iexact=book, chapter__number=mid_chap)
                mid_chap_verses = mid_chap_verses | verse_qs
                
            all_verses_qs = begin_chap_verses | mid_chap_verses | end_chap_verses
            verse_list = all_verses_qs.values_list('id', flat=True)

        else:
            chapter = int(chapter)
            qs = Verse.objects.filter(book__name__iexact=book, chapter__number=chapter)
            verse_list = qs.values_list('id', flat=True)
    #this checks if string spans multiple chapters
    elif len(chapver) == 3:
        #example isaiah 52:13-53:12
        #[52, 13-53, 12]
        start_chapter = int(chapter)
        mid = chapver[1].split('-')
        #deals with a/b designation in verses for example verse 14b, just translate to 14
        #enough to just take off last char?
        #see force_int method
        start_verse = force_int(mid[0])
        end_chapter = int(mid[1])
        end_verse = force_int(chapver[2])

        middle_chapters = range(start_chapter+1, end_chapter)
        
        begin_chap_verses = Verse.objects.filter(
            book__name__iexact=book, chapter__number=start_chapter,
            number__gte=start_verse)
            
        end_chap_verses = Verse.objects.filter(
            book__name__iexact=book, chapter__number=end_chapter,
            number__lte=end_verse)
            
        mid_chap_verses = Verse.objects.none()
        for mid_chap in middle_chapters:
            verse_qs = Verse.objects.filter(
                book__name__iexact=book, chapter__number=mid_chap)
            mid_chap_verses = mid_chap_verses | verse_qs
            
        all_verses_qs = begin_chap_verses | mid_chap_verses | end_chap_verses
        #to get value of specific field in all elements within queryset use
        #qs.value() for dict, or qs.values_list('fieldname', flat=True) for list
        verse_list = all_verses_qs.values_list('id', flat=True)
    else: #if verse designation, then parse the verse string
        verses = chapver[1]
        chapter = int(chapter)
        #if there's a dash in verses, get beginning and end number then get all verses in between
        if '-' in verses:
            startend = verses.split('-')
            start = force_int(startend[0])
            end = force_int(startend[1])
            qs = Verse.objects.filter(book__name__iexact=book,chapter__number=chapter,
                number__gte=start).filter(number__lte=end)
            verse_list = qs.values_list('id', flat=True)
        else:
            verses = force_int(verses)
            verse_object = Verse.objects.get(book__name__iexact=book, chapter__number=chapter, number=verses)
            verse_list.append(verse_object.id)
    verse_list = list(verse_list)
    return verse_list
    
def test_parsable(query):
    """
    function that receives as in put a query and returns true if parsable and false if not
    """
    try:
        verse_list = parse_string_to_verses(query)
        if len(verse_list) > 0:
            parsable = True
        else:
            parsable = False
    except:
        parsable = False
    return parsable
    
    
def check_song(ccli):
    """
    checks for song with ccli# in database. if not in database, will get song info
    from songselect in ccli. if song exists, doesn't do anything. 
    returns does_not_exist as either true or false
    """
    does_not_exist = False
    # checks if song is already in database
    try:
        song = Song.objects.get(ccli=int(ccli))
    except:
        # if song not in database, try to get song_info from url
        try:
            url = 'https://us.songselect.com/songs/' + ccli
            song_info = get_song_info_from_link(url)
            save_songs_from_dict(song_info)
        #if ccli is wrong or something, then return does_not_exist as true
        except:
            does_not_exist = True
    return does_not_exist

def force_int(entry):
    """
    accepts string entry with numbers and/or characters. If entry only contains
    numbers, will convert it to int then return value.
    If entry contains characters, will force remove characters then convert remains to int
    """
    try:
        result = int(entry)
    except:
        temp = re.sub(r'\D', '', entry)
        result = int(temp)
    return result
    
def get_song_info_from_link(url):
    """
    This takes a url as input and returns a dictionary of song information
    """
    song_html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(song_html)
    title = soup.title.text.lower()
    ccli = int(soup.find('p', {'class':'media-info-heading'}).text.split()[-1])
    #sometimes there is no original key
    try:
        original_key = soup.find_all('p', {'class':'media-info-heading'})[1].text.split()[-1]
    except:
        original_key = ''
    raw_authors = soup.find('ul', {'class': 'authors'}).text.split(',') #used to be split on '\r'
    lyrics = soup.select('.lyrics-prev')[0].text
    lyrics = lyrics.replace('  ', ', ')
    #populate author list: authors will be a list of lists.
    authors = []
    for author in raw_authors:
        #sometimes author name is foreign so can't use str on foreign characters
        #if can't use str, omitted. is my inability to form an elegant solution making me racist??
        try:
            author = str(author)
        except:
            continue
        #this gets rid of all commas in between authors
        author = author.replace(',','')
        # print author.strip().lower()
        authors.append(author.strip().lower())
    raw_publisher = soup.select('.copyright li')
    #populate publisher list: publishers will be a list of strings
    publishers = []
    public_domain = False
    for publisher in raw_publisher:
        #check each publisher for public domain. if present, then get rid of all publishers in place
        #of public domain
        text = publisher.text.lower()
        pd = text.find('public domain')
        if pd != -1:
            public_domain = True
            publishers = []
            publishers.append('Public Domain')
            break
        #this eliminates the majority of the cases where there is the admin in parens
        paren_index = text.find('(')
        #if there is no admin though, need to handle that differently so that hte last letter doesn't get cut off
        if paren_index == -1:
            pub = text
        else:
            pub = text[:paren_index - 1]
        publishers.append(pub)

    years = re.findall(r'\d{4}', publishers[0])
    #some entries don't have freaking publication years. UGH!!!
    #if there is no publication year or its public domain, add this filler year. will have to handle display this case in view
    if not years or public_domain:
        years = ['1111']
    publication_year = years[-1]
    pb_loc = publishers[0].find(publication_year)
    if not public_domain and publication_year!= '1111':
        publishers[0]= publishers[0][pb_loc+5:]
    if not public_domain and publication_year == '1111':
        publishers[0]= publishers[0][2:]
    #this addresses issue of if copyright info isn't in the strict form C YEAR PUBLISHER
    #can be C Year "and" Year "publisher" or something like that
    try:
        int(publication_year)
    except:
        publication_year = 0000
        publishers = []
        publishers.append('ERROR: Needs fixing')
    return {'title':title, 'ccli':ccli, 'original_key':original_key,
        'authors':authors, 'publication_year':publication_year, 'publishers':publishers, 'key_line':lyrics}

def save_songs_from_dict(dict):
    """
    Takes as input a dictionary of song information and returns the song object instance
    """
    ccli = dict['ccli']
    publication_year = int(dict['publication_year'])
    original_key = dict['original_key']
    key_line = dict['key_line']
    title = string.capwords(dict['title'])
    #finds location index of left parens
    loc = title.find('(')
    if loc != -1: #if left paren exists
        title = title[0:loc+1] + title[loc+1].upper() + title[loc+2:]
    try:
        song = Song.objects.get(ccli=ccli)
        new = False
    except:
        song = Song(title=title, ccli=ccli, publication_year=publication_year, original_key=original_key, key_line=key_line)
        song.save()
        new = True
        #first check for publishers in database
        publishers = dict['publishers']
        for publisher in publishers:
            pub_name = string.capwords(publisher)
            pub, new_pub = Publisher.objects.get_or_create(name=pub_name)
            if pub:
                song.publisher.add(pub)
            else:
                song.publisher.add(new_pub)
        #then check for authors
        authors = dict['authors']
        for author in authors:
        #THIS AREA NEEDS TO CHANGE TO FULL NAME RATHER THAN FIRST, MIDDLE, LAST
            # l = author.split()
            # mn = ''
            # if len(l)==3:
                # fn = l[0].title()
                # mn = l[1].title()
                # ln = l[2].title()
            # elif len(l)==2:
                # fn = l[0].title()
                # ln = l[1].title()
            # else: #who the freak doesn't have a first name and last name!
                # fn = l[0].title()
                # ln = l[0].title()
            # author = author.title()
            aut, new_aut = Author.objects.get_or_create(full_name=author.title())
            if aut:
                song.authors.add(aut)
            else:
                song.authors.add(new_aut)
    return (song, new)
    
def link_song_to_verses(song, verse_list):
    """
    verse_list accepts result from request.POST.getlist('verses'). It is a list of verse IDs
    song is a song object.
    this function will test if the song-verse combination exists. if yes, the SV popularity increases.
    if no, will create a song-verse combination with SV popularity 1.
    function will iterate through verse_list to create all song-verse combinations.
    Each time function is called, the popularity of the song increase by 1.
    """
    #gets only unique values
    verse_list = set(verse_list)
    #can only perform update on queryset so converted song object into query set
    song_as_qs = Song.objects.filter(ccli=song.ccli)
    song_pop = song.popularity
    #update popularity on queryset
    song_as_qs.update(popularity= song_pop +1)
    for verse_id in verse_list:
        verse = Verse.objects.get(pk=verse_id)
        if SongVerses.objects.filter(song=song, verse=verse).exists():
            popularity = SongVerses.objects.filter(song=song, verse=verse)[0].SV_popularity +1
            SongVerses.objects.filter(song=song, verse=verse).update(SV_popularity=popularity)

        else:
            songverse = SongVerses(song=song, verse=verse, SV_popularity=1)
            songverse.save()
    return 
    
def transpose(original, semitones, original_key, final_key):
    """
    takes as input the original chord, the number of semitones to adjust
    and the original key as parsed from the chordpro file
    for now, automated key detection is a bit too much for me.
    - parse original chord into the note sections
    - find the index
    - then offset all notes by semitones
    - for cases where offset value has 2 notes, use original key plus semitones to figure out which to use
    - must take final_key as well in order to get the intended enharmonic
        -for instance, Ab vs G#
    """
    slash_chord = False
    # if 'min' in original_key:
    if 'm' in original_key:
        major = False
        root = original_key[:-1]
        final_key_root = final_key[:-1]
    else:
        major = True
        root = original_key
        final_key_root = final_key


    notes_in_major_keys = {
        'C': ['C','D','E','F','G','A','B'],
        'C#': ['C#','D#','E#','F#','G#','A#','B#'],
        'Db': ['Db','Eb','F','Gb','Ab','Bb','C'],
        'D': ['D','E','F#','G','A','B','C#'],
        'Eb': ['Eb','F','G','Ab','Bb','C','D'],
        'E': ['E','F#','G#','A','B','C#','D#'],
        'F': ['F','G','A','Bb','C','D','E'],
        'F#': ['F#','G#','A#','B','C#','D#','E#'],
        'Gb': ['Gb','Ab','Bb','Cb','Db','Eb','F','Gb'],
        'G': ['G','A','B','C','D','E','F#'],
        'G#': ['G#','A#','B#','C#','D#','E#','G'],
        'Ab': ['Ab','Bb','C','Db','Eb','F','G'],
        'A': ['A','B','C#','D','E','F#','G#'],
        'Bb': ['Bb','C','D','Eb','F','G','A'],
        'B': ['B','C#','D#','E','F#','G#','A#']
    }

    notes_in_minor_keys = {
        'Abm': ['Ab','Bb','Cb','Db','Eb','Fb','Gb'],
        'Am': ['A','B','C','D','E','F','G'],
        'Bbm': ['Bb','C','Db','Eb','F','Gb','Ab'],
        'Bm': ['B','C#','D','E','F#','G','A'],
        'Cm': ['C','D','Eb','F','G','Ab','Bb'],
        'C#m': ['C#','D#','E','G#','F#','A','B'],
        'Dm': ['D','E','F','G','A','Bb','C','D'],
        'Ebm': ['Eb','F','Gb','Ab','Bb','Cb','Db'],
        'Em': ['E','F#','G','A','B','C','D'],
        'Fm': ['F','G','Ab','Bb','C','Db','Eb'],
        'F#m': ['F#','G#','A','B','C#','D','E'],
        'Gm': ['G','A','Bb','C','D','Eb','F'],
        'G#m': ['G#','A#','B','C#','D#','E','F#']
    }
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
    offsets = {
        0: ['Ab','G#'],
        1: ['A'],
        2: ['Bb', 'A#'],
        3: ['B', 'Cb'],
        4: ['C', 'B#'],
        5: ['Db','C#'],
        6: ['D'],
        7: ['Eb','D#'],
        8: ['E','Fb'],
        9: ['F', 'E#'],
        10: ['F#', 'Gb'],
        11: ['G']
    }
                
    #this section gets the individual notes into a list
    parsed_original = []
    if '/' in original:
        slash_chord = True
    if len(original) > 1:
        note = original[:2]
        #check if there is a sharp or flat
        if note[1] != '#' and note[1] != 'b':
            note = original[0]
            parsed_original.append(note)
        #if yes, then append that
        else:
            parsed_original.append(note)
        #check if it's a slash chord
        if slash_chord:
            slash_loc = original.find('/')
            second_note = original[slash_loc+1:]
            parsed_original.append(second_note)
    else:
        note = original
        parsed_original.append(note)
    #result is a list of parsed original notes before transposition.
    # print original #this is the original string
    # print parsed_original # this is the original notes in list format
    
    transposed = [] #this will be a list of transposed notes
    for note in parsed_original:
        index = indexes[note]
        new_position = index+semitones
        new_note = offsets[new_position%12] #gives a list of potential notes (1 or 2 length)
        if len(new_note) > 1: #if more than one note in list, test against notes in key
            new_key_index = (indexes[root] + semitones)%12
            #defaults to choosing the first note in list
            equivalent_keys = offsets[new_key_index]
            if final_key_root == equivalent_keys[0]:
                new_key = offsets[new_key_index][0]
            else:
                new_key = offsets[new_key_index][1]
            #is it a major key or minor?
            if major:
                if new_note[0] in notes_in_major_keys[new_key]:
                    transposed.append(new_note[0])
                else:
                    transposed.append(new_note[1])
            else:
                #need to get the right root note if the root note has two possibilites. Try except
                #no need for this in major since the list is created with the major in mind.
                try:
                    if new_note[0] in notes_in_minor_keys[new_key+'m']:
                        transposed.append(new_note[0])
                    else:
                        transposed.append(new_note[1])
                except KeyError:
                    new_key = offsets[new_key_index][1] #change root key to be the second possibliity
                    if new_note[0] in notes_in_minor_keys[new_key+'m']:
                        transposed.append(new_note[0])
                    else:
                        transposed.append(new_note[1])                    
        else:
            transposed.append(new_note[0])
    result = original
    #what happens when you have G/B and you transpose it to B/Eb?
    # will do replacement of G for B so result will be B/B
    # then replace first B with Eb so you get Eb/B
    # if we do the last note first though, everything should be fine. Replace B first with Eb
    # we also have to make a copy of the parsed original reversed in order to do the replace properly
    transposed = list(reversed(transposed))
    parsed_original_reversed = list(reversed(parsed_original))
    # print transposed
    for trans in transposed:
        position = transposed.index(trans)
        result = result.replace(parsed_original_reversed[position], trans, 1)
    return result