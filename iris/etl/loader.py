"""
This module contains a Loader class which provides two methods
sync_entity() and sync_nnr() to load data entities and many to
many relationships into database.

It will check if some entity or relationship exists in db, and
call create/update/delete for entity and add/remove for relationship
to make records in db are all the same as given data.
"""
from collections import defaultdict
import logging

# pylint: disable=W0142,C0103,W0511,R0914i,R0912
# W0142: Used * or ** magic
# C0103: Invalid name "x"
# W0511: FIXME: select_related
# R0914: Loader.sync_nnr: Too many local variables (25/15)
# R0912:138,4:Loader.sync_nnr: Too many branches (13/12)

log = logging.getLogger(__name__)


def mname(model_class):
    """
    Normalize model's name
    """
    return model_class.__name__.lower()


def getk(x, keys):
    """
    get string represent all `keys` of `item`
    """
    return '|'.join([unicode(x[c]) for c in keys])


def diff3(left, right, ckey, ukey=None):
    '''
    Diff `left` and `right` returns 4 sets as following:

    lonly: left only
    ronly: right only
    diff: both side but different

    * ckey is the candidate key to distinguish items in left and right
    * ukey is the updated key to see if items are different
    * all columns = pk + ckey + ukey
    '''
    l, r = 0, 0
    llen, rlen = len(left), len(right)
    lonly, ronly, diff = [], [], []

    while l < llen and r < rlen:
        this, that = left[l], right[r]
        lkey, rkey = getk(this, ckey), getk(that, ckey)
        if lkey < rkey:
            lonly.append(this)
            l += 1
        elif lkey == rkey:
            if ukey and getk(this, ukey) != getk(that, ukey):
                diff.append(dict(that, **this))
            l += 1
            r += 1
        else:
            ronly.append(that)
            r += 1

    while l < llen:
        lonly.append(left[l])
        l += 1
    while r < rlen:
        ronly.append(right[r])
        r += 1
    return lonly, ronly, diff


class Loader(object):
    """
    Smart loader to sync data into database
    """
    MODEL = {}
    PK = {}
    CKEY = {}
    NNM = defaultdict(dict)

    def register_entity(self, model, ckey, pk='id'):
        """
        Register a entity model
        `pk`: primary key
        `ckey`: candidate key, could be combined keys
        """
        name = mname(model)
        self.MODEL[name] = model
        self.CKEY[name] = (ckey,) if isinstance(ckey, basestring) else ckey
        self.PK[name] = pk

    def register_nnr(self, model1, model2, manager):
        """
        Register many to many relationship manager field name
        """
        self.NNM[mname(model1)][mname(model2)] = manager

    def sync_entity(self, left, model):
        """
        Sync entity of `model`
        """
        ckey = self.CKEY[mname(model)]
        cols = left[0].keys() if left else ckey
        ukey = tuple(set(cols) - set(ckey) - {'pk'})

        left.sort(key=lambda x: getk(x, ckey))
        # FIXME: select_related
        right = list(model.objects.all().values('pk', *cols))
        # must using python's sort not sql's order_by here, since order
        # of UPPER and lower letters may be differnet in python and sql
        right.sort(key=lambda x: getk(x, ckey))

        lonly, ronly, diff = diff3(left, right, ckey, ukey)
        log.info('Sync {:>20} +{:<5} -{:<5} U{:<5}'.format(
                 model.__name__, len(lonly), len(ronly), len(diff)))

        for i in self._shrink(lonly):
            model(**i).save()
        for i in self._shrink(diff):
            model(**i).save()

        def delete():
            """
            Since Django provide casacading deletion. For example, if delete
            a subdomain entity here, all its gittrees, packages and roles
            will all be deleted automatically. However sometimes it will have
            side-effect, if we rename a subdomain'name, its gittrees don't
            need to be deleted, just need to be updated. So we returns the
            delete function to caller to decide when to invoke.
            """
            model.objects.filter(pk__in=[i['pk'] for i in ronly]).delete()
        return delete

    def sync_nnr(self, data, model1, model2, remove=True):
        """
        Sync many to many relationship between `model1` and `model2`
        """
        ckey1, ckey2 = self.CKEY[mname(model1)], self.CKEY[mname(model2)]
        if data:
            cols1, cols2 = data[0][0].keys(), data[0][1].keys()
        else:
            cols1, cols2 = ckey1, ckey2
        ckey = ckey1 + ckey2
        nnm_name = self.NNM[mname(model1)][mname(model2)]

        left = [dict(i, **j) for i, j in data]
        left.sort(key=lambda x: getk(x, ckey))

        right = [dict(i, **j)
                 for i in model1.objects.all().values('pk', *cols1)
                 for j in getattr(model1.objects.get(pk=i.pop('pk')),
                                  nnm_name).all().values(*cols2)]
        right.sort(key=lambda x: getk(x, ckey))

        lonly, ronly = diff3(left, right, ckey)[:2]
        log.info('Sync {:>20} +{:<5} -{:<5}'.format(
                 ','.join([model1.__name__, model2.__name__]),
                 len(lonly), len(ronly)))

        idx1 = {getk(x, ckey1): x['pk']
                for x in model1.objects.all().values('pk', *ckey1)}
        idx2 = {getk(x, ckey2): x['pk']
                for x in model2.objects.all().values('pk', *ckey2)}

        toadd, todel = defaultdict(list), defaultdict(list)
        for item in lonly:
            key1, key2 = getk(item, ckey1), getk(item, ckey2)
            pk1, pk2 = idx1.get(key1), idx2.get(key2)
            if pk1 is None:
                log.warn("%s(%s) doesn't exist", model1.__name__, key1)
            if pk2 is None:
                log.warn("%s(%s) doesn't exist", model2.__name__, key2)
            if pk1 and pk2:
                toadd[pk1].append(pk2)
        for item in ronly:
            key1, key2 = getk(item, ckey1), getk(item, ckey2)
            pk1, pk2 = idx1.get(key1), idx2.get(key2)
            if pk1 is None:
                log.warn("%s(%s) doesn't exist", model1.__name__, key1)
            if pk2 is None:
                log.warn("%s(%s) doesn't exist", model2.__name__, key2)
            if pk1 and pk2:
                todel[pk1].append(pk2)

        for pk1, pk2s in toadd.items():
            getattr(model1(pk=pk1), nnm_name).add(*pk2s)
        if remove:
            for pk1, pk2s in todel.items():
                getattr(model1(pk=pk1), nnm_name).remove(*pk2s)

    def _shrink_to_pk(self, data, cgroup=None, model=None):
        '''
        Shrink given data column group(cgroup) to pk.

        If `cgroup` is not given, then all columns of data will be used,
        then the `model` that the data present must be given.
        '''
        assert cgroup or model
        if not data:
            return data
        if cgroup:
            parts = cgroup[0].split('__')
            prefix = '__'.join(parts[:-2])
            model = self.MODEL[parts[-2]]
            cols = [c.split('__')[-1] for c in cgroup]
        else:
            prefix = None
            cols = data[0].keys()

        idx = {getk(obj, cols): obj['pk']
               for obj in model.objects.all().values('pk', *cols)}
        for item in data:
            key = getk(item, cgroup)
            if key not in idx:
                raise ValueError('Can not shrink to pk for the bad '
                                 'reference: %s: %s' % (mname(model), item))
            for c in cgroup:
                item.pop(c)
            pk = self.PK[mname(model)]
            if prefix:
                field = '%s__%s_%s' % (prefix, mname(model), pk)
            else:
                field = '%s_%s' % (mname(model), pk)
            item[field] = idx[key]

        return data

    def _shrink(self, data):
        """
        Shrink columns of data by eliminate all fields from foreign key models
        and insert pk of foreign key models.

        For example: One GitTree item with the following fields:
            gitpath, subdomain__name, subdomain__domain__name
        will shrink to fields like this in the first step:
            gitpath, subdomain__name, subdomain__pk
        and this in the second step:
            gitpath, subdomain__pk
        then it can be used to save, since there isn't reference field.
        """
        if not data:
            return data

        def _group_columns(cols):
            """group cols by model name"""
            cols = data[0].keys()
            cgroups = defaultdict(list)
            for c in cols:
                parts = c.split('__')
                model = '__'.join(parts[:-1])
                cgroups[model].append(c)
            # sort col group by its level (number of __)
            # max level comes first, since it should be shrunk at first
            cgroups = sorted(
                cgroups.items(),
                key=lambda x: len(x[0].split('__')) if x[0] else 0,
                reverse=True)
            return [i[1] for i in cgroups]

        while 1:
            cgroups = _group_columns(data)
            if len(cgroups) < 2:
                break
            self._shrink_to_pk(data, cgroups[0])
        return data


def get_default_loader():
    """Get a default loader instance for IRIS models"""
    from django.contrib.auth.models import User
    from iris.core.models import (
        Domain, SubDomain, GitTree, Package, Product, Image, License,
        DomainRole, SubDomainRole, GitTreeRole,
        )
    loader = Loader()
    loader.register_entity(User, 'email')

    loader.register_entity(Domain, 'name')
    loader.register_entity(SubDomain, ('name', 'domain__name'))
    loader.register_entity(GitTree, 'gitpath')
    loader.register_entity(Package, 'name')
    loader.register_entity(Product, 'name')
    loader.register_entity(Image, ('name', 'target', 'product__name'))
    loader.register_entity(License, 'shortname')

    loader.register_entity(
        DomainRole, ('role', 'domain__name'), 'group_ptr_id')
    loader.register_entity(
        SubDomainRole,
        ('role', 'subdomain__name', 'subdomain__domain__name'),
        'group_ptr_id')
    loader.register_entity(
        GitTreeRole, ('role', 'gittree__gitpath'), 'group_ptr_id')

    loader.register_nnr(GitTree, Package, 'packages')
    loader.register_nnr(GitTree, License, 'licenses')
    loader.register_nnr(Product, GitTree, 'gittrees')
    loader.register_nnr(DomainRole, User, 'user_set')
    loader.register_nnr(SubDomainRole, User, 'user_set')
    loader.register_nnr(GitTreeRole, User, 'user_set')

    return loader
