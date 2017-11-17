from typing import List, Union

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, Count, When
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from recipes.managers import RecipeManager


class IngredientClass(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name_plural = 'Ingredient classes'

    def __str__(self):
        return '%s class' % self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    ingredient_class = models.ForeignKey(
        to='recipes.IngredientClass',
        related_name='ingredients',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            ('name', 'ingredient_class'),
        )

    def __str__(self):
        return '%s (%s)' % (
            self.name,
            self.ingredient_class,
        )


class RecipeComponent(models.Model):
    ingredient = models.ForeignKey(
        to='recipes.Ingredient',
        related_name='components',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    ingredient_class = models.ForeignKey(
        to='recipes.IngredientClass',
        related_name='components',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    @property
    def component(self) -> Union['Ingredient', 'IngredientClass']:
        if self.ingredient:
            return self.ingredient
        elif self.ingredient_class:
            return self.ingredient_class

    def __str__(self):
        is_ingredient = isinstance(self.component, Ingredient)
        return ('%s' if is_ingredient else 'Any %s') % self.component.name

    def clean(self):
        if not self.ingredient and not self.ingredient_class:
            raise ValidationError(_('At least one of `ingredient` and `ingredient_class` must be set.'))
        elif self.ingredient and self.ingredient_class:
            raise ValidationError(_('Only one of `ingredient` and `ingredient_class` can be set.'))


class Recipe(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    num_ingredients = models.IntegerField(default=0)
    num_classes = models.IntegerField(default=0)

    components = models.ManyToManyField(
        to='recipes.RecipeComponent',
    )

    objects = RecipeManager()

    def __str__(self):
        return '%s recipe: [%s]' % (
            self.name,
            ' + '.join(str(component) for component in self.components.all()),
        )

@receiver(m2m_changed, sender=Recipe.components.through)
def recipe_component_changed_update_recipe(**kwargs):
    action = kwargs.pop('action', None)
    pk_set = kwargs.pop('pk_set', None)
    recipe = kwargs.pop('instance', None)

    if action == 'pre_add':
        # Validate that the pk_set size will not exceed max recipe capacity
        if recipe.num_ingredients + recipe.num_classes + len(pk_set) > 5:
            raise ValidationError(_('Recipe cannot exceed 5 components.'))
    elif action in ['post_add', 'post_remove']:
        # Update num_ingredients and num_classes appropriately
        recipe_breakdown = recipe.components.aggregate(
            num_ingredients=Count(
                Case(
                    When(
                        ingredient__isnull=False,
                        then=1,
                    ),
                    output_field=models.IntegerField()
                )
            ),
            num_classes=Count(
                Case(
                    When(
                        ingredient_class__isnull=False,
                        then=1,
                    ),
                    output_field=models.IntegerField()
                )
            ),
        )
        recipe.num_ingredients = recipe_breakdown['num_ingredients']
        recipe.num_classes = recipe_breakdown['num_classes']

        recipe.save()
    elif action == 'post_clear':
        recipe.num_ingredients = recipe.num_classes = 0
        recipe.save()
