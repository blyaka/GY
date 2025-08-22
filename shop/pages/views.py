from django.shortcuts import render



def HomePage(request):
    return render(request, 'home.html')


def ContactsPage(request):
    return render(request, 'contacts.html')