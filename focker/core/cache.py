from contextvars import ContextVar
from .process import focker_subprocess_check_output
from .zfs import zfs_properties_cache
from typing import List
import json


# JAILS_CACHE = ContextVar('JAILS_CACHE')
# DATASET_CACHE = ContextVar('DATASET_CACHE')


class CacheBase:
    context_var = None

    def __init__(self):
        self.tok = None
        self.data = None

    def __enter__(self):
        self.tok = self.context_var.set(self)
        self.data = self.generate_cache()

    def __exit__(self, *excinfo):
        self.context_var.reset(self.tok)
        self.tok = None

    def generate_cache(self):
        raise NotImplementedError

    @classmethod
    def is_available(cls):
        return ( cls.context_var.get() is not None )

    @classmethod
    def instance(cls):
        return cls.context_var.get()

    @classmethod
    def get_property(cls, *args):
        if cls.context_var.get() is None:
            raise RuntimeError('No cache in the current context')
        return cls.context_var.get()._get_property(*args)

    def _get_property(self, *args):
        raise NotImplementedError

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def get(self, key, default=None):
        return self.data.get(key, default)


class JlsCache(CacheBase):
    context_var = ContextVar('JLS_CACHE', default=None)

    def generate_cache(self):
        info = focker_subprocess_check_output([ 'jls', '--libxo',  'json', '-n' ])
        info = json.loads(info)
        data = {}
        for j in info['jail-information']['jail']:
            jnam = j['name']
            if jnam in data:
                raise RuntimeError('More than one jail with the same name')
            data[jnam] = j
        return data


class ZfsPropertyCache(CacheBase):
    context_var = ContextVar('DATASET_CACHE', default=None)

    def __init__(self, focker_type: List[str] = None):
        super().__init__()
        self.focker_type = focker_type
        self.data = None

    def generate_cache(self):
        if self.focker_type:
            self.data = {}
            for ft in self.focker_type:
                self.data.update(zfs_properties_cache(ft))
        else:
            self.data = zfs_properties_cache()

    def _get_property(self, name, propname):
        return self.data.get(( name, propname ), '-')
