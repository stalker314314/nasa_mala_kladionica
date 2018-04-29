# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.forms.widgets import PasswordInput
from django.utils.translation import gettext as _

from nmkapp.models import Round, Match, Shot, Player, Team, Group


class RegisterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(initial='', required=True, label=_('First name*'), max_length=28)
        self.fields['last_name'] = forms.CharField(initial='', required=True, label=_('Last name*'), max_length=28)
        self.fields['email'] = forms.EmailField(initial='', required=True, label=_('E-mail*'), max_length=74)
        self.fields['username'] = forms.CharField(initial='', required=True, label=_('Username*'), max_length=28)
        self.fields['password'] = forms.CharField(initial='', required=True, label=_('Password*'), max_length=28,
                                                  min_length=5, widget=PasswordInput)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        if 'first_name' in cleaned_data and len(cleaned_data['first_name']) > 28:
            raise forms.ValidationError(
                {'first_name': [_('First name must be shorter than 28 characters in length'), ]})
        if 'last_name' in cleaned_data and len(cleaned_data['last_name']) > 28:
            raise forms.ValidationError({'last_name': [_('Last name must be shorter than 28 characters in length'), ]})
        if 'email' in cleaned_data and len(cleaned_data['email']) > 74:
            raise forms.ValidationError({'email': [_('E-mail address must be shorter than 74 characters'), ]})
        if 'username' in cleaned_data and len(cleaned_data['username']) > 28:
            raise forms.ValidationError({'username': [_('Username must be shorter than 28 characters'), ]})
        
        if 'username' in cleaned_data:
            existing_usernames = User.objects.filter(username=cleaned_data['username'])
            if len(existing_usernames) > 0:
                raise forms.ValidationError({'username': [_('Username already exists'), ]})
        if 'email' in cleaned_data: 
            existing_mails = User.objects.filter(email=cleaned_data['email'])
            if len(existing_mails) > 0:
                raise forms.ValidationError(
                    {'email': [_('This e-mail address already exists. '
                                 'If this is your e-mail, please reset password.'), ]})
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        rp = kwargs.pop('rp')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(initial='', required=True, label=_('E-mail'), max_length=74)


class ResetPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        rp = kwargs.pop('passwords')
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'] = forms.CharField(initial='', required=True, label=_('Password*'), max_length=28,
                                                  min_length=5, widget=PasswordInput)
        self.fields['password2'] = forms.CharField(initial='', required=True, label=_('Repeat password*'),
                                                   max_length=28, min_length=5, widget=PasswordInput)

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        if ('password' in cleaned_data) and ('password2' in cleaned_data):
            if cleaned_data['password'] != cleaned_data['password2']:
                raise forms.ValidationError({'password2': [_('Passwords do not match'), ]})
        return cleaned_data


class NewGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group')
        super(NewGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(initial='', required=True, label=_('Create a new crew'), max_length=64,
                                              min_length=5)

    def clean(self):
        cleaned_data = super(NewGroupForm, self).clean()
        if 'name' in cleaned_data:
            if len(cleaned_data['name']) > 64:
                raise forms.ValidationError({'name': [_('Crew name too long'), ]})
            groups = Group.objects.filter(name=cleaned_data['name'])
            if len(groups) > 0:
                raise forms.ValidationError({'name': [_('Sorry, but crew name is already taken'), ]})
        return cleaned_data


class AddToGroupForm(forms.Form):
    def __init__(self, player, *args, **kwargs):
        self._player = player
        group_key = kwargs.pop('group_key')
        super(AddToGroupForm, self).__init__(*args, **kwargs)
        self.fields['key'] = forms.CharField(initial='', required=True,
                                             label=_('Please enter invite code to join a crew, if you got one:'),
                                             max_length=8, min_length=0)

    def clean(self):
        cleaned_data = super(AddToGroupForm, self).clean()
        if 'key' in cleaned_data:
            if len(cleaned_data['key']) < 8:
                raise forms.ValidationError({'key': [_('Invite code should contain 8 numbers'), ]})
            groups = Group.objects.filter(group_key=cleaned_data['key'])
            if len(groups) == 0:
                raise forms.ValidationError({'key': [_('Invite code invalid'), ]})
            if len(Group.objects.filter(group_key=cleaned_data['key']).filter(players__in=[self._player])) > 0:
                raise forms.ValidationError({'key': [_('You are already member of this crew'), ]})
        return cleaned_data


class RoundForm(ModelForm):
    class Meta:
        model = Round
        fields = ['name', 'group_type']


class MatchForm(ModelForm):
    home_team = forms.ModelChoiceField(queryset=Team.objects.order_by('group_label', 'name'))
    away_team = forms.ModelChoiceField(queryset=Team.objects.order_by('group_label', 'name'))
    
    class Meta:
        model = Match
        fields = ['home_team', 'away_team', 'start_time', 'round', 'odd1', 'oddX', 'odd2']

    def clean(self):
        cleaned_data = super(MatchForm, self).clean()
        home_team = cleaned_data.get('home_team')
        away_team = cleaned_data.get('away_team')
        this_round = cleaned_data.get('round')
        
        if home_team == away_team:
            raise forms.ValidationError(_('Team cannot play match against itself'))
        if Shot.objects.filter(user_round__round=this_round).exists():
            raise forms.ValidationError(
                _('You cannot add new matches in this round, as some players already placed bets in this round'))
        matches = Match.objects.filter(round=this_round)
        for match in matches:
            if match.home_team == home_team or match.away_team == home_team:
                raise forms.ValidationError(_('Team %s already plays in this round') % home_team.name)
            if match.home_team == away_team or match.away_team == away_team:
                raise forms.ValidationError(_('Team %s already plays in this round') % away_team.name)
        return cleaned_data


class ResultsForm(ModelForm):
    class Meta:
        model = Match
        fields = ['score']
        labels = {'score': _('Result (in the <host>:<guest> format)')}

    def clean(self):
        cleaned_data = super(ResultsForm, self).clean()
        score = cleaned_data.get('score')
        scores = score.split(':')
        if len(scores) != 2:
            raise forms.ValidationError(_('There should be colon between two numbers'))
        try:
            int(scores[0])
            int(scores[1])
        except ValueError:
            raise forms.ValidationError(_('Cannot parse numbers in result'))
        return cleaned_data


class BettingForm(forms.Form):
    def __init__(self, *args, **kwargs):
            shots = kwargs.pop('shots')
            super(BettingForm, self).__init__(*args, **kwargs)
            for shot in shots:
                self.fields['%d_%d' % (shot.user_round.id, shot.match.id)] = forms.IntegerField(
                    initial=shot.shot,
                    required=False,
                    label='%s - %s' % (shot.match.home_team.name, shot.match.away_team.name),
                    widget=forms.RadioSelect(
                        choices=[[1, str(shot.match.odd1)], [0, str(shot.match.oddX)], [2, str(shot.match.odd2)]]))

    def clean(self):
        cleaned_data = super(BettingForm, self).clean()
        for name, value in self.cleaned_data.items():
            if value is None:
                raise forms.ValidationError(_('You must place all bets'))
        return cleaned_data


class PlayerForm(ModelForm):
    language = forms.ChoiceField(choices=settings.LANGUAGES)

    class Meta:
        model = Player
        fields = ['send_mail', 'language', 'timezone']
        labels = {'send_mail': _('Receive e-mail notifications'), 'language': _('Language'), 'timezone': _('Time zone')}

    def clean(self):
        cleaned_data = super(PlayerForm, self).clean()
        language = cleaned_data.get('language')
        available_languages = [lang_code for (lang_code, lang_name) in settings.LANGUAGES]
        if language not in available_languages:
            raise forms.ValidationError({'language': [_('Language {} is not available ').format(language), ]})
        return cleaned_data
