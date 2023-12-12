import json
import os
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)


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
    
    def get_type(self):
        type_name = self.type.get("name")
        type_args = self.type.get("args")
        match type_name:
            case "integer": 
                return Integer
            case "number": 
                return Numeric(**type_args)
            case "string": 
                return String(**type_args)
            case "date": 
                return Date
            case "foreign": 
                return ForeignKey(type_args)
            case _: 
                raise Exception(f"No matched column type found {type_name}")

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
