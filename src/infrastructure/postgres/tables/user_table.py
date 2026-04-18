from sqlalchemy import UUID, Column, MetaData, String, Table


metadata = MetaData()

user_table = Table(
    "users",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("father_name", String, nullable=True),
)
