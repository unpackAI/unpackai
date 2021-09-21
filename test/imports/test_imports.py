from pathlib import Path
import sys

def test_import():
    """Test import of unpackai"""
    unpackai_root = Path(__file__).parent.parent.parent
    sys.path.append(str(unpackai_root))
    import unpackai
