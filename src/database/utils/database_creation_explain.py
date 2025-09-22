from src.database.tipos_base.database import Database

def generate_ddl(file_path: str = "../assets/export.ddl") -> str:
    """Generate DDL for the database."""

    Database.create_all_tables(drop_if_exists=False)
    ddl = Database.generate_ddl()

    with open(file_path, "w") as f:
        f.write(ddl)

    return ddl

def generate_mer(file_path: str = "../assets/export.mer") -> str:
    """Generate MER for the database."""

    mer = Database.generate_mer()

    with open(file_path, "w") as f:
        f.write(mer)

    return mer