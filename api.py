#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import json
import os
import re
from scoring import get_score, get_interests
from store import Store
from abc import ABCMeta, abstractmethod


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

class ValidationError(Exception):
    pass


class Field(object):

    def __init__(self, required, nullable=False):
        self.label = None
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        return value

    def check_nullable_required(self, required, nullable, value):
        if value is not None:
            if not isinstance(value, int):
                if not value and not nullable:
                    raise ValidationError("Field %s must be not nullables" % self.label)
            elif value == 0 and not nullable:
                raise ValidationError("Field %s must be not nullables" % self.label)
        elif required:
            raise ValidationError("Field %s must be present" % self.label)

    def __set__(self, instance, value):
        self.check_nullable_required(self.required, self.nullable, value)
        if value is None:
            instance.__dict__[self.label] = value
        else:
            instance.__dict__[self.label] = self.validate(value)

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.label, None)


class CharField(Field):
    def __init__(self, required, nullable):
        super(CharField, self).__init__(required, nullable)

    def validate(self, value):
        if isinstance(value, (str, unicode)):
            return value
        else:
            raise ValidationError('Field %s is not a string' % self.label)


class ArgumentsField(Field):
    def __init__(self, required, nullable):
        super(ArgumentsField, self).__init__(required, nullable)

    def validate(self, value):
        if isinstance(value, dict):
            return value
        else:
            raise ValidationError('Arguments is not a valid json')


class EmailField(Field):

    def __init__(self, required, nullable):
        super(EmailField, self).__init__(required, nullable)

    def validate(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value):
                return value
            else:
                raise ValidationError('Email format is not valid')
        else:
            raise ValidationError('Email field has a wrong type')


class PhoneField(Field):

    def __init__(self, required, nullable):
        super(PhoneField, self).__init__(required, nullable)

    def validate(self, value):
        if isinstance(value, long) or isinstance(value, str) or isinstance(value, unicode)\
                or isinstance(value, int):
            value = str(value)
            if re.match(r"7\d{10}", value) and len(value) == 11:
                return value
            else:
                raise ValidationError('Phone number not valid')
        else:
            raise ValidationError('Phone field has a wrong type')


class DateField(Field):

    def __init__(self, required, nullable):
        super(DateField, self).__init__(required, nullable)

    def validate(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            if re.match(r"\d{2}\.\d{2}\.\d{4}", value):
                return value
            else:
                raise ValidationError('Date field is not a valid date')
        else:
            raise ValidationError('Date filed have a wrong type')


class BirthDayField(Field):

    def __init__(self, required, nullable):
        super(BirthDayField, self).__init__(required, nullable)

    def validate(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            if re.match(r"\d{2}\.\d{2}\.\d{4}", value):
                value = datetime.datetime.strptime(value, '%d.%m.%Y')
                delta = datetime.datetime.now() - value
                if delta.days/365 < 70:
                    return value
                else:
                    raise ValidationError('Сlient has been born for more than 70 years')
            else:
                raise ValidationError('Birthday field is not a valid date')
        else:
            raise ValidationError('Birthday filed have a wrong type')


class GenderField(Field):
    def __init__(self, required, nullable):
        super(GenderField, self).__init__(required, nullable)

    def validate(self, value):
        if isinstance(value, int):
            if value in [UNKNOWN, MALE, FEMALE]:
                return value
            else:
                raise ValidationError('Wrong gender field value')
        else:
            raise ValidationError('Gender filed has a wrong type')


class ClientIDsField(Field):
    def __init__(self, required):
        super(ClientIDsField, self).__init__(required)

    def validate(self, value):
        if isinstance(value, list) or isinstance(value, tuple):
            if all(isinstance(item, int) for item in value):
                return value
            else:
                raise ValidationError('Some client id is not an integer value')
        else:
            raise ValidationError('Client ids field is not an array')


class DeclarativeMethodRequest(type):

    def __new__(mcs, name, bases, attrs):
        declared_fields = []
        for key, value in attrs.iteritems():
            if isinstance(value, Field):
                value.label = key
                declared_fields.append(key)
        attrs['declarated_fields'] = declared_fields
        return super(DeclarativeMethodRequest, mcs).__new__(mcs, name, bases, attrs)


class Request(object):
    __metaclass__ = DeclarativeMethodRequest

    def __init__(self, request):
        self.errors = []
        for value in self.__class__.__dict__['declarated_fields']:
            try:
                if value in request:
                    self.__setattr__(value, request[value])
                else:
                    self.__setattr__(value, None)
            except ValidationError as E:
                self.errors.append(str(E))

    @property
    def is_valid(self):
        if self.errors:
            return False
        else:
            return True


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, request):
        super(MethodRequest, self).__init__(request)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, request):
        super(OnlineScoreRequest, self).__init__(request)


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def __init__(self, request):
        super(ClientsInterestsRequest, self).__init__(request)

    def handler(self, ctx, store):
        interests = {}
        for id in self.client_ids:
            interests[id] = get_interests(store, id)
        if interests:
            ctx['nclients'] = len(self.client_ids)
            return 200, interests
        else:
            logging.error('Request error "Can not connect to store db"')
            return NOT_FOUND, 'Can not connect to store db'


def check_auth(request):
    logging.debug('checking auth')
    if request.is_admin:
        logging.debug('is admin')
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        logging.debug('not an admin')
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        logging.debug('success auth')
        return True
    return False


class Handler(object):
    def __init__(self, request, ctx, store):
        self.request = request
        self.ctx = ctx
        self.store = store

    def get_error(self):
        responce = ''
        for error in self.request.errors:
            responce += error
            responce += '\r\n'
        code = INVALID_REQUEST
        return responce, code

    def handler(self):
        pass


class OnlineScoreRequestHandler(Handler):
    def __init__(self, request, ctx, store):
        super(OnlineScoreRequestHandler, self).__init__(request, ctx, store)

    def handler(self):
        fields = []
        for field in self.request.declarated_fields:
            if getattr(self.request, field):
                fields.append(field)
        if ('phone' in fields and 'email' in fields) \
            or ('first_name' in fields and 'last_name' in fields) \
            or ('gender' in fields and 'birthday' in fields):
            score = get_score(self.store, self.request.phone, self.request.email, self.request.birthday,
                                  self.request.gender, self.request.first_name, self.request.last_name)
            self.ctx['has'] = fields
            return {'score': score}, 200
        else:
            logging.error('Request error "Two much null arguments"')
            return 'Two much null arguments', INVALID_REQUEST,


class ClientsInterestsRequestHandler(Handler):
    def __init__(self, request, ctx, store):
        super(ClientsInterestsRequestHandler, self).__init__(request, ctx, store)

    def handler(self):
        if not self.request.is_valid:
            responce, code = self.get_error()
            return responce, code
        interests = {}
        for client_id in self.request.client_ids:
            interests[client_id] = get_interests(self.store, client_id)
        if interests:
            self.ctx['nclients'] = len(self.request.client_ids)
            return interests, 200
        else:
            logging.error('Request error "Can not connect to store db"')
            return 'Can not connect to store db', NOT_FOUND


class RequestHandler(Handler):
    def __init__(self, request, ctx, store):
        super(RequestHandler, self).__init__(request, ctx, store)

    def handler(self):
        if not self.request.is_valid:
            responce, code = self.get_error()
            return responce, code
        logging.debug('request is valid')
        if not check_auth(self.request):
            logging.debug('forbidden')
            return 'Forbidden', 403
        if self.request.method == 'online_score':
            logging.debug('online score')
            if self.request.is_admin:
                return {'score': 42}, 200
            else:
                responce, code = OnlineScoreRequestHandler(OnlineScoreRequest(self.request.arguments),
                                                        self.ctx, self.store).handler()
                return responce, code
        if self.request.method == 'clients_interests':
            logging.debug('clients interests')
            responce, code = ClientsInterestsRequestHandler(ClientsInterestsRequest(self.request.arguments),
                                                            self.ctx, self.store).handler()
            return responce, code
        logging.debug('wrong request method')
        return 'Wrong request method', BAD_REQUEST


def method_handler(request, ctx, store):
    logging.debug('Parcing request')
    responce, code = RequestHandler(MethodRequest(request['body']), ctx, store).handler()
    return responce, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store('127.0.0.1', '6379', '6370', 10, 10, 3)

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        responce, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            logging.info(request)
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    responce, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"responce": responce, "code": code}
        else:
            r = {"error": responce or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'opts.log')
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=log_path)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()







