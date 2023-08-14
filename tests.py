import pytest
from parse_reports import Parser

def test_margin():
    p = Parser("margin_01.sql")
    p.parse()

    ans = ["maker.raw$sales",
           "maker.olap$firm2",
           "maker.raw$logplace",
           "maker.olap$logplace2",
           "maker.raw$fullart",
           "center.dolist_selfcost",
           "maker.dim$goods",
           "maker.raw$classes_link_all",
           "maker.dim_date",
           "vklim.subclass4",
           "maker.rpas$subclass_mart",
           "maker.dim$subseason",
           "vklim.cm_idmfc",
           "maker.raw$supp"
]
    assert p.tables == ans

def test_margin_fields():
    p = Parser("margin_01.sql")
    p.parse()

    with open("margin_fields.txt", "r") as f:
        ans = f.read()

    ans = set(ans.lower().split())
    assert p.fields == ans
