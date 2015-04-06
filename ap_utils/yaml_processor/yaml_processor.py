import re
import types
from yaml import Loader, load, add_constructor
import codecs
import shutil
from tempfile import mkdtemp
import sys


__author__ = 'Alexander Pikovsky'


class _Loader(Loader):
    """Custom loader for Yaml config."""

    REPLACE_RE = re.compile(r'([^\w]+)')

    def __init__(self, *args, **kwargs):
        Loader.__init__(self, *args, **kwargs)

    def construct_mapping(self, node, deep=False):
        mapping = Loader.construct_mapping(self, node, deep)
        for key in mapping:
            if not isinstance(key, types.StringTypes): continue
            new = self.REPLACE_RE.sub('_', key)
            if new == key: continue
            mapping[new] = mapping.pop(key, None)
        return mapping


class YamlSection(object):
    """Simplifies access to a loaded yaml data (allows for access over properties)."""

    def __init__(self, raw_data):
        self.raw_data = raw_data

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        return self.get(item)

    def __setitem__(self, item, value):
        self.set(item, value)

    def __setattr__(self, item, value):
        if item == 'raw_data':
            object.__setattr__(self, item, value)
        else:
            self.set(item, value)

    def contains(self, name):
        return name in self.raw_data

    def get(self, name):
        """Returns given value or section."""
        if not name in self.raw_data:
            raise ValueError("Value '{0}' not found.".format(name))

        value = self.raw_data.get(name)
        return self._transform(value)

    def get_optional(self, name, default):
        """Returns given optional value or section."""
        value = self.raw_data.get(name, default)
        return self._transform(value)

    def set(self, item, value):
        self.raw_data[item] = value

    def get_section(self, name):
        """Returns given section."""
        section = self.get(name)
        if type(section) != YamlSection:
            raise ValueError("Value '{0}' is not a section.".format(name))

        return section

    def get_optional_section(self, name):
        """Returns given section."""
        section = self.get_optional(name, None)
        if section and type(section) != YamlSection:
            raise ValueError("Value '{0}' is not a section.".format(name))

        return section

    def _transform(self, value):
        if type(value) == dict:
            return YamlSection(value)
        elif type(value) == list:
            return [self._transform(item) for item in value]
        else:
            return value



class YamlProcessor(object):
    """
    Controls loading yaml file and creating/removing temporary directories. Must be used in a 'with' clause.

    Loaded data is available in self.data. Raw data accessor is available in self.raw_data.

    Supports following custom function calls embedded in the config file:
        random_temp_directory()

    Example:
        with YamlProcessor(my_yaml_file) as yaml_processor:
            data = yaml_processor.data
    """

    def __init__(self, config_file_path, silent=False):
        self.temp_dirs_to_remove = set()
        self.config_file_path = config_file_path
        self.silent = silent

    def __enter__(self):
        """
        Actually loads and parses the config file.
        """

        def do_unpack(head, *tail):
            return head, tail

        def random_temp_directory(remove=True, prefix='optobee_tmp'):
            """Custom embeddable function that creates a temporary directory."""
            dir = mkdtemp(prefix=prefix)
            if remove.lower() == 'true':
                self.temp_dirs_to_remove.add(dir)
            return dir

        custom_functions = {
            'random_temp_directory': random_temp_directory
        }

        def call_function_constructor(loader, node):
            parameter_re = re.compile(r'\s*([\w]+)\s*=\s*([\w]+)\s*')
            function_name = loader.construct_scalar(node)
            function_name, params = do_unpack(*function_name.split(','))
            param_dict = {}
            for param in params:
                match = re.match(parameter_re, param.encode('utf-8'))
                if not match: continue
                param_dict[match.group(1)] = match.group(2)

            return custom_functions[function_name](**param_dict)

        #add constructor to process custom functions embedded into yaml
        add_constructor(u'!call', call_function_constructor)

        with codecs.open(self.config_file_path, mode='r', encoding='utf-8') as input:
            #load data
            self.raw_data = load(input, _Loader)
            self.data = YamlSection(self.raw_data)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Performs clean-up."""

        #remove all temp dirs created by random_temp_directory()
        for dir in self.temp_dirs_to_remove:
            try:
                if not self.silent:
                    print 'Removing temp directory "{0}"'.format(dir)
                shutil.rmtree(dir)
            except Exception, e:
                print >>sys.stderr, 'Failed removing temp directory "{0}": {1}'.format(dir, e.message)

