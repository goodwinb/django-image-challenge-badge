from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from django.template.defaultfilters import slugify
from easy_thumbnails.files import Thumbnailer
from easy_thumbnails.files import ThumbnailFile
from easy_thumbnails.fields import ThumbnailerImageField
from os.path import join as pjoin
from PIL import Image as PImage
from settings import MEDIA_ROOT
from string import join
from tagging.fields import TagField
from tagging.models import Tag
from tempfile import *
import datetime
import os
import os.path
import random


class Badge (models.Model):
    name = models.CharField(max_length=100)
    badge_image = models.ImageField(upload_to="thumbs/")
    
    def __unicode__(self):
        return self.name
    
    
class Challenge (models.Model):
    approved = models.BooleanField(default=True)
    badge = models.ForeignKey(Badge, blank=True)
    date_created = models.DateTimeField(default=datetime.datetime.now())
    name = models.CharField(max_length=60)
    number_of_images = models.IntegerField()
    number_taken = models.IntegerField()
    score = models.DecimalField(max_digits=100, decimal_places=7, default=0)
    slug = models.SlugField(unique_for_date='date_created',
                            help_text="Suggested value automatically generate from name. Must be unique.")
    sponsored = models.BooleanField(default=False)
    sponsor_url = models.URLField(blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    users_voted = models.ManyToManyField(User, related_name='Users_Voted', blank=True)
    users_voted_up = models.ManyToManyField(User, related_name='Users_Voted_Up', blank=True)
    users_voted_down = models.ManyToManyField(User, related_name='Users_Voted_Down', blank=True)
    votes = models.IntegerField()
        
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Challenge, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return "/challengeentry/%s/%s/" % (self.date_created.strftime("%Y/%b/%d").lower(), self.slug)
    
    
class Feedback(models.Model):
    message = models.CharField(max_length=1000)
    email = models.EmailField(blank=True) 
    date_created = models.DateTimeField(default=datetime.datetime.now())
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_created']
    
    def __unicode__(self):
        return self.message[:15]
    
        
class Image(models.Model):
    def image_filename(instance, filename):
        extension = os.path.splitext(filename)[-1]
        generated_filename = ''
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
        temp_id_length = 14
        for y in range(temp_id_length):
            generated_filename += characters[random.randint(0, len(characters)-1)]
        return 'dump/%s%s' % (generated_filename, extension)
    def thumbnail_filename(instance, filename):
        extension = os.path.splitext(filename)[-1]
        generated_filename = ''
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
        temp_id_length = 14
        for y in range(temp_id_length):
            generated_filename += characters[random.randint(0, len(characters)-1)]
        return 'thumbs/%s%s' % (generated_filename, extension)    
    approved = models.BooleanField(default=False)
    challenges = models.ManyToManyField(Challenge, blank=True)
    date_created = models.DateTimeField(default=datetime.datetime.now())
    ip = models.IPAddressField()
    image = models.ImageField(upload_to=image_filename)
    media_type = models.IntegerField()
    tags = TagField()
    
    # Submit the image file to the thumbnail fields below in addition to submitting it to image
    thumbnail_small = ThumbnailerImageField(upload_to=thumbnail_filename, 
                                        resize_source=dict(size=(50, 50), crop='smart'), blank=True, null=True)
    thumbnail_large = ThumbnailerImageField(upload_to=thumbnail_filename, 
                                        resize_source=dict(size=(100, 100), crop='smart'), blank=True, null=True)
    title = models.CharField(max_length=60)
    user = models.ForeignKey(User)

           
    def size(self):
        """Image size."""
        return "%s x %s" % (self.width, self.height)

    def __unicode__(self):
        return self.image.name

    def hot_tag(self):
        try:
            tags = Tag.objects.get_for_object(self)
            #tags = tags.order_by('count')
            hot_tag = tags[0]
        except Exception, e:
            hot_tag = str(e)
        return hot_tag
    
    def challenges_(self):
        lst = [x[1] for x in self.challenges.values_list()]
        return str(join(lst, ', '))

    def thumbnail_small_(self):
        return """<a href="/site_media/%s"><img border="0" alt="" src="/site_media/%s" /></a>""" % (
                                                            (self.image.name, self.thumbnail_small.name))
    thumbnail_small_.allow_tags = True
    
    def thumbnail_large_(self):
        return """<a href="/site_media/%s"><img border="0" alt="" src="/site_media/%s" /></a>""" % (
                                                            (self.image.name, self.thumbnail_large.name))
    thumbnail_large_.allow_tags = True

        
class ChallengeImage(models.Model):
    challenge = models.ForeignKey(Challenge)
    image = models.ForeignKey(Image, null=True, blank=True)
    order = models.IntegerField()
    
    def __unicode__(self):
        return self.image.title

    @staticmethod
    def move_down(challenge_image_id):
        try:
            lower_model = ChallengeImage.objects.get(id=challenge_image_id)
            challenge_images = ChallengeImage.objects.filter(challenge=lower_model.challenge)
            higher_model = challenge_images.filter(order__gt=lower_model.order)[0]
            
            lower_model.order, higher_model.order = higher_model.order, lower_model.order

            higher_model.save()
            lower_model.save()
        except IndexError:
            pass
    
    @staticmethod           
    def move_up(challenge_image_id):
        try:
            higher_model = ChallengeImage.objects.get(id=challenge_image_id)
            challenge_images = ChallengeImage.objects.filter(challenge=higher_model.challenge)
            lower_model = challenge_images.filter(order__lt=higher_model.order)[0]

            lower_model.order, higher_model.order = higher_model.order, lower_model.order

            higher_model.save()
            lower_model.save()
        except IndexError:
            pass


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    advertiser = models.BooleanField(default=False)
    badges = models.ManyToManyField(Badge, blank=True)

    def __unicode__(self):
        return self.user.username
