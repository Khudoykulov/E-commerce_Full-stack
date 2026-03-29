from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from apps.account.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('id',)


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    description = models.TextField(null=True)
    views = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    # tags = models.ManyToManyField(Tag, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    worth = models.CharField(max_length=123, blank=True, null=True)
    modified_date = models.DateField(auto_now=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.id})'

    @property
    def average_rank(self) -> float:
        try:
            return sum(self.ranks.values_list('rank', flat=True)) / self.ranks.count()
        except ZeroDivisionError:
            return 0

    # @property
    # def get_quantity(self) -> int:
    #     incomes = sum(self.trades.filter(action=1).values_list('quantity', flat=True))
    #     outcomes = sum(self.trades.filter(action=2).values_list('quantity', flat=True))
    #     return incomes - outcomes

    @property
    def get_likes_count(self) -> int:
        return self.likes.count()

    @property
    def discounted_price(self) -> float:
        """Chegirmadan keyingi narx"""
        if self.discount and self.discount > 0:
            return round(float(self.price) * (100 - self.discount) / 100, 2)
        return float(self.price)

    @property
    def discount_amount(self) -> float:
        """Chegirma miqdori (pul)"""
        if self.discount and self.discount > 0:
            return round(float(self.price) * self.discount / 100, 2)
        return 0.0

    @property
    def is_available(self) -> bool:
        return self.quantity > 0

    @property
    def has_wishlist(self) -> bool:
        return self.wishlists.exists()

    @property
    def is_liked(self) -> bool:
        return self.likes.exists()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.product.name


# class Trade(models.Model):
#     ACTION = (
#         (1, _('Income')),
#         (2, _('Outcome')),
#     )
#     product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='trades')
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     action = models.PositiveSmallIntegerField(choices=ACTION, default=1)
#     quantity = models.PositiveIntegerField(default=0)
#     description = models.TextField(null=True)
#     created_date = models.DateField(auto_now_add=True)
#
#     def __str__(self):
#         return self.product.name


class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlists')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.product.name


class Like(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.product.name


class Rank(models.Model):
    RANK_CHOICE = ((r, r) for r in range(1, 11))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ranks')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    rank = models.PositiveSmallIntegerField(default=0, choices=RANK_CHOICE, db_index=True)

    def __str__(self):
        return self.product.name


class Comment(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    comment_image_url = models.CharField(max_length=500, blank=True, default='')
    top_level_comment_id = models.PositiveSmallIntegerField(null=True, blank=True, editable=False)
    created_date = models.DateField(auto_now_add=True)

    @property
    def tree(self):
        return Comment.objects.filter(top_level_comment_id=self.id)


class CommentImage(models.Model):
    image = models.ImageField(upload_to='comment/')

    def __str__(self):
        return self.image.url


def comment_post_save(sender, instance, created, **kwargs):
    if created:
        if instance.parent:
            # reply
            instance.top_level_comment_id = instance.parent.top_level_comment_id
        else:
            instance.top_level_comment_id = instance.id
        instance.save()


post_save.connect(comment_post_save, sender=Comment)
