#!c:\Users\madru\OneDrive - UPM\OneDrive - Universidad Politécnica de Madrid\SatChange\.venv\Scripts\python.exe

import sys

from osgeo.gdal import deprecation_warn

# import osgeo_utils.rgb2pct as a convenience to use as a script
from osgeo_utils.rgb2pct import *  # noqa
from osgeo_utils.rgb2pct import main

deprecation_warn("rgb2pct")
sys.exit(main(sys.argv))
