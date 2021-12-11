import tempfile
import zipfile
import requests
from pathlib import Path

from mealie.db.database import Database

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import MigrationReaders, import_image

class OpenEatsMigrator(BaseMigrator):
    def __init(self, archive: str, db: Database, session, user_id, int, group_id: int):
        super().__init__(archive, db, session, user_id, group_id)

        self.key_aliases = [
            MigrationAlias(key="name", alias="title", func=None),
            MigrationAlias(key="recipe_yield", alias="servings", func=None),
            MigrationAlias(key="org_url", alias="source", func=None),
        ]
    
    def _migrate(self) -> None:
        """
        Notes: for the migration URL, provide the whole URL to the API entpoint, if possible.
        If not, we default to using HTTPS
        """
        # Get all of the recipes from the given URL, assuming it works.
        base_url = self.archive
        if base_url.endswith('api/v1/recipe/recipes/'):
            api_url = base_url
        elif base_url.endswith('/'):
            api_url = base_url + 'api/v1/recipe/recipes'
        else:
            api_url = base_url + '/api/v1/recipe/recipes'

        if not (api_url.startswith('https://') or api_url.startswith('http://')):
            api_url = 'https://' + api_url

        existing_recipes = []
        while True:
            try:
                new_resp = requests.get(api_url)
                json_resp = new_resp
                existing_recipes.extend(json_resp)
                if not json_resp.get('next'):
                    break
            except Exception as ex:
                pass

        print(existing_recipes)

        # TODO(brycew): CONTINUE
        
