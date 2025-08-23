from django.shortcuts import render



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
    return render(request, 'buyer.html')