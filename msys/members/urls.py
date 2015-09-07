from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.members, name='memberList'),
    url(r'^add/$', views.addMember, name='addMember'),
    url(r'^details/(?P<member_id>\d+)/$', views.memberDetails, name='memberDetails'),
    url(r'^byID/(?P<rfid>[ A-Fa-f0-9]+)/$', views.memberDetailsByRFID, name='memberDetailsByRFID'),
    url(r'^edit/(?P<member_id>\d+)/$', views.editDetails, name='editDetails'),
    url(r'^memberships/$', views.memberships, name='membershipList'),
    url(r'^memberships/add/$', views.addMembership, name='addMembership'),
    url(r'^cards/$', views.cards, name='cardList'),
    url(r'^blocks/$', views.blocks, name='blockList'),
    url(r'^login/$', views.user_login, name='userLogin'),
    url(r'^logout/$', views.user_logout, name='userLogout'),
]
