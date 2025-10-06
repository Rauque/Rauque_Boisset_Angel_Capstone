from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ("name",)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Opciones de filtro
MATERIAL_CHOICES = [
    ("PVC", "PVC"),
    ("ALU", "Aluminio"),
]
GLASS_CHOICES = [
    ("LAM", "Laminado"),
    ("TEM", "Templado"),
    ("MON", "Monolítico"),
    ("TERM", "Termopanel"),
]
THICKNESS_CHOICES = [
    ("3", "3 mm"),
    ("4", "4 mm"),
    ("5", "5 mm"),
]
COLOR_CHOICES = [
    ("WOOD", "Folio madera"),
    ("TIT", "Titanio"),
    ("WHT", "Blanco"),
    ("RED", "Rojo"),
]

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    material = models.CharField(max_length=3, choices=MATERIAL_CHOICES)
    glass_type = models.CharField(max_length=4, choices=GLASS_CHOICES)
    thickness = models.CharField(max_length=2, choices=THICKNESS_CHOICES)
    color = models.CharField(max_length=5, choices=COLOR_CHOICES)

    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["material", "glass_type", "thickness", "color"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base = slugify(self.name)
            candidate = base
            i = 1
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
