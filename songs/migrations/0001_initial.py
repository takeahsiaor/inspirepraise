# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Publisher'
        db.create_table(u'songs_publisher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('state_province', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'songs', ['Publisher'])

        # Adding model 'Book'
        db.create_table(u'songs_book', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('num_chapters', self.gf('django.db.models.fields.IntegerField')()),
            ('order_index', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
        ))
        db.send_create_signal(u'songs', ['Book'])

        # Adding model 'Chapter'
        db.create_table(u'songs_chapter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Book'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('num_verses', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'songs', ['Chapter'])

        # Adding model 'Verse'
        db.create_table(u'songs_verse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Book'])),
            ('chapter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Chapter'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'songs', ['Verse'])

        # Adding model 'Author'
        db.create_table(u'songs_author', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal(u'songs', ['Author'])

        # Adding model 'Song'
        db.create_table(u'songs_song', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('ccli', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('key_line', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('original_key', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('recommended_key', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('popularity', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('publication_year', self.gf('django.db.models.fields.IntegerField')(max_length=4)),
        ))
        db.send_create_signal(u'songs', ['Song'])

        # Adding M2M table for field authors on 'Song'
        m2m_table_name = db.shorten_name(u'songs_song_authors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(orm[u'songs.song'], null=False)),
            ('author', models.ForeignKey(orm[u'songs.author'], null=False))
        ))
        db.create_unique(m2m_table_name, ['song_id', 'author_id'])

        # Adding M2M table for field publisher on 'Song'
        m2m_table_name = db.shorten_name(u'songs_song_publisher')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('song', models.ForeignKey(orm[u'songs.song'], null=False)),
            ('publisher', models.ForeignKey(orm[u'songs.publisher'], null=False))
        ))
        db.create_unique(m2m_table_name, ['song_id', 'publisher_id'])

        # Adding model 'SongVerses'
        db.create_table(u'songs_songverses', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Song'])),
            ('verse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['songs.Verse'])),
            ('SV_popularity', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'songs', ['SongVerses'])

        # Adding model 'Ministry'
        db.create_table(u'songs_ministry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state_province', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('set_list', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'songs', ['Ministry'])

        # Adding model 'Profile'
        db.create_table(u'songs_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('num_song_tags', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('num_verse_tags', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'songs', ['Profile'])

        # Adding M2M table for field ministries on 'Profile'
        m2m_table_name = db.shorten_name(u'songs_profile_ministries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm[u'songs.profile'], null=False)),
            ('ministry', models.ForeignKey(orm[u'songs.ministry'], null=False))
        ))
        db.create_unique(m2m_table_name, ['profile_id', 'ministry_id'])


    def backwards(self, orm):
        # Deleting model 'Publisher'
        db.delete_table(u'songs_publisher')

        # Deleting model 'Book'
        db.delete_table(u'songs_book')

        # Deleting model 'Chapter'
        db.delete_table(u'songs_chapter')

        # Deleting model 'Verse'
        db.delete_table(u'songs_verse')

        # Deleting model 'Author'
        db.delete_table(u'songs_author')

        # Deleting model 'Song'
        db.delete_table(u'songs_song')

        # Removing M2M table for field authors on 'Song'
        db.delete_table(db.shorten_name(u'songs_song_authors'))

        # Removing M2M table for field publisher on 'Song'
        db.delete_table(db.shorten_name(u'songs_song_publisher'))

        # Deleting model 'SongVerses'
        db.delete_table(u'songs_songverses')

        # Deleting model 'Ministry'
        db.delete_table(u'songs_ministry')

        # Deleting model 'Profile'
        db.delete_table(u'songs_profile')

        # Removing M2M table for field ministries on 'Profile'
        db.delete_table(db.shorten_name(u'songs_profile_ministries'))


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
        u'songs.song': {
            'Meta': {'object_name': 'Song'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['songs.Author']", 'symmetrical': 'False'}),
            'ccli': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
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