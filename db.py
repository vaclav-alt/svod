import csv
import sqlite3 as sq


class Database:
    def __init__(self, filename, cfg, tablename="incmort"):
        self.db = sq.connect(filename)
        self.cfg = cfg
        self.tablename = tablename

        self.c = self.db.cursor()
        self.create_table()
        self.insertQuery = self.insert_query_template()

    def write_csv(self, filename):
        print(f"Ukládám {filename}")

        sql3_cursor = self.db.cursor()
        sql3_cursor.execute(f'SELECT * FROM {self.tablename}')
        with open(filename, 'w', newline='') as out_csv_file:
            csv_out = csv.writer(out_csv_file)
            csv_out.writerow([d[0] for d in sql3_cursor.description])
            for result in sql3_cursor:
                csv_out.writerow(result)

    def insert_query_template(self) -> str:
        columns = ", ".join(self.cfg["database.columns"].values())
        value_keys = ", ".join(
            f"'{{{key}}}'" for key in self.cfg["database.columns"].keys()
    )
        query = f"insert into {self.tablename} ({columns}) values ({value_keys})"
        return query

    def compose_query(self, opts) -> str:
        for index, val in opts.items():
            if val == '':
                opts[index] = "NULL"
        return self.insertQuery.format(**opts)

    def create_table(self):
        query = f"create table {self.tablename} ("
        query += "id INTEGER PRIMARY KEY"
        for key, val in self.cfg["database.columns"].items():
            coltype = self.cfg["database.types"][key]
            query += f", {val} {coltype}"
        query += ")"
        self.c.execute(query)
        self.db.commit()

    def save_to_db(self, opts):
        sql_query = self.compose_query(opts)
        self.c.execute(sql_query)
