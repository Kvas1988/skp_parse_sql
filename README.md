# Parsing script to analyze SQL queries

## Install
```bash
git clone https://github.com/Kvas1988/skp_parse_sql.git
pip install -r requirements.txt
```

## Usage
You can run script with given path to sql-file
```bash
python parse_reports.py -f path/to/query.sql 
```

Or via python api
```python
from parse_reports import Parser

p = Parser("path/to/query")
p.parse()
print(p.fields)
print(p.tables)
```
