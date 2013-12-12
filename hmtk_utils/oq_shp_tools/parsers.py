# -*- coding: utf-8 -*-
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


"""
Module for parsing preformatted shapefiles containing information about
OQ-engine source typologies.
"""

import ogr
import os

from decimal import Decimal

from openquake.nrmllib.models import AreaSource, TGRMFD, NodalPlane, \
    HypocentralDepth, AreaGeometry


def _get_area_geometry(feature, only_geom=False):
    """
    This function gets the geometry of a polygon feature

    :parameter feature:
    :parameter only_geom:

    :returns:
        An instance of the :class:`AreaGeometry` defined in the oq-nrmllib
        models.py module
    """
    geometry = feature.GetGeometryRef()
    pts = geometry.GetGeometryRef(0)
    points = []
    wkt_str = 'POLYGON(('
    for point in xrange(pts.GetPointCount()):
        points.append((pts.GetX(point), pts.GetY(point)))
        wkt_str += '%.5f %.5f,' % (pts.GetX(point), pts.GetY(point))
    wkt_str += '))'

    if not only_geom:
        upp_seismo = feature.GetField('upp_seismo')
        low_seismo = feature.GetField('low_seismo')
    else:
        upp_seismo = 0.0
        low_seismo = 1.0

    # Create the area geometry object
    area_geom = AreaGeometry(wkt=wkt_str, upper_seismo_depth=upp_seismo,
                             lower_seismo_depth=low_seismo)

    return area_geom


def _get_hypo_depth_distr(feature):
    """
    Get information about the hypocentral depth distribution contained in the
    shapefile attribute table for the current feature

    :returns:
        A list of :class:`HypocentralDepth` instances defined in the oq-nrmllib
        models.py module

    """

    nodal_plane_list = []
    num_hdd = feature.GetField('num_hdd')
    for i in range(0, num_hdd):
        idx = i + 1
        depth = feature.GetField('hdd_d_%d' % (idx))
        prob = feature.GetField('hdd_w_%d' % (idx))
        if depth is not None:
            nodal_plane_list.append(HypocentralDepth(probability=prob,
                                                     depth=depth))
        else:
            print depth

    return nodal_plane_list


def _get_nodal_plane_distr(feature):
    """
    Get information about the nodal plane distribution contained in the
    shapefile attribute table for the current feature

    :returns:
        A list of :class:`NodalPlane` instances

    """

    nodal_plane_list = []
    num_npd = feature.GetField('num_npd')
    for i in range(0, num_npd):
        idx = i + 1
        strike = feature.GetField('strike_%d' % (idx))
        dip = feature.GetField('dip_%d' % (idx))
        rake = feature.GetField('rake_%d' % (idx))
        prob = feature.GetField('weight_%d' % (idx))

        nodal_plane_list.append(NodalPlane(probability=prob, strike=strike,
                                           dip=dip, rake=rake))
    return nodal_plane_list


def _get_truncGR_from_feature(feature):
    """
    Get fields from the attribute table and created a :class:`TGRMFD`
    instance

    :returns:
        A :class:`TGRMFD` instance

    """

    a_val = feature.GetField('a_value')
    b_val = feature.GetField('b_value')
    min_mag = feature.GetField('min_mag')
    max_mag = feature.GetField('max_mag')
    return TGRMFD(a_val=a_val, b_val=b_val, min_mag=min_mag, max_mag=max_mag)


def parse_area_source_shp(filename, only_geom=False, config={}):
    """
    Parse an preformatted shapefile containing information about area
    sources

    :parameter str filename:
        Name of the shapefile to be parsed
    :parameter dict config:
        A dictionary whose keys corresponds to the attributes of a
        :class:`AreaSource` instance. These attributes are assigned
        to each parsed area source.
    :parameter bool only_geometry:
        When True only geometry of sources is taken from the shapefile

    :returns:
        A list of :class:`AreaSource` istances

    """

    # Check if the input shapefile exists
    if not os.path.isfile(filename):
        raise IOError("This shapefile doesn't exists")

    # Open the shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    data_source = driver.Open(filename, 0)

    # Check that the input shapefile can be opened
    if data_source is None:
        raise IOError("This shapefile cannot be opened")

    layer = data_source.GetLayer()

    sourcelist = []
    feature = layer.GetNextFeature()
    cnt = 0
    while feature:
        print cnt

        # Create the area source geometry
        geometry = _get_area_geometry(feature, only_geom)

        if not only_geom:

            # General parameters
            src_id = feature.GetField('src_id')
            name = feature.GetField('src_name')
            tect_reg = feature.GetField('tect_reg')

            # Geometry parameters
            mag_scal = feature.GetField('mag_scal_r')
            rup_asp_ratio = feature.GetField('rup_asp_ra')

            # Computing the MFD distribution
            mfd_type = feature.GetField('mfd_type')
            if mfd_type == 'truncGutenbergRichterMFD':
                mfd = _get_truncGR_from_feature(feature)

            # Create the nodal plane distribution
            nodal_planes_list = _get_nodal_plane_distr(feature)

            # Create the hypocentral depth distribution
            hypo_depth_list = _get_hypo_depth_distr(feature)

            # Append the AreaSource to the list of sources
            areasource = AreaSource(id=src_id,
                                    name=name,
                                    geometry=geometry,
                                    trt=tect_reg,
                                    mag_scale_rel=mag_scal,
                                    rupt_aspect_ratio=rup_asp_ratio,
                                    mfd=mfd,
                                    nodal_plane_dist=nodal_planes_list,
                                    hypo_depth_dist=hypo_depth_list)

        else:

            src_id = 'Null'
            name = 'Null'
            tect_reg = 'Null'
            mag_scal = 'Null'
            rup_asp_ratio = 0.1
            mfd = TGRMFD(a_val=1.0, b_val=1.0, min_mag=4.0, max_mag=4.1)
            nodal_planes_list = [NodalPlane(probability=Decimal(1.0),
                                            strike=0.0,
                                            dip=0.0,
                                            rake=0.0)]
            hypo_depth_list = [HypocentralDepth(probability=1.0, depth=1.0)]

            # Append the AreaSource to the list of sources
            areasource = AreaSource(id=src_id,
                                    name=name,
                                    geometry=geometry,
                                    trt=tect_reg,
                                    mag_scale_rel=mag_scal,
                                    rupt_aspect_ratio=rup_asp_ratio,
                                    mfd=mfd,
                                    nodal_plane_dist=nodal_planes_list,
                                    hypo_depth_dist=hypo_depth_list)

        sourcelist.append(areasource)

        # Get the next feature
        feature = layer.GetNextFeature()

        cnt += 1

    return sourcelist
