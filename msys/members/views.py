"""
Views

This is where the main logic happens behind the scenes.

"""
import datetime
from members.models import *
from members.forms import *
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from time import sleep
"""
def ensure_login(in_fn):

    #This is a decorator to make sure user is logged in


    def wrapper():
        if not request.user.is_authenticated():
            return render(request, 'members/home.html', {})
        return in_fn()

    return wrapper
"""

def user_logout(request):
    """Log out the user"""
    logout(request)
    notes = ["Logged out successfully"]
    return render(request, 'members/login.html', {'notifications':notes})

def user_login(request):
    """
    This function attempts to authenticate the user
    """
    notes = None
    logged_in = False

    if request.method == 'POST':
        usr = request.POST['usr']
        pword = request.POST['pass']
        user = authenticate(username=usr, password=pword)
        if user is not None:
            login(request, user)
            return members(request)
            #return render(request, 'members/members.html', {'logged_in':True,
            #                                          'username':user.username})
        else:
            notes = ["Invalid login"]

    if request.user.is_authenticated():
        logged_in = True

    return render(request, 'members/login.html', {'notifications':notes, 'logged_in':logged_in})

def members(request):
    """Simply render a list of members"""
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    show_active = False
    member_list = Member.objects.all()
    
    if request.method == 'GET':
        if 'show_active' in request.GET:
            show_active = True

    return render(request,
                  'members/members.html',
                  {'member_list': member_list,
                   'show_active': show_active,
                   'logged_in': logged_in})

def memberDetails(request, member_id):
    """Show details about a specific Member"""
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    mem = get_object_or_404(Member, pk=member_id)

    cards = AccessCard.objects.filter(member=mem)

    return render(request,
                  'members/member_details.html',
                  {'member': mem,
                   'access_cards': cards,
                   'logged_in': logged_in}
                 )

def memberDetailsByRFID(request, rfid):
    """
    Get some details about a specific member

    Params:

    rfid -- a unique id related to a Member via AccessCard object
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    
    
    rfid = rfid.replace(' ', '').lower()
    card = get_object_or_404(AccessCard, unique_id=rfid)
    mem = card.member

    cards = AccessCard.objects.filter(member=mem)

    return render(request,
                  'members/member_details.html',
                  {'member': mem,
                   'access_cards': cards,
                   'logged_in': logged_in}
                 )

def editDetails(request, member_id):
    """
    For editing information about a Member
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    if request.method == 'POST':
        mem_form = MemberForm(request.POST)
        if mem_form.is_valid():
            edited_member = mem_form.save(commit=False)
            actual_member = get_object_or_404(Member, pk=member_id)
            edited_member.number = actual_member.number
            edited_member.pk = actual_member.pk
            edited_member.first_seen_date = actual_member.first_seen_date
            edited_member.last_seen_date = actual_member.first_seen_date
            edited_member.save()
            
            log_str = "{} edited member: {} with fields [".format(request.user.username,
                                                           actual_member)
            log_str += "{} -> {}, ".format(actual_member.number, edited_member.number)
            log_str += "{} -> {}, ".format(actual_member.type, edited_member.type)
            log_str += "{} -> {}, ".format(actual_member.first_name, edited_member.first_name)
            log_str += "{} -> {}, ".format(actual_member.last_name, edited_member.last_name)

            log_str += "{} -> {}, ".format(actual_member.address, edited_member.address)
            log_str += "{} -> {}, ".format(actual_member.city, edited_member.city)
            log_str += "{} -> {}, ".format(actual_member.postal_code, edited_member.postal_code)
            log_str += "{} -> {}, ".format(actual_member.phone_number, edited_member.phone_number)
            log_str += "{} -> {}, ".format(actual_member.email, edited_member.email)
            log_str += "{} -> {}, ".format(actual_member.emergency_contact, edited_member.emergency_contact)
            log_str += "{} -> {}, ".format(actual_member.emergency_phone_number, edited_member.emergency_phone_number)
            log_str += "{} -> {}, ".format(actual_member.stripe_customer_code, edited_member.stripe_customer_code)
            
            log_str += "]"
            LogEvent.log_now(log_str)
            
            return members(request)

    else:
        logged_in = True
        member = get_object_or_404(Member, pk=member_id)
        mem_form = MemberForm(instance=member)


    return render(request,
                  'members/editDetails.html',
                  {'member': member, 'member_form': mem_form, 'logged_in': logged_in})

def addMember(request):
    """Add a new Member"""
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})
        
    logged_in = True

    if request.method == 'POST':
        mem_form = MemberForm(request.POST)
        if mem_form.is_valid():
            new_member = mem_form.save(commit=False)
            new_member.number = Member.objects.all().count() + 1
            new_member.first_seen_date = datetime.date.today()
            new_member.last_seen_date = datetime.date.today()
            new_member.save()
            
            notes = "Created a new member: {}".format(new_member)
            
            log_str = "{} created a new member: {}".format(request.user.username,
                                                           new_member)
            LogEvent.log_now(log_str)
            
            member_list = Member.objects.all()
            
            return render(request,
                   'members/members.html',
                   {'member_list': member_list,
                   'msg_info': notes,
                   'logged_in': logged_in})

    else:
        mem_form = MemberForm()


    return render(request, 'members/add.html', {'mem_form': mem_form, 'logged_in': logged_in})


def memberships(request, member_id=None):
    """Render a list of Memberships"""
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    
    if member_id:
        m_list = Membership.objects.filter(member=member_id)
    else:
        m_list = Membership.objects.all()

        if request.method == 'GET' and 'show' in request.GET:
            if request.GET['show'] == 'expired':
                m_list = Membership.objects.filter(expire_date__lt=datetime.datetime.today())
            elif request.GET['show'] == 'active':
                m_list = Membership.objects.filter(expire_date__gte=datetime.datetime.today())

    return render(request, 'members/memberships.html', {'membership_list': m_list, 'logged_in': logged_in})

def addMembership(request, member_id=None):
    """Create a new Membership"""
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    if request.method == 'POST':
        ms_form = MembershipForm(request.POST)
        if ms_form.is_valid():
            new_membership = ms_form.save(commit=False)
            new_membership.save()
            info = 'Created new membership'
            
            log_str = "{} created a new memberhip: {}".format(request.user.username,
                                                           new_membership)
            LogEvent.log_now(log_str)


            m_list = Membership.objects.all()
            return render(request, 'members/main.html',
                          {'membership_list': m_list,
                           'msg_info': info,
                           'logged_in': logged_in, })

    else:
        ms_form = MembershipForm()
        if member_id:
            ms_form = MembershipForm(initial={'member':member_id})
    logged_in = True


    return render(request, 'members/add_membership.html', {'ms_form': ms_form, 'logged_in': logged_in})

def editMembership(request, m_ship):
    """ Edit a membership """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    if request.method == 'POST':
        ms_form = MembershipForm(request.POST)
        if ms_form.is_valid():
            edited_ms = ms_form.save(commit=False)
            actual_ms = get_object_or_404(Membership, pk=m_ship)
            edited_ms.pk = actual_ms.pk
            edited_ms.save()
            
            log_str = "{} modified a membership: {} -> {}".format(request.user.username,
                                                           actual_ms, edited_ms)
            LogEvent.log_now(log_str)
            
            return memberships(request)
    else:
        ship = get_object_or_404(Membership, pk=m_ship)
        ms_form = MembershipForm(instance=ship)


    return render(request,
                  'members/editMembership.html',
                  {'ship': ship, 'ms_form': ms_form, 'logged_in': logged_in})

def cards(request):
    """Render list of AccessCard objects"""
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    card_list = AccessCard.objects.all()

    return render(request, 'members/access_cards.html', {'card_list': card_list, 'logged_in': logged_in})

def checkCard(request, card_rfid):
    """
    Find a card by its uid and display its details.
    
    Will also present the option to create a new card
    """

    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    
    card_rfid = card_rfid.replace(' ', '').lower()

    try:
        card = AccessCard.objects.get(unique_id=card_rfid)
        
        return cardDetails(request, card.pk)
    except AccessCard.DoesNotExist:
        data = {'unique_id': card_rfid}
        c_form = CardForm(initial=data)

        notes = "Unrecognised card [{}].".format(card_rfid)
        notes += "Use the form below if you would like to create a new one"

        return render(request, 'members/add_card.html', {'card_form': c_form,
                                                         'msg_info': notes,
                                                         'logged_in': logged_in})

def cardDetails(request, card_id):
    """
    Get details about an AccessCard

    This will also fetch a list of AccessGroups associated with the Card.

    Optionally the user can request (via POST) to have a visual aid generated.
    The visual aid is a table of times over the next 7 days (hour-by-hour). The
    table will show the user which times the card provides access and which
    times it does not. This may be a slow and expensive opteration.
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    card = get_object_or_404(AccessCard, pk=card_id)

    group_list = card.accessgroup_set.all()

    t_cal = None

    if request.method == 'GET':
        if 'table' in request.GET:
            """
            This is the part where we generate the fancy
            calendar like table of access times for the
            next few days. This is probably an expensive
            operation and may need to be evaluated again
            if performance becomes an issue.


            It seems that due to the nature of django
            templates, we need to craft our datastructure
            to reflect how we want our HTML table to be
            constructed. Since HTML tables are constructed
            row by row our data should look like this:

            data = [ ['Mon', 'Tues', ... 'Sun'],
                     [ '12am', False, ... True ],
                     [ '1am', False, ... False ],
                     ...,
                     ...,
                     [ '11pm', True, ... True ] ]

            data is a list of 24 lists.
            """

            #first we get the datetime object with today's info
            today = datetime.datetime.today()

            #now we can start constructing our list of days
            t_cal = []
            for thing in range(24):
                t_cal.append([])


            #at this point we should have a list of empty lists. One for each of the next 7 days.

            #create a base datetime where it is the same day as today but 0h:00:00...
            base_dt = datetime.datetime(today.year, today.month, today. day)

            day_n = 0
            t_cal[0].append("Hour / Date")
            #first populate the first row with title stuff
            for n_Day in range(7):
                delta = datetime.timedelta(days=day_n)
                day = base_dt + delta
                t_cal[0].append(day.strftime("%A %b %d"))
                day_n += 1

            #now append the rows by hour with the first col being the title
            time_h = 0
            for row in t_cal[1:]:
                hour = base_dt + datetime.timedelta(hours=time_h)
                time_str = hour.strftime("%X")
                row.append(time_str)
                for n_day in range(7):
                    cell_dt = base_dt + datetime.timedelta(days=n_day, hours=time_h)
                    row.append(card.has_access_at_time(cell_dt.date(), cell_dt.time()))
                time_h += 1
        #end GET handler

    return render(request,
                  'members/card_details.html',
                  {'card': card,
                   'groups': group_list,
                   't_cal': t_cal,
                   'logged_in': logged_in})

def cardAssign(request, card_id):
    """
    Assign one or more AccessGroups to a card.
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    card = get_object_or_404(AccessCard, pk=card_id)

    if request.method == 'POST':

        #1) get list from user
        r_groups = []
        for key in request.POST.getlist('groups'):
            r_groups.append(AccessGroup.objects.get(pk=key))

        #2) remove (clear) current card relations to accessgroups
        card.accessgroup_set.clear()

        #3 link the card with the groups specified by user
        lg_txt = ''
        for grp in r_groups:
            card.accessgroup_set.add(grp)
            lg_txt += str(grp) + ', '

        notes = 'Updated AccessGroups associated with Card ' + str(card)
        
        log_str = "{} set access groups for card {} to [ {}]".format(request.user.username,
                                                                     card,
                                                                     lg_txt)
        LogEvent.log_now(log_str)

        groups = card.accessgroup_set.all()

        return render(request,
                      'members/card_details.html',
                      {'card': card,
                       'groups': groups,
                       'msg_info': notes,
                       'logged_in': logged_in})

    else:
        form = AddGroupToCardForm()
        #Now get all the AccessGroups
        groups = AccessGroup.objects.all()
        print(groups)
        return render(request,
                      'members/card_assign.html',
                      {'card': card,
                       'form': form,
                       'logged_in': logged_in})

def editCard(request, card_id):
    """
    Edit details of AccessCard
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    if request.method == 'POST':
        card_form = CardForm(request.POST)
        if card_form.is_valid():
            edited_card = card_form.save(commit=False)
            actual_card = get_object_or_404(AccessCard, pk=card_id)
            #commented out to allow modification of the ID
            #edited_card.unique_id = actual_card.unique_id
            edited_card.pk = actual_card.pk
            edited_card.save()
            
            log_str = "{} changed card: {} -> {}".format(request.user.username,
                                                         actual_card,
                                                         edited_card)
            LogEvent.log_now(log_str)
            
            return cards(request)

    else:
        logged_in = True
        card = get_object_or_404(AccessCard, pk=card_id)
        card_form = CardForm(instance=card)


    return render(request, 'members/editCard.html', {'card': card, 'card_form': card_form, 'logged_in': logged_in})



def addCard(request):
    """
    Create a new AccessCard
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    if request.method == 'POST':
        c_form = CardForm(request.POST)
        if c_form.is_valid():
            newCard = c_form.save(commit=False)
            #find out if we already have a card with the same ID
            sameCards = AccessCard.objects.filter(unique_id=newCard.unique_id)
            if len(sameCards) > 0:
                #already exists
                msg_err = "A card with that ID already exists"
                return render(request, 'members/add_card.html',
                              {'card_form': c_form,
                               'msg_err': msg_err,
                               'logged_in': logged_in, }) 
            
            newCard.unique_id = newCard.unique_id.replace(' ', '').lower()
            newCard.save()
            
            log_str = "{} created a new card: {}".format(request.user.username, newCard)
            LogEvent.log_now(log_str)
            
            info = 'Created new Access Card'
            c_list = AccessCard.objects.all()
            return render(request, 'members/main.html',
                          {'card_list': c_list,
                           'msg_info': info,
                           'logged_in': logged_in, })

    else:
        c_form = CardForm()

    logged_in = True


    return render(request, 'members/add_card.html', {'card_form': c_form, 'logged_in': logged_in})

def groups(request):
    """
    Get a list of AccessGroups
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    groups = AccessGroup.objects.all()

    return render(request, 'members/access_groups.html', {'group_list' : groups, 'logged_in' : logged_in})

def tblks(request):
    """
    Get a list of TimeBlocks
    """
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    block_list = TimeBlock.objects.all()

    return render(request, 'members/time_blocks.html', {'block_list' : block_list, 'logged_in' : logged_in})


def show_log(request):
    """
    Display log entries
    """
    
    if not request.user.is_authenticated():
        return render(request, 'members/home.html', {})

    logged_in = True
    log_list = LogEvent.objects.order_by('date').order_by('time').reverse()

    return render(request, 'members/show_log.html', {'log_list' : log_list, 'logged_in' : logged_in})
    

@csrf_exempt
def latency(request):
    """
    Used to for clients to test latency
    """

    if not settings.DEBUG:
        return HttpResponseForbidden()

    if request.method == 'POST':
        if 'time' in request.POST:
            nap_time = float(request.POST['time'])
            print("Sleeping {}s...".format(nap_time))
            if nap_time > 10:
                nap_time = 10
                print("Time too long: setting to {}s".format(nap_time))
            sleep(nap_time)

    return HttpResponse("ok", content_type="text/plain")

@csrf_exempt
def weekly_access(request):
    """
    Deliver info on what access a given ID card grants
    
    Generate a JSON datastructure to be returned to the user
    """
    data = {}
    if request.method == 'POST':
        if 'id' in request.POST:
            uID = request.POST['id']
            
            cards = AccessCard.objects.filter(unique_id=uID)
            for the_card in cards:
                access_groups = AccessGroup.objects.filter(card=the_card)
                for the_group in access_groups:
                    time_blocks = TimeBlock.objects.filter(group=the_group)
                    for block in time_blocks:
                        if block.day in data:
                            temp = data[block.day]
                            temp['start'] = min(block.start, temp['start'])
                            temp['end'] = max(block.end, temp['end'])
                            data[block.day] = temp
                        else:
                            data[block.day] = {'start': block.start, 'end': block.end}
            
            return JsonResponse(data)
            
    return HttpResponse("Nope", content_type="text/plain")

@csrf_exempt
def auth(request):
    """
    Authenticate access requests

    Uses a simple protocol on top of HTTP to communicate with msys clients
    """
    if request.method == 'POST':
        if 'id' in request.POST:
            uID = request.POST['id']

            cards = AccessCard.objects.filter(unique_id=uID)
            if len(cards) < 1:
                #we didnt find any cards matching the ID
                return HttpResponse("Denied", content_type="text/plain")
            else:
                #one or more cards found
                granted = False
                for card in cards:
                    if card.has_access_now():
                        granted = True
                        break

                if granted:
                    return HttpResponse("Granted", content_type="text/plain")

    response = HttpResponse("Denied", content_type="text/plain")
    return response
