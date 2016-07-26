from members.models import *
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

import datetime

def ensure_login(in_fn):
    """
    This is a decorator to make sure user is logged in
    """

    def wrapper():
        if not request.user.is_authenticated():
            return render(request, 'members/home.html', {})
        return in_fn()

    return wrapper    

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
    mem = get_object_or_404(Member, pk=member_id)

    accessList = AccessBlock.objects.filter(member = mem)
    cards = AccessCard.objects.filter(member = mem)

    return render(request,
                  'members/member_details.html',
                  {'member': mem,
                   'access_list': accessList,
                   'access_cards': cards,
                   'logged_in': logged_in}
    )

def memberDetailsByRFID(request, rfid):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    
    card = get_object_or_404(AccessCard, unique_id=rfid)
    mem = card.member

    accessList = AccessBlock.objects.filter(member = mem)

    return render(request,
                  'members/member_details.html',
                  {'member': mem,
                   'access_list': accessList,
                   'logged_in': logged_in}
    )

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

def addMembership(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    if request.method == 'POST':
        msForm = MembershipForm(request.POST)
        if msForm.is_valid():
            newMembership = msForm.save(commit=False)
            newMembership.save()
            info = 'Created new membership'
            

            mList = Membership.objects.all()
            return render(request, 'members/main.html',
                          {'membership_list': mList,
                           'msg_info': info,
                           'logged_in': logged_in, })

    else:
        msForm = MembershipForm()

    logged_in = True
    
    
    return render(request, 'members/add_membership.html', {'ms_form': msForm, 'logged_in': logged_in})



def cards(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    cards = AccessCard.objects.all()

    return render(request, 'members/access_cards.html', {'card_list': cards, 'logged_in': logged_in})


def addCard(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    if request.method == 'POST':
        cForm = CardForm(request.POST)
        if cForm.is_valid():
            newCard = cForm.save(commit=False)
            newCard.save()
            info = 'Created new Access Card'
            

            cList = AccessCard.objects.all()
            return render(request, 'members/main.html',
                          {'card_list': cList,
                           'msg_info': info,
                           'logged_in': logged_in, })

    else:
        cForm = CardForm()

    logged_in = True
    
    
    return render(request, 'members/add_card.html', {'card_form': cForm, 'logged_in': logged_in})

@ensure_login
def tblks(request):
    blocks = TimeBlock.objects.all()

    return render(request, 'members/time_blocks.html', {'block_list' : blocks, 'logged_in' : logged_in})


def blocks(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    blocks = AccessBlock.objects.all()

    return render(request, 'members/access_blocks.html', {'block_list': blocks, 'logged_in': logged_in})



def addBlock(request):
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    if request.method == 'POST':
        bForm = BlockForm(request.POST)
        if bForm.is_valid():
            newBlock = bForm.save(commit=False)
            newBlock.save()
            info = 'Created new Access Block'
            

            bList = AccessBlock.objects.all()
            return render(request, 'members/main.html',
                          {'block_list': bList,
                           'msg_info': info,
                           'logged_in': logged_in, })

    else:
        bForm = BlockForm()

    logged_in = True
    
    
    return render(request, 'members/add_block.html', {'block_form': bForm, 'logged_in': logged_in})


@csrf_exempt
def auth(request):
    if request.method == 'POST':
        if 'id' in request.POST:
            uID = request.POST['id']

            cards = AccessCard.objects.filter(unique_id=uID)
            if len(cards) < 1:
                return HttpResponse("Denied", content_type="text/plain")
            else:
                mem = cards[0].member

                if mem.has_access_now():
                    return HttpResponse("Granted", content_type="text/plain")

    response = HttpResponse("Denied", content_type="text/plain")
    return response
