# -*- coding: utf-8 -*-

from django.forms.models import ModelForm
from nmkapp.models import Round, Match, Shot, Player, Team, Group
from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import PasswordInput


class RegisterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(initial='', required=True, label='Ime*', max_length=28)
        self.fields['last_name'] = forms.CharField(initial='', required=True, label='Prezime*', max_length=28)
        self.fields['email'] = forms.EmailField(initial='', required=True, label='E-mail*', max_length=74)
        self.fields['username'] = forms.CharField(initial='', required=True, label='Korisničko ime*', max_length=28)
        self.fields['password'] = forms.CharField(initial='', required=True, label='Lozinka*', max_length=28,
                                                  min_length=5, widget=PasswordInput)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        if 'first_name' in cleaned_data and len(cleaned_data['first_name']) > 28:
            raise forms.ValidationError({'first_name': [u"Ime mora biti manje od 28 karaktera", ]})
        if 'last_name' in cleaned_data and len(cleaned_data['last_name']) > 28:
            raise forms.ValidationError({'last_name': [u"Prezime mora biti manje od 28 karaktera", ]})
        if 'email' in cleaned_data and len(cleaned_data['email']) > 74:
            raise forms.ValidationError({'email': [u"E-mail mora biti manji od 74 karaktera", ]})
        if 'username' in cleaned_data and len(cleaned_data['username']) > 28:
            raise forms.ValidationError({'username': [u"Korisničko ime mora biti manje od 28 karaktera", ]})
        
        if 'username' in cleaned_data:
            existing_usernames = User.objects.filter(username=cleaned_data['username'])
            if len(existing_usernames) > 0:
                raise forms.ValidationError({'username': [u"Korisničko ime već postoji", ]})
        if 'email' in cleaned_data: 
            existing_mails = User.objects.filter(email=cleaned_data['email'])
            if len(existing_mails) > 0:
                raise forms.ValidationError(
                    {'email': [u"Ovaj e-mail je već u upotrebi. Resetuj lozinku ako je ovo Vaš mail.", ]})
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        rp = kwargs.pop('rp')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(initial='', required=True, label='E-mail', max_length=74)


class ResetPasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        rp = kwargs.pop('passwords')
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'] = forms.CharField(initial='', required=True, label='Lozinka*', max_length=28,
                                                  min_length=5, widget=PasswordInput)
        self.fields['password2'] = forms.CharField(initial='', required=True, label='Lozinka ponovo*', max_length=28,
                                                   min_length=5, widget=PasswordInput)

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        if ('password' in cleaned_data) and ('password2' in cleaned_data):
            if cleaned_data['password'] != cleaned_data['password2']:
                raise forms.ValidationError({'password2': [u"Lozinke se ne poklapaju", ]})
        return cleaned_data


class NewGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group')
        super(NewGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(initial='', required=True, label=u'Napravi novu ekipu', max_length=64,
                                              min_length=5)

    def clean(self):
        cleaned_data = super(NewGroupForm, self).clean()
        if 'name' in cleaned_data:
            if len(cleaned_data['name']) > 64:
                raise forms.ValidationError({'name': [u"Ime ekipe predugačko", ]})
            groups = Group.objects.filter(name=cleaned_data['name'])
            if len(groups) > 0:
                raise forms.ValidationError({'name': [u"Nažalost, neko je već uzeo ovo ime ekipe", ]})
        return cleaned_data


class AddToGroupForm(forms.Form):
    def __init__(self, player, *args, **kwargs):
        self._player = player
        group_key = kwargs.pop('group_key')
        super(AddToGroupForm, self).__init__(*args, **kwargs)
        self.fields['key'] = forms.CharField(initial='', required=True,
                                             label=u'Ako si je dobio, unesi šifru-pozivnicu za upad u ekipu:',
                                             max_length=8, min_length=0)

    def clean(self):
        cleaned_data = super(AddToGroupForm, self).clean()
        if 'key' in cleaned_data:
            if len(cleaned_data['key']) < 8:
                raise forms.ValidationError({'key': [u"Šifra-pozivnica mora da ima 8 brojeva", ]})
            groups = Group.objects.filter(group_key=cleaned_data['key'])
            if len(groups) == 0:
                raise forms.ValidationError({'key': [u"Neispravna šifra-pozivnica", ]})
            if len(Group.objects.filter(group_key=cleaned_data['key']).filter(player__in=[self._player])) > 0:
                raise forms.ValidationError({'key': [u"Već ste u ovoj ekipi", ]})
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
        home_team = cleaned_data.get("home_team")
        away_team = cleaned_data.get("away_team")
        this_round = cleaned_data.get("round")
        
        if home_team == away_team:
            raise forms.ValidationError(u"Tim ne može da igra protiv samog sebe")
        if Shot.objects.filter(user_round__round=this_round).exists():
            raise forms.ValidationError(
                u"Ne možeš dodati nove mečeve u ovo kolo jer su neki ljudi već tipovali u ovom kolu")
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
                    widget=forms.RadioSelect(
                        choices=[[1, str(shot.match.odd1)], [0, str(shot.match.oddX)], [2, str(shot.match.odd2)]]))

    def clean(self):
        cleaned_data = super(BettingForm, self).clean()
        for name, value in self.cleaned_data.items():
            if value is None:
                raise forms.ValidationError(u"Morate uneti sve tipove")
        return cleaned_data


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['send_mail']
        labels = {'send_mail': u"Primaj obaveštenja na mail"}
