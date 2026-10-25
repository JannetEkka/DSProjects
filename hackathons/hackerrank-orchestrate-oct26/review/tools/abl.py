import sys, importlib, csv
sys.path.insert(0, "/tmp/cr/code")
import main as M
from audit.engine import AuditEngine
from pathlib import Path
flag = sys.argv[1]; out = sys.argv[2]; req = sys.argv[3]
if flag != "none": setattr(AuditEngine, flag, True if flag.startswith("DISABLE") else False)
M.run(Path(req), Path(out), Path("/tmp/cr/dataset"), True, None)
