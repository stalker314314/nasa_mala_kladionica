# -*- coding: utf-8 -*-

import logging
import random
import string
from datetime import datetime
from operator import itemgetter

import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail.message import EmailMessage
from django.db import transaction
from django.db.models.aggregates import Min
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.utils import timezone, translation
from django.utils.translation import gettext as _

from nmkapp.cache import StandingsCache, RoundStandingsCache
from nmkapp.forms import AddToGroupForm, BettingForm, ForgotPasswordForm, NewGroupForm, PointsForm, \
    RegisterForm, ResetPasswordForm
from nmkapp.logic import recalculate_round_points, recalculate_total_points
from nmkapp.model_forms import RoundForm, MatchForm, ResultsForm, PlayerForm
from nmkapp.models import Round, UserRound, Shot, Match, Team, Player, Group

logger = logging.getLogger(__name__)


def id_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@transaction.atomic
def register(request):
    logger.info('User is on register page')
    last_registration_time = datetime(2018, 6, 14, 16, 0, tzinfo=timezone.utc)
    if timezone.now() >= last_registration_time:
        raise Http404()

    registered = False
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            language = translation.get_language()
            available_languages = [lang_code for (lang_code, lang_name) in settings.LANGUAGES]
            if language not in available_languages:
                language = settings.LANGUAGE_CODE
            cleaned_data = form.cleaned_data
            user = User.objects.create_user(username=cleaned_data['email'],
                                            email=cleaned_data['email'],
                                            password=cleaned_data['password'],
                                            first_name=cleaned_data['first_name'],
                                            last_name=cleaned_data['last_name'],
                                            is_active=False,
                                            last_login=timezone.now())
            user.player.activation_code = id_generator()
            user.player.save()
            player = Player.objects.filter(user__id=user.id).get()
            player.language = language
            player.timezone = 'Europe/London'
            player.odd_format = Player.DECIMAL
            player.save()

            with translation.override(language):
                subject = _('[nmk] NMK registration successful')
                template = loader.get_template('mail/registered.html')
                message_text = template.render(
                    {'link': 'http://nmk.kokanovic.org/activate?id=%s' % user.player.activation_code})
            logger.info('Sending mail that user is registered to %s', user.email)
            msg = EmailMessage(subject, message_text, 'nmk@kokanovic.org', to=[user.email, ])
            msg.content_subtype = 'html'
            msg.send(fail_silently=False)
            registered = True
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form, 'registered': registered, 'no_menu': True})


@transaction.atomic
def forgotpassword(request):
    logger.info('User is on forgot password page')
    reset = False
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, rp={})
        if form.is_valid():
            cleaned_data = form.cleaned_data
            users = User.objects.filter(email=cleaned_data['email'])
            if len(users) > 0:
                user = users[0]
                user.player.reset_code = id_generator(size=32)
                user.player.save()

                with translation.override(user.player.language):
                    subject = _('[nmk] Reset password request')
                    template = loader.get_template('mail/resetpassword.html')
                    message_text = template.render(
                        {'link': 'http://nmk.kokanovic.org/profile/reset?id=%s' % user.player.reset_code,
                         'email': user.email})
                logger.info('Sending mail to reset user\'s password to %s', user.email)
                msg = EmailMessage(subject, message_text, 'nmk@kokanovic.org', to=[user.email, ])
                msg.content_subtype = 'html'
                msg.send(fail_silently=False)
                reset = True
    else:
        form = ForgotPasswordForm(rp={})
    return render(request, 'forgotpassword.html', {'form': form, 'reset': reset})


@transaction.atomic
def activation(request):
    logger.info('User is on activation page')
    activation_id = request.GET.get('id', '')
    success = False

    player = None
    if activation_id != '':
        players = Player.objects.filter(activation_code=activation_id)
        if len(players) == 1:
            players[0].user.is_active = True
            players[0].user.save()
            success = True
            player = players[0]
            StandingsCache().clear()
            rounds = RoundStandingsCache.clear_group()
            for nmk_round in rounds:
                RoundStandingsCache.clear_round(nmk_round)
    return render(request, 'activation.html', {'success': success, 'player': player})


@transaction.atomic
def reset_password(request):
    logger.info('User is on reset password page')
    reset_code = request.GET.get('id', '')
    nonvalid = True
    reset = False
    if reset_code != '':
        players = Player.objects.filter(reset_code=reset_code)
        if len(players) == 1:
            player = players[0]
            nonvalid = False
    if nonvalid:
        return render(request, 'resetpassword.html', {'nonvalid': nonvalid})

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST, passwords={})
        if form.is_valid():
            cleaned_data = form.cleaned_data
            player.user.set_password(cleaned_data['password'])
            player.user.save()
            reset = True
    else:
        form = ResetPasswordForm(passwords={})
    return render(request,
                  'resetpassword.html',
                  {'form': form, 'id': reset_code, 'nonvalid': nonvalid, 'reset': reset,
                   'email': player.user.email}
                  )


@login_required
@transaction.atomic
def home(request):
    logger.info('User %s is on betting page', request.user)
    active_rounds = Round.objects.filter(active=True).order_by('id')
    if len(active_rounds) == 0:
        messages.add_message(request, messages.INFO,
                             _('There is no active round currently to place bets, try again later'))
        return render(request, 'home.html', {'shots': []})

    bets = []
    for active_round in active_rounds:
        user_rounds = UserRound.objects.select_related('round').filter(user=request.user).filter(round=active_round)
        if len(user_rounds) != 1:
            messages.add_message(request, messages.INFO,
                                 _('There is no active round currently to place bets, try again later'))
            return render(request, 'home.html', {'shots': []})
    
        user_round = user_rounds[0]
        shots = Shot.objects.select_related('match', 'match__home_team', 'match__away_team', 'user_round').\
            filter(user_round=user_round).order_by('match__start_time')
        if len(shots) == 0:
            matches = Match.objects.select_related('home_team', 'away_team').filter(round=user_round.round).\
                order_by('start_time')
            shots = []
            for match in matches:
                shot = Shot(user_round=user_round, match=match)
                shots.append(shot)

        betting_allowed = True
        for shot in shots:
            if shot.match.start_time < timezone.now():
                betting_allowed = False
                break
    
        if not user_round.shot_allowed:
            betting_allowed = False

        form = None
        if betting_allowed:
            if request.method == 'POST' and\
                    ('save_'+str(active_round.id) in request.POST or
                     'final_save_'+str(active_round.id) in request.POST):
                logger.info('User %s posted betting', request.user)
                form = BettingForm(request.POST, shots=shots, player=request.user.player)
                if form.is_valid():
                    logger.info('User %s posted valid form %s', request.user, form.cleaned_data)
                    for user_round_match in form.cleaned_data:
                        user_round_id = int(user_round_match.split('_')[0])
                        match_id = int(user_round_match.split('_')[1])
                        shot = next(shot for shot in shots
                                    if shot.user_round.id == user_round_id and shot.match.id == match_id)
                        if shot is not None:
                            shot.shot = form.cleaned_data[user_round_match]
                            shot.save()
                    if 'final_save_'+str(active_round.id) in request.POST:
                        logger.info('User %s posted final save', request.user)
                        user_round.shot_allowed = False
                        user_round.save()
                    RoundStandingsCache.clear_round(user_round.round)
                    messages.add_message(request, messages.INFO, _('Bets successfully saved'))
                    return HttpResponseRedirect('/')
            else:
                form = BettingForm(shots=shots, player=request.user.player)

        time_left = format_time_left(shots)
        one_round_to_bet = {'form': form, 'shots': shots, 'round': active_round, 'time_left': time_left}
        bets.append(one_round_to_bet)
    return render(request, 'home.html', {'bets': bets})


def format_time_left(shots):
    if len(shots) > 0:
        seconds_left = (shots[0].match.start_time - timezone.now()).total_seconds()
        if seconds_left > 60*60*24:
            days = int(seconds_left/(60*60*24))
            return '%dd %dh' % (days, int((seconds_left - (days * 60 * 60 * 24))/(60 * 60)))
        elif seconds_left > 60*60:
            hours = int(seconds_left/(60*60))
            return '%dh %dmin' % (hours, int((seconds_left - hours * 60 * 60)/60))
        elif seconds_left > 60:
            minutes = int(seconds_left/60)
            print(seconds_left, minutes)
            return '%dmin %dsec' % (minutes, int(seconds_left - minutes * 60))
        elif seconds_left > 0:
            return '%dsec' % seconds_left
        else:
            return _('first match already started')
    else:
        return _('N/A')


@login_required
@transaction.atomic
def profile(request):
    if request.method == 'POST' and 'profile_change' in request.POST:
        old_language = request.user.player.language  # Save old language before we save form
        form = PlayerForm(request.POST, instance=request.user.player)
        if form.is_valid():
            form.save()
            request.session[settings.TIMEZONE_SESSION_KEY] = form.cleaned_data['timezone'].zone
            new_language = form.cleaned_data['language']
            if new_language != old_language:
                translation.activate(new_language)
                if hasattr(request, 'session'):
                    request.session[translation.LANGUAGE_SESSION_KEY] = new_language
            messages.add_message(request, messages.INFO, _('Settings successfully saved'))
    else:
        form = PlayerForm(instance=request.user.player)

    groups = Group.objects.filter(players__in=[request.user])
    return render(request, 'profile.html', {'form': form, 'current_user': request.user})


@login_required
@transaction.atomic
def crew(request):
    if request.method == 'POST' and 'new_group' in request.POST:
        form_new_group = NewGroupForm(request.POST, group={})
        if form_new_group.is_valid():
            cleaned_data = form_new_group.cleaned_data
            new_group = Group(name=cleaned_data['name'], group_key=id_generator(size=8, chars=string.digits),
                              owner=request.user)
            new_group.save()
            new_group.players.add(request.user)
            new_group.save()
            messages.add_message(request, messages.INFO,
                                 _('Crew created successfully. Now you can send invite code "%s" to your friends '
                                   'using chat/mail/SMS, so they too can join your new crew') % new_group.group_key)
    else:
        form_new_group = NewGroupForm(group={})

    if request.method == 'POST' and 'add_to_group' in request.POST:
        form_add_group = AddToGroupForm(request.user, request.POST, group_key={})
        if form_add_group.is_valid():
            cleaned_data = form_add_group.cleaned_data
            groups = Group.objects.filter(group_key=cleaned_data['key'])
            group = groups[0]
            group.players.add(request.user)
            group.save()
            RoundStandingsCache.clear_group(group)
            messages.add_message(request, messages.INFO, _('Joined crew successfully'))
    else:
        form_add_group = AddToGroupForm(request.user.player, group_key={})

    groups = Group.objects.filter(players__in=[request.user])
    return render(request, 'crew.html',
                  {'form_new_group': form_new_group, 'form_add_group': form_add_group,
                   'groups': groups, 'current_user': request.user}
                  )


@login_required
def results(request):
    return render(request, 'results.html')


def paypal(request):
    email = 'not logged'
    success = False
    if request.user.is_authenticated:
        email = request.user.email
        request.user.player.in_money = True
        request.user.player.save()
        
        groups = Group.objects.filter(id=1)
        group = groups[0]
        group.players.add(request.user)
        group.save()
        RoundStandingsCache.clear_group(group)
        success = True

    msg = EmailMessage(_('[nmk] Player payed paypal'), _('Player %s') % email, 'nmk@kokanovic.org',
                       to=['branko@kokanovi.org', ])
    msg.content_subtype = 'html'
    msg.send(fail_silently=True)
    return render(request, 'paypal.html', {'success': success})


@login_required
def results_league(request):
    groups = []
    group_labels = Team.objects.values('group_label').order_by('group_label').distinct()
    for group_label in group_labels:
        matches = Match.objects.filter(round__group_type=Round.LEAGUE).\
            filter(home_team__group_label=group_label['group_label']).order_by('round')
        teams = Team.objects.filter(group_label=group_label['group_label'])
        league = []
        for team in teams:
            league.append([team.name, 0, 0, 0, 0, 0])
        for match in matches:
            if match.result is None:
                continue
            team_in_league = None
            for l in league:
                if l[0] == match.home_team.name:
                    team_in_league = l
            if team_in_league is not None:
                team_in_league[1] += 1
                if match.result == 1:
                    team_in_league[2] += 1
                    team_in_league[5] += 3
                elif match.result == 0:
                    team_in_league[3] += 1
                    team_in_league[5] += 1
                else:
                    team_in_league[4] += 1
                    
            team_in_league = None
            for l in league:
                if l[0] == match.away_team.name:
                    team_in_league = l
            if team_in_league is not None:
                team_in_league[1] += 1
                if match.result == 1:
                    team_in_league[4] += 1
                elif match.result == 0:
                    team_in_league[3] += 1
                    team_in_league[5] += 1
                else:
                    team_in_league[5] += 3
                    team_in_league[2] += 1
        league = sorted(league, key=itemgetter(5), reverse=True)
        groups.append({'league': league, 'matches': matches, 'label': chr(group_label['group_label'] + ord('A'))})
    return render(request, 'results_league.html', {'groups': groups})


@login_required
def results_cup(request):
    rounds = []
    all_rounds = Round.objects.filter(group_type=Round.CUP).order_by('id')
    for my_round in all_rounds:
        matches = Match.objects.filter(round=my_round).order_by('start_time')
        one_round = [my_round, matches]
        rounds.append(one_round)
    return render(request, 'results_cup.html', {'rounds': rounds})


@login_required
def standings(request):
    selected_group = request.GET.get('group', '')
    all_groups = Group.objects.filter(players__in=[request.user])
    group = Group.objects.filter(players__in=[request.user]).filter(name=selected_group)
    if len(group) != 1:
        selected_group = ''
        group = None
    else:
        group = group[0]
    logger.info('User %s is on standings page for group %s', request.user, selected_group)

    rounds = Round.objects.order_by('id')
    
    nmk_standings = StandingsCache(group).get(rounds)

    return render(request,
                  'standings.html',
                  {'rounds': rounds, 'standings': nmk_standings, 'groups': all_groups, 'selected_group': selected_group}
                  )


@login_required
@transaction.atomic
def group_leave(request, group_id):
    group = get_object_or_404(Group, pk=int(group_id))
    # Check if user is in group at all
    if len(Group.objects.filter(pk=int(group_id)).filter(players__in=[request.user])) == 0:
        raise Http404()
    # Check if user is owner of the group
    error = None
    if request.user == group.owner:
        error = _('You cannot leave a crew that you created, you can only completely delete that crew.')

    if not error and request.method == 'POST':
        if '0' in request.POST:
            return HttpResponseRedirect('/crew')
        elif '1' in request.POST:
            RoundStandingsCache.clear_group(group)
            group.players.remove(request.user)
            messages.add_message(request, messages.INFO, _('Successfully left a crw "%s"') % group.name)
            return HttpResponseRedirect('/crew')
    return render(request, 'group_leave.html', {'error': error, 'group': group})


@login_required
@transaction.atomic
def group_delete(request, group_id):
    group = get_object_or_404(Group, pk=int(group_id))
    # Check if user is in group at all
    if len(Group.objects.filter(pk=int(group_id)).filter(players__in=[request.user])) == 0:
        raise Http404()
    # Check if user is owner of the group
    error = None
    if request.user != group.owner:
        error = _('You cannot delete crew that you are not owner of, you can only leave it.')

    if not error and request.method == 'POST':
        if '0' in request.POST:
            return HttpResponseRedirect('/crew')
        elif '1' in request.POST:
            group.players.clear()
            RoundStandingsCache.clear_group(group)
            StandingsCache(group).clear()
            group.delete()
            messages.add_message(request, messages.INFO, _('Crew "%s" deleted') % group.name)
            return HttpResponseRedirect('/crew')
    return render(request, 'group_delete.html', {'error': error, 'group': group})


@login_required
def round_standings(request, round_id):
    this_round = get_object_or_404(Round, pk=int(round_id))
    matches = Match.objects.select_related('round', 'home_team', 'away_team').\
        filter(round=this_round).order_by('start_time', 'id')

    selected_group = request.GET.get('group', '')

    logger.info('User %s is on round standings page for round %s for group %s',
                request.user, this_round.name, selected_group)

    all_groups = Group.objects.filter(players__in=[request.user])
    group = Group.objects.filter(players__in=[request.user]).filter(name=selected_group)
    if len(group) != 1:
        selected_group = ''
        group = None
    else:
        group = group[0]
        
    can_see_standings = False
    is_any_match_started = False
    for match in matches:
        if match.start_time < timezone.now():
            is_any_match_started = True
            break
    if is_any_match_started:
        can_see_standings = True
    else:
        logged_user_rounds = UserRound.objects.filter(user=request.user, round=this_round)
        if len(logged_user_rounds) == 1 and not logged_user_rounds[0].shot_allowed:
            can_see_standings = True

    round_standings_list = []
    
    if can_see_standings:
        round_standings_list = RoundStandingsCache(this_round, group).get()

    return render(request, 'roundstandings.html', {
                'can_see_standings': can_see_standings,
                'matches': matches,
                'round_standings': round_standings_list,
                'round': this_round,
                'groups': all_groups,
                'selected_group': selected_group})


def proposition(request):
    player = None
    if not request.user.is_anonymous:
        player = request.user.player
    return render(request, 'proposition.html', {'player': player})


@staff_member_required
def admin_rounds(request):
    rounds = Round.objects.order_by('id')
    message = ''
    set_active = request.GET.get('set_active', '0')
    try:
        set_active_id = int(set_active)
    except ValueError:
        # Try float.
        set_active_id = 0
    set_inactive = request.GET.get('set_inactive', '0')
    try:
        set_inactive_id = int(set_inactive)
    except ValueError:
        # Try float.
        set_inactive_id = 0
    if set_active_id != 0:
        should_be_active_round = get_object_or_404(Round, pk=int(set_active_id))
        should_be_active_round.active = True
        should_be_active_round.save()
        message = _('Round "%s" set as active') % should_be_active_round.name
        messages.add_message(request, messages.INFO, message)

        if settings.SEND_MAIL:
            all_players = Player.objects.\
                exclude(user__email='').filter(user__is_active=True).filter(send_mail_new_round=True)
            start_time = Match.objects.\
                filter(round=should_be_active_round).aggregate(Min('start_time'))['start_time__min']
            logger.info('Sending mail that round %s is active to %d players',
                        should_be_active_round.name, len(all_players))
            for player in all_players:
                with translation.override(player.language):
                    subject = _('[nmk] New round "%s" available') % should_be_active_round.name
                    template = loader.get_template('mail/round_active.html')
                    message_text = template.render({'round': should_be_active_round, 'start_time': start_time})
                msg = EmailMessage(subject, message_text, 'nmk@kokanovic.org', to=[player.user.email, ])
                msg.content_subtype = 'html'
                msg.send(fail_silently=False)

    elif set_inactive_id != 0:
        should_be_inactive_round = get_object_or_404(Round, pk=int(set_inactive_id))
        should_be_inactive_round.active = False
        should_be_inactive_round.save()
        message = _('Round "%s" set as inactive') % should_be_inactive_round.name
        messages.add_message(request, messages.INFO, message)

    return render(request, 'admin_rounds.html', {'rounds': rounds})


@staff_member_required
@transaction.atomic
def admin_rounds_edit(request):
    if request.method == 'POST':
        form = RoundForm(request.POST)
        if form.is_valid():
            new_round = form.save()
            users = User.objects.all()
            for user in users:
                user_round = UserRound(user=user, round=new_round, shot_allowed=True, points=0)
                user_round.save()
            groups = Group.objects.all()
            for group in groups:
                StandingsCache(group).clear()
            StandingsCache().clear()
            # repopulate cache
            rounds = Round.objects.all()
            for group in groups:
                StandingsCache(group).get(rounds)
            StandingsCache().get(rounds)

            messages.add_message(request, messages.INFO, _('New round "%s" created successfully') % new_round.name)
            return HttpResponseRedirect('/admin/rounds')
    else:
        form = RoundForm()

    return render(request, 'admin_rounds_edit.html', {'form': form, })


@staff_member_required
def admin_matches(request):
    matches = Match.objects.order_by('round__id', 'start_time')
    return render(request, 'admin_matches.html', {'matches': matches})


@staff_member_required
@transaction.atomic
def admin_matches_edit(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _('Match successfully added'))
            return HttpResponseRedirect('/admin/matches')
    else:
        form = MatchForm()

    return render(request, 'admin_matches_edit.html', {'form': form, })


@staff_member_required
def admin_results(request):
    matches = Match.objects.all()
    return render(request, 'admin_results.html', {'matches': matches})


@staff_member_required
@transaction.atomic
def admin_results_change(request, match_id):
    match = get_object_or_404(Match, pk=int(match_id))

    if request.method == 'POST':
        form = ResultsForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            scores = match.score.split(':')
            score_home = int(scores[0])
            score_away = int(scores[1])
            if score_home > score_away:
                match.result = 1
            elif score_home == score_away:
                match.result = 0
            else:
                match.result = 2
            match.save()
            logger.info('User %s set result for match %s', request.user, match)
            recalculate_round_points(match.round)
            messages.add_message(request, messages.INFO, _('Result added successfully'))
            
            # invalidate cache of shots for all user in this round
            RoundStandingsCache.repopulate_round(match.round)
            groups = Group.objects.all()
            for group in groups:
                StandingsCache(group).clear()
            StandingsCache().clear()
            # repopulate cache
            rounds = Round.objects.all()
            for group in groups:
                StandingsCache(group).get(rounds)
            StandingsCache().get(rounds)

            # send mail if this is the last match from round
            if settings.SEND_MAIL:
                count_matches_without_result = Match.objects.all().\
                    filter(round=match.round).filter(result__isnull=True).count()
                if count_matches_without_result == 0:
                    all_players = Player.objects.\
                        exclude(user__email='').filter(user__is_active=True).filter(send_mail_results_available=True)
                    logger.info('Sending mail that round %s have all results to %d', match.round, len(all_players))
                    for player in all_players:
                        with translation.override(player.language):
                            subject = _('[nmk] All results from round "%s" received') % match.round.name
                            template = loader.get_template('mail/result_added.html')
                            message_text = template.render({'round': match.round})
                        msg = EmailMessage(subject, message_text, 'nmk@kokanovic.org', to=[player.user.email, ])
                        msg.content_subtype = 'html'
                        msg.send(fail_silently=False)
                
            return HttpResponseRedirect('/admin/results')
    else:
        form = ResultsForm(instance=match)

    return render(request, 'admin_results_change.html', {'form': form, 'match': match})


@staff_member_required
@transaction.atomic
def admin_points(request):
    if request.method == 'POST':
        form = PointsForm(request.POST)
        if form.is_valid():
            recalculate_points = form.cleaned_data['recalculate_points']
            clear_cache = form.cleaned_data['clear_cache']
            repopulate_cache = form.cleaned_data['repopulate_cache']

            if recalculate_points:
                rounds = Round.objects.all()
                for nmk_round in rounds:
                    recalculate_round_points(nmk_round, recalculate_total=False)
                recalculate_total_points()
            if clear_cache or repopulate_cache:
                groups = Group.objects.all()
                for group in groups:
                    StandingsCache(group).clear()
                StandingsCache().clear()
                for nmk_round in rounds:
                    RoundStandingsCache.clear_round(nmk_round)
            if repopulate_cache:
                groups = Group.objects.all()
                rounds = Round.objects.order_by('id')
                for group in groups:
                    StandingsCache(group).get(rounds)
                StandingsCache().get(rounds)
                for nmk_round in rounds:
                    for group in groups:
                        RoundStandingsCache(nmk_round, group).get()
                    RoundStandingsCache(nmk_round).get()
    else:
        form = PointsForm()
    return render(request, 'admin_points.html', {'form': form})


class CustomLoginView(LoginView):
    def get_success_url(self):
        url = super(CustomLoginView, self).get_success_url()
        user = self.request.user
        if user.is_authenticated:
            language = user.player.language or settings.LANGUAGE_CODE
            available_languages = [lang_code for (lang_code, lang_name) in settings.LANGUAGES]
            if language in available_languages:
                translation.activate(language)
                if hasattr(self.request, 'session'):
                    self.request.session[translation.LANGUAGE_SESSION_KEY] = language
            timezone = user.player.timezone
            if timezone.zone in pytz.all_timezones:
                self.request.session[settings.TIMEZONE_SESSION_KEY] = timezone.zone
        return url
