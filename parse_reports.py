import sqlparse
import argparse

class Parser():
    def __init__(self, path: str) -> None:
        self.tables = []
        self.fields = []
        self.state = "IDLE"
        self.query = self.read_file(path)
        
        self.tokens = sqlparse.parse(self.query)
        if len(self.tokens) > 1:
            print("got", len(self.tokens), "queries")
        self.tokens = self.tokens[0]

    def read_file(self, path: str) -> str:
        # TODO: error handle here
        with open(path, "r", encoding="Windows-1251") as f:
            return f.read()

    def add_token(self, token):
        if self.state == "SELECT":
            self.fields.append(token.value)
        elif self.state == "FROM":
            self.tables.append(token.value.split()[0])
        elif self.state == "APPEND":
            table_name = (self.tables[-1] + "$" + token.value).split()[0]
            self.tables[-1] = table_name
            self.state = "FROM"


    def parse(self, tokens = None):
        if not tokens:
            tokens = self.tokens

        for i, token in enumerate(tokens):
            # print(token.value)
            if isinstance( token, sqlparse.sql.Token):
                if token.value.upper() in ["SELECT", "FROM", "GROUP BY"]:
                    self.state = token.value.upper()
                    # print(self.state)

                elif token.value == "$":
                    self.state = "APPEND"

                elif isinstance(token, sqlparse.sql.IdentifierList) or \
                     isinstance(token, sqlparse.sql.Parenthesis):
                    self.parse(tokens = token)

                elif isinstance(token, sqlparse.sql.Identifier):
                    # print(i, token.value)
                    self.add_token(token)

    def print_output(self):
        print(self.tables)
        print(self.fields)


def main():
    parser = argparse.ArgumentParser() 
    parser.add_argument("-f", "--filename", required=False)
    args = parser.parse_args()

    if args.filename:
        print(args.filename)
        sql_parser = Parser(args.filename)
        sql_parser.parse()
        sql_parser.print_output()
    else:
        # sql_parser = Parser("test.sql")
        sql_parser = Parser("margin_01.sql")
        sql_parser.parse()
        sql_parser.print_output()
    

if __name__ == "__main__":
    main()
