from __future__ import unicode_literals

import io
import re
import ast

from .exceptions import MoultScannerError
from .compat import str_
from . import utils, log


_fallback_re = re.compile(r'''
    ^[\ \t]*(
        from[\ \t]+[\w\.]+[\ \t]+import\s+\([\s\w,]+\)|
        from[\ \t]+[\w\.]+[\ \t]+import[\ \t\w,]+|
        import[\ \t]+\([\s\w,]+\)|
        import[\ \t]+[\ \t\w,]+
    )
''', re.VERBOSE | re.MULTILINE | re.UNICODE)


def ast_value(val, scope, return_name=False):
    '''Recursively parse out an AST value.  This makes no attempt to load
    modules or reconstruct functions on purpose.  We do not want to
    inadvertently call destructive code.
    '''
    # :TODO: refactor the hell out of this
    try:
        if isinstance(val, (ast.Assign, ast.Delete)):
            if hasattr(val, 'value'):
                value = ast_value(val.value, scope)
            else:
                value = None
            for t in val.targets:
                name = ast_value(t, scope, return_name=True)
                if isinstance(t.ctx, ast.Del):
                    if name in scope:
                        scope.pop(name)
                elif isinstance(t.ctx, ast.Store):
                    scope[name] = value
            return
        elif isinstance(val, ast.Expr) and isinstance(val.value, ast.Name):
            return ast_value(val.value)

        if isinstance(val, ast.Name):
            if isinstance(val.ctx, ast.Load):
                if val.id == 'None':
                    return None
                elif val.id == 'True':
                    return True
                elif val.id == 'False':
                    return False

                if val.id in scope:
                    return scope[val.id]

                if return_name:
                    return val.id
            elif isinstance(val.ctx, ast.Store):
                if return_name:
                    return val.id
            return None

        if isinstance(val, ast.Subscript):
            toslice = ast_value(val.value, scope)
            theslice = ast_value(val.slice, scope)
            return toslice[theslice]
        elif isinstance(val, ast.Index):
            return ast_value(val.value, scope)
        elif isinstance(val, ast.Slice):
            lower = ast_value(val.lower)
            upper = ast_value(val.upper)
            step = ast_value(val.step)
            return slice(lower, upper, step)

        if isinstance(val, list):
            return [ast_value(x, scope) for x in val]
        elif isinstance(val, tuple):
            return tuple(ast_value(x, scope) for x in val)

        if isinstance(val, ast.Attribute):
            name = ast_value(val.value, scope, return_name=True)
            if isinstance(val.ctx, ast.Load):
                return '.'.join((name, val.attr))
            if return_name:
                return name
        elif isinstance(val, ast.keyword):
            return {val.arg: ast_value(val.value, scope)}
        elif isinstance(val, ast.List):
            return [ast_value(x, scope) for x in val.elts]
        elif isinstance(val, ast.Tuple):
            return tuple(ast_value(x, scope) for x in val.elts)
        elif isinstance(val, ast.Dict):
            return dict(zip([ast_value(x, scope) for x in val.keys],
                            [ast_value(x, scope) for x in val.values]))
        elif isinstance(val, ast.Num):
            return val.n
        elif isinstance(val, ast.Str):
            return val.s
        elif hasattr(ast, 'Bytes') and isinstance(val, ast.Bytes):
            return bytes(val.s)
    except Exception:
        # Don't care, just return None
        pass

    return None


def flatten_call_args(args, kwlist, starargs, kwargs):
    if starargs:
        args.extend(starargs)

    keywords = {}
    for kw in kwlist:
        keywords.update(kw)

    if kwargs:
        keywords.update(keywords)

    return args, keywords


def get_args(args, kwargs, arg_names):
    '''Get arguments as a dict.
    '''
    n_args = len(arg_names)
    if len(args) + len(kwargs) > n_args:
        raise MoultScannerError('Too many arguments supplied. Expected: {}'.format(n_args))

    out_args = {}
    for i, a in enumerate(args):
        out_args[arg_names[i]] = a

    for a in arg_names:
        if a not in out_args:
            out_args[a] = None

    out_args.update(kwargs)
    return out_args


def parse_programmatic_import(node, scope):
    name = ast_value(node.func, scope, return_name=True)
    if not name:
        return []

    args, kwargs = flatten_call_args(ast_value(node.args, scope),
                                     ast_value(node.keywords, scope),
                                     ast_value(node.starargs, scope),
                                     ast_value(node.kwargs, scope))

    imports = []

    if name.endswith('__import__'):
        func_args = get_args(args, kwargs, ['name', 'globals', 'locals',
                                            'fromlist', 'level'])
        log.debug('Found `__import__` with args: {}'.format(func_args))
        if not func_args['name']:
            raise MoultScannerError('No name supplied for __import__')
        if func_args['fromlist']:
            if not hasattr(func_args['fromlist'], '__iter__'):
                raise MoultScannerError('__import__ fromlist is not iterable type')
            for fromname in func_args['fromlist']:
                imports.append((func_args['name'], fromname))
        else:
            imports.append((None, func_args['name']))
    elif name.endswith('import_module'):
        func_args = get_args(args, kwargs, ['name', 'package'])
        log.debug('Found `import_module` with args: {}'.format(func_args))
        if not func_args['name']:
            raise MoultScannerError('No name supplied for import_module')
        if func_args['package'] and not isinstance(func_args['package'], (bytes, str_)):
            raise MoultScannerError('import_module package not string type')
        imports.append((func_args['package'], func_args['name']))

    return imports


class ResolvedImport(object):
    def __init__(self, import_path, import_root):
        module = import_path.split('.', 1)[0]
        self.module = module
        self.import_path = import_path
        self.is_stdlib = utils.is_stdlib(module)
        self.filename = None

        if not self.is_stdlib:
            self.filename = utils.file_containing_import(import_path, import_root)

    def __repr__(self):
        return '<ResolvedImport {} ({})>'.format(self.import_path, self.filename)


class ImportNodeVisitor(ast.NodeVisitor):
    '''A simplistic AST visitor that looks for easily identified imports.

    It can resolve simple assignment variables defined within the module.
    '''
    def reset(self, filename):
        self.filename = filename
        self.import_path, self.import_root = utils.import_path_from_file(filename)

    def add_import(self, *names):
        for module, name in names:
            if module and module.startswith('.'):
                module = utils.resolve_import(module, self.import_path)
            elif not module:
                module = ''
            module = '.'.join((module, name.strip('.'))).strip('.')
            if module not in self._imports:
                self._imports.add(module)
                self.imports.append(ResolvedImport(module, self.import_root))

    def visit_Module(self, node):
        log.debug('Resetting AST visitor with module path: %s', self.import_path)
        self._imports = set()
        self.imports = []
        self.scope = {}
        if node:
            self.generic_visit(node)

    def visit_Import(self, node):
        for n in node.names:
            self.add_import((n.name, ''))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = '{}{}'.format('.' * node.level, str_(node.module or ''))
        for n in node.names:
            self.add_import((module, n.name))
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            try:
                self.add_import(*parse_programmatic_import(node.value, self.scope))
            except MoultScannerError as e:
                log.debug('%s, File: %s', e, self.filename)
        elif isinstance(node.value, ast.Name):
            ast_value(node.value, self.scope)
        self.generic_visit(node)

    def visit_Assign(self, node):
        ast_value(node, self.scope)

    def visit_Delete(self, node):
        ast_value(node, self.scope)

    def visit(self, node):
        super(ImportNodeVisitor, self).visit(node)


ast_visitor = ImportNodeVisitor()


def _ast_scan_file_re(filename):
    try:
        with io.open(filename, 'rt', encoding='utf8') as fp:
            script = fp.read()
            normalized = ''
            for imp in _fallback_re.finditer(script):
                imp_line = imp.group(1)
                try:
                    imp_line = imp_line.decode('utf8')
                except AttributeError:
                    pass
                except UnicodeEncodeError:
                    log.warn('Unicode import failed: %s', imp_line)
                    continue
                imp_line = re.sub(r'[\(\)]', '', imp_line)
                normalized += ' '.join(imp_line.split()).strip(',') + '\n'
            log.debug('Normalized imports:\n%s', normalized)

            try:
                root = ast.parse(normalized, filename=filename)
            except SyntaxError:
                log.error('Could not parse file using regex scan: %s', filename)
                log.info('Exception:', exc_info=True)
                return None, None

            log.debug('Starting AST Scan (regex): %s', filename)
            ast_visitor.reset(filename)
            ast_visitor.visit(root)
            return ast_visitor.scope, ast_visitor.imports
    except IOError:
        log.warn('Could not open file: %s', filename)

    return None, None


def ast_scan_file(filename, re_fallback=True):
    '''Scans a file for imports using AST.

    In addition to normal imports, try to get imports via `__import__`
    or `import_module` calls. The AST parser should be able to resolve
    simple variable assignments in cases where these functions are called
    with variables instead of strings.
    '''
    try:
        with io.open(filename, 'rb') as fp:
            try:
                root = ast.parse(fp.read(), filename=filename)
            except (SyntaxError, IndentationError):
                if re_fallback:
                    log.debug('Falling back to regex scanner')
                    return _ast_scan_file_re(filename)
                else:
                    log.error('Could not parse file: %s', filename)
                    log.info('Exception:', exc_info=True)
                return None, None
            log.debug('Starting AST Scan: %s', filename)
            ast_visitor.reset(filename)
            ast_visitor.visit(root)
            log.debug('Project path: %s', ast_visitor.import_root)
            return ast_visitor.scope, ast_visitor.imports
    except IOError:
        log.warn('Could not open file: %s', filename)

    return None, None
