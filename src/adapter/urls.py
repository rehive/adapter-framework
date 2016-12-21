from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = (
    url(r'^withdraw/$', views.WithdrawView.as_view(), name='withdraw'),
    url(r'^deposit/$', views.DepositView.as_view(), name='deposit'),
    # url(r'^operating/balance/$', views.BalanceView.as_view(), name='operating_balance'),
    # url(r'^operating/account/$', views.OperatingAccountView.as_view(), name='operating_account'),
    # url(r'^user/account/$', views.UserAccountView.as_view(), name='user_account'),
    url(r'^$', views.adapter_root)

)

urlpatterns = format_suffix_patterns(urlpatterns)
