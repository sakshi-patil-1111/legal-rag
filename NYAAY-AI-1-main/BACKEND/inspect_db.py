from sqlalchemy import create_engine, inspect

engine = create_engine("sqlite:///./nyaay.db")
insp = inspect(engine)

tables = insp.get_table_names()
print("Tables:", tables)

if "users" in tables:
    print("\nusers columns:")
    for col in insp.get_columns("users"):
        print(f"  {col['name']:<18} {str(col['type']):<25} nullable={col['nullable']}")
else:
    print("ERROR: users table not found!")
