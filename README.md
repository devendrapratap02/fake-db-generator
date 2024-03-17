# JSON Schema to Database Generator (FDG)

FDG (JSON Schema to Database Generator) is a Python tool that allows you to generate database tables and populate data based on a provided JSON schema. It provides a simple command-line interface to quickly create and populate database tables without the need for manual schema definition.

## Features

- Convert JSON schema to database tables
- Populate data into the database from JSON schema
- Supports various databases

## Installation

You can install FDG using pip:

```bash
pip install https://github.com/devendrapratap02/fake-db-generator.git
```

## Usage

After installing FDG, you can use the fdg command followed by various options:

- c: Create the database table
- p: Populate data into the database
- f <path>: Specify the path to the JSON schema file
- d: Download example schema
- h: Display help

### Example Usage

```bash
fdg -c -f schema.json
fdg -p -f data.json
fdg -cpf schema.json
```

### Supported Databases

FDG supports connection to any kind of database, allowing flexibility in your database choice.

## Example JSON Schemas

You can find example JSON schemas in the [fdg/data/](fdg/data/) folder:
