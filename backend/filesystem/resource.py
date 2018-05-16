import json
import os

import db
import conf
import storage


def load(owner, path):
    return Resource(owner, path, new=False)


def new(owner, path, group, permission,
        isdir=False, md5='', mimetype='application/octet-stream'):
    return Resource(owner, path, group, permission, isdir, md5,
                    mimetype=mimetype)


class Resource(object):

    def __init__(self, owner, path, group='',
                 permission=conf.default_permission,
                 isdir=False,
                 md5='',
                 mimetype=None,
                 new=True):
        self.owner = owner
        self.path = path
        self.group = group
        self.permission = permission
        self.md5 = md5
        self.mimetype = mimetype
        self.isdir = isdir
        self.new = new
        self.parent_path = os.path.dirname(path)

        if new:
            self.exists = db.is_resource_exists(self.owner, self.path)
        else:
            self.load()

        self.permission = int(self.permission, 8)

    def load(self):
        a = db.load_resource(self.owner, self.path)
        if a is None:
            self.exists = False
        else:
            (
                self.group,
                self.permission,
                self.md5,
                self.mimetype,
                self.parent_path
            ) = a
            self.permission = self.permission or conf.default_permission
            self.isdir = not bool(self.md5)
            self.exists = True

    def readable_by(self, visitor):
        if not self.exists:
            return False
        if self.is_owner(visitor):
            return True
        if visitor in self.group_users:
            return self.is_readable_by_group_user
        else:
            return self.is_writable_by_other_user

    def writable_by(self, visitor):
        if self.is_owner(visitor):
            return True
        if self.exists:
            if visitor in self.group_users:
                return self.is_writable_by_group_user
            else:
                return self.is_writable_by_other_user
        else:
            resource = Resource(self.owner, self.parent_path, new=False)
            if visitor in resource.group_users:
                return resource.is_writable_by_group_user
            else:
                return resource.is_writable_by_other_user

    @property
    def is_readable_by_group_user(self):
        return self.permission & 020

    @property
    def is_writable_by_group_user(self):
        return self.permission & 040

    @property
    def is_readable_by_other_user(self):
        return self.permission & 002

    @property
    def is_writable_by_other_user(self):
        return self.permission & 004

    def is_owner(self, visitor):
        return visitor == self.owner

    def accessible_by(self, visitor, mode):
        if mode == 'r':
            return self.readable_by(visitor)
        else:
            return self.writable_by(visitor)

    @property
    def group_users(self):
        return db.get_group_users(self.group)

    @property
    def parent_resource(self):
        return load(self.owner, self.parent_path)

    def serialize(self):
        db_resource = load(self.owner, self.path)
        if db_resource.exists and db_resource.isdir != self.isdir:
            raise Exception('incompatible')
        db.serialize_resource(self)

        parent_resource = self.parent_resource
        if not parent_resource.exists:
            parent_resource.serialize()

    def list(self):
        return db.list_directory(self.owner, self.path)

    def save(self, data, pos=0, part_size=None):
        storage.get_default_storage().save(self.md5, data, pos, part_size)

    def chunked_load(self):
        return storage.get_default_storage().chunked_load(self.md5)
