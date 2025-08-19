from django.db import models
from django.db.models import Q, UniqueConstraint
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import random



def generate_article() -> str:

    return str(random.randint(10000, 99999))


hex_validator = RegexValidator(
    regex=r"^#([0-9A-Fa-f]{6})$",
    message="Укажите HEX в формате #RRGGBB",
)

article_validator = RegexValidator(
    regex=r"^\d{5}$",
    message="Артикул должен состоять ровно из 5 цифр",
)



class Collection(models.Model):
    name = models.CharField("Название коллекции", max_length=100, db_index=True)
    date_of_creation = models.DateField("Дата выпуска")

    class Meta:
        verbose_name = "Коллекция"
        verbose_name_plural = "Коллекции"
        ordering = ("-date_of_creation", "name")
        indexes = [
            models.Index(fields=("date_of_creation",)),
        ]

    def __str__(self) -> str:
        return self.name


class Color(models.Model):
    name = models.CharField("Цвет", max_length=50, unique=True)
    hex_code = models.CharField("HEX-код", max_length=7, validators=[hex_validator], unique=True)

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.hex_code})"


class Size(models.Model):
    name = models.CharField("Размер", max_length=20, unique=True)

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Fabric(models.Model):
    name = models.CharField("Материал", max_length=50, unique=True)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name





class Product(models.Model):
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="products", verbose_name="Коллекция"
    )
    name = models.CharField("Название", max_length=100, db_index=True)
    article = models.CharField(
        "Артикул", max_length=5, unique=True, editable=False, validators=[article_validator]
    )
    colors = models.ManyToManyField(Color, verbose_name="Цвета", blank=True, related_name="products")
    sizes = models.ManyToManyField(Size, verbose_name="Размеры", blank=True, related_name="products")
    description = models.TextField("Описание", blank=True)
    price = models.PositiveIntegerField("Цена", validators=[MinValueValidator(0)], db_index=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("name", "id")
        indexes = [
            models.Index(fields=("article",)),
            models.Index(fields=("price",)),
            models.Index(fields=("name",)),
        ]

    def save(self, *args, **kwargs):
        if not self.article:
            new_article = generate_article()
            while Product.objects.filter(article=new_article).exists():
                new_article = generate_article()
            self.article = new_article
        super().save(*args, **kwargs)

    def get_featured_image(self):
        return self.images.filter(is_featured=True).first() or self.images.order_by("order", "id").first()

    def __str__(self) -> str:
        return f"{self.name} ({self.article})"


class ProductFabric(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="fabrics", verbose_name="Товар"
    )
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE, verbose_name="Материал")
    percentage = models.PositiveIntegerField(
        "Содержание, %", validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    class Meta:
        verbose_name = "Состав материала"
        verbose_name_plural = "Состав материала"
        ordering = ("product", "fabric")
        constraints = [
            UniqueConstraint(fields=("product", "fabric"), name="uniq_fabric_per_product"),
        ]

    def clean(self):
        if not self.product_id:
            return
        qs = ProductFabric.objects.filter(product=self.product).exclude(pk=self.pk)
        total = qs.aggregate(s=models.Sum("percentage"))["s"] or 0
        if total + (self.percentage or 0) > 100:
            from django.core.exceptions import ValidationError
            raise ValidationError({"percentage": "Сумма процентов состава по товару не может превышать 100%."})

    def __str__(self) -> str:
        return f"{self.product.name}: {self.fabric.name} — {self.percentage}%"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    image = models.ImageField("Фото", upload_to="products/")
    is_featured = models.BooleanField("Главное фото", default=False)
    order = models.PositiveIntegerField("Порядок", default=0, db_index=True)

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фотографии товара"
        ordering = ("order", "id")
        constraints = [
            UniqueConstraint(
                fields=("product",),
                condition=Q(is_featured=True),
                name="uniq_featured_image_per_product",
            ),
        ]
        indexes = [
            models.Index(fields=("product", "order")),
        ]

    def save(self, *args, **kwargs):
        if self.is_featured and self.product_id:
            ProductImage.objects.filter(product=self.product, is_featured=True).exclude(pk=self.pk).update(is_featured=False)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        tag = "главное" if self.is_featured else f"#{self.order}"
        return f"{self.product.name} — {tag}"
