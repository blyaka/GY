from django.shortcuts import render
from django.urls import reverse



def HomePage(request):
    return render(request, 'home.html')


def ContactsPage(request):
    return render(request, 'contacts.html')

def DeliveryPage(request):
    return render(request, 'delivery.html')

def RefundPage(request):
    return render(request, 'refund_exchange.html')


def PrivacyPage(request):
    return render(request, 'privacy_policy.html')

def OfferPage(request):
    return render(request, 'offer.html')

def AboutPage(request):
    return render(request, 'about.html')

def BuyerPage(request):
    ctx = {
        'offer_url': reverse('offer'),
        'privacy_url': reverse('privacy'),
    }
    return render(request, 'buyer.html', ctx)

def PrivaLabPage(request):
    return render(request, 'prive_lab.html')


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)