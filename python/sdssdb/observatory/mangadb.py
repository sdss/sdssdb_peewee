#!/usr/bin/env python
# encoding: utf-8
#
# platedb.py
#
# Created by José Sánchez-Gallego on 18 Jun 2017.
#
# This file contains models for the APO/LCO platedb schema. Is has
# been mostly generated using the pwiz.py script, with some
# manual modifications.


from __future__ import absolute_import, division, print_function

from peewee import (BooleanField, FloatField, ForeignKeyField, IntegerField,
                    PrimaryKeyField, TextField)

from sdssdb.observatory import BaseModel, database

from .platedb import Exposure as PlatedbExposure
from .platedb import Plate as PlatedbPlate


database = database  # To avoid annoying PEP8 warning


class UnknownField(object):

    def __init__(self, *_, **__):
        pass


class CurrentStatus(BaseModel):
    camera = TextField(null=True)
    exposure_no = IntegerField(null=True)
    flavor = TextField(null=True)
    mjd = IntegerField(null=True)
    pk = PrimaryKeyField()
    unpluggedifu = BooleanField(null=True)

    class Meta:
        db_table = 'current_status'
        schema = 'mangadb'


class Plate(BaseModel):
    all_sky_plate = BooleanField(null=True)
    comment = TextField(null=True)
    commissioning_plate = BooleanField(null=True)
    manga_tileid = IntegerField(null=True)
    neverobserve = BooleanField()
    pk = PrimaryKeyField()
    platedb_plate = ForeignKeyField(column_name='platedb_plate_pk',
                                    null=True,
                                    model=PlatedbPlate,
                                    field='pk')
    special_plate = BooleanField(null=True)

    class Meta:
        db_table = 'plate'
        schema = 'mangadb'


class DataCube(BaseModel):
    b1_sn2 = FloatField(null=True)
    b2_sn2 = FloatField(null=True)
    pk = PrimaryKeyField()
    platedb_plate = ForeignKeyField(column_name='plate_pk',
                                    null=True,
                                    model=PlatedbPlate,
                                    field='pk')
    r1_sn2 = FloatField(null=True)
    r2_sn2 = FloatField(null=True)

    class Meta:
        db_table = 'data_cube'
        schema = 'mangadb'


class ExposureStatus(BaseModel):
    label = TextField(null=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'exposure_status'
        schema = 'mangadb'


class SetStatus(BaseModel):
    label = TextField(null=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'set_status'
        schema = 'mangadb'


class Set(BaseModel):
    comment = TextField(null=True)
    name = TextField(null=True)
    pk = PrimaryKeyField()
    status = ForeignKeyField(column_name='set_status_pk',
                             null=True, model=SetStatus,
                             field='pk',
                             backref='sets')

    class Meta:
        db_table = 'set'
        schema = 'mangadb'


class Exposure(BaseModel):
    comment = TextField(null=True)
    data_cube = ForeignKeyField(column_name='data_cube_pk',
                                null=True,
                                model=DataCube,
                                backref='exposures',
                                field='pk')
    dither_dec = FloatField(null=True)
    dither_position = UnknownField(null=True)  # ARRAY
    dither_ra = FloatField(null=True)
    status = ForeignKeyField(column_name='exposure_status_pk',
                             null=True,
                             model=ExposureStatus,
                             field='pk',
                             backref='exposures')
    ha = FloatField(null=True)
    pk = PrimaryKeyField()
    platedb_exposure = ForeignKeyField(column_name='platedb_exposure_pk',
                                       null=True,
                                       model=PlatedbExposure,
                                       field='pk',
                                       backref='mangadb_exposure')
    seeing = FloatField(null=True)
    set = ForeignKeyField(column_name='set_pk',
                          null=True,
                          model=Set,
                          field='pk',
                          backref='exposures')
    transparency = FloatField(null=True)

    class Meta:
        db_table = 'exposure'
        schema = 'mangadb'


class ExposureToDataCube(BaseModel):
    data_cube = ForeignKeyField(column_name='data_cube_pk',
                                null=True,
                                model=DataCube,
                                field='pk')
    exposure = ForeignKeyField(column_name='exposure_pk',
                               null=True,
                               model=Exposure,
                               field='pk')
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'exposure_to_data_cube'
        schema = 'mangadb'


class Filelist(BaseModel):
    name = TextField(null=True)
    path = TextField(null=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'filelist'
        schema = 'mangadb'


class Sn2Values(BaseModel):
    b1_sn2 = FloatField(null=True)
    b2_sn2 = FloatField(null=True)
    exposure = ForeignKeyField(column_name='exposure_pk',
                               null=True,
                               model=Exposure,
                               backref='sn2_values',
                               field='pk')
    pipeline_info_pk = IntegerField(null=True)
    pk = PrimaryKeyField()
    r1_sn2 = FloatField(null=True)
    r2_sn2 = FloatField(null=True)

    class Meta:
        db_table = 'sn2_values'
        schema = 'mangadb'


class Spectrum(BaseModel):
    data_cube = ForeignKeyField(column_name='data_cube_pk',
                                null=True,
                                model=DataCube,
                                backref='spectrums',
                                field='pk')
    exposure = ForeignKeyField(column_name='exposure_pk',
                               null=True,
                               model=Exposure,
                               backref='spectrums',
                               field='pk')
    fiber = IntegerField(null=True)
    ifu_no = IntegerField(null=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'spectrum'
        schema = 'mangadb'
