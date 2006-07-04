#===============================================================================
#    Copyright 2005, Tassos Koutsovassilis
#
#    This file is part of Porcupine.
#    Porcupine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2.1 of the License, or
#    (at your option) any later version.
#    Porcupine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#    You should have received a copy of the GNU Lesser General Public License
#    along with Porcupine; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#===============================================================================
"""This module provides the essential API for runtime manipulation of the
custom Porcupine objects and data types. It is mainly intended for
install/uninstall scripts packed with the B{pakager} deployment utility.
"""

import inspect, sys, types, time

from porcupine.utils import misc
from porcupine import systemObjects
from porcupine import datatypes
from porcupine.administration import offlinedb

class GenericSchemaEditor(object):
    def __init__(self, classobj):
        self._class = misc.getClassByName(classobj)
        self._bases = self._class.__bases__
        self.doc = self._class.__doc__
        self._attrs = {}
        self._methods = {}
        self._properties = {}
        sourcelines = inspect.getsourcelines(self._class)
        startline = sourcelines[1]
        endline = startline + len(sourcelines[0]) - 1
        self.boundaries = (startline, endline)
        
        self._instance = self._class()
        for prop in self._class.__slots__:
            self._attrs[prop] = getattr(self._instance, prop)

        for member_name in self._class.__dict__:
            member = self._class.__dict__[member_name]
            if type(member) == types.FunctionType:
                self._methods[member_name] = member
            elif type(member) == property:
                self._properties[member_name] = member
                
        self._module = sys.modules[self._class.__module__]
        self._newimports = []
        self._imports = {}
        
        moduledict = self._module.__dict__
        for x in moduledict:
            if type(moduledict[x]) == types.ModuleType:
                self._imports[moduledict[x]] = x
            elif callable(moduledict[x]) and \
                    (sys.modules[moduledict[x].__module__] != self._module):
                imported = misc.getClassByName(moduledict[x].__module__ + \
                                               '.' + x)
                self._imports[imported] = x
    
    def generateCode(self):
        raise NotImplementedError
    
    def _getFullName(self, callable):
        module = misc.getClassByName(callable.__module__)
        if self._imports.has_key(module):
            return self._imports[module] + '.' + callable.__name__
        else:
            if module == self._module:
                return callable.__name__
            self._newimports.append(module)
            local_name = callable.__module__.split('.')[-1]
            counter = 2
            while local_name in self._module.__dict__:
                local_name += str(counter)
                counter += 1
            self._imports[module] = local_name
            return(local_name + '.' + callable.__name__)
    
    def _generateImports(self):
        imports_code = []
        for mod in self._imports:
            if type(mod) == types.ModuleType:
                if mod.__name__ == self._imports[mod]:
                    imports_code.append('import ' + mod.__name__ + '\n')
                else:
                    modname = '.'.join(mod.__name__.split('.')[:-1])
                    attrname = mod.__name__.split('.')[-1]
                    if attrname == self._imports[mod]:
                        imports_code.append( 'from %s import %s\n' %
                            (modname, self._imports[mod]) )
                    else:
                        imports_code.append( 'from %s import %s as %s\n' %
                            (modname, attrname, self._imports[mod]) )
            else:
                imports_code.append( 'from %s import %s\n' %
                    (mod.__module__, self._imports[mod]) )
        return imports_code
        
    def _removeImports(self, sourcelines):
        import_lines = []
        for lineno, line in enumerate(sourcelines):
            if line[:4]=='from' or line[:5]=='import':
                import_lines.append(lineno)
        import_lines.reverse()
        for lineno in import_lines:
            del sourcelines[lineno]
        return min(import_lines)
        
    def _cleanupImports(self, sourcelines):
        source = ''.join(sourcelines)
        unused = []
        for module in self._imports:
            if self._imports[module] not in source:
                unused.append(module)
        for module in unused:
            del self._imports[module]        
            
    def commitChanges(self):
        module_source = inspect.getsourcelines(self._module)[0]
        new_source = module_source[:self.boundaries[0] - 1]
        new_source.extend(self.generateCode())
        new_source.extend(module_source[self.boundaries[1]:])
        
        imports_line = self._removeImports(new_source)
        self._cleanupImports(new_source)
        new_imports = self._generateImports()
        for no, imprt in enumerate(new_imports):
            new_source.insert(imports_line + no, imprt)
        
        modulefilename = self._module.__file__
        if modulefilename[-1] in ['c', 'o']:
            modulefilename = modulefilename[:-1]
        
        modfile = file(modulefilename, 'w')
        modfile.writelines(new_source)
        modfile.close()
        
class ItemEditor(GenericSchemaEditor):
    def __init__(self, classobj):
        GenericSchemaEditor.__init__(self, classobj)
        self._addedProps = {}
        if issubclass(self._class, systemObjects.GenericItem):
            self.containment = None
            self.image = self._class.__image__
            if self._instance.isCollection:
                self.containment = list(self._class.containment)
        else:
            raise TypeError, 'Invalid argument. ' + \
                'ItemEditor accepts only subclasses of GenericItem'
    
    def addProperty(self, name, value):
        self._attrs[name] = value
        self._addedProps[name] = value
        
    def removeProperty(self, name):
        from porcupine.oql.command import OqlCommand
        db = offlinedb.getHandle()
        oql_command = OqlCommand()
        rs = oql_command.execute(
            "select * from deep('/') where instanceof('%s')" %
            self._instance.contentclass)
        try:
            if len(rs):
                txn = offlinedb.OfflineTransaction()
                try:
                    for item in rs:
                        if hasattr(item, name):
                            delattr(item, name)
                        db.putItem(item, txn)
                    txn.commit()
                except Exception, e:
                    txn.abort()
                    raise e
                    sys.exit(2)
        finally:
            offlinedb.close()
        
        if self._attrs.has_key(name):
            del self._attrs[name]
            
    def commitChanges(self):
        GenericSchemaEditor.commitChanges(self)
        if len(self._addedProps):
            #we must reload the class module
            oMod = misc.getClassByName(self._class.__module__)
            reload(oMod)
            from porcupine.oql.command import OqlCommand
            
            db = offlinedb.getHandle()
            oql_command = OqlCommand()
            rs = oql_command.execute(
                "select * from deep('/') where instanceof('%s')" %
                self._instance.contentclass)
            try:
                if len(rs):
                    txn = offlinedb.OfflineTransaction()
                    try:
                        for item in rs:
                            for name in self._addedProps:
                                if not hasattr(item, name):
                                    setattr(item, name, self._addedProps[name])
                            db.putItem(item, txn)
                        txn.commit()
                    except Exception, e:
                        txn.abort()
                        raise e
                        sys.exit(2)
            finally:
                offlinedb.close()



    def generateCode(self):
        bases = [self._getFullName(x) for x in self._bases]

        code = ['# auto generated by codegen at %s\n' % time.asctime()]
        code.append('class %s(%s):\n' % (self._class.__name__, ','.join(bases)))
        
        # doc
        doc = self.doc.split('\n')
        if len(doc)==1:
            code.append('    "%s"\n' % doc[0])
        else:
            code.append('    """\n')
            code.extend(['%s\n' % x for x in doc if x.strip()])
            code.append('    """\n')
        
        # __image__
        code.append('    __image__ = "%s"\n' % self.image)
        
        # slots
        code.append('    __slots__ = (\n')
        code.extend(["        '%s',\n" % prop for prop in self._attrs])
        code.append('    )\n')
        
        #props
        code.append(
            '    __props__ = ' + \
            '+'.join( [x + '.__props__' for x in bases] ) + \
            ' + __slots__\n'
        )
        
        # containment
        if self.containment:
            code.append('    containment = (\n')
            code.extend(["        '%s',\n" % x for x in self.containment])
            code.extend('    )\n')
        
        if self._attrs:
            #__init__
            code.append('\n')
            code.append('    def __init__(self):\n')
            code.extend(['        %s.__init__(self)\n' % x for x in bases])
            
            # props
            for prop in [x for x in self._attrs
                    if self._attrs[x].__class__.__module__ != '__builtin__']:
                code.append('        self.%s = %s()\n' %
                        (prop, self._getFullName(self._attrs[prop].__class__)))
            for prop in [x for x in self._attrs
                    if self._attrs[x].__class__.__module__ == '__builtin__']:
                #print self._attrs[x].__class__
                code.append('        self.%s = %s\n' %
                        (prop, repr(self._attrs[prop])))
        
        #methods
        for meth in self._methods:
            method = self._methods[meth]
            if method.__name__ != '__init__':
                code.append('\n')
                code.extend(inspect.getsourcelines(self._methods[meth])[0])
            
        #properties
        for property_name in self._properties:
            code.append('\n')
            prop_descriptor = self._properties[property_name]
            fget = fset = None
            if prop_descriptor.fget:
                fget = prop_descriptor.fget.__name__
            if prop_descriptor.fset:
                fset = prop_descriptor.fset.__name__
            code.extend('    %s = property(%s, %s)' %
                        (property_name, fget, fset))
        
        return code
        
class DatatypeEditor(GenericSchemaEditor):
    def __init__(self, classobj):
        GenericSchemaEditor.__init__(self, classobj)
        if issubclass(self._class, datatypes.DataType):
            self.isRequired = self._class.isRequired
            self.relCc = None
            self.relAttr = None
            self.compositeClass = None
            if hasattr(self._class, 'relCc'):
                self.relCc = list(self._class.relCc)
            if hasattr(self._class, 'relAttr'):
                self.relAttr = self._class.relAttr
            if hasattr(self._class, 'compositeClass'):
                self.compositeClass = self._class.compositeClass
        else:
            raise TypeError, 'Invalid argument. ' + \
                'DatatypeEditor accepts only subclasses of DataType'

    def generateCode(self):
        bases = [self._getFullName(x) for x in self._bases]

        code = ['# auto generated by codegen at %s\n' % time.asctime()]
        code.append('class %s(%s):\n' % (self._class.__name__, ','.join(bases)))
        
        # doc
        doc = self.doc.split('\n')
        if len(doc)==1:
            code.append('    "%s"\n' % doc[0])
        else:
            code.append('    """\n')
            code.extend(['%s\n' % x for x in doc if x.strip()])
            code.append('    """\n')
        
        # slots
        code.append('    __slots__ = (\n')
        code.extend(["        '%s',\n" % prop for prop in self._attrs])
        code.append('    )\n')

        # isRequired
        code.append('    isRequired = %s\n' % str(self.isRequired))
        
        # relCc
        if self.relCc and (issubclass(self._class, datatypes.Reference1) or \
                           issubclass(self._class, datatypes.ReferenceN)):
            code.append('    relCc = (\n')
            code.extend(["        '%s',\n" % x for x in self.relCc])
            code.extend('    )\n')
        # relAttr
        if self.relAttr and (issubclass(self._class, datatypes.Relator1) or \
                             issubclass(self._class, datatypes.RelatorN)):
            code.append("    relAttr = '%s'\n" % self.relAttr)
        # compositeClass
        if self.compositeClass and \
                issubclass(self._class, datatypes.Composition):
            code.append("    compositeClass = '%s'\n" % self.compositeClass)
        

        if self._attrs:
            #__init__
            code.append('\n')
            code.append('    def __init__(self):\n')
            code.extend(['        %s.__init__(self)\n' % x for x in bases])
            
            # props
            for prop in [x for x in self._attrs
                    if self._attrs[x].__class__.__module__ != '__builtin__']:
                code.append('        self.%s = %s()\n' %
                        (prop, self._getFullName(self._attrs[prop].__class__)))
            for prop in [x for x in self._attrs
                    if self._attrs[x].__class__.__module__ == '__builtin__']:
                code.append('        self.%s = %s\n' % 
                        (prop, repr(self._attrs[prop])))
        
        #methods
        for meth in self._methods:
            method = self._methods[meth]
            if method.__name__ != '__init__':
                code.append('\n')
                code.extend(inspect.getsourcelines(self._methods[meth])[0])
            
        #properties
        for property_name in self._properties:
            code.append('\n')
            prop_descriptor = self._properties[property_name]
            fget = fset = None
            if prop_descriptor.fget:
                fget = prop_descriptor.fget.__name__
            if prop_descriptor.fset:
                fset = prop_descriptor.fset.__name__
            code.extend('    %s = property(%s, %s)' %
                        (property_name, fget, fset))
        
        return code
