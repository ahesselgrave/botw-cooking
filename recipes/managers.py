from typing import List, Optional

from django.db import models
from django.db.models import Q, Count, F, Sum
from functools import reduce
from operator import ior


class RecipeManager(models.Manager):
    def from_ingredients(self, *args: 'Ingredient') -> models.QuerySet:
        # OR all Q objects for each ingredient and its class
        q_filter = reduce(
            ior,  # | operator
            [
                Q(components__ingredient=i) |
                Q(components__ingredient_class=i.ingredient_class)
                for i in args
            ]
        )

        # Have to left outer join to remove some jank in the group by having count calculation
        return self.annotate(
            num_components=Sum(F('num_ingredients') + F('num_classes')),
        ).filter(
            num_components=len(args),
        ).filter(
            q_filter,
        ).order_by(
            '-num_ingredients',
        )

    def best_match_from_ingredients(self, *args: 'Ingredient') -> Optional['Recipe']:
        return self.from_ingredients(*args).first()
