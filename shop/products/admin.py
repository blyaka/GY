# admin.py
from django.contrib import admin
from django import forms
from django.db.models import Sum
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe

from .models import (
    Collection, Color, Size, Fabric,
    Product, ProductImage, ProductFabric
)


class ColorInput(forms.TextInput):
    input_type = "color"
    def __init__(self, attrs=None):
        base = {"style": "width: 80px; height: 40px; padding: 0; border: none;"}
        base.update(attrs or {})
        super().__init__(attrs=base)

class ColorAdminForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ["name", "hex_code"]
        widgets = {"hex_code": ColorInput()}

    def clean_hex_code(self):
        hx = (self.cleaned_data.get("hex_code") or "").strip()
        if not hx.startswith("#"):
            hx = "#" + hx
        if len(hx) != 7:
            raise forms.ValidationError("HEX должен быть в формате #RRGGBB.")
        return hx.upper()

class ProductFabricInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = 0
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            if not form.cleaned_data or form.errors:
                continue
            pct = form.cleaned_data.get("percentage") or 0
            total += pct
        if total > 100:
            raise forms.ValidationError("Сумма процентов состава по товару не может превышать 100%.")

class ProductImageInlineForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image", "is_featured", "order"]






@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "preview", "is_featured", "order")
    list_editable = ("is_featured", "order")
    search_fields = ("product__name", "product__article")
    list_filter = ("is_featured",)
    readonly_fields = ("preview",)

    def preview(self, obj):
        if not obj.image:
            return "—"
        return mark_safe(f'<img src="{obj.image.url}" style="height:60px;border-radius:4px;">')
    preview.short_description = "Превью"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageInlineForm
    extra = 1
    fields = ("preview", "image", "is_featured", "order")
    readonly_fields = ("preview",)
    ordering = ("order", "id")

    def preview(self, obj):
        if not getattr(obj, "image", None):
            return "—"
        try:
            url = obj.image.url
        except Exception:
            return "—"
        return mark_safe(f'<img src="{url}" style="height:60px;border-radius:4px;">')
    preview.short_description = "Превью"


class ProductFabricInline(admin.TabularInline):
    model = ProductFabric
    formset = ProductFabricInlineFormSet
    extra = 1
    autocomplete_fields = ("fabric",)
    fields = ("fabric", "percentage")




@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    form = ColorAdminForm
    list_display = ("name", "hex_swatch", "hex_code")
    search_fields = ("name", "hex_code")
    ordering = ("name",)

    def hex_swatch(self, obj):
        return mark_safe(
            f'<span style="display:inline-block;width:28px;height:18px;'
            f'border:1px solid #ccc;background:{obj.hex_code};vertical-align:middle;"></span>'
        )
    hex_swatch.short_description = "Цвет"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Fabric)
class FabricAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "date_of_creation")
    search_fields = ("name",)
    list_filter = ("date_of_creation",)
    ordering = ("-date_of_creation", "name")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "collection", "price", "featured_thumb")
    list_select_related = ("collection",)
    search_fields = ("name", "article", "collection__name")
    list_filter = ("collection", "colors", "sizes")
    autocomplete_fields = ("collection",)
    filter_horizontal = ("colors", "sizes")
    inlines = (ProductImageInline, ProductFabricInline)
    save_as = True
    save_on_top = True
    readonly_fields = ("article", "featured_thumb")

    base_fieldsets = (
        ("Основное", {"fields": ("collection", "name", "description")}),
        ("Параметры", {"fields": ("price", "colors", "sizes")}),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.base_fieldsets
        return self.base_fieldsets + (
            ("Служебное", {"fields": ("article", "featured_thumb")}),
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("images", "colors", "sizes")

    def featured_thumb(self, obj):
        img = obj.get_featured_image()
        if not img:
            return "—"
        try:
            url = img.image.url
        except Exception:
            return "—"
        from django.utils.safestring import mark_safe
        return mark_safe(f'<img src="{url}" style="height:45px;border-radius:4px;">')
    featured_thumb.short_description = "Обложка"

