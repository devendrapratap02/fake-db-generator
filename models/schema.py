import json
import os
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

class DbType(Enum):
    MySql = "mysql"
    Postgres = "psql"
    SqLite = "sqlite"

class DbOptions(BaseModel):
    dbtype: DbType = Field(exclude=True)
    drivername: str
    username: str
    password: str
    host: str
    database: str

class DbColumn(BaseModel):
    name: str
    type: dict
    options: dict

class DbTable(BaseModel):
    name: str
    columns: list[DbColumn]

class PopulateField(BaseModel):
    name: str
    generator: str
    args: Optional[Any] = None

class DbPopulate(BaseModel):
    name: str
    fields: list[PopulateField]
    count: int

class DbSchema(BaseModel):
    database: DbOptions
    tables: Optional[list[DbTable]]
    populate: list[DbPopulate]

def load_schema(filename):
    with open(filename) as file:
        db = json.load(file)
    
    return DbSchema(**db)

if __name__ == "__main__":
    filename = os.path.join(os.path.dirname(__file__), "..", "data", "schema.json")
    sc = load_schema(filename)
