# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic



class LoggedTime(models.Model):
    """
    a period of time spent doing something
    """
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    group = generic.GenericForeignKey("content_type", "object_id")
    
    summary = models.CharField(_("summary"), max_length=200)
    owner = models.ForeignKey(User, verbose_name=_("owner"))
    start = models.DateTimeField(_("start time"))
    finish = models.DateTimeField(_("finish time"))
    
    def duration(self):
        return self.finish - self.start
    
    def __unicode__(self):
        return self.summary
    
    def __len__(self):
        return self.duration()

