from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Player(models.Model):
    user = models.OneToOneField(User)
    points = models.FloatField(default=0)

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = Player.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User) 

class Team(models.Model):
    name = models.CharField(max_length=255)
    group_label = models.IntegerField()

    def __str__(self):
        return "%s (%c)" % (self.name, chr(self.group_label + ord('A')))
    
class Round(models.Model):
    LEAGUE = 'League'
    CUP = 'Cup'
    GROUP_TYPE = (
        (LEAGUE, 'League'),
        (CUP, 'Cup'),
    )
    name = models.CharField(max_length=16, unique=True)
    active = models.BooleanField(default=False)
    group_type = models.CharField(max_length=16, choices = GROUP_TYPE, default=LEAGUE)
    
    def __str__(self):
        return "%s - %s%s" % (self.name, self.group_type, " (Active)" if self.active else "")

class Match(models.Model):
    start_time = models.DateTimeField()
    result = models.IntegerField(null=True, blank=True)
    score = models.CharField(max_length=6, null=True, blank=True)
    round = models.ForeignKey('Round')
    home_team = models.ForeignKey('Team', related_name='home_team')
    away_team = models.ForeignKey('Team', related_name='away_team')
    
    odd1 = models.FloatField()
    oddX = models.FloatField()
    odd2 = models.FloatField()
    
    def __str__(self):
        result = " [%s, %s]" % (self.result, self.score) if self.result != None else ""
        return "%s - %s @%s %s" % (self.home_team, self.away_team, self.start_time, result)

class UserRound(models.Model):
    user = models.ForeignKey(User)
    round = models.ForeignKey('Round')
    shot_allowed = models.BooleanField(default=True)
    points = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'round')

class Shot(models.Model):
    user_round = models.ForeignKey('UserRound')
    match = models.ForeignKey('Match')
    shot = models.IntegerField()

    class Meta:
        unique_together = ('user_round', 'match')