# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.forms.models import ModelForm
from django.utils.translation import gettext as _

from nmkapp.models import Round, Match, Shot, Player, Team


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
        if score is None:
            raise forms.ValidationError(_('There should be colon between two numbers'))
        scores = score.split(':')
        if len(scores) != 2:
            raise forms.ValidationError(_('There should be colon between two numbers'))
        try:
            int(scores[0])
            int(scores[1])
        except ValueError:
            raise forms.ValidationError(_('Cannot parse numbers in result'))
        return cleaned_data


class PlayerForm(ModelForm):
    language = forms.ChoiceField(choices=settings.LANGUAGES)

    class Meta:
        model = Player
        fields = ['language', 'timezone', 'odd_format', 'send_mail_round_started', 'send_mail_reminder',
                  'send_mail_new_round', 'send_mail_results_available']
        labels = {'language': _('Language'), 'timezone': _('Time zone'), 'odd_format': _('Odd format'),
                  'send_mail_reminder': _('Betting reminder'),
                  'send_mail_round_started': _('All bets are final'),
                  'send_mail_new_round': _('New round available'),
                  'send_mail_results_available': _('All results are final')}

    def clean(self):
        cleaned_data = super(PlayerForm, self).clean()
        language = cleaned_data.get('language')
        available_languages = [lang_code for (lang_code, lang_name) in settings.LANGUAGES]
        if language not in available_languages:
            raise forms.ValidationError({'language': [_('Language {} is not available').format(language), ]})
        return cleaned_data
