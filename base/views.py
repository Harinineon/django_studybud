from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.
# rooms = [
#     {'id':1, 'name':"Let's Learn python!"},
#     {'id':2, 'name':"Design with me"},
#     {'id':3, 'name':"Frontend Development"},
# ]

#get username and password
#check if user exists
#if user does not exist show error message
#if user exists authenticate
#then by login() create session and redirect

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:   #if user is already logged in and he manually tries to give /login
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email = email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email = email, password = password)

        if user is not None:
            login(request, user)    #creates session in our db and browser (inspect-application-sesssion-cookies)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')


    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()   #for displaying constraints like username length password length and constraints

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')


    context = {'form':form}
    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
    )

    topics =  Topic.objects.all()[0:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) #when a topic is selected only activity feed related to that topic is displayed

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count,'room_messages':room_messages}
    return render(request, 'base/home.html',context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created') #here we are querying the child class of Room ie Message (syntax use small letter)
    participants = room.participants.all()
    #for many-to-one use _set.all() for many-to-many use .all()

    if request.method == 'POST':    #for adding a new comment
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)     #add user who has commented
        return redirect('room', pk=room.id)
    
    context = {'room':room, 'room_messages':room_messages,'participants':participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)          #for feed component
    rooms = user.room_set.all()             #for feed component
    room_messages = user.message_set.all()   #for activity component
    topics = Topic.objects.all()            #for topics component
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request,'base/profile.html',context)


@login_required(login_url = 'login')  #if user not authenticated ie sessionid not in db then redirected to login page
#this is done before crud operations because if we want to do crud op then we should first login

def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()    #to display topics as dropdown
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)   #created is false for new topics so it will create topic orelse it will get topic
        
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    context = {'form':form,'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:   #to make sure room can be editted by the host only
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')
    
    context = {'form':form,'topics':topics,'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')

def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:   #to make sure room can be deleted by the host only
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html',{'obj':room})

@login_required(login_url = 'login')

def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:   #to make sure room can be deleted by the host only
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
        
    return render(request, 'base/delete.html',{'obj':message})

@login_required(login_url = 'login')

def updateUser(request):
    user = request.user
    form = UserForm(instance=user)   #form function from forms.py (it will display already present details)
    context={'form':form}

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)     #processing the new updated profile fields
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)   

    return render(request,'base/update-user.html',context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics=Topic.objects.filter(name__icontains=q)
    context={'topics':topics}
    return render(request,'base/topics.html',context)

def activityPage(request):
    room_messages= Message.objects.all()
    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)