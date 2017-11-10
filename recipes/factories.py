import factory
from factory.django import DjangoModelFactory


class IngredientClassFactory(DjangoModelFactory):
    class Meta:
        model = 'recipes.IngredientClass'

    name = factory.Faker('name')


class IngredientFactory(DjangoModelFactory):
    class Meta:
        model = 'recipes.Ingredient'

    name = factory.Faker('name')
    ingredient_class = factory.SubFactory(IngredientClassFactory)


class RecipeComponentFactory(DjangoModelFactory):
    class Meta:
        model = 'recipes.RecipeComponent'


class RecipeFactory(DjangoModelFactory):
    class Meta:
        model = 'recipes.Recipe'

    name = factory.Faker('name')

    @factory.post_generation
    def components(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for component in extracted:
                self.components.add(component)
