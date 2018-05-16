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


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from peewee import TextField, DecimalField, IntegerField, BooleanField
from peewee import BigIntegerField, ForeignKeyField, DateTimeField, DateField
from peewee import CompositeKey, CharField, PrimaryKeyField, ManyToManyField, DeferredThroughModel

from sdssdb.observatory import BaseModel, database


database = database  # To avoid annoying PEP8 warning


class UnknownField(object):

    def __init__(self, *_, **__):
        pass


class Cartridge(BaseModel):
    broken_fibers = TextField(null=True)
    guide_fiber_throughput = DecimalField(null=True)
    number = IntegerField(null=True, unique=True)
    online = BooleanField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'cartridge'
        schema = 'platedb'


class Design(BaseModel):
    comment = TextField(null=True)
    pk = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'design'
        schema = 'platedb'

    def get_value_for_field(self, field):
        """Returns the value of a design field."""

        design_field = DesignField.select().where(DesignField.label == field.lower()).first()
        if design_field is None:
            raise ValueError('invalid field name')

        return DesignValue.select().where((DesignValue.design == self) &
                                          (DesignValue.field == design_field)).first()


class PlateCompletionStatus(BaseModel):
    label = TextField(null=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'plate_completion_status'
        schema = 'platedb'


class PlateLocation(BaseModel):
    label = TextField(unique=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'plate_location'
        schema = 'platedb'


class PlateRun(BaseModel):
    label = TextField(null=True, unique=True)
    pk = BigIntegerField(primary_key=True)
    year = IntegerField(null=True)

    class Meta:
        db_table = 'plate_run'
        schema = 'platedb'


class TileStatus(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'tile_status'
        schema = 'platedb'


class Tile(BaseModel):
    id = IntegerField(null=True, unique=True)
    pk = PrimaryKeyField()
    tile_status = ForeignKeyField(column_name='tile_status_pk',
                                  model=TileStatus,
                                  backref='tiles',
                                  field='pk')

    class Meta:
        db_table = 'tile'
        schema = 'platedb'


class SurveyMode(BaseModel):
    definition_label = TextField(null=True)
    label = TextField(null=True, unique=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'survey_mode'
        schema = 'platedb'


class Survey(BaseModel):
    label = TextField(null=True, unique=True)
    pk = PrimaryKeyField()
    plateplan_name = TextField()

    class Meta:
        db_table = 'survey'
        schema = 'platedb'


class PlateStatus(BaseModel):
    label = TextField(null=True, unique=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'plate_status'
        schema = 'platedb'


PlateSurveyThroughModel = DeferredThroughModel()
PlateStatusThroughModel = DeferredThroughModel()


class Plate(BaseModel):

    print_fields = ['plate_id']

    chunk = TextField(null=True)
    comment = TextField(null=True)
    current_survey_mode = ForeignKeyField(column_name='current_survey_mode_pk',
                                          null=True,
                                          model=SurveyMode,
                                          field='pk')
    design = ForeignKeyField(column_name='design_pk',
                             null=True,
                             model=Design,
                             backref='plates',
                             field='pk')
    epoch = DecimalField(null=True)
    location_id = BigIntegerField(column_name='location_id', null=True)
    name = TextField(null=True)
    pk = BigIntegerField(primary_key=True)
    plate_completion_status_pk = ForeignKeyField(
        column_name='plate_completion_status_pk',
        null=True,
        model=PlateCompletionStatus,
        backref='plates',
        field='pk')
    plate_id = IntegerField(column_name='plate_id', unique=True)
    plate_location = ForeignKeyField(column_name='plate_location_pk',
                                     model=PlateLocation,
                                     field='pk')
    plate_run = ForeignKeyField(column_name='plate_run_pk',
                                null=True,
                                model=PlateRun,
                                field='pk')
    rerun = TextField(null=True)
    temperature = DecimalField(null=True)
    tile_id = IntegerField(column_name='tile_id', null=True)
    tile = ForeignKeyField(column_name='tile_pk',
                           null=True,
                           model=Tile,
                           backref='plates',
                           field='pk')
    surveys = ManyToManyField(model=Survey,
                              through_model=PlateSurveyThroughModel,
                              backref='plates')
    statuses = ManyToManyField(model=PlateStatus,
                               through_model=PlateStatusThroughModel,
                               backref='plates')

    class Meta:
        db_table = 'plate'
        schema = 'platedb'


class PluggingStatus(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'plugging_status'
        schema = 'platedb'


class Instrument(BaseModel):
    label = TextField(null=True, unique=True)
    pk = PrimaryKeyField()
    short_label = TextField(null=True)

    class Meta:
        db_table = 'instrument'
        schema = 'platedb'


PluggingInstrumentDeferred = DeferredThroughModel()


class Plugging(BaseModel):
    cartridge = ForeignKeyField(column_name='cartridge_pk',
                                null=True,
                                model=Cartridge,
                                backref='pluggings',
                                field='pk')
    fscan = IntegerField(column_name='fscan_id', null=True)
    fscan_mjd = IntegerField(null=True)
    name = TextField(null=True)
    pk = PrimaryKeyField()
    plate = ForeignKeyField(column_name='plate_pk',
                            model=Plate,
                            backref='pluggings',
                            field='pk')
    status = ForeignKeyField(column_name='plugging_status_pk',
                             model=PluggingStatus, field='pk',
                             backref='pluggings')

    instruments = ManyToManyField(model=Instrument,
                                  through_model=PluggingInstrumentDeferred,
                                  backref='pluggings')

    class Meta:
        db_table = 'plugging'
        schema = 'platedb'


class ActivePlugging(BaseModel):
    pk = PrimaryKeyField()
    plugging = ForeignKeyField(column_name='plugging_pk', model=Plugging,
                               backref='active_plugging',
                               field='pk', unique=True)

    class Meta:
        db_table = 'active_plugging'
        schema = 'platedb'


class ApogeeThreshold(BaseModel):
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'apogee_threshold'
        schema = 'platedb'


class BossPluggingInfo(BaseModel):
    first_dr = TextField(null=True)
    pk = PrimaryKeyField()
    plugging = ForeignKeyField(column_name='plugging_pk', model=Plugging,
                               backref='boss_plugging_info', field='pk')

    class Meta:
        db_table = 'boss_plugging_info'
        schema = 'platedb'


class Camera(BaseModel):
    instrument = ForeignKeyField(column_name='instrument_pk', null=True,
                                 model=Instrument,
                                 backref='cameras', field='pk')
    label = TextField(null=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'camera'
        schema = 'platedb'


class BossSn2Threshold(BaseModel):
    camera = ForeignKeyField(column_name='camera_pk', model=Camera,
                             backref='boss_sn2_thresholds', field='pk')
    min_exposures = IntegerField(null=True)
    pk = PrimaryKeyField()
    sn2_min = DecimalField(null=True)
    sn2_threshold = DecimalField()
    version = IntegerField(null=True)

    class Meta:
        db_table = 'boss_sn2_threshold'
        schema = 'platedb'


class ExposureFlavor(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'exposure_flavor'
        schema = 'platedb'


class ExposureStatus(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'exposure_status'
        schema = 'platedb'


class Pointing(BaseModel):
    center_dec = DecimalField(null=True)
    center_ra = DecimalField(null=True)
    design = ForeignKeyField(column_name='design_pk', model=Design,
                             backref='pointings', field='pk')
    pk = BigIntegerField(primary_key=True)
    pointing_no = IntegerField(null=True)

    class Meta:
        db_table = 'pointing'
        schema = 'platedb'


class PlatePointing(BaseModel):
    ha_observable_max = DecimalField(null=True)
    ha_observable_min = DecimalField(null=True)
    hour_angle = DecimalField(null=True)
    pk = PrimaryKeyField()
    plate = ForeignKeyField(column_name='plate_pk', null=True, model=Plate,
                            backref='plate_pointings', field='pk')
    pointing_name = CharField(null=False)
    pointing = ForeignKeyField(column_name='pointing_pk', null=True,
                               model=Pointing, field='pk',
                               backref='plate_pointings')
    priority = IntegerField()

    class Meta:
        db_table = 'plate_pointing'
        indexes = (
            (('plate_pk', 'pointing_name'), True),
        )
        schema = 'platedb'


class ObservationStatus(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'observation_status'
        schema = 'platedb'


class Observation(BaseModel):
    comment = TextField(null=True)
    mjd = DecimalField(null=True)
    observation_status = ForeignKeyField(column_name='observation_status_pk',
                                         model=ObservationStatus,
                                         backref='observations',
                                         field='pk')
    pk = PrimaryKeyField()
    plate_pointing = ForeignKeyField(column_name='plate_pointing_pk', null=True,
                                     model=PlatePointing,
                                     backref='observtions', field='pk')
    plugging = ForeignKeyField(column_name='plugging_pk', null=True,
                               model=Plugging, backref='observations', field='pk')

    class Meta:
        db_table = 'observation'
        schema = 'platedb'


class Exposure(BaseModel):
    camera = ForeignKeyField(column_name='camera_pk', null=True,
                             model=Camera, backref='exposures', field='pk')
    comment = TextField(null=True)
    exposure_flavor = ForeignKeyField(column_name='exposure_flavor_pk',
                                      null=True,
                                      model=ExposureFlavor,
                                      field='pk')
    exposure_no = IntegerField(null=True)
    exposure_status = ForeignKeyField(column_name='exposure_status_pk',
                                      model=ExposureStatus,
                                      field='pk')
    exposure_time = DecimalField(null=True)
    observation = ForeignKeyField(column_name='observation_pk', null=True, model=Observation,
                                  backref='exposures', field='pk')
    pk = PrimaryKeyField()
    start_time = DecimalField(null=True)
    survey_mode = ForeignKeyField(column_name='survey_mode_pk',
                                  null=True, model=SurveyMode, field='pk')
    survey = ForeignKeyField(column_name='survey_pk', null=True,
                             model=Survey, backref='exposures', field='pk')

    class Meta:
        db_table = 'exposure'
        indexes = (
            (('exposure_no', 'survey_pk'), True),
        )
        schema = 'platedb'


class CameraFrame(BaseModel):
    camera = ForeignKeyField(column_name='camera_pk', model=Camera,
                             backref='camera_frames', field='pk')
    comment = TextField(null=True)
    exposure = ForeignKeyField(column_name='exposure_pk', model=Exposure,
                               backref='camera_frames', field='pk')
    pk = PrimaryKeyField()
    sn2 = DecimalField(null=True)

    class Meta:
        db_table = 'camera_frame'
        schema = 'platedb'


# class CartridgeToSurvey(BaseModel):
#     cartridge_pk = ForeignKeyField(column_name='cartridge_pk', model=Cartridge,
#                                    backref='cartridge_cartridge_pk_set', field='pk')
#     survey_pk = ForeignKeyField(column_name='survey_pk', model=Survey,
#                                 backref='survey_survey_pk_set', field='pk')
#
#     class Meta:
#         db_table = 'cartridge_to_survey'
#         indexes = (
#             (('cartridge_pk', 'survey_pk'), True),
#         )
#         schema = 'platedb'
#         primary_key = CompositeKey('cartridge_pk', 'survey_pk')


class CmmMeas(BaseModel):
    cmmfilename = TextField(null=True)
    date = DateField(null=True)
    fitoffsetx = DecimalField(null=True)
    fitoffsety = DecimalField(null=True)
    fitqpang = DecimalField(null=True)
    fitqpmag = DecimalField(null=True)
    fitrot = DecimalField(null=True)
    fitscale = DecimalField(null=True)
    pk = PrimaryKeyField()
    plate = ForeignKeyField(column_name='plate_pk', null=True, model=Plate,
                            backref='cmm_measurements', field='pk')

    class Meta:
        db_table = 'cmm_meas'
        schema = 'platedb'


class Constants(BaseModel):
    name = CharField(primary_key=True)
    value = CharField(null=True)

    class Meta:
        db_table = 'constants'
        schema = 'platedb'


class DesignField(BaseModel):
    label = TextField(unique=True)
    pk = BigIntegerField(primary_key=True)

    class Meta:
        db_table = 'design_field'
        schema = 'platedb'


class DesignValue(BaseModel):
    field = ForeignKeyField(column_name='design_field_pk',
                            null=True, model=DesignField, field='pk')
    design = ForeignKeyField(column_name='design_pk', null=True,
                             model=Design, backref='values', field='pk')
    pk = BigIntegerField(primary_key=True)
    value = TextField(null=True)

    class Meta:
        db_table = 'design_value'
        indexes = ((('design_pk', 'design_field_pk'), True),)
        schema = 'platedb'

    def __repr__(self):
        return '<DesignValue: pk={0}, design={1}, field={2}, value={3}>'.format(self.pk,
                                                                                self.design_pk,
                                                                                self.field.label,
                                                                                self.value)


class ExposureHeaderKeyword(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'exposure_header_keyword'
        schema = 'platedb'


class ExposureHeaderValue(BaseModel):
    comment = TextField(null=True)
    exposure_header_keyword = ForeignKeyField(column_name='exposure_header_keyword_pk',
                                              model=ExposureHeaderKeyword,
                                              field='pk')
    exposure = ForeignKeyField(column_name='exposure_pk', model=Exposure,
                               backref='exposure_header_values', field='pk')
    index = IntegerField()
    pk = PrimaryKeyField()
    value = TextField()

    class Meta:
        db_table = 'exposure_header_value'
        schema = 'platedb'


class PlPlugmapM(BaseModel):
    checked_in = BooleanField(null=True)
    dirname = TextField(null=True)
    file = TextField(null=True)
    filename = TextField(null=True)
    fscan = IntegerField(column_name='fscan_id', null=True)
    fscan_mjd = IntegerField(null=True)
    md5_checksum = TextField(null=True)
    pk = PrimaryKeyField()
    plugging = ForeignKeyField(column_name='plugging_pk', null=True,
                               model=Plugging, backref='plplugmapms', field='pk')
    pointing_name = CharField(null=True)

    class Meta:
        db_table = 'pl_plugmap_m'
        schema = 'platedb'


class ObjectType(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'object_type'
        schema = 'platedb'


class PlateHoleType(BaseModel):
    label = TextField()
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'plate_hole_type'
        schema = 'platedb'


class PlateHolesFile(BaseModel):
    filename = TextField()
    pk = PrimaryKeyField()
    plate = ForeignKeyField(column_name='plate_pk', model=Plate,
                            backref='plate_hole_files', field='pk')

    class Meta:
        db_table = 'plate_holes_file'
        schema = 'platedb'


class PlateHole(BaseModel):
    apogee_target1 = IntegerField(null=True)
    apogee_target2 = IntegerField(null=True)
    catalog_object_pk = IntegerField(index=True, null=True)
    object_type = ForeignKeyField(column_name='object_type_pk',
                                  null=True, model=ObjectType, field='pk')
    pk = PrimaryKeyField()
    plate_hole_type = ForeignKeyField(column_name='plate_hole_type_pk',
                                      null=True,
                                      model=PlateHoleType,
                                      field='pk')
    plate_holes_file = ForeignKeyField(column_name='plate_holes_file_pk',
                                       null=True,
                                       model=PlateHolesFile,
                                       field='pk',
                                       backref='plate_holes')
    pointing_number = IntegerField(null=True)
    tmass_h = DecimalField(null=True)
    tmass_j = DecimalField(null=True)
    tmass_k = DecimalField(null=True)
    xfocal = DecimalField(null=True)
    yfocal = DecimalField(null=True)

    class Meta:
        db_table = 'plate_hole'
        schema = 'platedb'


class Fiber(BaseModel):
    fiber = IntegerField(column_name='fiber_id')
    pk = PrimaryKeyField()
    pl_plugmap_m = ForeignKeyField(column_name='pl_plugmap_m_pk',
                                   model=PlPlugmapM, field='pk')
    plate_hole = ForeignKeyField(column_name='plate_hole_pk', model=PlateHole,
                                 backref='fibers', field='pk')

    class Meta:
        db_table = 'fiber'
        schema = 'platedb'


class Gprobe(BaseModel):
    cartridge = ForeignKeyField(column_name='cartridge_pk', null=True, model=Cartridge,
                                backref='gprobes', field='pk')
    exists = IntegerField(null=True)
    fiber_type = UnknownField()  # USER-DEFINED
    focus_offset = DecimalField(null=True)
    gprobe = IntegerField(column_name='gprobe_id', null=True)
    pk = PrimaryKeyField()
    radius = DecimalField(null=True)
    rotation = DecimalField(null=True)
    x_center = DecimalField(null=True)
    x_ferrule_offset = DecimalField(null=True)
    y_center = DecimalField(null=True)
    y_ferrule_offset = DecimalField(null=True)

    class Meta:
        db_table = 'gprobe'
        schema = 'platedb'


class HoleMeas(BaseModel):
    cmm_meas = ForeignKeyField(column_name='cmm_meas_pk', null=True,
                               model=CmmMeas, field='pk')
    diaerr = DecimalField(null=True)
    measx = DecimalField(null=True)
    measy = DecimalField(null=True)
    nomdia = DecimalField(null=True)
    nomx = DecimalField(null=True)
    nomy = DecimalField(null=True)
    pk = PrimaryKeyField()
    plate_hole = ForeignKeyField(column_name='plate_hole_pk', null=True, model=PlateHole,
                                 backref='hole_measurements', field='pk')
    qpresidr = DecimalField(null=True)
    qpresidx = DecimalField(null=True)
    qpresidy = DecimalField(null=True)
    residr = DecimalField(null=True)
    residx = DecimalField(null=True)
    residy = DecimalField(null=True)

    class Meta:
        db_table = 'hole_meas'
        schema = 'platedb'


class PlateCompletionStatusHistory(BaseModel):
    comment = TextField()
    first_name = TextField(null=True)
    last_name = TextField(null=True)
    pk = PrimaryKeyField()
    plate_completion_status = ForeignKeyField(column_name='plate_completion_status_pk',
                                              model=PlateCompletionStatus,
                                              backref='plate_completion_status_history',
                                              field='pk')
    plate = ForeignKeyField(column_name='plate_pk', model=Plate,
                            backref='plate_completion_status_history', field='pk')
    timestamp = DateTimeField()

    class Meta:
        db_table = 'plate_completion_status_history'
        schema = 'platedb'


class PlateInput(BaseModel):
    comment = TextField(null=True)
    design = ForeignKeyField(column_name='design_pk', null=True,
                             model=Design, backref='inputs', field='pk')
    filepath = TextField(null=True)
    input_number = IntegerField(null=True)
    md5_checksum = TextField(null=True)
    pk = BigIntegerField(primary_key=True)
    priority = IntegerField(null=True)

    class Meta:
        db_table = 'plate_input'
        schema = 'platedb'


# class PlatePointingToPointingStatus(BaseModel):
#     pk = BigIntegerField(primary_key=True)
#     plate_pointing_pk = ForeignKeyField(column_name='plate_pointing_pk',
#                                         null=True,
#                                         model=PlatePointing,
#                                         backref='plate_pointing_plate_pointing_pk_set',
#                                         field='pk')
#     pointing_status_pk = ForeignKeyField(
#         column_name='pointing_status_pk', null=True, model=PlateStatus, field='pk')
#
#     class Meta:
#         db_table = 'plate_pointing_to_pointing_status'
#         indexes = (
#             (('plate_pointing_pk', 'pointing_status_pk'), True),
#         )
#         schema = 'platedb'


class PlateRunToDesign(BaseModel):
    design_pk = BigIntegerField(null=True)
    pk = BigIntegerField(primary_key=True)
    plate_run_pk = BigIntegerField(null=True)

    class Meta:
        db_table = 'plate_run_to_design'
        indexes = (
            (('plate_run_pk', 'design_pk'), True),
        )
        schema = 'platedb'


# class PlateToInstrument(BaseModel):
#     instrument_pk = ForeignKeyField(column_name='instrument_pk', null=True, model=Instrument,
#                                     backref='instrument_instrument_pk_set', field='pk')
#     pk = BigIntegerField(primary_key=True)
#     plate_pk = ForeignKeyField(column_name='plate_pk', null=True, model=Plate,
#                                backref='plate_plate_pk_set', field='pk')
#
#     class Meta:
#         db_table = 'plate_to_instrument'
#         indexes = (
#             (('plate_pk', 'instrument_pk'), True),
#         )
#         schema = 'platedb'


class PlateToPlateStatus(BaseModel):
    pk = BigIntegerField(primary_key=True)
    plate = ForeignKeyField(column_name='plate_pk', null=True,
                            model=Plate,
                            field='pk')
    plate_status = ForeignKeyField(column_name='plate_status_pk', null=True,
                                   model=PlateStatus, field='pk')

    class Meta:
        db_table = 'plate_to_plate_status'
        indexes = (
            (('plate_status_pk', 'plate_pk'), True),
        )
        schema = 'platedb'


class PlateToSurvey(BaseModel):
    pk = PrimaryKeyField()
    plate = ForeignKeyField(column_name='plate_pk', null=True, model=Plate,
                            field='pk')
    survey = ForeignKeyField(column_name='survey_pk', null=True,
                             model=Survey, field='pk')

    class Meta:
        db_table = 'plate_to_survey'
        indexes = (
            (('plate_pk', 'survey_pk'), True),
        )
        schema = 'platedb'


class PluggingToBossSn2Threshold(BaseModel):
    boss_sn2_threshold_version = IntegerField()
    plugging_pk = IntegerField()

    class Meta:
        db_table = 'plugging_to_boss_sn2_threshold'
        indexes = (
            (('plugging_pk', 'boss_sn2_threshold_version'), True),
        )
        schema = 'platedb'
        primary_key = CompositeKey('boss_sn2_threshold_version', 'plugging_pk')


class PluggingToInstrument(BaseModel):
    instrument = ForeignKeyField(column_name='instrument_pk', null=True, model=Instrument,
                                 field='pk')
    pk = PrimaryKeyField()
    plugging = ForeignKeyField(column_name='plugging_pk', null=True,
                               model=Plugging, field='pk')

    class Meta:
        db_table = 'plugging_to_instrument'
        indexes = (
            (('plugging_pk', 'instrument_pk'), True),
        )
        schema = 'platedb'


class PointingStatus(BaseModel):
    label = TextField(null=True, unique=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'pointing_status'
        schema = 'platedb'


class ProfTolerances(BaseModel):
    pk = PrimaryKeyField()
    r1_high = DecimalField()
    r1_low = DecimalField()
    r2_high = DecimalField()
    r2_low = DecimalField()
    r3_high = DecimalField()
    r3_low = DecimalField()
    r4_high = DecimalField()
    r4_low = DecimalField()
    r5_high = DecimalField()
    r5_low = DecimalField()
    survey = ForeignKeyField(column_name='survey_pk', model=Survey,
                             backref='prof_tolerances', field='pk')
    version = IntegerField()

    class Meta:
        db_table = 'prof_tolerances'
        schema = 'platedb'


class Profilometry(BaseModel):
    comment = TextField(null=True)
    pk = PrimaryKeyField()
    plugging = ForeignKeyField(column_name='plugging_pk', model=Plugging,
                               backref='profilometries', field='pk')
    prof_tolerances = ForeignKeyField(column_name='prof_tolerances_pk', model=ProfTolerances,
                                      backref='profilometries', field='pk')
    timestamp = DateTimeField()

    class Meta:
        db_table = 'profilometry'
        schema = 'platedb'


class ProfMeasurement(BaseModel):
    number = IntegerField()
    pk = PrimaryKeyField()
    profilometry = ForeignKeyField(column_name='profilometry_pk',
                                   model=Profilometry, field='pk')
    r1 = DecimalField(null=True)
    r2 = DecimalField(null=True)
    r3 = DecimalField(null=True)
    r4 = DecimalField(null=True)
    r5 = DecimalField(null=True)
    timestamp = DateTimeField(null=True)

    class Meta:
        db_table = 'prof_measurement'
        schema = 'platedb'


class Test(BaseModel):
    label = TextField(null=True)
    pk = PrimaryKeyField()

    class Meta:
        db_table = 'test'
        schema = 'platedb'


class TileStatusHistory(BaseModel):
    comment = TextField()
    first_name = TextField(null=True)
    last_name = TextField(null=True)
    pk = PrimaryKeyField()
    tile = ForeignKeyField(column_name='tile_pk', model=Tile,
                           backref='tile_status_history', field='pk')
    tile_status = ForeignKeyField(column_name='tile_status_pk', model=TileStatus,
                                  backref='tile_status_history', field='pk')
    timestamp = DateTimeField()

    class Meta:
        db_table = 'tile_status_history'
        schema = 'platedb'


PlateSurveyThroughModel.set_model(PlateToSurvey)
PlateStatusThroughModel.set_model(PlateToPlateStatus)
PluggingInstrumentDeferred.set_model(PluggingToInstrument)
