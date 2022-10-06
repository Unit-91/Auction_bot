import sqlite3


class LiteBase:
    def __init__(self, base_name):
        self.base_name = base_name
        self.base = None
        self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.base:
            self.base.close()

    def connect(self):
        self.base = sqlite3.connect(self.base_name)
        self.cursor = self.base.cursor()

    def close(self):
        self.base.close()

    def _create_insert_string(self, column_names, insert_elem: str = None):
        string = ''

        for name in column_names:
            if insert_elem:
                string += f'{insert_elem}, '
            else:
                string += f'{name}, '

        return string[:-2]

    def create_table(self, table_name, primary_key_name, *args):
        columns = self._create_insert_string(args)

        if primary_key_name:
            columns = f'{primary_key_name} PRIMARY KEY, ' + columns

        self.base.execute(f'CREATE TABLE IF NOT EXISTS {table_name}({columns})')
        self.base.commit()

    def save_rows(self, table_name, lst):
        question_marks = self._create_insert_string(lst[0], insert_elem='?')

        self.cursor.executemany(f'INSERT INTO {table_name} VALUES({question_marks})', lst)
        self.base.commit()

    def save_row(self, table_name, *args):
        question_marks = self._create_insert_string(args, insert_elem='?')

        self.cursor.execute(f'INSERT INTO {table_name} VALUES({question_marks})', args)
        self.base.commit()

    def load_all_rows(self, table_name):
        rows_lst = self.cursor.execute(f'SELECT * FROM {table_name}').fetchall()

        return rows_lst

    def load_some_rows(self, table_name, key, value):
        rows_lst = self.cursor.execute(f'SELECT * FROM {table_name} WHERE {key} == ?', (value,)).fetchall()

        return rows_lst

    def load_row(self, table_name, key, value):
        lst = self.cursor.execute(f'SELECT * FROM {table_name} WHERE {key} == ?', (value,)).fetchall()

        if lst:
            row = lst[0]

            return row

    def remove_row(self, table_name, key, value):
        self.cursor.execute(f'DELETE FROM {table_name} WHERE {key} == ?', (value,))
        self.base.commit()

    def load_all_columns(self, key, table_name):
        tupls_list = self.cursor.execute(f'SELECT {key} FROM {table_name}').fetchall()

        return [tpl[0] for tpl in tupls_list]

    def load_column(self, table_name, column_name, key, value):
        lst = self.cursor.execute(f'SELECT {column_name} FROM {table_name}\
        WHERE {key} == ?', (value,)).fetchall()

        return lst[0][0]

    def update_column(self, table_name, column_name, column_value, key, value):
        self.cursor.execute(f'UPDATE {table_name} SET {column_name} == ?\
        WHERE {key} == ?', (column_value, value))

        self.base.commit()
