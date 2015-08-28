from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.members, name='memberList'),
    url(r'^add/$', views.addMember, name='addMember'),
    url(r'^details/(?P<member_id>\d+)/$', views.memberDetails, name='memberDetails'),
    url(r'^edit/(?P<member_id>\d+)/$', views.editDetails, name='editDetails'),
    url(r'^memberships/$', views.memberships, name='membershipList'),
    url(r'^login/$', views.user_login, name='userLogin'),
    url(r'^logout/$', views.user_logout, name='userLogout'),
]
