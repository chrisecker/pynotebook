"""
Smoke test of an installed Linux package, run by the job "linux" in a
container: pnb uses the included pynotebook and cerealizer, loads the
example notebooks and starts.
"""

import glob, subprocess, sys

sys.path.insert(0, '/usr/share/pnb')  # as packaging/linux/pnb
import cerealizer, pynotebook, wx

for module in (cerealizer, pynotebook):
    assert module.__file__.startswith('/usr/share/pnb/'), module
from pynotebook import graphics, cerealizerformat
graphics.register_classes()
examples = sorted(glob.glob('/usr/share/doc/pnb/examples/*.pnb'))
assert examples
for name in examples:
    assert len(cerealizerformat.loads(open(name, 'rb').read())), name

# pnb runs until the window is closed: still alive after 5 s means it started
try:
    subprocess.run(['xvfb-run', '-a', 'pnb', examples[0]], timeout=5,
                   check=True, capture_output=True, text=True)
    sys.exit('pnb exited early')
except subprocess.TimeoutExpired:
    pass
print('pnb ok, wx', wx.version(), 'examples', len(examples))
