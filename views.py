# -*- coding: utf-8 -*-


from django.http import HttpResponse, HttpResponseForbidden
from django.db.models.loading import get_model
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import datetime

from __init__ import *
from signals import payment_done

import logging
logger = logging.getLogger(__name__)

def payment(request):
	order_id = int(request.REQUEST.get("InvId"))
	price = float(request.REQUEST.get("OutSum"))
	sign = request.REQUEST.get("SignatureValue").lower()
	our_sign = sign_order2(order_id, request.REQUEST.get("OutSum"))

	model_data = settings.ROBOKASSA_ORDER_MODEL.split('.')
	order_model = get_model(model_data[0], model_data[2])

	try:
		order = order_model.objects.get(id=order_id)
	except ObjectDoesNotExist:
		logger.error("payment(): order %d does not exists" % order_id)
		return HttpResponse("ERROR#INVALID_ORDER")
	
	if (order.price != price):
		logger.error("payment(): order %d have wrong price %d, but expected %d" % (order_id, price, order.price))
		return HttpResponse("ERROR#INVALID_PRICE")

	if (order.status != 0):
		logger.error("payment(): order %d wrong status" % order_id)
		return HttpResponse("ERROR#WRONG_STATUS")

	if (our_sign != sign):
		logger.error("payment(): order %d has sign %s, but expected is %s" % (order_id, our_sign, sign))
		return HttpResponse("ERROR#INVALID_SIGN")
	

	order.status = 1
	order.payed_date = datetime.datetime.now()
	order.save()

	payment_done.send(sender=None,request=request,order=order)

	return HttpResponse("OK%d" % order_id)


def success(request):
	order_id = int(request.REQUEST.get("InvId"))
	price = float(request.REQUEST.get("OutSum"))
	sign = request.REQUEST.get("SignatureValue").lower()
	our_sign = sign_success(order_id, request.REQUEST.get("OutSum"))

	model_data = settings.ROBOKASSA_ORDER_MODEL.split('.')
	order_model = get_model(model_data[0], model_data[2])

	try:
		order = order_model.objects.get(id=order_id)
	except ObjectDoesNotExist:
		logger.error("payment_success(): order %d does not exists" % order_id)
		return redirect(reverse("payment_fail"))

	if (order.status != 1):
		logger.error("payment_success(): order %d not payed" % order_id)
		return redirect(reverse("payment_fail"))

	if (order.price != price):
		logger.error("payment_success(): order %d have wrong price %d, but expected %d" % (order_id, price, order.price))
		return redirect(reverse("payment_fail"))

	if (our_sign != sign):
		logger.error("payment_success(): order %d has bad sign %s, expected %s" % (order_id, sign, our_sign))
		return redirect(reverse("payment_fail"))

	return render_to_response(settings.ROBOKASSA_SUCCESS_TEMPLATE, dict(request=request, order=order))


def fail(request):
	return render_to_response(settings.ROBOKASSA_FAIL_TEMPLATE, dict(request=request))

