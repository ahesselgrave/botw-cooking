from django import forms
from django.contrib import admin
from recipes.models import (
    Ingredient, IngredientClass,
    RecipeComponent, Recipe,
)
from django.utils.translation import ugettext_lazy as _


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientClass)
class IngredientClassAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeComponent)
class RecipeComponentAdmin(admin.ModelAdmin):
    pass


class RecipeForm(forms.ModelForm):
    components = forms.ModelMultipleChoiceField(
        queryset=RecipeComponent.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'inline',
            },
        ),
    )
    def clean_components(self):
        if len(self.cleaned_data['components']) > 5:
            raise forms.ValidationError(_('Recipe cannot exceed 5 components.'))
        return self.cleaned_data['components']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = [
        'num_ingredients',
        'num_classes',
    ]

    form = RecipeForm
