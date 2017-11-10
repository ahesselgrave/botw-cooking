from django.test import TestCase

from recipes.factories import IngredientFactory, RecipeFactory, RecipeComponentFactory


class RecipeCombinationExactIngredientsTest(TestCase):
    def setUp(self):
        self.first_ingredient = IngredientFactory.create()
        self.second_ingredient = IngredientFactory.create()
        self.wrong_ingredient = IngredientFactory.create()

        self.first_component = RecipeComponentFactory.create(
            ingredient=self.first_ingredient,
        )
        self.second_component = RecipeComponentFactory.create(
            ingredient=self.second_ingredient,
        )

        self.valid_recipe = RecipeFactory.create(
            components=[
                self.first_component,
                self.second_component,
            ]
        )

    def test_exact_ingredient_combination(self):
        self.assertTrue(
            self.valid_recipe.confirm_ingredients_match([
                self.first_ingredient,
                self.second_ingredient,
            ])
        )

    def test_ingredient_order_doesnt_matter(self):
        self.assertTrue(
            self.valid_recipe.confirm_ingredients_match([
                self.second_ingredient,
                self.first_ingredient,
            ])
        )

    def test_missing_ingredient_fails(self):
        self.assertFalse(
            self.valid_recipe.confirm_ingredients_match([
                self.first_ingredient,
            ])
        )

        self.assertFalse(
            self.valid_recipe.confirm_ingredients_match([
                self.second_ingredient,
            ])
        )

    def test_extra_ingredients_fail(self):
        self.assertFalse(
            self.valid_recipe.confirm_ingredients_match([
                self.first_ingredient,
                self.first_ingredient,
                self.second_ingredient,
            ])
        )

    def test_wrong_ingredient_fails(self):
        self.assertFalse(
            self.valid_recipe.confirm_ingredients_match([
                self.first_ingredient,
                self.second_ingredient,
                self.wrong_ingredient,
            ])
        )
