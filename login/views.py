# Create your views here.

import datetime
from login.forms import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import feedparser
from newspaper.article import Article
from login.models import *


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['fname'],
                last_name=form.cleaned_data['lname']
            )
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    return render(request, 'registration/sign_up.html', {'form': form})


#
# TODO in Register : Login the fresh USER
# @csrf_protect
# def login(request):
#     if request.method == 'POST':
#         form = Login(request.POST)
#         if form.is_valid():
#             user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
#             auth_login(request, user)


# Show a register success page for 2 seconds. and then redirect to Login
def register_success(request):
    return render(request, 'registration/success.html',)


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
@csrf_protect
def home(request):
    # Check if user have sources
    check_sources = Sourcing.objects.filter(created_by_id=request.user.id)
    if check_sources:
        return HttpResponseRedirect('/stories_list/')
    else:
        return HttpResponseRedirect('/add_source/')


@login_required
@csrf_protect
def add_source(request):
    if request.method == 'POST':
        form = AddSource(request.POST, user=request.user)
        # If form is valid, Save source.
        if form.is_valid():
            user_id = User.objects.get(id=request.user.id)
            source = Sourcing(
                name=form.cleaned_data['name'],
                rss_url=form.cleaned_data['rss_url'],
                created_by=user_id,
                updated_by=user_id,
            )
            source.save()
            return HttpResponseRedirect('/add_source/')
    form = AddSource(user=request.user)
    return render(request, 'add_source.html', {'form': form})


@login_required
def sources_list(request):
    user = User.objects.get(username=request.user)
    if user.is_staff or user.is_superuser:
        data = Sourcing.objects.all()
        return render(request, 'sources.html', {'data': data})
    else:
        data = Sourcing.objects.filter(created_by_id=user.id)
    return render(request, 'sources.html', {'data': data})


@csrf_exempt
def edit_source(request):
    if request.method == 'GET':
        if request.GET.get('item_id') is None:
            return HttpResponseRedirect('/sources_list/')
        else:
            # Get id of the Source URL
            item_id = int(request.GET.get('item_id'))
            # Get Sourcing obj for this id.
            source_obj = Sourcing.objects.get(id=item_id)
            form = {
                'name': source_obj.name,
                'rss_url': source_obj.rss_url,
                'item_id': source_obj.id,
            }
            form = EditSource(form, user=request.user)
        return render_to_response('edit_source.html', {'form': form, 'user': request.user, 'id': source_obj})
    if request.method == 'POST':
        form = EditSource(request.POST, user=request.user)
        if form.is_valid():
            source_instance = Sourcing.objects.get(id=form.cleaned_data['item_id'])
            source_instance.name = form.cleaned_data['name']
            source_instance.rss_url = form.cleaned_data['rss_url']
            source_instance.updated_by_id = request.user.id
            source_instance.save()
            return HttpResponseRedirect('/sources_list/')
        else:
            return render(request, 'edit_source.html', {'form': form})
    return HttpResponseRedirect('/sources_list/')


# Remove item from database and return to Sources page with rest list of Sources
def remove_source(request):
    if request.method == 'GET':
        # Get id of the item to be deleted
        item_id = int(request.GET.get('item_id'))
        # Get Sourcing Obj
        source_instance = Sourcing.objects.get(id=item_id)
        source_instance.delete()
        return HttpResponseRedirect('/sources_list/')
    return HttpResponseRedirect('/sources_list/')


@login_required
@csrf_protect
def search_source(request):
    user = request.user
    query = request.GET['q']
    if query == '':
        return HttpResponseRedirect('/sources_list/')
    elif request.user.is_staff or request.user.is_superuser:
        data = Sourcing.objects.filter(models.Q(name__icontains=query) | models.Q(rss_url__icontains=query))
        return render_to_response('sources.html', {'data': data, 'user': request.user})
    else:
        data = Sourcing.objects.filter(
            models.Q(name__icontains=query) | models.Q(rss_url__icontains=query),
            created_by_id=user.id
        )
    return render_to_response('sources.html', {'data': data, 'user': request.user})


@login_required
def fetch_story(request):
    if request.method == 'GET':
        story_list = []
        source_id = request.GET.get('item_id')
        rss_obj = Sourcing.objects.get(id=source_id)
        feed_data = feedparser.parse(rss_obj.rss_url)
        if feed_data.bozo == 1:
            url_error = {
                'Possible Wrong URL. Click here to go back to Sources page.'
            }
            return render_to_response('fetch_story.html', {'url_error': url_error, 'user': request.user})
        else:
            for data in feed_data.get('entries'):
                story_url = data.get('link')
                if story_url is None:
                    rss_error = {
                        'Either RSS is empty or RSS is broken. Click here to go back to Story Listing page'
                    }
                    return render_to_response('fetch_story.html', {'rss_error': rss_error, 'user': request.user})
                article = Article(story_url)
                article.download()
                article.parse()
                article_instance = article
                if article_instance.publish_date is None:
                    article_instance.publish_date = datetime.datetime.now()
                story = Stories(
                    title=article_instance.title,
                    source=rss_obj,
                    pub_date=article_instance.publish_date,
                    body_text=article_instance.text,
                    url=article_instance.url
                )
                story.save()
                story_list += [article_instance]

            return render_to_response('fetch_story.html', {
                                                        'data': story_list,
                                                        'rss_id': rss_obj,
                                                        'user': request.user})
    else:
        return HttpResponseRedirect('/sources_list/')


@login_required
def stories_list(request):
    user_id = User.objects.get(id=request.user.id)
    if user_id.is_staff or user_id.is_superuser:
        data = Stories.objects.all()
        return render(request, 'stories.html', {'data': data})
    else:
        data = Stories.objects.filter(source_id__created_by_id=user_id)
    return render(request, 'stories.html', {'data': data})


@login_required
@csrf_protect
def search_stories(request):
    query = request.GET['q']
    if query == '':
        return HttpResponseRedirect('/stories/')
    elif request.user.is_staff or request.user.is_superuser:
        data = Stories.objects.filter(models.Q(body_text__icontains=query) | models.Q(title__icontains=query))
        return render_to_response('stories.html', {'data': data, 'user': request.user})
    else:
        data = Stories.objects.filter(models.Q(
                                    body_text__icontains=query) | models.Q(title__icontains=query),
                                    source_id__created_by_id=request.user.id)
    return render_to_response('stories.html', {'data': data, 'user': request.user})


# Remove item from database and return to Sources page with rest list of Sources
def remove_story(request):
    if request.method == 'GET':
        item_id = int(request.GET.get('item_id'))
        story_instance = Stories.objects.get(id=item_id)
        story_instance.delete()
    return HttpResponseRedirect('/stories_list/')


@login_required
@csrf_protect
def add_story(request):
    if request.method == 'POST':
        form = AddStory(request.POST, user=request.user)
        if form.is_valid():
            story = Stories(
                title=form.cleaned_data['title'],
                body_text=form.cleaned_data['body'],
                pub_date=form.cleaned_data['pub_date'],
                source_id=form.cleaned_data['source'].id,
                url=form.cleaned_data['url']
            )
            story.save()
            return HttpResponseRedirect('/add_story/')
        else:
            return render(request, 'add_story.html', {'form': form})
    else:
        form = AddStory(user=request.user)
    return render(request, 'add_story.html', {'form': form})


@csrf_exempt
def edit_story(request):
    if request.method == 'GET':
        if request.GET.get('item_id') is None:
            return HttpResponseRedirect('/stories_list/')
        else:
            item_id = int(request.GET.get('item_id'))
            item = Stories.objects.get(id=item_id)
            form = {
                'title': item.title,
                'url': item.url,
                'body': item.body_text,
                'source': item.source_id,
                'pub_date': datetime.datetime.strftime(item.pub_date, '%Y-%m-%d %H:%M:%S'),
                'item_id': item.id,
            }
            form = EditStory(form, user=request.user)
            return render_to_response('edit_story.html', {'form': form, 'user': request.user})
    if request.method == 'POST':
        form = EditStory(request.POST, user=request.user)
        if form.is_valid():
            instance = Stories.objects.get(id=form.cleaned_data['item_id'])
            instance.title = form.cleaned_data['title']
            instance.url = form.cleaned_data['url']
            instance.pub_date = form.cleaned_data['pub_date']
            instance.body_text = form.cleaned_data['body']
            instance.source_id = form.cleaned_data['source'].id
            instance.save()
            return HttpResponseRedirect('/stories_list/')
        else:
            return render(request, 'edit_story.html', {'form': form})

    return HttpResponseRedirect('/stories_list/')
