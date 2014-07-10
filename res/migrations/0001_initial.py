# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Attribute'
        db.create_table('res_attribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(blank=True, max_length=200)),
        ))
        db.send_create_signal('res', ['Attribute'])

        # Adding model 'Room'
        db.create_table('res_room', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('capacity', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=0)),
            ('description', self.gf('django.db.models.fields.CharField')(blank=True, max_length=2000)),
        ))
        db.send_create_signal('res', ['Room'])

        # Adding M2M table for field attributes on 'Room'
        m2m_table_name = db.shorten_name('res_room_attributes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('room', models.ForeignKey(orm['res.room'], null=False)),
            ('attribute', models.ForeignKey(orm['res.attribute'], null=False))
        ))
        db.create_unique(m2m_table_name, ['room_id', 'attribute_id'])

        # Adding model 'Free'
        db.create_table('res_free', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['res.Room'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('starthour', self.gf('django.db.models.fields.TimeField')()),
            ('endhour', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('res', ['Free'])

        # Adding model 'Reservation'
        db.create_table('res_reservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['res.Room'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('starthour', self.gf('django.db.models.fields.TimeField')()),
            ('endhour', self.gf('django.db.models.fields.TimeField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('res', ['Reservation'])


    def backwards(self, orm):
        # Deleting model 'Attribute'
        db.delete_table('res_attribute')

        # Deleting model 'Room'
        db.delete_table('res_room')

        # Removing M2M table for field attributes on 'Room'
        db.delete_table(db.shorten_name('res_room_attributes'))

        # Deleting model 'Free'
        db.delete_table('res_free')

        # Deleting model 'Reservation'
        db.delete_table('res_reservation')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'to': "orm['auth.Group']", 'blank': 'True', 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'res.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'description': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'res.free': {
            'Meta': {'object_name': 'Free'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'endhour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['res.Room']"}),
            'starthour': ('django.db.models.fields.TimeField', [], {})
        },
        'res.reservation': {
            'Meta': {'object_name': 'Reservation'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'endhour': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['res.Room']"}),
            'starthour': ('django.db.models.fields.TimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'res.room': {
            'Meta': {'object_name': 'Room'},
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['res.Attribute']", 'symmetrical': 'False'}),
            'capacity': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '2000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['res']