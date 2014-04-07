from bs4 import BeautifulSoup
import pickle
import urllib2

f  = open('wordtoworship_links.txt', 'r')
link_list = pickle.load(f)
f.close()




all_html = []

for link in link_list:
    html = urllib2.urlopen('http://www.wordtoworship.com' + link).read()
    all_html.append(html)
    
f = open('all_wordtoworship_html.txt', 'w')
pickle.dump(all_html, f)
f.close()