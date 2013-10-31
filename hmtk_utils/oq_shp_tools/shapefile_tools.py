import sys
from osgeo import ogr

def add_string_field(layer,field_name,length=32): 
    """
    :parameter layer:
        An instance of the class 
    :parameter str field_name:
        An instance of the class 
    """
    field_defn = ogr.FieldDefn(field_name, ogr.OFTString )
    field_defn.SetWidth(length)
    if layer.CreateField(field_defn) != 0:
        print "Creating "+field_name+" field failed.\n"
        sys.exit(1)
    return layer

def add_integer_field(layer,field_name): 
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

def add_real_field(layer,field_name): 
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
            lyr = add_string_field(lyr,att['name'],att['len'])
        elif att['type'] == 'Real': 
            lyr = add_real_field(lyr,att['name'])
        elif att['type'] == 'Integer': 
            lyr = add_integer_field(lyr,att['name'])
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
