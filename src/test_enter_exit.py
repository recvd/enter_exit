import os
from pathlib import Path

import enter_exit

root_path = Path(os.getcwd()).parent
data_path = root_path / root_path / "data" / "raw" / "nets_philly_ACT_FFA_WAL.csv"
