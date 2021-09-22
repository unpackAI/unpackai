from pathlib import Path
import sys

from IPython.core import magic

# We are temporarily patching "register_cell_magic"
# because it leads to errors in tests otherwise
magic.register_cell_magic = lambda fn: fn

# We add root dir in sys.path to be able to import "unpackai" in our tests
unpackai_root = Path(__file__).parent.parent.parent
sys.path.append(str(unpackai_root))