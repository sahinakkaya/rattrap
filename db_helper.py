import sqlite3 as sql
from ratslap import Ratslap


class DBHelper:
    def __init__(self, filename="settings_test.db"):
        self.filename = filename
        self.conn = sql.connect(filename)
        self.c = self.conn.cursor()
        self.setup()

    def setup(self):
        defaults = Ratslap.defaults
        self.drop_table("defaults")
        self.create_table("defaults", defaults["f3"])
        for mode in defaults.values():
            self.insert_values("defaults", **mode)
        self.drop_table("profiles")

    def create_table(self, table_name, columns):
        self.c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
        self.commit()

    def insert_values(self, table_name, **kwargs):
        self.c.execute(f"INSERT INTO {table_name} "
                       f"VALUES ({', '.join([':' + key for key in kwargs])})", kwargs)
        self.commit()

    def get_column_names(self, table_name):
        table_info = self.c.execute(f"PRAGMA table_info({table_name})").fetchall()
        return [info[1] for info in table_info]

    def update_value(self, table_name, key, new_value, **conditions):
        self.c.execute(f"UPDATE {table_name} SET {key} = '{new_value}'"
                       f" WHERE {' AND '.join([key + ' = ' + repr(conditions[key]) for key in conditions])}")
        self.commit()

    def select(self, table_name, columns, **conditions):
        return self.c.execute(
            f"SELECT {', '.join(columns)} FROM {table_name} "
            "WHERE " + " AND ".join([key + " = " + repr(conditions[key]) for key in conditions]) if conditions else "")

    def drop_table(self, table_name):
        self.c.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.commit()

    def commit(self):
        self.conn.commit()


if __name__ == '__main__':
    db = DBHelper()
    db.conn.close()
