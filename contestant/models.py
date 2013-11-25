from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
DEPT = (('CS','CSE'),('EE','EEE'),('ME','MECHANICAL'))
CONTEST = ((1,'Coderpool'),(2,'Coderpool Junior'),(3,'The Girls Who Code'))

class Contestant(models.Model):
    user = models.ForeignKey(User)
    gender = models.CharField(max_length = 10,choices = (('Male','Male'),('Female','Female')))
    password = models.CharField(max_length = 50)
    dept = models.CharField(max_length=10,choices = DEPT)

    def __unicode__(self):
        return self.user.username

class Participant(models.Model):
    contestant = models.ForeignKey(Contestant)
    contest = models.IntegerField(choices = CONTEST)
    added = models.BooleanField(default = False)
    score = models.IntegerField()

    def __unicode__(self):
        return self.contestant.user.username
admin.site.register(Contestant)
admin.site.register(Participant)
