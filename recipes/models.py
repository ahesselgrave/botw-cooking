from typing import List, Union

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class IngredientClass(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

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
    def _component(self) -> Union['Ingredient', 'IngredientClass']:
        if self.ingredient:
            return self.ingredient
        elif self.ingredient_class:
            return self.ingredient_class

    def __str__(self):
        return 'RecipeComponent: (%s)' % self._component

    def matches(self, ingredient: 'Ingredient') -> bool:
        component = self._component
        if isinstance(component, Ingredient):
            return ingredient == component
        elif isinstance(component, IngredientClass):
            return ingredient.ingredient_class == component

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

    components = models.ManyToManyField(
        to='recipes.RecipeComponent',
    )

    def confirm_ingredients_match(self, ingredients: List['Ingredient']) -> bool:
        """
        Returns true if given ingredients create this recipe
        """
        recipe_components = list(self.components.all())
        for ingredient in ingredients:
            # Test ingredient along all components
            ingredient_matches = False
            for component in recipe_components:
                if component.matches(ingredient):
                    ingredient_matches = True
                    recipe_components.remove(component)
                    break

            # If ingredient matched none of the components, the recipe is wrong
            if not ingredient_matches:
                return False

        # Check that all components were accounted for
        if len(recipe_components) > 0:
            return False

        return True

    def __str__(self):
        return '%s recipe: [%s]' % (
            self.name,
            ','.join(str(component) for component in self.components.all()),
        )
