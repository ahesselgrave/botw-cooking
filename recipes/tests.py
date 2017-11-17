from django.test import TestCase

from recipes.factories import IngredientFactory, RecipeFactory, RecipeComponentFactory, IngredientClassFactory
from recipes.models import Recipe


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

    def tearDown(self):
        self.first_ingredient.delete()
        self.second_ingredient.delete()
        self.wrong_ingredient.delete()

        self.first_component.delete()
        self.second_component.delete()

        self.valid_recipe.delete()

    def test_exact_ingredient_combination(self):
        self.assertEqual(
            Recipe.objects.best_match_from_ingredients(
                self.first_ingredient,
                self.second_ingredient,
            ),
            self.valid_recipe,
        )

    def test_ingredient_order_doesnt_matter(self):
        self.assertEqual(
            Recipe.objects.best_match_from_ingredients(
                self.second_ingredient,
                self.first_ingredient,
            ),
            self.valid_recipe
        )

    def test_missing_ingredient_fails(self):
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.first_ingredient,
            )
        )

        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.second_ingredient,
            )
        )

    def test_extra_ingredients_fail(self):
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.first_ingredient,
                self.first_ingredient,
                self.second_ingredient,
            )
        )

    def test_wrong_ingredient_fails(self):
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.first_ingredient,
                self.second_ingredient,
                self.wrong_ingredient,
            )
        )


class RecipeCombinationClassOnlyTest(TestCase):
    def setUp(self):
        self.first_class = IngredientClassFactory.create()
        self.second_class = IngredientClassFactory.create()
        self.wrong_class = IngredientClassFactory.create()

        self.first_component = RecipeComponentFactory.create(
            ingredient_class=self.first_class,
        )
        self.second_component = RecipeComponentFactory.create(
            ingredient_class=self.second_class,
        )

        self.valid_recipe = RecipeFactory.create(
            components=[
                self.first_component,
                self.second_component,
            ]
        )

        self.first_class_ingredient = IngredientFactory.create(
            ingredient_class=self.first_class,
        )
        self.other_first_class_ingredient = IngredientFactory.create(
            ingredient_class=self.first_class,
        )
        self.second_class_ingredient = IngredientFactory.create(
            ingredient_class=self.second_class,
        )
        self.wrong_class_ingredient = IngredientFactory.create(
            ingredient_class=self.wrong_class,
        )

    def tearDown(self):
        self.first_class.delete()
        self.second_class.delete()
        self.wrong_class.delete()

        self.first_component.delete()
        self.second_component.delete()

        self.valid_recipe.delete()

        self.first_class_ingredient.delete()
        self.other_first_class_ingredient.delete()
        self.second_class_ingredient.delete()
        self.wrong_class_ingredient.delete()

    def test_class_match_recipe(self):
        self.assertEqual(
            Recipe.objects.best_match_from_ingredients(
                self.first_class_ingredient,
                self.second_class_ingredient,
            ),
            self.valid_recipe,
        )

    def test_class_order_doesnt_matter(self):
        self.assertEqual(
            Recipe.objects.best_match_from_ingredients(
                self.second_class_ingredient,
                self.first_class_ingredient,
            ),
            self.valid_recipe,
        )

    def test_other_ingredient_in_class_matches(self):
        self.assertEqual(
            Recipe.objects.best_match_from_ingredients(
                self.other_first_class_ingredient,
                self.second_class_ingredient,
            ),
            self.valid_recipe,
        )

    def test_wrong_ingredient_class_fails(self):
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.wrong_class_ingredient,
                self.second_class_ingredient,
            ),
            self.valid_recipe,
        )
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.first_class_ingredient,
                self.wrong_class_ingredient,
            ),
            self.valid_recipe,
        )

    def test_missing_class_fails(self):
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.first_class_ingredient,
            ),
            self.valid_recipe,
        )
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.second_class_ingredient,
            ),
            self.valid_recipe,
        )

    def test_extra_ingredient_fails(self):
        self.assertIsNone(
            Recipe.objects.best_match_from_ingredients(
                self.first_class_ingredient,
                self.second_class_ingredient,
                self.second_class_ingredient,
            ),
            self.valid_recipe,
        )
