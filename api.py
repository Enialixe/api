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

    def __init__(self, requred, nullable=False):
        self.label = None
        self.requred = requred
        self.nullable = nullable

    def vallidate(self, value):
        return value

    def check_nullable_requred(self, requred, nullable, value):
        if value is not None:
            if value or (not value and nullable):
                return value
            elif (not value and not nullable):
                raise ValidationError("Field %s must be not nullables" % self.label)
        elif requred:
            raise ValidationError("Field %s must be present" % self.label)
        else:
            return None

    def __set__(self, instance, value):
        value = self.check_nullable_requred(self.requred, self.nullable, value)
        if value is None:
            instance.__dict__[self.label] = value
        else:
            instance.__dict__[self.label] = self.vallidate(value)

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.label, None)


class CharField(Field):
    def __init__(self, requred, nullable):
        super(CharField, self).__init__(requred, nullable)

    def vallidate(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        else:
            print(type(value))
            print(value)
            raise ValidationError('Field %s is not a string' % self.label)


class ArgumentsField(Field):
    def __init__(self, requred, nullable):
        super(ArgumentsField, self).__init__(requred, nullable)

    def vallidate(self, value):
        if isinstance(value, dict):
            return value
        else:
            raise ValidationError('Arguments is not a valid json')


class EmailField(Field):

    def __init__(self, requred, nullable):
        super(EmailField, self).__init__(requred, nullable)

    def vallidate(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value):
                return value
            else:
                raise ValidationError('Email format is not valid')
        else:
            raise ValidationError('Email field has a wrong type')


class PhoneField(Field):

    def __init__(self, requred, nullable):
        super(PhoneField, self).__init__(requred, nullable)

    def vallidate(self, value):
        if isinstance(value, int) or isinstance(value, str) or isinstance(value, unicode):
            value = str(value)
            if re.match(r"7\d{10}", value) and len(value) == 11:
                return value
            else:
                raise ValidationError('Phone number not valid')
        else:
            raise ValidationError('Phone field has a wrong type')


class DateField(Field):

    def __init__(self, requred, nullable):
        super(DateField, self).__init__(requred, nullable)

    def vallidate(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            if re.match(r"\d{2}\.\d{2}\.\d{4}", value):
                return value
            else:
                raise ValidationError('Date field is not a valid date')
        else:
            raise ValidationError('Date filed have a wrong type')


class BirthDayField(Field):

    def __init__(self, requred, nullable):
        super(BirthDayField, self).__init__(requred, nullable)

    def vallidate(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            if re.match(r"\d{2}\.\d{2}\.\d{4}", value):
                value = datetime.datetime.strptime(value, '%d.%m.%Y')
                delta = datetime.datetime.now() - value
                if delta.days/365<70:
                    return value
                else:
                    raise ValidationError('Сlient has been born for more than 70 years')
            else:
                raise ValidationError('Birthday field is not a valid date')
        else:
            raise ValidationError('Birthday filed have a wrong type')


class GenderField(Field):
    def __init__(self, requred, nullable):
        super(GenderField, self).__init__(requred, nullable)

    def vallidate(self, value):
        if isinstance(value, int):
             if value in [UNKNOWN, MALE, FEMALE]:
                return value
             else:
                raise ValidationError('Wrong gender field value')
        else:
            raise ValidationError('Gender filed has a wrong type')


class ClientIDsField(Field):
    def __init__(self, requred):
        super(ClientIDsField, self).__init__(requred)

    def vallidate(self, value):
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
        responce = ''
        for error in self.errors:
            responce += error
            responce += '\r\n'
        if responce:
            logging.error('Request error %s' %responce)
            return INVALID_REQUEST, responce
        else:
            return 0, responce


class MethodRequest(Request):
    account = CharField(requred=False, nullable=True)
    login = CharField(requred=True, nullable=True)
    token = CharField(requred=True, nullable=True)
    arguments = ArgumentsField(requred=True, nullable=True)
    method = CharField(requred=True, nullable=False)

    def __init__(self, request):
        super(MethodRequest, self).__init__(request)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class OnlineScoreRequest(Request):
    first_name = CharField(requred=False, nullable=True)
    last_name = CharField(requred=False, nullable=True)
    email = EmailField(requred=False, nullable=True)
    phone = PhoneField(requred=False, nullable=True)
    birthday = BirthDayField(requred=False, nullable=True)
    gender = GenderField(requred=False, nullable=True)

    def __init__(self, request, admin):
        super(OnlineScoreRequest, self).__init__(request)
        self.is_admin = admin

    def handler(self, ctx, store):
        fields = []
        if self.is_admin:
            score = 42
            return 200, {'score': score}
        else:
            for field, value in self.__dict__.items():
                if value is not None and field != 'errors' and field != 'is_admin':
                    fields.append(field)
            if ('phone' in fields and 'email' in fields) \
                or ('first_name' in fields and 'last_name' in fields) \
                or ('gender' in fields and 'birthday' in fields):
                score = get_score(store, self.phone, self.email, self.birthday, self.gender, self.first_name,
                              self.last_name)
                ctx['has'] = fields
                return 200, {'score': score}
            else:
                logging.error('Request error "Two much null arguments"')
                return INVALID_REQUEST, 'Two much null arguments'


class ClientsInterestsRequest(Request):

    client_ids = ClientIDsField(requred=True)
    date = DateField(requred=False, nullable=True)

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


def method_handler(request, ctx, store):
    logging.debug('Parcing request')
    request = MethodRequest(request['body'])
    code, responce = request.is_valid
    print(request.method)
    if not responce or not code:
        logging.debug('request is valid')
        if not check_auth(request):
            logging.debug('forbidden')
            code = 403
            responce = 'Forbidden'
        elif request.method == 'online_score':
            logging.debug('online score')
            score_request = OnlineScoreRequest(request.arguments, request.is_admin)
            code, responce = score_request.is_valid
            if not responce or not code:
                logging.debug('online score is valid')
                code, responce = score_request.handler(ctx, store)
        elif request.method == 'clients_interests':
            logging.debug('clients interests')
            clients_request = ClientsInterestsRequest(request.arguments)
            code, responce = clients_request.is_valid
            if not responce or not code:
                logging.debug('clients interests is valid')
                code, responce = clients_request.handler(ctx, store)
        else:
            logging.debug('wrong request method')
            return 'Wrong request method', BAD_REQUEST
    return responce, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store()

    def get_request_id(self, headers):
        print(headers)
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        responce, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception as E:
            print(E)
            code = BAD_REQUEST

        if request:
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







