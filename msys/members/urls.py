from django.conf.urls import url
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    url(r'^$', views.members, name='memberList'),
    url(r'^add/$', views.addMember, name='addMember'),
    url(r'^details/(?P<member_id>\d+)/$', views.memberDetails, name='memberDetails'),
    url(r'^byID/(?P<rfid>[ A-Fa-f0-9]+)/$', views.memberDetailsByRFID, name='memberDetailsByRFID'),
    url(r'^edit/(?P<member_id>\d+)/$', views.editDetails, name='editDetails'),
    re_path(r'^checkin/(?P<member_id>\d+)/$', views.memberCheckin, name='memberCheckin'),
    
    url(r'^memberships/$', views.memberships, name='membershipList'),
    url(r'^memberships/by-member/(?P<member_id>\d+)/$', views.memberships, name='membershipsByMember'),
    url(r'^memberships/add/$', views.addMembership, name='addMembership'),
    url(r'^memberships/add/for-member/(?P<member_id>\d+)/$', views.addMembership, name='addMembershipForMember'),
    url(r'^memberships/edit/(?P<m_ship>\d+)/$', views.editMembership, name='editMembership'),
    
    url(r'^promos/$', views.promos, name='promoList'),
    url(r'^promos/edit/(?P<promo_id>\d+)/$', views.editPromo, name='editPromo'),
    url(r'^promos/add/$', views.addPromo, name='addPromo'),
    url(r'^promos/items/(?P<promo_id>\d+)/$', views.promoItems, name='promoItems'),
    url(r'^promos/items/add/$', views.addPromoItem, name='addPromoItem'),
    url(r'^promos/items/add/(?P<promo_id>\d+)/$', views.addPromoItem_fromPromo, name='addPromoItemFromPromo'),
    url(r'^promos/items/edit/(?P<pi_id>\d+)/$', views.editPromoItem, name='editPromoItem'),
    url(r'^promos/items/redeem/(?P<pi_id>\d+)/$', views.redeemPromoItem, name='redeemPromoItem'),
    
    url(r'^cards/$', views.cards, name='cardList'),
    url(r'^cards/add/$', views.addCard, name='addCard'),
    url(r'^cards/add/(?P<member_id>\d+)$', views.addCard, name='addCardForMember'),
    url(r'^cards/check/(?P<card_rfid>[ A-Fa-f0-9]+)/$', views.checkCard, name='checkCard'),
    re_path(r'^cards/checkin/(?P<card_rfid>[ A-Fa-f0-9]+)/$', views.cardCheckin, name='cardCheckin'),
    url(r'^cards/details/(?P<card_id>\d+)/$', views.cardDetails, name='cardDetails'),
    url(r'^cards/assign/(?P<card_id>\d+)/$', views.cardAssign, name='assignCard'),
    url(r'^cards/edit/(?P<card_id>\d+)/$', views.editCard, name='editCard'),
    
    url(r'^blks/$', views.tblks, name='blklst'),
    url(r'^groups/$', views.groups, name='groupList'),
    url(r'^logs/events/$', views.event_log, name='eventLog'),
    url(r'^logs/access/$', views.access_log, name='accessLog'),
    re_path(r'^logs/checkins/$', views.checkin_log, name='checkinLog'),
    
    url(r'^incidents/$', views.incidents, name='incidentList'),
    url(r'^incidents/report/$', views.incidentReport, name='incidentReport'),
    url(r'^incidents/view/(?P<report_id>\d+)/$', views.viewIncident, name='viewIncident'),
    url(r'^incidents/report/(?P<ir_id>\d+)/$', views.editIncidentReport, name='editReport'),
    
    url(r'^login/$', views.user_login, name='userLogin'),
    url(r'^logout/$', views.user_logout, name='userLogout'),
    url(r'latency/$', views.latency, name='latency'),
    url(r'^weekly_access/$', views.weekly_access, name='weekly_access'),
    url(r'^auth/$', views.auth, name='auth'),
]
