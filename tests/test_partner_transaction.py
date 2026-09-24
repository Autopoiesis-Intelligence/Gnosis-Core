import sqlite3, pytest
from gnosis.self_learning.partner_transaction import partner_learning_transaction

def conn():
 c=sqlite3.connect(":memory:",isolation_level=None);c.execute("CREATE TABLE marker(v TEXT)");return c

def test_success_commits():
 c=conn()
 with partner_learning_transaction(c): c.execute("INSERT INTO marker VALUES ('ok')")
 assert c.execute("SELECT count(*) FROM marker").fetchone()[0]==1
@pytest.mark.parametrize("p",["write","audit","head","commit"])
def test_failure_rolls_back(p):
 c=conn()
 with pytest.raises(RuntimeError):
  with partner_learning_transaction(c,failure_point=p): c.execute("INSERT INTO marker VALUES ('partial')")
 assert c.execute("SELECT count(*) FROM marker").fetchone()[0]==0

def test_reuse_canonical_transaction():
 c=conn()
 with partner_learning_transaction(c): c.execute("INSERT INTO marker VALUES ('canonical')")
 assert c.execute("SELECT v FROM marker").fetchone()[0]=="canonical"
