# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext as _

from timezone_field import TimeZoneField


class Player(models.Model):
    DECIMAL = 1
    FRACTIONAL = 2
    ODD_FORMAT = (
        (1, _('Decimal (European)')),
        (2, _('Fractional (UK)')),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    in_money = models.BooleanField(default=False)
    points = models.FloatField(default=0)
    send_mail = models.BooleanField(default=True)
    activation_code = models.CharField(max_length=255)
    reset_code = models.CharField(max_length=255)
    language = models.CharField(max_length=255, blank=True, null=True, default='en')
    timezone = TimeZoneField(default='Europe/London')
    odd_format = models.IntegerField(choices=ODD_FORMAT, default=DECIMAL)

    def __str__(self):
        return '%s (money: %s, points: %.2f)' % (self.user, 'yes' if self.in_money else 'no', self.points)


class Group(models.Model):
    name = models.CharField(unique=True, max_length=255)
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.PROTECT)
    players = models.ManyToManyField(User, related_name='nmkgroup')
    group_key = models.CharField(max_length=8)
    
    def __str__(self):
        return self.name


def create_user_profile(sender, instance, created, **kwargs):  
    if created:
        profile, created = Player.objects.get_or_create(user=instance)
        rounds = Round.objects.all()
        for nmk_round in rounds:
            user_round = UserRound(user=instance, round=nmk_round)
            user_round.save()


post_save.connect(create_user_profile, sender=User) 


class Team(models.Model):
    name = models.CharField(max_length=255)
    group_label = models.IntegerField()

    def __str__(self):
        return u'%s (%c)' % (self.name, chr(self.group_label + ord('A')))


class Round(models.Model):
    LEAGUE = 'League'
    CUP = 'Cup'
    GROUP_TYPE = (
        (LEAGUE, 'League'),
        (CUP, 'Cup'),
    )
    name = models.CharField(max_length=16, unique=True)
    active = models.BooleanField(default=False)
    group_type = models.CharField(max_length=16, choices=GROUP_TYPE, default=LEAGUE)
    
    def __str__(self):
        return '%s - %s%s' % (self.name, self.group_type, ' (Active)' if self.active else '')


class Match(models.Model):
    start_time = models.DateTimeField()
    result = models.IntegerField(null=True, blank=True)
    score = models.CharField(max_length=6, null=True, blank=True)
    round = models.ForeignKey('Round', on_delete=models.PROTECT)
    home_team = models.ForeignKey('Team', related_name='home_team', on_delete=models.PROTECT)
    away_team = models.ForeignKey('Team', related_name='away_team', on_delete=models.PROTECT)
    
    odd1 = models.FloatField()
    oddX = models.FloatField()
    odd2 = models.FloatField()
    
    def __str__(self):
        result = ' [%s, %s]' % (self.result, self.score) if self.result is not None else ''
        return '%s - %s @%s %s' % (self.home_team, self.away_team, self.start_time, result)


class UserRound(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    round = models.ForeignKey('Round', on_delete=models.PROTECT)
    shot_allowed = models.BooleanField(default=True)
    points = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'round')


class Shot(models.Model):
    user_round = models.ForeignKey('UserRound', on_delete=models.PROTECT)
    match = models.ForeignKey('Match', on_delete=models.PROTECT)
    shot = models.IntegerField()

    class Meta:
        unique_together = ('user_round', 'match')
