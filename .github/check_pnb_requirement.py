import sys, zipfile
from packaging.requirements import Requirement

version, wheel = sys.argv[1:3]
with zipfile.ZipFile(wheel) as z:
    meta = z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode()
req = next(Requirement(l.split(':', 1)[1]) for l in meta.splitlines()
           if l.startswith('Requires-Dist:') and Requirement(l.split(':', 1)[1]).name == 'pynotebook')
if version not in req.specifier:
    sys.exit("pnb requires %s, but pynotebook is %s" % (req, version))
print("ok:", req, "accepts", version)
