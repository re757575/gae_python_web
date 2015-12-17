# coding=utf-8

from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
import logging


class Customers(ndb.Model):
    type = ndb.IntegerProperty(required=True)
    clientName = ndb.StringProperty(required=True)
    clientAddress = ndb.StringProperty()
    clientTel = ndb.StringProperty()
    clientFax = ndb.StringProperty()
    vatNumber = ndb.StringProperty()
    status = ndb.BooleanProperty(required=True, default=True)
    billingAddress = ndb.StringProperty()
    note = ndb.TextProperty()
    createOperatorAccount = ndb.UserProperty()
    createDateTime = ndb.DateTimeProperty(auto_now_add=True)
    createTimeStamp = ndb.FloatProperty(required=True)
    page = 1
    limit = 10

    # 取得客戶資料
    @classmethod
    def _get_all_customers(cls, param):

        customers = cls.query()

        if param:
            if 'q' in param and 'query_type' in param and param['q'] and param['query_type']:
                customers = customers.filter(
                    Customers._properties[param['query_type']] == str(param['q']))

            if 'customers_type' in param and param['customers_type']:
                customers = customers.filter(
                    Customers._properties['type'] == int(param['customers_type']))

            # 排序
            if 'order_by' in param and param['order_by']:
                customers = customers.order(Customers._properties['order_by'])
            else:
                customers = customers.order(-Customers.createTimeStamp)

            total = customers.count()
            customers = customers.fetch(
                cls.limit, offset=(cls.page - 1) * cls.limit)

        return {'result': customers, 'total': total}

    # 更新客戶資料 DOTO:需修改成動態參數
    @classmethod
    def _update_customers(cls, id, type, clientName, clientAddress, clientTel, note):
        customers = cls(id=id, type=type, clientName=clientName,
                        clientAddress=clientAddress, note=note)
        customers.put()
        return customers

    # 新增客戶資料
    @classmethod
    def _insert_customers(cls, type, clientName, clientAddress, clientTel, note, createOperatorAccount, createTimeStamp):

        customers = Customers(type=type, clientName=clientName, clientAddress=clientAddress, clientTel=clientTel,
                              note=note, createOperatorAccount=createOperatorAccount, createTimeStamp=createTimeStamp)
        customers.put()
        return customers

    # 刪除客戶資料
    @classmethod
    def _delete_customers(cls, id):
        key = ndb.Key(Customers, id)
        key.delete()
