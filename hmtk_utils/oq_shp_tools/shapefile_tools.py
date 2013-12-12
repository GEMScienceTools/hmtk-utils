# coding=utf-8
#
# LICENSE
#
# Copyright (c) 2010-2013, GEM Foundation, G. Weatherill, M. Pagani,
# D. Monelli.
#
# The Hazard Modeller's Toolkit is free software: you can redistribute
# it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>
#
# DISCLAIMER
# 
# The software Hazard Modeller's Toolkit (hmtk) provided herein
# is released as a prototype implementation on behalf of
# scientists and engineers working within the GEM Foundation (Global
# Earthquake Model).
#
# It is distributed for the purpose of open collaboration and in the
# hope that it will be useful to the scientific, engineering, disaster
# risk and software design communities.
#
# The software is NOT distributed as part of GEM’s OpenQuake suite
# (http://www.globalquakemodel.org/openquake) and must be considered as a
# separate entity. The software provided herein is designed and implemented
# by scientific staff. It is not developed to the design standards, nor
# subject to same level of critical review by professional software
# developers, as GEM’s OpenQuake software suite.
#
# Feedback and contribution to the software is welcome, and can be
# directed to the hazard scientific staff of the GEM Model Facility
# (hazard@globalquakemodel.org).
#
# The Hazard Modeller's Toolkit (hmtk) is therefore distributed WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# The GEM Foundation, and the authors of the software, assume no
# liability for use of the software.
#

import sys
from osgeo import ogr


def _add_string_field(layer, field_name, length=32):
    """
    :parameter layer:
        An instance of the class
    :parameter str field_name:
        An instance of the class
    """
    field_defn = ogr.FieldDefn(field_name, ogr.OFTString)
    field_defn.SetWidth(length)
    if layer.CreateField(field_defn) != 0:
        print "Creating "+field_name+" field failed.\n"
        sys.exit(1)
    return layer


def _add_integer_field(layer, field_name):
    """
    :parameter layer:
        An instance of the class
    :parameter str field_name:
        An instance of the class
    """
    field_defn = ogr.FieldDefn(field_name, ogr.OFTInteger)
    if layer.CreateField(field_defn) != 0:
        print "Creating "+field_name+" field failed.\n"
        sys.exit(1)
    return layer


def _add_real_field(layer, field_name):
    """
    :parameter layer:
        An instance of the class
    :parameter str field_name:
        An instance of the class
    """
    field_defn = ogr.FieldDefn(field_name, ogr.OFTReal)
    if layer.CreateField(field_defn) != 0:
        print "Creating "+field_name+" field failed.\n"
        sys.exit(1)
    return layer


def add_attributes(lyr, attributes):
    """
    :parameter lyr:
    :parameter attributes:
    """
    for att in attributes:
        if att['type'] == 'String':
            lyr = _add_string_field(lyr, att['name'], att['len'])
        elif att['type'] == 'Real':
            lyr = _add_real_field(lyr, att['name'])
        elif att['type'] == 'Integer':
            lyr = _add_integer_field(lyr, att['name'])
        else:
            pass
    return lyr


def create_datasource(shp_file_path):
    """
    :parameter str shp_file_path:
        Path of the folder where the shapefile will be created
    """
    # Instantiate the driver to
    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName(driverName)
    if drv is None:
        print "%s driver not available.\n" % driverName
        sys.exit(1)
    # Open the shapefile
    ds = drv.CreateDataSource(shp_file_path)
    if ds is None:
        print "Creation of output file failed.\n"
        sys.exit(1)
    return ds
