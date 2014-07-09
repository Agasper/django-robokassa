django-robokassa
================

Python API for www.robokassa.ru payment service

* Add to urls.py
```python
url(r'^payment/', include("robokassa.urls")),
```

* Add to settings.py
```python
ROBOKASSA_LOGIN = "your_login"
ROBOKASSA_PWD1 = "password1"
ROBOKASSA_PWD2 = "password2"
ROBOKASSA_ORDER_MODEL = "yoursite.models.OrderModel"
ROBOKASSA_SUCCESS_TEMPLATE = "payment_success.html"
ROBOKASSA_FAIL_TEMPLATE = "payment_fail.html"
```
* Your order model should contains these fields:
```python
status = models.SmallIntegerField(default=0)
payed_date = models.DateTimeField(null=True,default=None)
price = models.PositiveIntegerField()
```
* Connect to a signal, if you need it
```python
from robokassa.signals import payment_done
from robokassa import send_sms, send_sms_async
def payment_done_callback(sender, **kwargs):
        #some useful code
        order = kwargs["order"]
        send_sms_async(order.phone, "Congratulations !!!")
payment_done.connect(payment_done_callback, dispatch_uid="payment_done")
```
* In the ```ROBOKASSA_SUCCESS_TEMPLATE``` and ```ROBOKASSA_FAIL_TEMPLATE``` you can use the ```order``` and ```request``` variable to display success text.

* To create a new order use ```robokassa.get_payment_url``` function.

```python
order = models.Order(status=0, price = 100)
order.save()
url = robokassa.get_payment_url(order.id, order.price, u"Buying new HDD", test=False)
return redirect(url)
```
