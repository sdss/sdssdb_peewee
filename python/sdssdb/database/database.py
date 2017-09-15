#!/usr/bin/env python
# encoding: utf-8
#
# database.py
#
# Created by José Sánchez-Gallego on 18 Jun 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import socket
import warnings

from peewee import PostgresqlDatabase, OperationalError

from sdssdb import config


__all__ = ('SDSSDatabase', 'ObservatoryDatabase')


class SDSSDatabase(PostgresqlDatabase):

    def __init__(self):

        super(SDSSDatabase, self).__init__(None)
        self.connected = False

    def _test_connection(self):
        """Checks whether the connection is correct."""

        try:
            self.connect()
            self.connected = True
        except OperationalError:

            warnings.warn('failed to connect to database {0}. '
                          'Setting database to None.'.format(self.database),
                          UserWarning)
            self.init(None)
            self.connected = False

    def connect_from_config(self, config_key):
        """Initialises the database from the config file."""

        db_configuration = config[config_key].copy()

        dbname = db_configuration.pop('database')
        self.init(dbname, **db_configuration)
        self._test_connection()

    def connect_from_parameters(self, **params):
        """Initialises the database from a dictionary of parameters."""

        dbname = params.pop('database')
        self.init(dbname, **params)
        self._test_connection()

    def check_connection(self):
        """Checks whether the connection is open or can be connected."""

        if self.connected and self.get_conn().closed == 0:
            return True

        try:
            self.connect()
            self.connected = True
            return True
        except OperationalError:
            return False


class ObservatoryDatabase(SDSSDatabase):

    APO = 'apo'
    LCO = 'lco'
    LOCAL = 'local'

    def __init__(self, autoconnect=True, admin=False):

        super(ObservatoryDatabase, self).__init__()

        self.location = None

        self.set_location()

        if autoconnect:
            self.autoconnect()

        if self.connected and admin:
            self.become_admin()

    def dsn_parameters(self):
        """Returns the DSN parameters of the connection."""

        try:
            params = self.get_conn().get_dsn_parameters()
            return params
        except AttributeError:
            return None

    def set_location(self):
        """Determines observatory location."""

        hostname = socket.gethostname()

        if 'sdss4-db' in hostname:
            if hostname.endswith('lco.cl'):
                self.location = self.LCO
            else:
                self.location = self.APO
        else:
            self.location = self.LOCAL

    def autoconnect(self):
        """Tries to select the best possible connection to the db."""

        if self.location == self.APO:
            self.connect_from_config('apo')
        elif self.location == self.LCO:
            self.connect_from_config('lco')
        else:
            self.connect_from_config('local')

    def _become(self, user):
        """Internal method to change the connection to a certain user."""

        if not self.connected:
            raise RuntimeError('DB has not been initialised.')

        dsn_params = self.dsn_parameters()
        if dsn_params is None:
            raise RuntimeError('cannot determine the DSN parameters. '
                               'The DB may be disconnected.')

        try:
            dsn_params['user'] = user
            dbname = dsn_params.pop('dbname')
            self.init(dbname, **dsn_params)
            self.connect()
        except OperationalError as ee:
            raise RuntimeError('cannot connect to database with '
                               'user {0}'.format(user))

    def become_admin(self):
        """Becomes the admin user."""

        self._become(config['apo_admin'])

    def become_user(self):
        """Becomes the non-admin user."""

        self._become(config['apo_user'])
