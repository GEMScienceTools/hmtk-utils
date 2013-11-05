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
"""

import os
import unittest

from hmtk_utils.oq_shp_tools.parsers import parse_area_source_shp


class ParsersTestCase(unittest.TestCase):
    """
    """
    BASE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'dat')

    def setUp(self):
        """
        Fix the name of the sample shapefile

        """

        flnme = 'oq_area_source_template.shp'
        self.filename = os.path.join(self.BASE_DATA_PATH, flnme)

    def test_raise_ioerror(self):
        """
        This checks that an excepion is raise when the shapefile doesn't exist
        """

        filename = os.path.join(self.BASE_DATA_PATH, 'pippo.shp')
        self.assertRaises(IOError, parse_area_source_shp, filename)

    def test_parse_area_source_shp(self):
        """
        This tests that the parameters in the shapefile attribute table are
        correct.
        """

        # Get the list of area sources included in the shapefile
        source_list = parse_area_source_shp(self.filename)

        # Check the parameters of the first source
        src = source_list[0]
        self.assertTrue(src.id == '1')
        self.assertTrue(src.name == 'Sample OQ area source')
        self.assertTrue(src.trt == 'Active Shallow Crust')
        self.assertTrue(src.mag_scale_rel == 'WC1994')
        self.assertTrue(src.rupt_aspect_ratio == 2.0)
        # Check mfd
        self.assertTrue(src.mfd.a_val == 3.001)
        self.assertTrue(src.mfd.b_val == 1.001)
        # Check nodal plane
        self.assertTrue(src.nodal_plane_dist[0].rake == 179.9)
        self.assertTrue(src.nodal_plane_dist[0].strike == 359.9)
        self.assertTrue(src.nodal_plane_dist[0].dip == 89.99)
        self.assertTrue(src.nodal_plane_dist[0].probability == 1.0)
        # Check nodal plane
        self.assertTrue(src.hypo_depth_dist[0].depth == 10.0)
        self.assertTrue(src.hypo_depth_dist[0].probability == 1.0)
        # Check nodal plane
        self.assertTrue(src.geometry.upper_seismo_depth == 0.0)
        self.assertTrue(src.geometry.lower_seismo_depth == 20.0)
