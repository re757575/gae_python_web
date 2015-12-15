# coding=utf-8

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import render_to_response
from datetime import datetime
import random
import logging
import models
import time
import json

from google.appengine.api import users
from google.appengine.ext import ndb


def error404(request):
    response = render_to_response(
        '404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def error500(request):
    response = render_to_response(
        '500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


def home(request):

    # if request.method == 'GET':
    #     logging.info('GET')
    #     if 'section' in request.GET and request.GET['section'] is not None and request.GET['section'] != '':
    #         logging.info(request.GET['section'])
    # elif request.method == 'POST':
    #     logging.info('POST')

    user = users.get_current_user()
    if user:
        user = {
            'userName': user.nickname(),
            'logoutUrl': users.create_logout_url('/')
        }
        return render(request, "index.html", user)
    else:
        return HttpResponseRedirect(users.create_login_url('/'))


# 客戶資料列表
def customers(request):
    user = users.get_current_user()

    if request.method == 'GET':

        q = query_type = query_client_type = None

        # 查詢值
        if 'q' in request.GET:
            q = request.GET['q']

        # 查詢條件
        if 'query_type' in request.GET:
            query_type = request.GET['query_type']

        # 客戶類型
        if 'query_client_type' in request.GET:
            query_client_type = request.GET['query_client_type']

        params = {
            'q': q,
            'query_type': query_type,
            'customers_type': query_client_type
        }
        customers = models.AllCustomers(params)

        data = {
            'user': user,
            'customers': customers,
            'action': '新增',
            'clientType': {1: '政府', 2: '企業', 3: '個人'}
        }
        # cc = models.Customers.query().filter(models.Customers.clientName == '4').fetch()
        logging.info(customers)
        return render(request, "customers.html", data)


# 客戶資料新增
def customersAdd(request):
    user = users.get_current_user()

    if request.method == 'GET':
        data = {
            'user': user,
            'action': '新增',
            'clientType': {1: '政府', 2: '企業', 3: '個人'}
        }
        return render(request, "customers/customers-data-handle.html", data)

    else:
        clientName = request.POST['clientName']
        type = int(request.POST['type'])
        clientAddress = request.POST['clientAddress']
        clientTel = request.POST['clientTel']

        createTimeStamp = time.mktime(datetime.now().timetuple())
        models.InsertCustomers(
            type, clientName, clientAddress, clientTel, '備註...', user, createTimeStamp)

        respData = {
            'title': '客戶資料',
            'message': '新增成功。 (三秒後自動返回)'
        }

        response = render_to_response('success.html', respData)
        response['refresh'] = '3;URL=/customers/'
        return response


# 客戶資料刪除
def customersDelete(request, id):
    if request.method == 'DELETE':
        models.DeleteCustomers(int(id))

        response_data = {}
        response_data['result'] = 1
        response_data['message'] = 'success'

        return HttpResponse(json.dumps(response_data), content_type="application/json")


# 客戶資料修改
def customersModify(request, id):

    if request.method == 'GET':
        customer = ndb.Key('Customers', int(id)).get()
        data = {
            'customer': customer,
            'action': '修改',
            'clientType': {1: '政府', 2: '企業', 3: '個人'}
        }
        return render(request, "customers/customers-data-handle.html", data)

    elif request.method == 'POST':

        clientName = request.POST['clientName']
        type = int(request.POST['type'])
        clientAddress = request.POST['clientAddress']
        clientTel = request.POST['clientTel']

        _c = models.Customers()
        customer = _c.get_by_id(int(id))

        customer.clientName = clientName
        customer.type = type
        customer.clientAddress = clientAddress
        customer.clientTel = clientTel
        customer.put()

        respData = {
            'title': '客戶資料',
            'message': '修改成功。 (三秒後自動返回)'
        }

        response = render_to_response('success.html', respData)
        response['refresh'] = '3;URL=/customers/'
        return response
