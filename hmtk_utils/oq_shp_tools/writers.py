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
Module for parsing nrml and create preformatted shapefiles
"""

import sys
import re

import osgeo.ogr as ogr
import osgeo.osr as osr

import shapefile_tools as shpt

from openquake.nrmllib.hazard.parsers import SourceModelParser
from openquake.nrmllib.models import AreaSource, TGRMFD, SourceModel
from openquake.nrmllib.models import IncrementalMFD

MAPPING_GENERAL = {'src_id': 'id', 'src_name': 'name', 'tect_reg': 'trt',
                   'mag_scal_r': 'mag_scale_rel',
                   'rup_asp_ra': 'rupt_aspect_ratio'}

MAPPING_MFD_TGR = {'a_value': 'a_val', 'b_value': 'b_val',
                   'min_mag': 'min_mag', 'max_mag': 'max_mag'}

MAPPING_MFD_INCR = {'min_mag': 'min_mag', 'bin_width': 'bin_width'}

MAPPING_POLY_GEOM = {'upp_seismo': 'upper_seismo_depth',
                     'low_seismo': 'lower_seismo_depth'}

MAPPING_NPD = {'weight': 'probability', 'strike': 'strike',
               'dip': 'dip', 'rake': 'rake'}

MAPPING_HDD = {'hdd_w': 'probability', 'hdd_d': 'depth'}


def _get_max_nodal_plane_number(sourceModel):
    """
    This finds the maximum number of nodal planes and maximum number of
    hypocentral depths used in a source model.

    :parameter sourceModel:
        An instance of :class:`SourceModel`:
    :returns:
        Three integers, the maximum number of nodal planes used assigned to a
        single source and the maximum number of hypocentral depths assigned
        to a source.
    """
    num = 0
    numhd = 0
    cnt = 0
    numbins = 0
    for src in sourceModel.sources:

        if isinstance(src, AreaSource):
            num = len(src.nodal_plane_dist) if \
                len(src.nodal_plane_dist) > num else num
            numhd = len(src.hypo_depth_dist) if \
                len(src.hypo_depth_dist) > numhd else numhd

            if isinstance(src.mfd, IncrementalMFD):
                numbins = len(src.mfd.occur_rates) if \
                    len(src.mfd.occur_rates) > numhd else numhd

            cnt += 1
    print 'The model contains %d area sources' % (cnt)
    return num, numhd, numbins


def _get_polygon(areasrc):
    """
    This extracts the lons and lats from a WKT string which describes a
    polygon

    :parameter string areasrc:
        A WKT string descibing a polygon geometry
    :returns:
        Two lists containing longitudes and latitudes, respectively
    """

    str = areasrc.geometry.wkt
    str = re.sub('POLYGON\(\(', '', str)
    str = re.sub('\)\)', '', str)
    aa = re.split('\,', str)
    lons = []
    lats = []
    for str in aa:
        bb = re.split('\s+', re.sub('^\s+', '', str))
        lons.append(float(bb[0]))
        lats.append(float(bb[1]))
    return lons, lats


def _get_area_incmfd_attr(max_np, max_hd, max_bins):
    """
    Fix the set of attributes used to describe an area source with an
    incremental magnitude-frequency distribution

    :parameter int max_np:
        Maximum number of nodal planes
    :parameter int max_hd:
        Maximum number of hypocentral depths
    :parameter int max_bins:
        Maximum number of bins
    :returns:
        A dictionary specifying the list of fields in the attribute table and
        their properties.
    """

    att = []
    att.append({'name': 'src_id', 'type': 'String', 'len': 10})
    att.append({'name': 'src_name', 'type': 'String', 'len': 30})
    att.append({'name': 'tect_reg', 'type': 'String', 'len': 30})
    att.append({'name': 'upp_seismo', 'type': 'Real'})
    att.append({'name': 'low_seismo', 'type': 'Real'})
    att.append({'name': 'mag_scal_r', 'type': 'String', 'len': 15})
    att.append({'name': 'rup_asp_ra', 'type': 'Real'})
    att.append({'name': 'mfd_type', 'type': 'String', 'len': 20})

    att.append({'name': 'min_mag', 'type': 'Real'})
    att.append({'name': 'bin_width', 'type': 'Real'})
    att.append({'name': 'num_bins', 'type': 'Integer'})
    for i in range(1, max_bins+1):
        lab = 'or_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})

    att.append({'name': 'num_npd', 'type': 'Integer'})
    for i in range(1, max_np+1):
        lab = 'weight_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'strike_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'rake_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'dip_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})

    att.append({'name': 'num_hdd', 'type': 'Integer'})
    for i in range(1, max_hd+1):
        lab = 'hdd_d_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'hdd_w_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})

    return att


def _get_area_tgrmfd_attr(max_np, max_hd):
    """
    Fix the set of attributes used to describe an area source with a
    truncated GR magnitude-frequency distribution

    :parameter int max_np:
        Maximum number of nodal planes
    :parameter int max_hd:
        Maximum number of hypocentral depths
    :returns:
        A dictionary specifying the list of fields in the attribute table and
        their properties.
    """

    att = []
    att.append({'name': 'src_id', 'type': 'String', 'len': 10})
    att.append({'name': 'src_name', 'type': 'String', 'len': 30})
    att.append({'name': 'tect_reg', 'type': 'String', 'len': 30})
    att.append({'name': 'upp_seismo', 'type': 'Real'})
    att.append({'name': 'low_seismo', 'type': 'Real'})
    att.append({'name': 'mag_scal_r', 'type': 'String', 'len': 15})
    att.append({'name': 'rup_asp_ra', 'type': 'Real'})

    att.append({'name': 'mfd_type', 'type': 'String', 'len': 20})
    att.append({'name': 'min_mag', 'type': 'Real'})
    att.append({'name': 'max_mag', 'type': 'Real'})
    att.append({'name': 'a_value', 'type': 'Real'})
    att.append({'name': 'b_value', 'type': 'Real'})

    att.append({'name': 'num_npd', 'type': 'Integer'})
    for i in range(1, max_np+1):
        lab = 'weight_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'strike_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'rake_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'dip_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})

    att.append({'name': 'num_hdd', 'type': 'Integer'})
    for i in range(1, max_hd+1):
        lab = 'hdd_d_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
        lab = 'hdd_w_%d' % (i)
        att.append({'name': lab, 'type': 'Real'})
    return att


def _write_area_source_incmfd(src, lyr, max_np, max_hd):
    """
    This creates a shapefile containing the area sources with a truncated GR
    magnitude-frequency distribution included in a :class:`SourceModel`
    instance.

    :parameter src:
        An instance of :class:`AreaSource`
    :parameter lyr:
        A layer
    :parameter int max_np:
        Maximum number of nodal planes
    :parameter int max_hd:
        Maximum number of hypocentral depths
    """

    # Create the geometry
    lons, lats = _get_polygon(src)
    feat = ogr.Feature(lyr.GetLayerDefn())
    oring = ogr.Geometry(ogr.wkbLinearRing)
    for lon, lat in zip(lons, lats):
        oring.AddPoint(lon, lat, 0.0)
    oring.CloseRings()

    # Set standard parameters such as name, id, tectonic region
    for key in MAPPING_GENERAL.keys():
        feat.SetField(key, getattr(src, MAPPING_GENERAL[key]))

    # Set mfd parameters
    feat.SetField('mfd_type', 'IncrementalMFD')
    for key in MAPPING_MFD_INCR.keys():
        feat.SetField(key, getattr(src.mfd, MAPPING_MFD_INCR[key]))

    for i, occ in enumerate(src.mfd.occur_rates):
        tmp_str = 'or_%d' % (i+1)
        feat.SetField(tmp_str, occ)

    # Set geometry parameters
    for key in MAPPING_POLY_GEOM.keys():
        feat.SetField(key, getattr(src.geometry, MAPPING_POLY_GEOM[key]))

    # Set nodal plane distribution
    cnt = 1
    feat.SetField('num_npd', int(max_np))
    for npd in src.nodal_plane_dist:
        for key in MAPPING_NPD:
            tmp_str = '%s_%d' % (key, cnt)
            if key == 'weight':
                value = float(getattr(npd, MAPPING_NPD[key]))
            else:
                value = getattr(npd, MAPPING_NPD[key])
            feat.SetField(tmp_str, value)
        cnt += 1

    # Set hypocentral plane distribution
    cnt = 1
    feat.SetField('num_hdd', int(max_hd))
    for hdd in src.hypo_depth_dist:
        for key in MAPPING_HDD:
            tmp_str = '%s_%d' % (key, cnt)
            if key == 'hdd_w':
                value = float(getattr(hdd, MAPPING_HDD[key]))
            else:
                value = getattr(hdd, MAPPING_HDD[key])
            feat.SetField(tmp_str, value)
        cnt += 1

    # Creating the polygon and adding the geometry
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(oring)
    feat.SetGeometry(polygon)

    if lyr.CreateFeature(feat) != 0:
        print "Failed to create feature in shapefile.\n"
        sys.exit(1)

    polygon.Destroy()
    feat.Destroy()


def _write_area_source_tgrmfd(src, lyr, max_np, max_hd):
    """
    This creates a shapefile containing the area sources with a truncated GR
    magnitude-frequency distribution included in a :class:`SourceModel`
    instance.

    :parameter src:
        An instance of :class:`AreaSource`
    :parameter lyr:
        A layer
    :parameter int max_np:
        Maximum number of nodal planes
    :parameter int max_hd:
        Maximum number of hypocentral depths
    """

    # Create feature
    feat = ogr.Feature(lyr.GetLayerDefn())

    # Create the geometry
    lons, lats = _get_polygon(src)
    oring = ogr.Geometry(ogr.wkbLinearRing)
    for lon, lat in zip(lons, lats):
        oring.AddPoint(lon, lat, 0.0)
    oring.CloseRings()

    # Set standard parameters such as name, id, tectonic region
    for key in MAPPING_GENERAL.keys():
        feat.SetField(key, getattr(src, MAPPING_GENERAL[key]))

    # Set mfd parameters
    feat.SetField('mfd_type', 'truncGutenbergRichterMFD')
    for key in MAPPING_MFD_TGR.keys():
        feat.SetField(key, getattr(src.mfd, MAPPING_MFD_TGR[key]))

    # Set geometry parameters
    for key in MAPPING_POLY_GEOM.keys():
        feat.SetField(key, getattr(src.geometry, MAPPING_POLY_GEOM[key]))

    # Set nodal plane distribution
    cnt = 1
    feat.SetField('num_npd', int(max_np))
    for npd in src.nodal_plane_dist:
        for key in MAPPING_NPD:
            tmp_str = '%s_%d' % (key, cnt)
            if key == 'weight':
                value = float(getattr(npd, MAPPING_NPD[key]))
            else:
                value = getattr(npd, MAPPING_NPD[key])
            feat.SetField(tmp_str, value)
        cnt += 1

    # Set hypocentral plane distribution
    cnt = 1
    feat.SetField('num_hdd', int(max_hd))
    for hdd in src.hypo_depth_dist:
        for key in MAPPING_HDD:
            tmp_str = '%s_%d' % (key, cnt)
            if key == 'hdd_w':
                value = float(getattr(hdd, MAPPING_HDD[key]))
            else:
                value = getattr(hdd, MAPPING_HDD[key])
            feat.SetField(tmp_str, value)
        cnt += 1

    # Creating the polygon and adding the geometry
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(oring)
    feat.SetGeometry(polygon)

    if lyr.CreateFeature(feat) != 0:
        print "Failed to create feature in shapefile.\n"
        sys.exit(1)

    polygon.Destroy()
    feat.Destroy()


def _create_area_source_incmfd_shapefile(shapefile_path, max_np, max_hd,
                                         max_bins):
    """
    Create a shapefile which contains area sources with a truncated GR mfd

    :parameter string shapefile_path:
        Path to the folder where the shapefile will be created
    :parameter int max_np:
        Maximum number of nodal planes
    :parameter int max_hd:
        Maximum number of hypocentral depths
    :returns:
        Returns an updated data set
    """

    spatialReference = osr.SpatialReference()
    spatialReference.SetWellKnownGeogCS('WGS84')

    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName(driverName)
    if drv is None:
        print "%s driver not available.\n" % driverName
        sys.exit(1)

    layer_name = "as_incr"
    ds = drv.CreateDataSource(shapefile_path+layer_name+".shp")
    if ds is None:
        print "Creation of output file failed.\n"
        sys.exit(1)

    # Create the layer
    lyr = ds.CreateLayer(layer_name,
                         spatialReference,
                         ogr.wkbPolygon)
    if lyr is None:
        print "Layer creation failed.\n"
        sys.exit(1)

    # Add attributes definition to this layer
    attributes = _get_area_incmfd_attr(max_np, max_hd, max_bins)
    lyr = shpt.add_attributes(lyr, attributes)
    del attributes

    return ds


def _create_area_source_tgrmfd_shapefile(shapefile_path, max_np, max_hd):
    """
    Create a shapefile which contains area sources with a truncated GR mfd

    :parameter string shapefile_path:
        Path to the folder where the shapefile will be created
    :parameter int max_np:
        Maximum number of nodal planes
    :parameter int max_hd:
        Maximum number of hypocentral depths
    :returns:
        Returns an updated data set
    """

    spatialReference = osr.SpatialReference()
    spatialReference.SetWellKnownGeogCS('WGS84')

    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName(driverName)
    if drv is None:
        print "%s driver not available.\n" % driverName
        sys.exit(1)

    layer_name = "as_trgr"
    ds = drv.CreateDataSource(shapefile_path+layer_name+".shp")
    if ds is None:
        print "Creation of output file failed.\n"
        sys.exit(1)

    # Create the layer
    lyr = ds.CreateLayer(layer_name,
                         spatialReference,
                         ogr.wkbPolygon)
    if lyr is None:
        print "Layer creation failed.\n"
        sys.exit(1)

    # Add attributes definition to this layer
    attributes = _get_area_tgrmfd_attr(max_np, max_hd)
    lyr = shpt.add_attributes(lyr, attributes)
    del attributes

    return ds


def write_shps(nrml_data, out_directory):
    """
    This creates a set of shapefiles each one containing a set of sources
    with uniform characteristics.

    :parameter nrml_data:
        The name of the file containing the model to be tranformed into a
        shapefile or an instance of :class:`SourceModel`
    :parameter out_directory:
        The directory where all the shapefiles will be created
    """

    if isinstance(nrml_data, SourceModel):
        source_model = nrml_data
    else:
        pass

    # Find the maximum number of nodal planes and the maximum number of
    # hypocentral depths used for a source
    parser = SourceModelParser(nrml_data)
    source_model = parser.parse()
    max_np, max_hd, max_bins = _get_max_nodal_plane_number(source_model)

    # ---- Create shapefile: Area sources with incremental mfd
    data_set_as_incr = _create_area_source_incmfd_shapefile(out_directory,
                                                            max_np, max_hd,
                                                            max_bins)
    parser = SourceModelParser(nrml_data)
    source_model1 = parser.parse()

    lyr = data_set_as_incr.GetLayer()
    for source in source_model1.sources:
        # Add area sources
        if isinstance(source, AreaSource):
            if isinstance(source.mfd, IncrementalMFD):
                _write_area_source_incmfd(source, lyr, max_np, max_hd)

    data_set_as_incr.Destroy()
    del lyr
    del parser, source_model1

    # ---- Create the shapefile: area sources with truncated GR
    data_set_as_trgr = _create_area_source_tgrmfd_shapefile(out_directory,
                                                            max_np, max_hd)
    parser = SourceModelParser(nrml_data)
    source_model1 = parser.parse()

    # Get the layer from the dataset
    lyr = data_set_as_trgr.GetLayer()

    for source in source_model1.sources:
        # Add area sources
        if isinstance(source, AreaSource):
            if isinstance(source.mfd, TGRMFD):
                _write_area_source_tgrmfd(source, lyr, max_np, max_hd)
    del data_set_as_trgr
