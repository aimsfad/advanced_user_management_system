import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "user_management_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "users")

_client: Optional[MongoClient] = None
_collection: Optional[Collection] = None

SEARCHABLE_FIELDS = {
    "all": "All Fields",
    "first_name": "First Name",
    "last_name": "Last Name",
    "birth_date": "Birth Date",
    "birth_place": "Birth Place",
    "phone_number": "Phone Number",
}


def get_collection() -> Collection:
    """Create and return the MongoDB users collection."""
    global _client, _collection

    if _collection is not None:
        return _collection

    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        database = _client[DB_NAME]
        _collection = database[COLLECTION_NAME]
        _collection.create_index([("phone_number", ASCENDING)], unique=True)
        return _collection
    except ConnectionFailure as exc:
        raise RuntimeError(
            "Cannot connect to MongoDB. Check that MongoDB is running or that MONGO_URI is correct."
        ) from exc
    except PyMongoError as exc:
        raise RuntimeError(f"MongoDB error: {exc}") from exc


def _stringify_ids(users: List[Dict[str, str]]) -> List[Dict[str, str]]:
    for user in users:
        user["_id"] = str(user["_id"])
    return users


def add_user(user_data: Dict[str, str]) -> str:
    try:
        result = get_collection().insert_one(user_data)
        return str(result.inserted_id)
    except DuplicateKeyError as exc:
        raise ValueError("Phone number already exists. It must be unique.") from exc
    except PyMongoError as exc:
        raise RuntimeError(f"Could not add user: {exc}") from exc


def get_all_users() -> List[Dict[str, str]]:
    try:
        users = list(get_collection().find().sort("created_at", -1))
        return _stringify_ids(users)
    except PyMongoError as exc:
        raise RuntimeError(f"Could not fetch users: {exc}") from exc


def search_users(keyword: str, field: str = "all") -> List[Dict[str, str]]:
    """Search users by all fields or by one selected field.

    Names and birth place use case-insensitive partial matching.
    Birth date and phone number use exact matching because they are structured values.
    """
    keyword = keyword.strip()
    field = field if field in SEARCHABLE_FIELDS else "all"

    if not keyword:
        return get_all_users()

    text_fields = ["first_name", "last_name", "birth_place"]
    exact_fields = ["birth_date", "phone_number"]

    if field == "all":
        query = {
            "$or": [
                {text_field: {"$regex": keyword, "$options": "i"}} for text_field in text_fields
            ]
            + [{exact_field: keyword} for exact_field in exact_fields]
        }
    elif field in text_fields:
        query = {field: {"$regex": keyword, "$options": "i"}}
    else:
        query = {field: keyword}

    try:
        users = list(get_collection().find(query).sort("created_at", -1))
        return _stringify_ids(users)
    except PyMongoError as exc:
        raise RuntimeError(f"Could not search users: {exc}") from exc


def update_user(user_id, new_data: Dict[str, str]) -> int:
    from bson import ObjectId

    try:
        result = get_collection().update_one({"_id": ObjectId(user_id)}, {"$set": new_data})
        return result.modified_count
    except DuplicateKeyError as exc:
        raise ValueError("Phone number already exists. It must be unique.") from exc
    except PyMongoError as exc:
        raise RuntimeError(f"Could not update user: {exc}") from exc


def delete_user(user_id) -> int:
    from bson import ObjectId

    try:
        result = get_collection().delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count
    except PyMongoError as exc:
        raise RuntimeError(f"Could not delete user: {exc}") from exc
