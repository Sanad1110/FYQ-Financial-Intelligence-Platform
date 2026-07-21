import sqlite3, json, os
from datetime import datetime, timezone
DB_PATH=os.path.join(os.path.dirname(__file__),'fyq_clients.db')
def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
def init_db():
    with conn() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,sector TEXT,cr_number TEXT,created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY AUTOINCREMENT,client_id INTEGER NOT NULL,name TEXT NOT NULL,fiscal_year TEXT,currency TEXT,created_at TEXT NOT NULL,FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE); CREATE TABLE IF NOT EXISTS analyses(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER NOT NULL,payload_json TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);''')
def now(): return datetime.now(timezone.utc).isoformat()
def list_clients():
    with conn() as c: return [dict(r) for r in c.execute('SELECT * FROM clients ORDER BY id DESC')]
def create_client(d):
    with conn() as c:
        cur=c.execute('INSERT INTO clients(name,sector,cr_number,created_at) VALUES(?,?,?,?)',(d['name'].strip(),d.get('sector',''),d.get('cr_number',''),now())); return cur.lastrowid
def delete_client(cid):
    with conn() as c: c.execute('DELETE FROM clients WHERE id=?',(cid,))
def list_projects(cid):
    with conn() as c: return [dict(r) for r in c.execute('SELECT * FROM projects WHERE client_id=? ORDER BY id DESC',(cid,))]
def create_project(d):
    with conn() as c:
        cur=c.execute('INSERT INTO projects(client_id,name,fiscal_year,currency,created_at) VALUES(?,?,?,?,?)',(d['client_id'],d['name'].strip(),d.get('fiscal_year',''),d.get('currency','ريال'),now())); return cur.lastrowid
def save_analysis(d):
    with conn() as c:
        cur=c.execute('INSERT INTO analyses(project_id,payload_json,created_at) VALUES(?,?,?)',(d['project_id'],json.dumps(d.get('payload',{}),ensure_ascii=False),now())); return cur.lastrowid
def list_analyses(pid):
    with conn() as c:
        rows=[]
        for r in c.execute('SELECT * FROM analyses WHERE project_id=? ORDER BY id DESC',(pid,)):
            x=dict(r); x['payload']=json.loads(x.pop('payload_json')); rows.append(x)
        return rows
def get_analysis(aid):
    with conn() as c:
        r=c.execute('SELECT * FROM analyses WHERE id=?',(aid,)).fetchone()
        if not r: return None
        x=dict(r); x['payload']=json.loads(x.pop('payload_json')); return x
init_db()
