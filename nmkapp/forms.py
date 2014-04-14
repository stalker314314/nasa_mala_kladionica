# -*- coding: utf-8 -*-

from django.forms.models import ModelForm
from nmkapp.models import Round, Match, Shot
from django import forms
from nmkapp.widgets import DateTimeWidget

class RoundForm(ModelForm):
    class Meta:
        model = Round
        fields = ['name', 'group_type']

class MatchForm(ModelForm):
    
    class Meta:
        model = Match
        fields = ['home_team', 'away_team', 'start_time', 'round', 'odd1', 'oddX', 'odd2']
        widgets = {
            #Use localization
            'start_time': DateTimeWidget(attrs={'id':"start_time"}, usel10n = False)
        }

    def clean(self):
        cleaned_data = super(MatchForm, self).clean()
        home_team = cleaned_data.get("home_team")
        away_team = cleaned_data.get("away_team")
        this_round = cleaned_data.get("round")
        
        if home_team == away_team:
            raise forms.ValidationError(u"Tim ne može da igra protiv samog sebe")
        if Shot.objects.filter(user_round__round=this_round).exists():
            raise forms.ValidationError(u"Ne možete dodati nove mečeve u ovo kolo jer su neki ljudi već tipovali u ovom kolu")
        matches = Match.objects.filter(round=this_round)
        for match in matches:
            if match.home_team == home_team or match.away_team == home_team:
                raise forms.ValidationError(u"Tim %s već igra u ovom kolu" % home_team.name)
            if match.home_team == away_team or match.away_team == away_team:
                raise forms.ValidationError(u"Tim %s već igra u ovom kolu" % away_team.name)
        return cleaned_data

class ResultsForm(ModelForm):
    class Meta:
        model = Match
        fields = ['score']
        labels = {'score': u"Rezultat (u obliku <domaćin>:<gost>)"}

    def clean(self):
        cleaned_data = super(ResultsForm, self).clean()
        score = cleaned_data.get("score")
        scores = score.split(":")
        if len(scores) != 2:
            raise forms.ValidationError(u"Između dva broja mora da stoji dve tačke")
        try:
            int(scores[0])
            int(scores[1])
        except ValueError:
            raise forms.ValidationError(u"Ne mogu da parsiram brojeve u rezultatu")
        return cleaned_data

class BettingForm(forms.Form):

    def __init__(self, *args, **kwargs):
            shots = kwargs.pop('shots')
            super(BettingForm, self).__init__(*args, **kwargs)
            for shot in shots:
                self.fields['%d_%d' % (shot.user_round.id, shot.match.id)] = forms.IntegerField(
                    initial=shot.shot,
                    required=False,
                    label="%s - %s" % (shot.match.home_team.name, shot.match.away_team.name),
                    widget=forms.RadioSelect(choices=[[1, str(shot.match.odd1)],[0, str(shot.match.oddX)], [2, str(shot.match.odd2)]]))

    def clean(self):
        cleaned_data = super(BettingForm, self).clean()
        for name, value in self.cleaned_data.items():
            if value == None:
                raise forms.ValidationError(u"Morate uneti sve tipove")
        return cleaned_data