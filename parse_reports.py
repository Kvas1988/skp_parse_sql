import re
import sqlparse
import argparse
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import pandas as pd
from os import path, listdir
from datetime import datetime
import tomli


class Parser():
    def __init__(self, path: str, engine: Engine) -> None:
        self.path = path
        self.engine = engine
        self.data = []
        self.tables = []
        self.fields = set()
        self.state = "IDLE"
        self.query = self.read_file(path)

        self.tokens = sqlparse.parse(self.query)
        if len(self.tokens) > 1:
            print("got", len(self.tokens), "queries")
        self.tokens = self.tokens[0]

        self.syntax_words = ['select', 'from', 'case', 'trunc', 'as', 'like',
                             'trunc', 'max', 'min', 'nvl', 'upper', 'avg',
                             'sum', 'when', 'else', 'then', 'end', 'and',
                             '*', 'is', 'null',  '', 'not', 'nvl2', ',',
                             '=', '+', '-', '>', '<', '>=', '<=', '!=', "/"]

    def read_file(self, path: str) -> str:
        # TODO: error handle here
        with open(path, "r", encoding="Windows-1251") as f:
            return f.read()

    def add_token(self, token):
        if self.state == "SELECT":
            # self.fields.append(token.value)
            self.handle_field(token)
        elif self.state == "FROM":
            self.tables.append(token.value.split()[0].lower())
        elif self.state == "APPEND":
            table_name = (self.tables[-1] + "$" + token.value).split()[0].lower()
            self.tables[-1] = table_name
            self.state = "FROM"

    def handle_field(self, token):
        arr = token.value.lower().split()
        arr = [w for t in arr for w in re.split('\(|\)', t)]
        arr = [w for w in arr if w not in self.syntax_words]
        arr = [w for w in arr if not re.match("[0-9]|'\d{2}\.\d{2}\.\d{4}'|'.*'", w)]
        arr = [w for w in arr if not re.match('".*"|\'.*\'', w)]
        arr = [re.sub('-|.*\.|,', '', w) for w in arr]
        for w in set(arr):
            self.fields.add(w)

    def parse(self):
        self.__parse_query()
        self.check_dwh()
        return self.to_df()

    def __parse_query(self, tokens=None):
        if not tokens:
            tokens = self.tokens

        for token in tokens:
            if token.value.upper() == "DELETE":
                print("YOU SHALL NOT PASS")
                return

            # print(token.value)
            if token.value.upper() in ["SELECT", "FROM", "GROUP BY"]:
                self.state = token.value.upper()
                # print(self.state)

            elif token.value == "$":
                self.state = "APPEND"

            elif isinstance(token, sqlparse.sql.IdentifierList) or \
                 isinstance(token, sqlparse.sql.Parenthesis):
                self.__parse_query(tokens=token)

            elif isinstance(token, sqlparse.sql.Identifier):
                # print(i, token.value)
                self.add_token(token)

    def print_output(self):
        print(self.tables)
        print(self.fields)

    def check_dwh(self):
        params = dict()
        params['columns'] = tuple(self.fields)
        params['columns'] = [c.upper() for c in params['columns']]

        tables = tuple([re.split('\.', t, maxsplit=1) for t in self.tables])
        params['owners'] = tuple(set([t[0].upper() for t in tables]))

        params['tables'] = tuple([t[1] if len(t) > 1 else t[0] for t in tables])
        params['tables'] = [t.upper() for t in params['tables']]

        q = """
                 SELECT t.OWNER,
                        t.TABLE_NAME,
                        t.owner || '.' || t.table_name fullname,
                        t.COLUMN_NAME
                FROM all_tab_columns t
                 WHERE t.OWNER in :owners
                 AND t.TABLE_NAME in :tables
                 AND t.COLUMN_NAME in :columns
                 """

        t = text(q)
        t = t.bindparams(bindparam('owners', expanding=True))
        t = t.bindparams(bindparam('tables', expanding=True))
        t = t.bindparams(bindparam('columns', expanding=True))

        session = sessionmaker(self.engine)
        with session.begin() as s:
            data = s.execute(t, params).all()

        for row in data:
            self.data.append([v for v in row])

    def to_df(self):
        headers = ['owner', 'table_name', 'table_fullname', 'column']
        df = pd.DataFrame(self.data, columns=headers)
        df['sql_path'] = self.path
        return df


def handle_folder(folder: str, engine: Engine):
    df = pd.DataFrame()
    for f in listdir(folder):
        print(f)
        fp = path.join(folder, f)
        sql_parser = Parser(fp, engine)
        df = pd.concat([df, sql_parser.parse()])
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_excel('result_' + ts + '.xlsx', index=False)


def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument("-f", "--filename", required=False)
    args = parser.parse_args()

    try:
        with open("config.toml", 'rb') as f:
            conf = tomli.load(f)
        engine = create_engine(conf['DB_CONN'])
    except (OSError, KeyError):
        print("ERROR: CREATE config.toml WITH DWH_CONN PARAMETER")
        quit()

    if args.filename:
        if path.isfile(args.filename):
            sql_parser = Parser(args.filename, engine)
            df = sql_parser.parse()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            df.to_excel('result_' + ts + '.xlsx', index=False)
        else:
            handle_folder(args.filename, engine)
    else:
        print("RUN SCRIPT WITH -f filepath.sql (OR -f folder\)")


if __name__ == "__main__":
    main()
