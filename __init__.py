# -*- coding: utf-8 -*-

from django.conf import settings
import hashlib
import threading
import urllib
import json
import requests

def sign_order(id, price):
	m = hashlib.md5()
	s = "%s:%d:%d:%s" % (settings.ROBOKASSA_LOGIN, price, id, settings.ROBOKASSA_PWD1)
	m.update(s)
	return m.hexdigest().lower()

def sign_order2(id, price):
	m = hashlib.md5()
	s = "%s:%d:%s" % (str(price), id, settings.ROBOKASSA_PWD2)
	m.update(s)
	return m.hexdigest().lower()

def sign_success(id, price):
	m = hashlib.md5()
	s = "%s:%d:%s" % (str(price), id, settings.ROBOKASSA_PWD1)
	m.update(s)
	return m.hexdigest().lower()

def get_sms_sign(phone, message):
	m = hashlib.md5()
	s = "%s:%s:%s:%s" % ("naidi_kvartiru_com_ip", phone.encode("utf-8"), message.encode('utf-8'), "vL1vsF38G3QyrCjTjIZA")
	m.update(s)
	return m.hexdigest().lower()	

def get_payment_url(id, price, description, culture="ru", test=False):
	url = "https://merchant.roboxchange.com/Index.aspx?"
	if (test):
		url = "http://test.robokassa.ru/Index.aspx?"

	params = dict()
	params["MrchLogin"] = settings.ROBOKASSA_LOGIN
	params["OutSum"] = price
	params["InvId"] = id
	params["Desc"] = description.encode('utf-8')
	params["IncCurrLabel"] = ""
	params["SignatureValue"] = sign_order(id, price)
	params["Culture"] = culture

	return url + urllib.urlencode(params)


def send_sms(phone, message):
	phone = ''.join(x for x in phone if x.isdigit())
	url = "https://services.robokassa.ru/SMS/?"
	
	params = dict()
	params["login"] = "naidi_kvartiru_com_ip"#settings.ROBOKASSA_LOGIN
	params["phone"] = phone
	params["message"] = message.encode('utf-8')
	params["signature"] = get_sms_sign(phone, message)

	print url + urllib.urlencode(params)

	r = requests.get(url + urllib.urlencode(params))
	if (r.status_code != 200):
		raise Exception("Bad response: %d" % r.status_code)

	#{"result":false,"count":null,"errorCode":5,"errorMessage":"sms not availible for partner now"}
	obj = json.loads(r.text)

	if (obj["errorCode"] != 0):
		raise Exception(obj["errorMessage"])

def send_sms_async(phone, message):
	threading.Thread(target=send_sms, args=(phone,message)).start()