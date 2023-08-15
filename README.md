# Parsing script to analyze SQL queries

## Install
```bash
git clone https://github.com/Kvas1988/skp_parse_sql.git
pip install -r requirements.txt
```
Also you should create config.toml file with DB_CONN parameter:
```toml
DB_CONN = 'oracle://user:password@server.addr.com/dbname'
```

## Usage
You can run script with given path to sql-file
```bash
python parse_reports.py -f path/to/query.sql 
python parse_reports.py -f path/with/quries/
```

Or via python api
```python
from sqlalchemy.engine import create_engine
from parse_reports import Parser

engine = create_engine("YOUR_DB_CREDS")
p = Parser("path/to/query", engine)
df = p.parse() # return is pandas DataFrame
```
