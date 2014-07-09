# -*- coding: utf-8 -*-


from django.conf.urls import patterns, include, url



urlpatterns = patterns('robokassa.views',
    url(r'^$', "payment", name='payment'),
    url(r'success$', "success", name='payment_success'),
    url(r'fail$', "fail", name='payment_fail'),
)