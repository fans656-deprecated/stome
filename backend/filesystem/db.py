import os
import sqlite3
import json

from flask import g

import conf


def get_db():
    if not hasattr(g, '_db'):
        g._db = sqlite3.connect(conf.db_fname)
    return g._db


def close_db():
    if hasattr(g, '_db'):
        g._db.close()


def get_group_users(group):
    c = get_db().cursor()
    c.execute('select users from usergroup where name = ?', (group,))
    a = c.fetchone()
    if a is None:
        return []
    else:
        return json.loads(a)


def serialize_resource(r):
    print 'serialize_resource', r.owner, r.path, r.permission
    db = get_db()
    db.execute('''
        insert or replace into resource values (
            ?, ?, ?, ?, ?, ?, ?
        )
               ''', (
                   r.owner, r.path, r.group,
                   '{:02o}'.format(r.permission),
                   r.md5,
                   r.mimetype,
                   r.parent_path,
               ))
    db.commit()


def load_resource(owner, path):
    c = get_db().cursor()
    c.execute('''
        select usergroup, permission, md5, mimetype, parent_path from resource
        where owner = ? and path = ?
    ''', (owner, path))
    return c.fetchone()


def is_resource_exists(owner, path):
    c = get_db().cursor()
    c.execute('''
        select 1 from resource where owner = ? and path = ?
    ''', (owner, path))
    return c.fetchone()


def list_directory(owner, path):
    c = get_db().cursor()
    c.execute('''
        select path, md5 from resource where owner = ? and parent_path = ?
    ''', (owner, path))
    a = c.fetchall()
    dirs = []
    files = []
    if a:
        for path, md5 in a:
            if not path:
                continue
            name = os.path.basename(path)
            path = '/' + path
            if md5:
                files.append({'name': name, 'path': path})
            else:
                dirs.append({'name': name, 'path': path})
    return {'dirs': dirs, 'files': files}


def init_db():
    db = sqlite3.connect(conf.db_fname)
    db.execute('drop table if exists resource')
    db.execute('''
create table resource (
    owner text,
    path text,
    usergroup text,
    permission text,
    md5 text,
    mimetype text,
    parent_path text,
    primary key (owner, path)
)
               ''')
    db.execute('drop table if exists usergroup')
    db.execute('''
create table usergroup (
    name text,
    users text
)
               ''')


if __name__ == '__main__':
    init_db()
