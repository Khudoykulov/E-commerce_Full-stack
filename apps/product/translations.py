from modeltranslation.translator import register, TranslationOptions
from .models import Category, Product
from apps.account.models import NewBlock, Advice
@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(NewBlock)
class NewBlockTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(Advice)
class AdviceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
