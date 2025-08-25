from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProfileForm, UserEmailForm
from .models import Profile
from django.contrib import messages
from products.models import Product, ProductImage
from django.db.models import OuterRef, Subquery, Case, When
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest

def PersonalAccountPage(request):
    return render(request, 'account/lk.html')


def _ensure_profile(user):
    return Profile.objects.get_or_create(user=user)[0]


class ProfileEditView(LoginRequiredMixin, View):
    template_name = "account/profile_edit.html"

    def get(self, request):
        profile = _ensure_profile(request.user)
        return render(request, self.template_name, {
            "pform": ProfileForm(instance=profile),
            "uform": UserEmailForm(instance=request.user),
        })

    def post(self, request):
        profile = _ensure_profile(request.user)
        pform = ProfileForm(request.POST, instance=profile)
        uform = UserEmailForm(request.POST, instance=request.user)
        if pform.is_valid() and uform.is_valid():
            pform.save()
            old_email = request.user.email
            user = uform.save()
            try:
                from allauth.account.models import EmailAddress
                ea, _ = EmailAddress.objects.get_or_create(user=user, email=user.email)
                if not ea.verified:
                    ea.set_as_primary()
                    ea.send_confirmation(request)
                if old_email and old_email != user.email:
                    EmailAddress.objects.filter(user=user, email=old_email).delete()
            except Exception:
                pass
            messages.success(request, "Данные профиля успешно изменены!")
            return redirect("lk_edit")
        return render(request, self.template_name, {"pform": pform, "uform": uform})




def _ensure_profile(user):
    return Profile.objects.get_or_create(user=user)[0]

def _thumb_subquery():
    return (ProductImage.objects
            .filter(product=OuterRef('pk'))
            .order_by(
                Case(When(is_featured=True, then=0), default=1),
                'order', 'id'
            )
            .values('id')[:1])

class FavoriteListView(LoginRequiredMixin, View):
    template_name = 'account/favorites.html'
    per_page = 6

    def get(self, request):
        profile = _ensure_profile(request.user)

        qs = (Product.objects
              .filter(favorite_links__profile=profile)
              .annotate(thumb_id=Subquery(_thumb_subquery()))
              .select_related('category', 'collection')
              .prefetch_related('images', 'colors', 'sizes'))

        paginator = Paginator(qs, self.per_page)
        page = request.GET.get('page', 1)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        fav_ids = set(profile.favorite_links.values_list('product_id', flat=True))
        ctx = {
            'items': items,
            'is_paginated': items.has_other_pages(),
            'paginator': paginator,
            'page_obj': items,
            'fav_ids': list(fav_ids),
        }
        return render(request, self.template_name, ctx)






@require_POST
@login_required
def favorite_toggle_api(request):
    import json
    try:
        payload = json.loads(request.body.decode('utf-8'))
        pid = int(payload.get('product_id'))
    except Exception:
        return HttpResponseBadRequest('invalid payload')

    profile = _ensure_profile(request.user)
    try:
        product = Product.objects.get(pk=pid)
    except Product.DoesNotExist:
        return HttpResponseBadRequest('product not found')

    link_qs = profile.favorite_links.filter(product=product)
    if link_qs.exists():
        link_qs.delete()
        return JsonResponse({'ok': True, 'on': False, 'product_id': pid})
    profile.favorite_links.create(product=product)
    return JsonResponse({'ok': True, 'on': True, 'product_id': pid})
