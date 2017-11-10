from django.test import TestCase

from recipes.factories import IngredientFactory, RecipeFactory, RecipeComponentFactory


class RecipeComponentIngredientMatching(TestCase):
    def setUp(self):
        self.ingredient = IngredientFactory.create()
        self.ingredient_class = self.ingredient.ingredient_class
        self.other_ingredient = IngredientFactory.create(
            ingredient_class=self.ingredient_class,
        )

        self.wrong_ingredient = IngredientFactory.create()
        self.wrong_ingredient_class = self.wrong_ingredient.ingredient_class

        self.ingredient_recipe_component = RecipeComponentFactory.create(
            ingredient=self.ingredient,
        )
        self.class_recipe_component = RecipeComponentFactory.create(
            ingredient_class=self.ingredient_class,
        )

    def test_exact_ingredient_match(self):
        self.assertTrue(
            self.ingredient_recipe_component.matches(self.ingredient)
        )

    def test_ingredient_class_match(self):
        self.assertTrue(
            self.ingredient_recipe_component.matches(self.ingredient)
        )

        self.assertTrue(
            self.class_recipe_component.matches(self.other_ingredient)
        )


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
