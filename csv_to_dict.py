import pickle

#may need to change this in the future to not be to a dict
#for absolute backup regeneration, could have multiple entries with same CCLI
f = open('C:/dropbox/django/song_to_verse.csv', 'r')
result_string = f.read()
f.close()
songs = result_string.split('\n')

song_verse_dict = {}

for song_string in songs:
    if len(song_string) == 0:
        continue
    elements = song_string.split(',')
    ccli = elements[0]
    verse_list = elements[1:]
    song_verse_dict[ccli] = verse_list

print len(song_verse_dict)    
print song_verse_dict
f = open('C:/dropbox/django/dict_to_import.txt', 'w')
pickle.dump(song_verse_dict, f)
f.close()