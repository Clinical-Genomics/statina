from typing import Optional, Literal, List, Iterable

from pydantic import parse_obj_as

from statina.adapter import StatinaAdapter
from statina.constants import SCOPES, sort_table
from statina.crud.utils import paginate
from statina.models.database import User


def get_users_text_query(query_string: str) -> dict:
    """Text search with regex, case insensitive"""
    return {
        "$or": [
            {"username": {"$regex": query_string, "$options": "i"}},
            {"email": {"$regex": query_string, "$options": "i"}},
        ]
    }


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
    query_string: Optional[str] = "",
    role: Literal["", "admin", "unconfirmed", "inactive", "R", "RW"] = "",
    sort_key: Literal["added", "username", "email"] = "added",
    sort_direction: Literal["ascending", "descending"] = "ascending",
) -> List[User]:
    """
    Query users from the user collection.
    Pagination can be enabled with <page_size> and <page_num> options.
    No pagination enabled by default.
    """
    skip, limit = paginate(page_size=page_size, page_num=page_num)
    users: Iterable[dict] = (
        adapter.user_collection.find(
            {
                "$and": [
                    {"role": {"$in": [role or x for x in SCOPES]}},
                    get_users_text_query(query_string=query_string),
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
    query_string: Optional[str] = "",
    role: Literal["", "admin", "unconfirmed", "inactive", "R", "RW"] = "",
) -> int:
    """Count all queried users from the user collection"""
    return adapter.user_collection.count_documents(
        filter={
            "$and": [
                {"role": {"$in": [role or x for x in SCOPES]}},
                get_users_text_query(query_string=query_string),
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
