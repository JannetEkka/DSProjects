import sys
sys.path.insert(0, "/tmp/cr2/code")
from audit import config
setattr(config, sys.argv[1], type(getattr(config, sys.argv[1]))(float(sys.argv[2])))
import main as M
from pathlib import Path
M.run(Path(sys.argv[4]), Path(sys.argv[3]), Path("/tmp/cr2/dataset"), True, None)
