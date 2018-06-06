# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.forms.widgets import PasswordInput
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from nmkapp.models import Group
from nmkapp.logic import convert_odd_format


class RegisterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['display_name'] = forms.CharField(initial='', required=True, label=_('Display name'), max_length=28)
        self.fields['email'] = forms.EmailField(initial='', required=True, label=_('E-mail'), max_length=74)
        self.fields['password'] = forms.CharField(initial='', required=True, label=_('Password'), max_length=28,
                                                  min_length=5, widget=PasswordInput)
        accept_terms_validity_message = _('You have to accept terms and conditions to register')
        self.fields['accept_terms'] = forms.BooleanField(
            initial=True, required=True, label=mark_safe(_('I accept <a href="/terms">Terms and Conditions</a>')),
            error_messages={'required': accept_terms_validity_message},
            widget = forms.CheckboxInput(attrs={
                'oninvalid': 'this.setCustomValidity(\'{0}\')'.format(accept_terms_validity_message),
                'onchange': "setCustomValidity('')"
            }))
        over_18_validity_message = _('You must be over 18 to play on sharkz.bet')
        self.fields['over_18'] = forms.BooleanField(
            initial=True, required=True, label=_('I am over 18 years old'),
            error_messages={'required': over_18_validity_message},
            widget=forms.CheckboxInput(attrs={
                'oninvalid': 'this.setCustomValidity(\'{0}\')'.format(over_18_validity_message),
                'onchange': "setCustomValidity('')"
            }))

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        if 'display_name' in cleaned_data and len(cleaned_data['display_name']) > 28:
            raise forms.ValidationError(
                {'display_name': [_('Display name must be shorter than 28 characters in length'), ]})
        if 'email' in cleaned_data and len(cleaned_data['email']) > 74:
            raise forms.ValidationError({'email': [_('E-mail address must be shorter than 74 characters'), ]})

        if 'email' in cleaned_data:
            existing_mails = User.objects.filter(email=cleaned_data['email'])
            if len(existing_mails) > 0:
                raise forms.ValidationError(
                    {'email': [_('This e-mail address already exists. '
                                 'If this is your e-mail, please reset password.'), ]})
        if 'display_name' in cleaned_data:
            existing_first_name = User.objects.filter(first_name__iexact=cleaned_data['display_name'])
            if len(existing_first_name) > 0:
                raise forms.ValidationError(
                    {'display_name': [_('This display name is already taken. '
                                 'If this is your display name by any chance, please log in.'), ]})
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


class CreatePasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"),
                                    min_length=5,
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    min_length=5,
                                    widget=forms.PasswordInput)


class RequestDisplayNameForm(forms.Form):
    display_name = forms.CharField(label=_('Choose Display Name'), required=True, max_length=28, min_length=3)

    def clean(self):
        cleaned_data = super(RequestDisplayNameForm, self).clean()
        if 'display_name' in cleaned_data:
            users = User.objects.filter(first_name__iexact=cleaned_data['display_name'])
            if len(users) > 0:
                raise forms.ValidationError(
                    {'display_name':
                         [_('Sorry, but name "{0}" is already taken'.format(cleaned_data['display_name']))]})


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


class BettingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        shots = kwargs.pop('shots')
        player = kwargs.pop('player')
        super(BettingForm, self).__init__(*args, **kwargs)
        for shot in shots:
            odd1 = convert_odd_format(shot.match.odd1, player.odd_format)
            oddX = convert_odd_format(shot.match.oddX, player.odd_format)
            odd2 = convert_odd_format(shot.match.odd2, player.odd_format)
            self.fields['%d_%d' % (shot.user_round.id, shot.match.id)] = forms.IntegerField(
                initial=shot.shot,
                required=False,
                label='%s - %s' % (shot.match.home_team.name, shot.match.away_team.name),
                widget=forms.RadioSelect(choices=[[1, odd1], [0, oddX], [2, odd2]]))

    def clean(self):
        cleaned_data = super(BettingForm, self).clean()
        for name, value in self.cleaned_data.items():
            if value is None:
                raise forms.ValidationError(_('You must place all bets'))
        return cleaned_data


class PointsForm(forms.Form):
    def __init__(self, *args, **kwargs):
            super(PointsForm, self).__init__(*args, **kwargs)
            self.fields['recalculate_points'] = forms.BooleanField(
                initial=True, required=False, label=_('Recalculate points'))
            self.fields['clear_cache'] = forms.BooleanField(
                initial=True, required=False, label=_('Clear cache'))
            self.fields['repopulate_cache'] = forms.BooleanField(
                initial=True, required=False, label=_('Repopulate cache'))
