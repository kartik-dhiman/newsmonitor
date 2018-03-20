# Create your views here.

import datetime
from login.forms import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render , render_to_response , get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Q
import feedparser
from newspaper.article import Article
from login.models import *
from django.views.generic.edit import UpdateView




@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # user = Subscription(
            #     username=form.cleaned_data['username'],
            #     password=form.cleaned_data['password1'],
            #     email=form.cleaned_data['email'],
            #     fname=form.cleaned_data['fname'],
            #     lname=form.cleaned_data['lname'],
            # )
            # user.save()

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
    variables = RequestContext(request, {'form': form})
    #variables['form']=RegistrationForm()

    return render(request, 'registration/sign_up.html', {'form': form})

#
#
# @csrf_protect
# def login(request):
#     if request.method == 'POST':
#         form = Login(request.POST)
#         if form.is_valid():
#             user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
#             auth_login(request, user)
#             s = Sourcing.objects.filter(created_by_id=user.id)
#             if s:
#                 return HttpResponseRedirect('/sources/')
#             else:
#                 return HttpResponseRedirect('add_source/')
#         else:
#             return render(request, 'registration/login.html', {'form': form})
#     form = Login()
#     return render(request, 'registration/login.html', {'form': form})
#





def register_success(request):
    return render(request,
        'registration/success.html',
    )

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
@csrf_protect
def home(request):
    s = Sourcing.objects.filter(created_by_id=request.user.id)
    if s:
        return HttpResponseRedirect('/stories')
    else:
        return HttpResponseRedirect('/add_source/')

    # return render_to_response(
    #     'home.html',
    #     {'user': request.user,
    #      }
    # )



@login_required
@csrf_protect
def add_source(request):
    if request.method == 'POST':
        form = AddSource(request.POST, user=request.user)
        if form.is_valid():
            s = User.objects.get(id=request.user.id)
            print(form.cleaned_data, "___________________________________________________________--")
            user = Sourcing(
                name=form.cleaned_data['name'],
                rss_url=form.cleaned_data['rss_url'],
                created_by=s,
                updated_by=s,
            )
            user.save()
            return HttpResponseRedirect('/add_source/')
        else:
            return render(request, 'add_source.html', {'form': form})
    elif request.method == 'GET':
        if request.GET.get('item_id') is None:
            form = AddSource(request)
            return render(request, 'add_source.html', {'form': form})
        item_id = int(request.GET.get('item_id'))
        item = Sourcing.objects.get(id=item_id)
        form = {
            'name':item.name,
            'rss_url':item.rss_url
        }
        print(form,"________________________________HERE____________________________")
        form=AddSource(form, user=request.user)
        return render(request,'add_source.html', {'form':form})
    else:
        form = AddSource(user=request.user)
        return render(request, 'add_source.html', {'form': form})









@login_required
def sources(request):
    s = User.objects.get(username=request.user)
    if s.is_staff or s.is_superuser:
        data = Sourcing.objects.all()
        return render(request, 'sources.html', {'data': data})
    else:
        data = Sourcing.objects.filter(created_by_id=s.id)
        return render(request, 'sources.html', {'data': data})

#
# def edit_source(request):
#     if request.method == 'GET':
#         user = request.user
#         if request.GET.get('item_id') is None:
#             return HttpResponseRedirect('/sources/')
#         else:
#             item_id = int(request.GET.get('item_id'))
#             item = Sourcing.objects.get(id=item_id)
#             form = {
#                 'name':item.name,
#                 'rss_url':item.rss_url
#             }
#             form=EditSource(form)
#             return render_to_response('edit_source.html',{'form':form})
#     elif request.method == 'POST':
#         user = request.user
#         form = EditSource()
#         if form.is_valid():
#             user = Sourcing(
#                 name=form.cleaned_data['name'],
#                 rss_url=form.cleaned_data['rss_url'],
#                 created_by=user.id,
#                 updated_by=user.id
#             )
#             user.save()
#             return HttpResponseRedirect('/sources/')
#         else:
#             return render(request, 'edit_source.html', {'form': form})
#
#     return HttpResponseRedirect('/sources/')
#



#-------------Remove item from database and return to Sources page with rest list of Sources
@csrf_protect
def remove_items(request):
    if request.method == 'POST':
        item_id = int(request.POST.get('item_id'))          # item_id    - ID of the item in the list of Sources page
        item = Sourcing.objects.get(id=item_id)             # Get the related database entry for that item
        item.delete()                                     # Deletes the item
        return HttpResponseRedirect('/sources/')            # Redirect to Sources view
    else:
        return HttpResponseRedirect('/sources/')




#-------------Search the database for field - Name
@login_required
def search(request):
    user = request.user
    query = request.GET['q']
    if (query==''):                                                              # If query Empty -> redirect to Sources
        return HttpResponseRedirect('/sources/')
    else:
        data = Sourcing.objects.filter(name__contains=query, created_by_id=user.id)        # Filter Entries by Name : ( Created by Self )
        return render_to_response('sources.html', {'data': data , 'user':request.user } )                # Return list to Sources



# Just elements page
def elements(request):
    return render(request, 'elements.html')



# TODO fetch stories
@login_required
@csrf_protect
def fetch_story(request):
    if request.method == 'POST':
        story_dict = []
        id = request.POST.get('item_id')
        rss_url_id = Sourcing.objects.get(id__iexact=id)
        feed_data = feedparser.parse(rss_url_id.rss_url)
        if feed_data.bozo == 1:
            data = {
                'Possible Wrong URL. Click here to go back to Sources page.':'data'
            }
            return render_to_response('fetch_story.html', {'data':data, 'user':request.user })
        else:
            for data in feed_data.get('entries'):
                story_url = data.get('link')
                article = Article(story_url)
                article.download()
                article.parse()
                data_var=article
                if data_var.publish_date is None:
                    data_var.publish_date = datetime.datetime.now()
                user = Stories(
                    title=data_var.title,
                    source=rss_url_id,
                    pub_date=data_var.publish_date,
                    body_text=data_var.text,
                    url=data_var.url
                )
                user.save()
                print(data,"**************************************************************************************")
                story_dict += [data_var]

            return render(request, 'fetch_story.html' , {'data':story_dict,
                                                         'rss_id':rss_url_id,
                                                         'user':request.user} )
    else:
        return HttpResponseRedirect('/sources/')





@login_required
def stories(request):
    user_id = User.objects.get(id=request.user.id)
    print(user_id)
    if user_id.is_staff or user_id.is_superuser:
        data = Stories.objects.all()
        return render(request, 'stories.html', {'data': data})
    else:
        data = Stories.objects.filter(source_id__created_by_id=user_id)
        print(data, "__________________________________________________________________________-")
        return render(request, 'stories.html', {'data': data})


@login_required
def search_stories(request):
    user = request.user
    query = request.GET['q']
    if (query==''):                                                              # If query Empty -> redirect to Sources
        return HttpResponseRedirect('/stories/')
    else:
        data = Stories.objects.filter(models.Q(body_text__icontains=query) | models.Q(title__icontains=query) , source_id__created_by_id=user.id)        # Filter Entries by Name : ( Created by Self )
        return render_to_response('stories.html', {'data': data , 'user':request.user } )




#-------------Remove item from database and return to Sources page with rest list of Sources
@csrf_protect
def remove_story(request):
    if request.method == 'POST':
        item_id = int(request.POST.get('item_id'))          # item_id    - ID of the item in the list of Sources page
        item = Stories.objects.get(id=item_id)             # Get the related database entry for that item
        item.delete()                                       # Deletes the item
        return HttpResponseRedirect('/stories/')            # Redirect to Sources view



@login_required
@csrf_protect
def add_story(request):
    if request.method == 'POST':
        form = AddStory(request.POST, user=request.user)
        if form.is_valid():
            print(form.cleaned_data,"_________________________________________________________________________________________")
            user = Stories(
                title=form.cleaned_data['title'],
                body_text=form.cleaned_data['body'],
                pub_date=form.cleaned_data['pub_date'],
                source_id=form.cleaned_data['source'].id,
                url=form.cleaned_data['url']
            )
            user.save()
            return HttpResponseRedirect('/add_story/')
        else:
            return render(request, 'add_story.html', {'form': form})
    else:
        form = AddStory(user = request.user)
        return render(request, 'add_story.html', {'form': form})