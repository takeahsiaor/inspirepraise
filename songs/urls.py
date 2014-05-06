from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()
from songs import views, forms

from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail
from songs.forms import RegistrationFormEmailAsUsername

class RegistrationViewUniqueEmail(RegistrationView):
    form_class = RegistrationFormEmailAsUsername

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'worship.views.home', name='home'),
    # url(r'^worship/', include('worship.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^time/plus/(\d{1,2})/$', hours_ahead),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/$', views.home),
    url(r'^$', views.home), #for just domain to go to home
    url(r'^search/by-info/$', views.search_info),
    url(r'^search/all-songs/$', views.search_all),
    url(r'^search/by-verses/$', views.search_verses),
    url(r'^contact/$', views.contact),
    url(r'^contact/thanks/$', views.contact_thanks),
    url(r'^add-ministry/$', views.add_ministry),
    url(r'^tag-song/(?P<ccli>\d{1,8})/$', views.tag_song), #may need to change this
    url(r'^lookup/$', views.lookup),
    url(r'success/$', views.success), #no caret means will match all ending in success
    url(r'^accounts/profile/$', views.profile),
    url(r'^ministry/(?P<ministry_code>\d{1,5})/$', views.ministry_profile),
    url(r'^ministry/(?P<ministry_code>\d{1,5})/leave/$', views.leave_ministry),
    url(r'^ministry/(?P<ministry_code>\d{1,5})/delete/$', views.delete_ministry),
    url(r'^invite-to-ministry/(?P<ministry_code>\d{1,5})/$', views.invite_to_ministry),
    url(r'^accept-invitation/$', views.accept_ministry_invitation),
    url(r'^edit-ministry/(?P<ministry_code>\d{1,5})/$', views.edit_ministry),
    url(r'^admin-rights/', views.ministry_admin_rights),
    url(r'^passreset/$', auth_views.password_reset, name='forgot_password1'),
    url(r'^accounts/login/$', views.login_user),
    url(r'^accounts/profile/edit/$', views.edit_profile),
    url(r'^logout/$', views.logout_view),
    url(r'^deactivate/$', views.deactivate_account_view),
    url(r'^deactivate/confirm/yes/$', views.deactivate_account_confirm),
    url(r'^forbidden/$', views.forbidden),
    # url(r'^accounts/register/$', RegistrationViewUniqueEmail.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration_email.backends.default.urls')),
    url(r'^tag-verses/$', views.tag_verses),
    url(r'^st/$', views.tag_verse_song_search),
    url(r'^songs-with-chords/$', views.search_songs_with_chords),
    #change these someday to not be url parameters but get context parameters
    url(r'^song-info-pop/(?P<ccli>[0-9]{1,10})$', views.song_info_pop),
    url(r"^is-parsable/$", views.is_parsable),
    url(r'^tag-handler/$', views.tag_handler),
    url(r'^tag-setlist/$', views.tag_setlist),
    url(r'^chord-template/$', views.create_chord_template),
    url(r'^update-setlist/$', views.update_setlist),
    url(r'^push-setlist/$', views.push_setlist),
    url(r'^push-setlist-decision/$', views.push_setlist_decision),
    url(r'^setlist/$', views.setlist),
    # url(r'^captcha/', include('captcha.urls')),
    url(r'^testchord/$', views.chord_html), 
    url(r'^modalchord/$', views.modal_chord_html),
    url(r'^modalarchivesetlist/$', views.modal_archive_setlist),
    url(r'^pdf/$', views.chord_pdf),
    url(r'^lyrics/$', views.lyrics_to_text),
    # url(r'^send-setlist-to-archive/$', views.archive_setlist),
    url(r'^archived-setlist/$', views.display_archived_setlist),
    url(r'^song-usage-details-profile/$', views.song_usage_details_profile),
    url(r'^song-usage-details-ministry/$', views.song_usage_details_ministry),
    url(r'^change-song-stats-context/$', views.change_song_stats_context),
    
    # url(r'^suggest/$', views.suggestion),
    
    # one time utilities
    url(r'^import-dict/$', views.import_songverse_from_file),
    url(r'^import-verse-song-csv', views.import_versesongs_from_csv),
    url(r'^load-cclis/$', views.load_ccli_list),
    url(r'^load-chords/$', views.push_chords_to_database), 
    # url(r'^worshiptogether/$', views.worshiptogether),
    # url(r'^crawl/$', views.crawl_songselect),
    # url(r'^scrape/$', views.crawl_wordtoworship_letter),
    
    # obsolete
    # url(r'^book/$', views.add_book),
    # url(r'^book_list/$', views.book_list),
    # url(r'^songs/$', views.add_song),
    # url(r'^author/$', views.add_author),
    # url(r'^search/by-info/results-handler/$', views.search_info_results),
    # url(r'^search/by-verses/results-handler/$', views.search_verses_results),
    # url(r'^publisher/$', views.add_publisher),
    # url(r'^add_pop/author', views.add_author_pop), #no dollar at end means will match all beginning with author
    # url(r'^add_pop/publisher', views.add_publisher_pop),
    # url(r'^chapters_in_book/(?P<book_id>\d{1,2})/$', views.chapters_in_book), #check all parameters for cleaned data
    # url(r'^verses_in_chapter/(?P<chapter_id>\d{1,5})/$', views.verses_in_chapter),
    # url(r'^songs_in_alpha/(?P<alpha>[A-Za-z]{1,3})/$', views.songs_in_alpha),
    # url(r'^alpha/$', views.alpha),
)
