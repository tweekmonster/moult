from __future__ import unicode_literals

from .compat import PY3


class PyModule(object):
    def __init__(self, name, version, location='', missing=False):
        self.name = name
        self.import_names = [name]
        self.version = version
        self.is_scan = version in ('SCRIPT', 'MODULE', 'DIRECTORY')
        self.frameworks = []
        self.location = location
        self._dependencies = []  # The string list of dependencies
        self.dependencies = []
        self.dependants = []
        self._dependants = []  # This is a shadow dependant list for the turtles
        self.installed_scripts = []
        self.installed_files = []
        self.user = False
        self.local = False
        self.hidden = False
        self.missing = missing

    def set_import_names(self, names):
        self.import_names = [x.replace('/', '.') for x in names]

    def add_framework(self, framework):
        if framework not in self.frameworks:
            self.frameworks.append(framework)

    def add_dependency(self, dep):
        if dep not in self.dependencies:
            if dep.is_scan:
                self.dependencies.insert(0, dep)
            else:
                self.dependencies.append(dep)

    def remove_dependency(self, dep):
        if dep in self.dependencies:
            self.dependencies.remove(dep)

    def add_dependant(self, dep):
        if dep not in self.dependants:
            if dep.is_scan:
                self.dependants.insert(0, dep)
                self._dependants.insert(0, dep)
            else:
                self.dependants.append(dep)
                self._dependants.append(dep)

    def remove_dependant(self, dep):
        if dep in self._dependants:
            self._dependants.remove(dep)

    def restore_dependants(self):
        self._dependants = self.dependants[:]

    def __hash__(self):
        return hash((self.name, self.version))

    def __unicode__(self):
        if self.is_scan:
            fmt = '{name} [{version}]'
        else:
            fmt = '{name} ({version})'
        return fmt.format(name=self.name, version=self.version)

    def __str__(self):
        if PY3:
            return self.__unicode__()
        return self.__unicode__().encode('utf8')

    def __bytes__(self):
        return self.__unicode__().encode('utf8')

    def __repr__(self):
        r = '<PyModule {}>'.format(self.__unicode__())
        if PY3:
            return r
        return r.encode('utf8')
