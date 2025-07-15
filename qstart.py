#coding=utf-8
#Author:PengCheng
import sys,os
import subprocess
import sqlite3
import tkinter as tk
from tkinter import ttk


class DbC(object):
    def __init__(self, _file):
        super().__init__()
        self.c = sqlite3.connect(_file)
        self.lastq = None
    
    def reCreate(self):
        self.c.execute('DROP TABLE IF EXISTS CMDB')
        self.c.execute('CREATE TABLE CMDB (KEY TEXT PRIMARY KEY,IMAGE TEXT, COMMAND TEXT NOT NULL)')
        self.c.execute('DROP TABLE IF EXISTS MADB')
        self.c.execute('CREATE TABLE MADB (KEY TEXT PRIMARY KEY,VALUE TEXT)')
        self.c.execute('INSERT INTO MADB (KEY,VALUE) VALUES (?,?)',('uptime','0'))
        self.c.commit()
    
    def getSetting(self, _k):
        return self.c.execute('SELECT VALUE FROM MADB WHERE KEY = ?', [_k]).fetchone()[0]
    
    def updateSetting(self, _k, _v):
        self.c.execute('INSERT OR REPLACE INTO MADB (KEY,VALUE) VALUES (?,?)', [_k, _v])
    
    def batchInsert(self, _data):
        self.c.executemany('INSERT OR REPLACE INTO CMDB (KEY,IMAGE,COMMAND) VALUES (?,?,?)',_data)
        self.c.commit()
    
    def qHeaderItems(self,count=8):
        return self.c.execute("SELECT KEY,IMAGE,COMMAND FROM CMDB WHERE IMAGE IS NOT ''  LIMIT ?", [count]).fetchall()

    def quickq(self, _k):
        self.lastq = self.c.execute("SELECT KEY,IMAGE,COMMAND FROM CMDB WHERE KEY LIKE ? LIMIT 1", ['%'+_k+'%']).fetchone()
        return self.lastq


class FCore(object):
    def __init__(self):
        super().__init__()
        dbpath = os.path.join(os.getenv('USERPROFILE'),'.qstart.db')
        dbexists = os.path.isfile(dbpath)
        self.db = DbC(dbpath)
        if not dbexists: self.db.reCreate()
        cff = os.path.join(os.path.dirname(__file__),'qstart.cfg')
        if self.db.getSetting('uptime') != str(os.path.getmtime(cff)):
            self.db.reCreate()
            self.db.batchInsert(self.readCfg(cff))
            self.db.updateSetting('uptime', str(os.path.getmtime(cff)))
    
    def readCfg(self, cff):
        cfgdata = []
        with open(cff) as _f:
            for rawl in _f:
                if rawl.startswith('#'):continue
                cfgdata.append(rawl.strip(' \r\n|').split('|'))
        return cfgdata
    
    @staticmethod
    def startCmd(data):
        cmdd = data[2]
        ccmd = ['start "%s"'%data[0]]
        if os.path.isfile(cmdd):
            ccmd.extend(['/D', os.path.dirname(cmdd)])
        ccmd.append(cmdd)
        os.system(' '.join(ccmd))

def main():
    fc = FCore()
    root = tk.Tk()
    uv = {
        'itxt': tk.StringVar(),
        'stxt': tk.StringVar(),
    }
    root.attributes('-toolwindow',2)
    root.title("qstart")
    tw = ttk.Entry(textvariable=uv['itxt'])
    intx = tw
    def tcc(_e):
        if _e.keycode == 13: # enter
            uv['itxt'].set(uv['stxt'].get())
            fc.startCmd(fc.db.lastq)
            root.quit()
        elif _e.keycode == 27: # esc
            root.quit()
        elif _e.keycode in (9,40): # tab down
            uv['itxt'].set(uv['stxt'].get())
            return 'break'
        else:
            aftx = uv['itxt'].get()+_e.char
            qq = fc.db.quickq(aftx)
            uv['stxt'].set('' if not qq else qq[0])
    tw.bind('<KeyPress>',tcc)
    tw.pack()
    tw = ttk.Label(textvariable=uv['stxt'])
    tw.pack()
    def gbtnc(data):
        def _fn():
            fc.startCmd(data)
            root.quit()
        return _fn
    for eab in fc.db.qHeaderItems():
        # print(eab)
        tw = ttk.Button(text=eab[0],command=gbtnc(eab))
        tw.pack()
    def aftc():
        intx.focus_set()
    root.after_idle(aftc)
    root.mainloop()


if __name__ == '__main__':
    main()
