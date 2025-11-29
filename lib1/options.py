# début du "options" version "5"
import sys

class Options:
    def __init__(self):
        self.mode_simulation = True
        self.chemin_lib = '/lib1' if self._lib_exists() else '/'
        self._ajuster_path()

    def _lib_exists(self):
        try:
            open('/lib1/options.py').close()
            return True
        except OSError:
            return False

    def _ajuster_path(self):
        if self.chemin_lib not in sys.path:
            sys.path.insert(0, self.chemin_lib)

version = ('options.py', 5)
print(f"Chargement module: {version} → lib={Options().chemin_lib}")
# fin du "options" version "5"