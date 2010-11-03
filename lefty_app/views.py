from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.db import IntegrityError, connection
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from lefty_app.models import *
from lefty_app.forms import *
from settings import MEDIA_URL
from tagging.models import Tag, TaggedItem
from tagging.utils import get_tag_list
import operator


def add_image_to_challenge(request, image_id, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    challenge.approved = True
    image = get_object_or_404(Image, pk=image_id)
    challenge_image, created = ChallengeImage.objects.get_or_create(
                                    challenge=challenge,
                                    image=image,
                                    order=challenge.number_of_images + 1)
    challenge.number_of_images = challenge.number_of_images + 1
    challenge.save()
    return HttpResponseRedirect('/setup_challenge_images/' + str(challenge_id))


def challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    challenge_images_list = ChallengeImage.objects.filter(
        challenge=challenge).order_by('order')
    paginator = Paginator(challenge_images_list, 1)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        challenge_images = paginator.page(page)
    except (EmptyPage, InvalidPage):
        challenge_images = paginator.page(paginator.num_pages)
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'challenge_images': challenge_images,
        'challenge': challenge,
        'media_url': MEDIA_URL,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('challenge.html', variables,
                              context_instance=RequestContext(request))


def challenge_entry(request, year, month, day, slug):
    date_stamp = time.strptime(year + month + day, "%Y%b%d")
    date_created = datetime.date(*date_stamp[:3])
    challenge = Challenge.objects.get(date_created__year=date_created.year,
                              date_created__month=date_created.month,
                              date_created__day=date_created.day,
                              slug=slug)
    challenge_images_list = ChallengeImage.objects.filter(
        challenge=challenge).order_by('order')
    paginator = Paginator(challenge_images_list, 1)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        challenge_images = paginator.page(page)
    except (EmptyPage, InvalidPage):
        challenge_images = paginator.page(paginator.num_pages)
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'challenge_images': challenge_images,
        'challenge': challenge,
        'media_url': MEDIA_URL,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('challenge.html', variables,
                              context_instance=RequestContext(request))


def challenge_vote(request, challenge_id, vote):
    try:
        user = request.user
        # vote == 'up' or 'down'. Don't let someone vote up 2,634 points
        if vote == 'up':
            vote_int = 1
        else:
            vote_int = -1
        challenge = get_object_or_404(Challenge, id=challenge_id)
        user_voted = challenge.users_voted.filter(
            username=request.user.username)
        if not user_voted:
            challenge.score += vote_int
            challenge.users_voted.add(request.user)
            if vote == 'up':
                challenge.users_voted_up.add(request.user)
            else:
                challenge.users_voted_down.add(request.user)
        challenge.save()
    except:
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/')


def feedback(request):
    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST)
        received = False
        if feedback_form.is_valid():
            feedback, created = Feedback.objects.get_or_create(
                                message=feedback_form.cleaned_data['message'],
                                email=feedback_form.cleaned_data['email'],)
            if created:
                received = True
                feedback_form = FeedbackForm()
    else:
        feedback_form = FeedbackForm()
        received = False
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'received': received,
        'feedback_form': feedback_form,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('feedback.html', variables,
                              context_instance=RequestContext(request))


def find_challenges(request):
    if request.POST:
        form = FindChallengesForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            challenges_list = Challenge.objects.filter(name__icontains=name)
    else:
        form = FindChallengesForm()
        challenges_list = Challenge.objects.filter(approved=True).order_by(
            '-date_created')
    paginator = Paginator(challenges_list, 12)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        challenges = paginator.page(page)
    except (EmptyPage, InvalidPage):
        challenges = paginator.page(paginator.num_pages)
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'form': form,
        'challenges': challenges,
        'media_url': MEDIA_URL,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('find_challenges.html', variables,
                              context_instance=RequestContext(request))


@login_required
def image_upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            submitters_IP = request.META['REMOTE_ADDR']
            if submitters_IP == '127.0.0.1':
                submitters_IP = '68.12.157.90'
            user = request.user

            image, created = Image.objects.get_or_create(
                                    image=form.cleaned_data['image'],
                                    thumbnail_small=form.cleaned_data['image'],
                                    thumbnail_large=form.cleaned_data['image'],
                                    title=form.cleaned_data['title'],
                                    media_type=1,
                                    user=user,
                                    tags=form.cleaned_data['tags'],
                                    ip=submitters_IP,
                                    )
            form = ImageForm()
    else:
        form = ImageForm()
    try:
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'form': form,
        'media_url': MEDIA_URL,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('image_upload.html', variables,
                              context_instance=RequestContext(request))


def legal(request):
    return render_to_response('legal.html')


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


def lose(request, challenge_id):
    challenges = Challenge.objects.filter(approved=True)[:10]
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'challenges': challenges,
        'media_url': MEDIA_URL,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('lose.html', variables,
                              context_instance=RequestContext(request))


def main_page(request):
    if request.GET.has_key('id'):
        id = request.GET['id']
        featured = Image.objects.get(id=id, approved=True)
        feature_list = Image.objects.filter(approved=True, pk__gte=int(id))
        gallery = TaggedItem.objects.get_related(featured,
                                                 Image.objects.filter(
                                                     approved=True))[:14]
    else:
        feature_list = Image.objects.filter(approved=True)
        feature_list = feature_list.order_by('-date_created')
        gallery = feature_list.order_by('?')[:14]
    challenges = Challenge.objects.filter(approved=True).order_by(
        '-score')[:10]
    tags = Tag.objects.usage_for_model(Image, counts=True, min_count=None,
                                       filters=None)[:75]
    paginator = Paginator(feature_list, 1)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        features = paginator.page(page)
    except (EmptyPage, InvalidPage):
        features = paginator.page(paginator.num_pages)
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'features': features,
        'gallery': gallery,
        'challenges': challenges,
        'media_url': MEDIA_URL,
        'tags': tags,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('main.html', variables,
                              context_instance=RequestContext(request))


@login_required
def move(request, direction, challenge_image_id):
    challenge_image = get_object_or_404(ChallengeImage, pk=challenge_image_id)
    user = request.user
    challenge = challenge_image.challenge
    if user == challenge.user:
        if direction == "up":
            challenge_image.move_up(challenge_image.id)
        if direction == "down":
            challenge_image.move_down(challenge_image.id)
    return HttpResponseRedirect('/setup_challenge_images/' + str(challenge.id))


def registration_page(request):
    msg = ''
    if request.GET.has_key('msg'):
        msg_id = request.GET['msg']
        if msg_id == 1:
            msg = 'You can only win a badge for a challenge if you are ' +
            'registered.  Why not get started today?'
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                            username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'],
                            email=form.cleaned_data['email'],
                            )
            user_profile = UserProfile.objects.get_or_create(
                                user=user,)
            return HttpResponseRedirect('/login/')
    else:
        form = RegistrationForm()
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'form': form,
        'msg': msg,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('registration/register.html', variables,
                              context_instance=RequestContext(request))


@login_required
def remove(request, challenge_image_id):
    challenge_image = get_object_or_404(ChallengeImage, pk=challenge_image_id)
    user = request.user
    challenge = challenge_image.challenge
    if user == challenge.user:
        challenge_image.delete()
    return HttpResponseRedirect('/setup_challenge_images/' + str(challenge.id))


@login_required
def setup_challenge(request):
    badges = Badge.objects.all().order_by('name')
    if request.POST:
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge, created = Challenge.objects.get_or_create(
                                    approved=False,
                                    badge=form.cleaned_data['badge'],
                                    name=form.cleaned_data['name'],
                                    number_of_images=0,
                                    number_taken=0,
                                    user=request.user,
                                    votes=0)
            if created:
                return HttpResponseRedirect('/setup_challenge_images/' +
                                            str(challenge.id))
    else:
        form = ChallengeForm()
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'form': form,
        'media_url': MEDIA_URL,
        'badges': badges,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('setup_challenge.html', variables,
                              context_instance=RequestContext(request))


@login_required
def setup_challenge_images(request, challenge_id):
    challenge = Challenge.objects.get(pk=int(challenge_id))
    challenge_images = ChallengeImage.objects.filter(
        challenge=challenge).order_by('order')
    if request.POST:
        form = SearchForm(request.POST)
        if form.is_valid():
            tag_search = form.cleaned_data['tag']
            title_search = form.cleaned_data['title']
            search_results = Image.objects.filter(approved=True,
                                                title__icontains=title_search,
                                                tags__icontains=tag_search)
    else:
        form = SearchForm()
        user = request.user
        search_results = Image.objects.filter(approved=True, user=user)

    paginator = Paginator(search_results, 12)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pic_results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pic_results = paginator.page(paginator.num_pages)
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'form': form,
        'media_url': MEDIA_URL,
        'challenge': challenge,
        'challenge_images': challenge_images,
        'pic_results': pic_results,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('setup_challenge_images.html', variables,
                              context_instance=RequestContext(request))


def tag_page(request, tag_name):
    try:
        my_tag = Tag.objects.get(name=tag_name)
        tags = Tag.objects.filter().order_by('?')[:10]
    except:
        my_tag = ''
        tags = Tag.objects.filter().order_by('?')[:10]
    if request.GET.has_key('id'):
        id = request.GET['id']
        featured = Image.objects.get(id=id, approved=True)
        feature_list = Image.objects.filter(approved=True, id__gte=id)
        gallery = TaggedItem.objects.get_related(featured,
                                                 Image.objects.filter(
                                                     approved=True))[:6]
    else:
        feature_list = TaggedItem.objects.get_by_model(Image, my_tag)
        gallery = TaggedItem.objects.get_by_model(Image, my_tag)
        gallery = gallery.filter(approved=True)

    paginator = Paginator(feature_list, 1)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        features = paginator.page(page)
    except (EmptyPage, InvalidPage):
        features = paginator.page(paginator.num_pages)
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'features': features,
        'gallery': gallery,
        'tag': tag_name,
        'tags': tags,
        'media_url': MEDIA_URL,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('tag.html', variables,
                              context_instance=RequestContext(request))


def user(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = UserProfile.objects.get(user=user)
    challenges = Challenge.objects.filter(user=user)
    gallery_list = Image.objects.filter(approved=True, user=user)
    badges = user_profile.badges.all()
    paginator = Paginator(gallery_list, 12)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        gallery = paginator.page(page)
    except (EmptyPage, InvalidPage):
        gallery = paginator.page(paginator.num_pages)
    try:
        profile = UserProfile.objects.get(user=user)
        userbadges = profile.badges.all()
        badgecount = userbadges.count()
        userbadges = userbadges[:4]
    except Exception, exx:
        userbadges = []
        badgecount = 0
    variables = RequestContext(request, {
        'gallery': gallery,
        'badges': badges,
        'media_url': MEDIA_URL,
        'challenges': challenges,
        'userbadges': userbadges,
        'badgecount': badgecount,
        })
    return render_to_response('user.html', variables,
                              context_instance=RequestContext(request))


def win(request, challenge_id):
    try:
        user = request.user
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.badges.add(challenge.badge)
        user_profile.save()
        username = user.username
        return HttpResponseRedirect('/user/' + username + '?msg=1')
    except Exception, ex:
        return HttpResponseRedirect('/signup?msg=1')
