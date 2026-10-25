import sys, csv
sys.path.insert(0, "/tmp/cr2/code")
from audit import config
H = float(sys.argv[1]); config.WORKFLOW_WINDOW_H = H
from audit import workflow
d = list(workflow.WorkflowModel.workflow_resources.__defaults__) if hasattr(workflow, "WorkflowModel") else None
for name in dir(workflow):
    obj = getattr(workflow, name)
    f = getattr(obj, "workflow_resources", None)
    if f and f.__defaults__: f.__defaults__ = (H,) + f.__defaults__[1:]
import main as M
from pathlib import Path
M.run(Path(sys.argv[3]), Path(sys.argv[2]), Path("/tmp/cr2/dataset"), True, None)
