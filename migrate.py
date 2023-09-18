import sqlite3

# Conecta a la base de datos o la crea si no existe
conn = sqlite3.connect('appdistribution.db')

# Crea un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Define la consulta SQL para crear la tabla "apps"
create_table_query = """
CREATE TABLE IF NOT EXISTS apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    build TEXT NOT NULL,
    uuid TEXT NOT NULL
);
"""

# Ejecuta la consulta SQL para crear la tabla
cursor.execute(create_table_query)

# Guarda los cambios en la base de datos
conn.commit()

# Cierra la conexión a la base de datos
conn.close()

print("Base de datos 'appdistribution.db' y tabla 'apps' creadas con éxito.")
