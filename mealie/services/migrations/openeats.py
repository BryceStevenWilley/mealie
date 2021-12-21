import requests

from mealie.db.database import Database

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import scrape_image


def tag_to_str(tags: list[dict]):
    if not isinstance(tags, list):
        return None
    if tags:
        return [x.get("title").strip() for x in tags]


class OpenEatsMigrator(BaseMigrator):
    def __init__(self, archive: str, db: Database, session, user_id: int, group_id: int, add_migration_tag: bool):
        super().__init__(archive, db, session, user_id, group_id, add_migration_tag)

        self.key_aliases = [
            MigrationAlias(key="name", alias="title", func=None),
            MigrationAlias(key="recipe_yield", alias="servings", func=None),
            MigrationAlias(key="org_url", alias="source", func=None),
            MigrationAlias(key="tags", alias="tags", func=tag_to_str),
        ]

    def _migrate(self) -> None:
        """
        Notes: for the migration URL, provide the whole URL to the API entpoint, if possible.
        If not, we default to using HTTPS
        """
        # Get all of the recipes from the given URL, assuming it works.
        base_url = self.archive
        if base_url.endswith("api/v1/recipe/recipes/"):
            api_url = base_url
        elif base_url.endswith("/"):
            api_url = base_url + "api/v1/recipe/recipes"
        else:
            api_url = base_url + "/api/v1/recipe/recipes"

        if not (api_url.startswith("https://") or api_url.startswith("http://")):
            api_url = "https://" + api_url

        current_url = api_url
        existing_recipes = []
        while True:
            try:
                new_resp = requests.get(current_url)
                json_resp = new_resp.json()
                if "results" in json_resp:
                    existing_recipes.extend(json_resp["results"])
                if json_resp.get("next"):
                    current_url = json_resp.get("next")
                else:
                    break
            except Exception as ex:
                raise ex

        all_recipes = []
        for oe_recipe in existing_recipes:
            print(oe_recipe)
            recipe_new = self.clean_recipe_dictionary(oe_recipe)
            print(recipe_new)
            all_recipes.append(recipe_new)

        all_statuses = self.import_recipes_to_database(all_recipes)

        for oe_recipe in existing_recipes:
            scrape_image(oe_recipe)
