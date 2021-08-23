from mealie.schema.meal_plan.meal import MealPlanOut
from mealie.schema.user.user import GroupInDB
from sqlalchemy.orm.session import Session

from ._base_access_model import BaseAccessModel


class GroupDataAccessModel(BaseAccessModel):
    def get_meals(self, session: Session, match_value: str, match_key: str = "name") -> list[MealPlanOut]:
        """A Helper function to get the group from the database and return a sorted list of

        Args:
            session (Session): SqlAlchemy Session
            match_value (str): Match Value
            match_key (str, optional): Match Key. Defaults to "name".

        Returns:
            list[MealPlanOut]: [description]
        """
        group: GroupInDB = session.query(self.sql_model).filter_by(**{match_key: match_value}).one_or_none()

        return group.mealplans