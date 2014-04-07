# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'SetlistArchive'
        db.delete_table(u'songs_setlistarchive')

        # Adding model 'Setlist'
        db.create_table(u'songs_setlist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Profile'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(default='')),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'songs', ['Setlist'])

        # Adding model 'SetlistSong'
        db.create_table(u'songs_setlistsong', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('setlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Setlist'])),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Song'])),
            ('notes', self.gf('django.db.models.fields.TextField')(default='')),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('capo_key', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('order', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'songs', ['SetlistSong'])

        # Deleting field 'Profile.setlist'
        db.delete_column(u'songs_profile', 'setlist')


    def backwards(self, orm):
        # Adding model 'SetlistArchive'
        db.create_table(u'songs_setlistarchive', (
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Profile'])),
            ('created_by', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('setlist', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'songs', ['SetlistArchive'])

        # Deleting model 'Setlist'
        db.delete_table(u'songs_setlist')

        # Deleting model 'SetlistSong'
        db.delete_table(u'songs_setlistsong')

        # Adding field 'Profile.setlist'
        db.add_column(u'songs_profile', 'setlist',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'songs.author': {
            'Meta': {'object_name': 'Author'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'songs.book': {
            'Meta': {'object_name': 'Book'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'num_chapters': ('django.db.models.fields.IntegerField', [], {}),
            'order_index': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'songs.chapter': {
            'Meta': {'object_name': 'Chapter'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Book']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_verses': ('django.db.models.fields.IntegerField', [], {}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        u'songs.ministry': {
            'Meta': {'object_name': 'Ministry'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'set_list': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'songs.profile': {
            'Meta': {'object_name': 'Profile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ministries': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['songs.Ministry']", 'symmetrical': 'False', 'blank': 'True'}),
            'num_song_tags': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_verse_tags': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'songs.publisher': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Publisher'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'state_province': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'songs.setlist': {
            'Meta': {'object_name': 'Setlist'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Profile']"}),
            'songs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['songs.Song']", 'through': u"orm['songs.SetlistSong']", 'symmetrical': 'False'})
        },
        u'songs.setlistsong': {
            'Meta': {'object_name': 'SetlistSong'},
            'capo_key': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'order': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'setlist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Setlist']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Song']"})
        },
        u'songs.song': {
            'Meta': {'object_name': 'Song'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['songs.Author']", 'symmetrical': 'False'}),
            'ccli': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'chords': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'key_line': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'original_key': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'publication_year': ('django.db.models.fields.IntegerField', [], {'max_length': '4'}),
            'publisher': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['songs.Publisher']", 'symmetrical': 'False'}),
            'recommended_key': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'verses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['songs.Verse']", 'symmetrical': 'False', 'through': u"orm['songs.SongVerses']", 'blank': 'True'})
        },
        u'songs.songverses': {
            'Meta': {'object_name': 'SongVerses'},
            'SV_popularity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Song']"}),
            'verse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Verse']"})
        },
        u'songs.verse': {
            'Meta': {'object_name': 'Verse'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Book']"}),
            'chapter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['songs.Chapter']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['songs']