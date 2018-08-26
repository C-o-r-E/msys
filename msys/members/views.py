"""
Views

This is where the main logic happens behind the scenes.

"""
import datetime
from members.models import *
from members.forms import *
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.conf import settings
from time import sleep

import stripe

def login_required(wrapped):
    """
    This is a decorator to make sure user is logged in
    """
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated:
            return render(args[0], 'members/home.html', {})
        return wrapped(*args, **kwargs)

    return wrapper

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

    if request.user.is_authenticated:
        logged_in = True

    return render(request, 'members/login.html', {'notifications':notes, 'logged_in':logged_in})

@login_required
def members(request):
    show_active = False
    member_list = Member.objects.all().order_by('-last_seen_date')

    if request.method == 'GET':
        if 'show_active' in request.GET:
            show_active = True

    return render(request,
                  'members/members.html',
                  {'member_list': member_list,
                   'show_active': show_active,
                   'logged_in': True})

@login_required
def memberDetails(request, member_id):
    """Show details about a specific Member"""
    mem = get_object_or_404(Member, pk=member_id)

    cards = AccessCard.objects.filter(member=mem)

    stripe_info = None
    subs = None

    if mem.stripe_customer_code:
        stripe.api_key = settings.STRIPE_KEY
        print(f"member has stripe code : [{mem.stripe_customer_code}]") #todo remove

        sd = stripe.Customer.retrieve(mem.stripe_customer_code).to_dict()
        stripe_info = {}
        for key in ['id', 'account_balance',
                    'created', 'delinquent', 'description',
                    'email']:
            stripe_info[key] = sd[key]
        if len(sd['subscriptions']['data']) > 0:
            subs =  sd['subscriptions']['data'][0].to_dict()['items']['data']

        # Corey Note: Right now there is too much going on in the template
        # This really should be cleaned up so that any data manipulation happens here
        

    return render(request,
                  'members/member_details.html',
                  {'member': mem,
                   'access_cards': cards,
                   'stripe_info': stripe_info,
                   'subs': subs,
                   'logged_in': True}
                 )

@login_required
def memberDetailsByRFID(request, rfid):
    """
    Get some details about a specific member

    Params:

    rfid -- a unique id related to a Member via AccessCard object
    """
    rfid = rfid.replace(' ', '').lower()
    card = get_object_or_404(AccessCard, unique_id=rfid)
    mem = card.member

    cards = AccessCard.objects.filter(member=mem)

    return render(request,
                  'members/member_details.html',
                  {'member': mem,
                   'access_cards': cards,
                   'logged_in': True}
                 )

@login_required
def editDetails(request, member_id):
    """
    For editing information about a Member
    """

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

            attributes = ['number', 'type', 'first_name', 'last_name',
                          'address', 'city', 'postal_code', 'email',
                          'emergency_contact', 'emergency_phone_number',
                          'stripe_customer_code', 'brief_notes',
                          ]

            diff_list = []

            for a in attributes:
                old = getattr(actual_member, a)
                new = getattr(edited_member, a)

                if old != new:
                    diff_list.append("<{}: ({}) -> ({})>".format(a, old, new))

            log_str = "{} edited member: {} with fields [{}]".format(
                request.user.username,
                actual_member,
                ",\n".join(diff_list))
            LogEvent.log_now(log_str)

            return members(request)
        else: #form not valid
            member = get_object_or_404(Member, pk=member_id)

    else:
        member = get_object_or_404(Member, pk=member_id)
        mem_form = MemberForm(instance=member)

    return render(request,
                  'members/editDetails.html',
                  {'member': member, 'member_form': mem_form, 'logged_in': True})

@login_required
def addMember(request):
    """Add a new Member"""

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
                    'logged_in': True})

    else:
        mem_form = MemberForm()

    return render(request, 'members/add.html', {'mem_form': mem_form, 'logged_in': True})

@login_required
def memberships(request, member_id=None):
    """Render a list of Memberships"""
    if member_id:
        m_list = Membership.objects.filter(member=member_id)
    else:
        m_list = Membership.objects.all()

        if request.method == 'GET' and 'show' in request.GET:
            if request.GET['show'] == 'expired':
                m_list = Membership.objects.filter(expire_date__lt=datetime.datetime.today())
            elif request.GET['show'] == 'active':
                m_list = Membership.objects.filter(expire_date__gte=datetime.datetime.today())

    return render(request, 'members/memberships.html', {'membership_list': m_list, 'logged_in': True})

@login_required
def addMembership(request, member_id=None):
    """Create a new Membership"""
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
                           'logged_in': True, })

    else:
        ms_form = MembershipForm()
        if member_id:
            ms_form = MembershipForm(initial={'member':member_id})

    return render(request, 'members/add_membership.html', {'ms_form': ms_form, 'logged_in': True})

@login_required
def editMembership(request, m_ship):
    """ Edit a membership """
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
                  {'ship': ship, 'ms_form': ms_form, 'logged_in': True})

@login_required
def promos(request):
    """ Render list of Promotion objects """
    promo_list = Promotion.objects.all()
    return render(request, 'members/promos.html', {'promo_list': promo_list, 'logged_in': True})

@login_required
def editPromo(request, promo_id):
    """
    Edit details of Promotion
    """
    if request.method == 'POST':
        promo_form = PromoForm(request.POST)
        if promo_form.is_valid():
            edited_promo = promo_form.save(commit=False)
            actual_promo = get_object_or_404(Promotion, pk=promo_id)
            edited_promo.pk = actual_promo.pk
            edited_promo.save()

            log_str = "{} changed promotion: [{} qty:{}] -> [{} qty:{}]".format(
                                                         request.user.username,
                                                         actual_promo,
                                                         actual_promo.quantity,
                                                         edited_promo,
                                                         edited_promo.quantity)
            LogEvent.log_now(log_str)

            return promos(request)

    else:
        promo = get_object_or_404(Promotion, pk=promo_id)
        promo_form = PromoForm(instance=promo)

    return render(request, 'members/editPromo.html',
                  {'promo': promo, 'promo_form': promo_form, 'logged_in': True})

@login_required
def addPromo(request):
    """
    Add new Promotion
    """
    if request.method == 'POST':
        promo_form = PromoForm(request.POST)
        if promo_form.is_valid():
            new_promo = promo_form.save(commit=False)
            pname = str(new_promo.name)
            if pname.strip() == "":
                new_promo.name = "Unlabeled Promotion"
            new_promo.save()

            log_str = "{} created promotion: [{} qty:{}]".format(request.user.username,
                                                         new_promo,
                                                         new_promo.quantity)
            LogEvent.log_now(log_str)

            return promos(request)

    else:
        promo_form = PromoForm()

    return render(request, 'members/editPromo.html', {'promo_form': promo_form, 'logged_in': True})

@login_required
def promoItems(request, promo_id):
    """
    Get a list of promo items
    """
    promo = get_object_or_404(Promotion, pk=promo_id)
    items = promo.promo_item_set.all()
    return render(request, 'members/promoItems.html', {'promo': promo, 'items': items, 'logged_in': True})

@login_required
def addPromoItem(request):
    """
    Add new Promotion Item (instance of promotion)
    """
    if request.method == 'POST':
        pi_form = PromoItemForm(request.POST)
        if pi_form.is_valid():
            new_pi = pi_form.save(commit=False)
            new_pi.save()

            log_str = "{} created promo item: [{}]".format(request.user.username,
                                                         new_pi)
            LogEvent.log_now(log_str)

            return promoItems(request, new_pi.promo.pk)

    else:
        pi = PromoItemForm()

    return render(request, 'members/editPromoItem.html', {'promo_form': pi, 'logged_in': True})

@login_required
def addPromoItem_fromPromo(request, promo_id):
    """
    Add new Promotion Item (instance of promotion) based on a Promo

    This allows us to fill in some details for the user
    """
    promotion = get_object_or_404(Promotion, pk=promo_id)
    #item = Promo_item(promo=Promotion, used=0, total=promotion.quantity)
    data = {'promo': promo_id, 'used': 0, 'total': promotion.quantity}
    pi = PromoItemForm(initial=data)

    return render(request, 'members/editPromoItem.html', {'promo_form': pi, 'logged_in': True})

@login_required
def editPromoItem(request, pi_id):
    """
    Edit details of Promo Item
    """
    if request.method == 'POST':
        pi_form = PromoItemForm(request.POST)
        if pi_form.is_valid():
            edited_pi = pi_form.save(commit=False)
            actual_pi = get_object_or_404(Promo_item, pk=pi_id)
            edited_pi.pk = actual_pi.pk
            print("edited = {}".format(edited_pi))
            edited_pi.save()

            log_str = "{} changed promo item: [{}] -> [{}]".format(
                                                         request.user.username,
                                                         actual_pi,
                                                         edited_pi)
            LogEvent.log_now(log_str)

            return promoItems(request, edited_pi.promo.pk)

    else:
        pi = get_object_or_404(Promo_item, pk=pi_id)
        pi_form = PromoItemForm(instance=pi)

    return render(request, 'members/editPromoItem.html',
                  {'promo_item': pi, 'promo_form': pi_form, 'logged_in': True})

@login_required
def redeemPromoItem(request, pi_id):
    """
    Use a promo item to create a membership
    """
    pi = get_object_or_404(Promo_item, pk=pi_id)

    if pi.used < pi.total:
        pi.used += 1
        pi.save()

        ms = Membership(member=pi.member,
                        start_date=datetime.datetime.today().date(),
                        expire_date=datetime.datetime.today().date())
        ms.save()

        ps = Promo_sub(promo=pi.promo, membership=ms)
        ps.save()

        log_str = "{} redeemed promo item: [{}]".format(
                                                         request.user.username,
                                                         pi)
        LogEvent.log_now(log_str)

        return editMembership(request, ms.pk)

    else:
        promo = get_object_or_404(Promotion, pk=pi.promo.pk)
        items = promo.promo_item_set.all()
        msg_err = "Item [{}] has no quantity remaining".format(pi)
        return render(request, 'members/promoItems.html', {'promo': promo,
                                                           'items': items,
                                                           'msg_err': msg_err,
                                                           'logged_in': True})

@login_required
def cards(request):
    """Render list of AccessCard objects"""
    card_list = AccessCard.objects.all()
    return render(request, 'members/access_cards.html', {'card_list': card_list,
                                                         'logged_in': True})

@login_required
def checkCard(request, card_rfid):
    """
    Find a card by its uid and display its details.

    Will also present the option to create a new card
    """
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
                                                         'logged_in': True})

@login_required
def cardDetails(request, card_id):
    """
    Get details about an AccessCard

    This will also fetch a list of AccessGroups associated with the Card.

    Optionally the user can request (via POST) to have a visual aid generated.
    The visual aid is a table of times over the next 7 days (hour-by-hour). The
    table will show the user which times the card provides access and which
    times it does not. This may be a slow and expensive opteration.
    """
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
                   'logged_in': True})

@login_required
def cardAssign(request, card_id):
    """
    Assign one or more AccessGroups to a card.
    """
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
                       'logged_in': True})

    else:
        form = AddGroupToCardForm()
        #Now get all the AccessGroups
        groups = AccessGroup.objects.all()
        print(groups)
        return render(request,
                      'members/card_assign.html',
                      {'card': card,
                       'form': form,
                       'logged_in': True})

def editCard(request, card_id):
    """
    Edit details of AccessCard
    """
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
        card = get_object_or_404(AccessCard, pk=card_id)
        card_form = CardForm(instance=card)


    return render(request, 'members/editCard.html', {'card': card,
                                                     'card_form': card_form,
                                                     'logged_in': True})

@login_required
def addCard(request):
    """
    Create a new AccessCard
    """
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
                               'logged_in': True })

            newCard.unique_id = newCard.unique_id.replace(' ', '').lower()
            newCard.save()

            log_str = "{} created a new card: {}".format(request.user.username, newCard)
            LogEvent.log_now(log_str)

            info = 'Created new Access Card'
            c_list = AccessCard.objects.all()
            return render(request, 'members/main.html',
                          {'card_list': c_list,
                           'msg_info': info,
                           'logged_in': True })

    else:
        c_form = CardForm()

    return render(request, 'members/add_card.html', {'card_form': c_form, 'logged_in': True})

@login_required
def groups(request):
    """
    Get a list of AccessGroups
    """
    groups = AccessGroup.objects.all()
    return render(request, 'members/access_groups.html', {'group_list': groups,
                                                          'logged_in': True})

@login_required
def tblks(request):
    """
    Get a list of TimeBlocks
    """
    block_list = TimeBlock.objects.all()
    return render(request, 'members/time_blocks.html', {'block_list': block_list,
                                                        'logged_in': True})

@login_required
def event_log(request):
    """
    Display log entries
    """
    logs = LogEvent.objects.all().order_by('-pk')
    paginator = Paginator(logs, 25)

    page = request.GET.get('page')
    try:
        log_list = paginator.page(page)
    except PageNotAnInteger:
        log_list = paginator.page(1)
    except EmptyPage:
        log_list = paginator.page(paginator.num_pages)

    return render(request, 'members/event_log.html', {'log_list': log_list,
                                                      'logged_in': True})

@login_required
def access_log(request):
    """
    Display log entries
    """
    logs = LogAccessRequest.objects.all().order_by('-pk')
    paginator = Paginator(logs, 25)

    page = request.GET.get('page')
    try:
        log_list = paginator.page(page)
    except PageNotAnInteger:
        log_list = paginator.page(1)
    except EmptyPage:
        log_list = paginator.page(paginator.num_pages)

    return render(request, 'members/access_log.html', {'log_list': log_list,
                                                       'logged_in': True})

@login_required
def incidents(request):
    """
    Display a list of incident reports
    """
    reports = IncidentReport.objects.all().order_by('-pk')
    paginator = Paginator(reports, 25)

    page = request.GET.get('page')
    try:
        report_list = paginator.page(page)
    except PageNotAnInteger:
        report_list = paginator.page(1)
    except EmptyPage:
        report_list = paginator.page(paginator.num_pages)

    return render(request, 'members/incident_list.html', {'report_list': report_list,
                                                          'logged_in': True})

@login_required
def incidentReport(request):
    """
    Create a new incident report
    """
    if request.method == 'POST':
        ir_form = IncidentReportForm(request.POST)
        if ir_form.is_valid():
            new_report = ir_form.save(commit=False)
            new_report.post_date = datetime.date.today()
            new_report.post_time = datetime.datetime.now().time()
            new_report.save()

            #deal with the many-to-many relationships
            for m in request.POST.getlist('effected_members'):
                mem = Member.objects.get(pk=m)
                new_report.effected_members.add(mem)
            for m in request.POST.getlist('staff_on_duty'):
                mem = Member.objects.get(pk=m)
                new_report.staff_on_duty.add(mem)

            log_str = "{} created incident report: [{}]".format(request.user.username,
                                                                new_report)
            LogEvent.log_now(log_str)

            email_body = render_to_string('members/email_incident.html',
                                          {'user': request.user.username,
                                           'report': new_report})
            send_mail(str(new_report),
                      email_body,
                      'mr_saturn@heliosmakerspace.ca',
                      ['council@heliosmakerspace.ca'],
                      fail_silently=False,
                      )

            return incidents(request)

    else:
        ir_form = IncidentReportForm()

    return render(request, 'members/edit_incident.html', {'report_form': ir_form, 'logged_in': True})

@login_required
def editIncidentReport(request, ir_id):
    """
    Edit incident report
    """
    if request.method == 'POST':
        ir_form = IncidentReportForm(request.POST)
        if ir_form.is_valid():
            edited_ir = ir_form.save(commit=False)
            actual_ir = get_object_or_404(IncidentReport, pk=ir_id)
            edited_ir.pk = actual_ir.pk
            edited_ir.post_date = actual_ir.post_date
            edited_ir.post_time = actual_ir.post_time
            edited_ir.save()

            #deal with the many-to-many relationships
            edited_ir.effected_members.clear()
            for m in request.POST.getlist('effected_members'):
                mem = Member.objects.get(pk=m)
                edited_ir.effected_members.add(mem)
            edited_ir.staff_on_duty.clear()
            for m in request.POST.getlist('staff_on_duty'):
                mem = Member.objects.get(pk=m)
                edited_ir.staff_on_duty.add(mem)

            log_str = "{} changed incident report: [{}] -> [{}]".format(
                                                         request.user.username,
                                                         actual_ir,
                                                         edited_ir)
            LogEvent.log_now(log_str)

            return incidents(request)

    else:
        ir = get_object_or_404(IncidentReport, pk=ir_id)
        ir_form = IncidentReportForm(instance=ir)

    return render(request, 'members/edit_incident.html',
                  {'report': ir, 'report_form': ir_form, 'logged_in': True})

@login_required
def viewIncident(request, report_id):
    """
    Read only display of report
    """
    report = get_object_or_404(IncidentReport, pk=report_id)

    return render(request, 'members/report_details.html',
                  {'report': report, 'logged_in': True})

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
                log_str = "Denied access for ID: {} [card not found]".format(uID)
                LogAccessRequest.log_now(log_str)
                #return HttpResponse("Denied", content_type="text/plain")
            else:
                #one or more cards found
                for card in cards:
                    card.member.last_seen_date = datetime.date.today()
                    card.member.save()
                    if card.has_access_now():
                        log_str = "Granted access for card {}".format(card)
                        LogAccessRequest.log_now(log_str)
                        return HttpResponse("Granted", content_type="text/plain")
                    else:
                        log_str = "Denied access for card: {} [no access at this time]".format(card)
                        LogAccessRequest.log_now(log_str)


    response = HttpResponse("Denied", content_type="text/plain")
    return response
