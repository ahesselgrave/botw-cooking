from typing import List

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class IngredientClass(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    image = models.ImageField()

    ingredient_class = models.ForeignKey(
        to='recipes.IngredientClass',
        related_name='ingredients',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            ('name', 'ingredient_class'),
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
    image = models.ImageField()
    components = models.ManyToManyField(
        to='recipes.RecipeComponent',
    )

    def confirm_ingredients_match(self, ingredients: List['Ingredient']) -> bool:
        """
        Returns true if given ingredients create this recipe
        """
        recipe_components = self.components.all()

        recipe_matches = True
        for ingredient in ingredients:
            if not recipe_matches:
                return False

            # Test ingredient along all components
            ingredient_matches = True
            for component in recipe_components:
                # TODO: don't O(n^2) this
                matches = False
                if component.ingredient_class:
                    # Check if ingredient class is same component
                    matches = ingredient.ingredient_class == component.ingredient_class
                elif component.ingredient:
                    # Check if exact ingredient matches component
                    matches = ingredient == component.ingredient

                ingredient_matches = ingredient_matches and matches

            recipe_matches = recipe_matches and ingredient_matches

        return True
