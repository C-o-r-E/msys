from members.models import Member, MemberForm, Membership
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout

import datetime

def user_logout(request):
    logout(request)
    notes = ["Logged out successfully"]
    return render(request, 'members/login.html', { 'notifications':notes })

def user_login(request):
    notes = None
    logged_in = False

    if request.method == 'POST':
        usr = request.POST['usr']
        pword = request.POST['pass']
        user = authenticate(username = usr, password = pword)
        if user is not None:
            login(request, user)
            return members(request)
            #return render(request, 'members/members.html', {'logged_in':True,
            #                                          'username':user.username})
        else:
            notes = ["Invalid login"]
        
    if request.user.is_authenticated():
        logged_in = True

    return render(request, 'members/login.html', { 'notifications':notes, 'logged_in':logged_in })

def members(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    memberList = Member.objects.all()

    return render(request, 'members/members.html', {'member_list': memberList, 'logged_in': logged_in})

def memberDetails(request, member_id):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    member = get_object_or_404(Member, pk=member_id)


    return render(request, 'members/member_details.html', {'member': member, 'logged_in': logged_in})

def editDetails(request, member_id):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    if request.method == 'POST':
        memForm = MemberForm(request.POST)
        if memForm.is_valid():
            editedMember = memForm.save(commit=False)
            actualMember = get_object_or_404(Member, pk=member_id)
            editedMember.number = actualMember.number
            editedMember.pk = actualMember.pk
            editedMember.first_seen_date = actualMember.first_seen_date
            editedMember.last_seen_date = actualMember.first_seen_date
            editedMember.save()
            #return HttpResponseRedirect('../')
            return members(request)

    else:
        logged_in = True
        member = get_object_or_404(Member, pk=member_id)
        memForm = MemberForm(instance=member)


    return render(request, 'members/editDetails.html', {'member': member, 'member_form': memForm, 'logged_in': logged_in})

def addMember(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    if request.method == 'POST':
        memForm = MemberForm(request.POST)
        if memForm.is_valid():
            newMember = memForm.save(commit=False)
            newMember.number = Member.objects.all().count() + 1
            newMember.first_seen_date = datetime.date.today()
            newMember.last_seen_date = datetime.date.today()
            newMember.save()
            return HttpResponseRedirect('../')

    else:
        memForm = MemberForm()

    logged_in = True
    
    
    return render(request, 'members/add.html', {'mem_form': memForm, 'logged_in': logged_in})


def memberships(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    mList = Membership.objects.all()

    if request.method == 'GET' and 'show' in request.GET:
        if request.GET['show'] == 'expired':
            mList = Membership.objects.filter(expire_date__lt = datetime.datetime.today())
        elif request.GET['show'] == 'active':
            mList = Membership.objects.filter(expire_date__gte = datetime.datetime.today())
            
    return render(request, 'members/memberships.html', {'membership_list': mList, 'logged_in': logged_in})
