from typing import Optional, Literal, List, Iterable

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import SCOPES, sort_table
from statina.crud.utils import paginate
from statina.models.database import User


def users(
    adapter: StatinaAdapter,
) -> List[User]:
    """Return all users from the batch collection"""
    users: Iterable[dict] = adapter.user_collection.find()
    return parse_obj_as(List[User], list(users))


def query_users(
    adapter: StatinaAdapter,
    page_size: int = 0,
    page_num: int = 0,
    text: Optional[str] = "",
    role: Literal["", "admin", "unconfirmed", "inactive", "R", "RW"] = "",
    sort_key: Literal["added", "username", "email"] = "added",
    sort_direction: Literal["ascending", "descending"] = "ascending",
) -> List[User]:
    """Query users from the user collection"""
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    users: Iterable[dict] = (
        adapter.user_collection.find(
            {
                "$and": [
                    {"role": {"$in": [role or x for x in SCOPES]}},
                    {
                        "$or": [
                            {"username": {"$regex": text, "$options": "i"}},
                            {"email": {"$regex": text, "$options": "i"}},
                        ]
                    },
                ]
            }
        )
        .sort(sort_key, sort_table.get(sort_direction))
        .skip(skip)
        .limit(limit)
    )
    return parse_obj_as(List[User], list(users))


def count_query_users(
    adapter: StatinaAdapter,
    text: Optional[str] = "",
    role: Literal["", "admin", "unconfirmed", "inactive", "R", "RW"] = "",
) -> int:
    """Count all queried users from the user collection"""
    return adapter.user_collection.count_documents(
        filter={
            "$and": [
                {"role": {"$in": [role or x for x in SCOPES]}},
                {
                    "$or": [
                        {"username": {"$regex": text, "$options": "i"}},
                        {"email": {"$regex": text, "$options": "i"}},
                    ]
                },
            ]
        }
    )


def user(
    adapter: StatinaAdapter, email: Optional[str] = None, user_name: Optional[str] = None
) -> Optional[User]:
    """Find user from user collection"""
    if email:
        raw_user: dict = adapter.user_collection.find_one({"email": email})
    elif user_name:
        raw_user: dict = adapter.user_collection.find_one({"username": user_name})
    else:
        raise SyntaxError("Have to use email or user_name")
    if not raw_user:
        return None
    return User(**raw_user)
