#!/usr/bin/env python
#===============================================================================
#    Copyright 2005-2009, Tassos Koutsovassilis
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
"Porcupine Server Package Manager"

import getopt
import sys
import os
import tarfile
import io
try:
    # python 2.6
    import ConfigParser as configparser
except ImportError:
    # python 3
    import configparser
from xml.dom import minidom

from porcupine import db
from porcupine import datatypes
from porcupine.core import persist
from porcupine.utils.misc import freeze_support
from porcupine.administration import offlinedb
from porcupine.administration import configfiles
from porcupine.config.settings import settings

__usage__ = """
Install package:
    python pakager.py -i -p PACKAGE_FILE or
    python pakager.py --install --package=PACKAGE_FILE
    
Uninstall package:
    python pakager.py -u -p PACKAGE_FILE or
    python pakager.py --uninstall --package=PACKAGE_FILE
    
Create package:
    python pakager.py -c -d PACKAGE_DEFINITION_FILE or
    python pakager.py --create --def=PACKAGE_DEFINITION_FILE
"""

class Package(object):
    tmp_folder = settings['global']['temp_folder']

    def __init__(self, package_file=None, ini_file=None):
        self.package_files = []
        self.db = None
        self.name = None
        self.version = None
        self.package_file = None
        
        if package_file:
            self.package_file = tarfile.open(package_file, 'r:gz')
            ini_file = io.StringIO(
                self.package_file.extractfile('_pkg.ini').read().decode())
        elif ini_file:
            ini_file = open(ini_file)
        
        if ini_file:
            self.config_file = configparser.RawConfigParser()
            self.config_file.readfp(ini_file)
            self.name = self.config_file.get('package', 'name')
            self.version = self.config_file.get('package', 'version')
            if not package_file:
                self.package_file = tarfile.open(self.name + '-' + \
                                                 self.version + '.ppf', 'w:gz')
    
    def close(self):
        if self.package_file:
            self.package_file.close()
    
    def _export_item(self, item, clear_roles_inherited=True):
        it_file = open(self.tmp_folder + '/' + item._id, 'wb')
        if clear_roles_inherited:
            item.inheritRoles = False
        
        # load external attributes
        for prop in [getattr(item, x) for x in item.__props__]:
            if isinstance(prop, datatypes.ExternalAttribute):
                prop.get_value()
        
        it_file.write(persist.dumps(item))
        it_file.close()
        self.package_files.append((
                self.package_file.gettarinfo(
                    it_file.name,
                    '_db/' + os.path.basename(it_file.name)),
                it_file.name))
        if item.isCollection:
            [self._export_item(child, False)
             for child in item.get_children()]
    
    def _import_item(self, fileobj):
        stream = fileobj.read()
        item = persist.loads(stream)
        #check if the item already exists
        old_item = self.db.get_item(item.id)
        if old_item is None:
            # write external attributes
            for prop in [getattr(item, x) for x in item.__props__
                         if hasattr(item, x)]:
                if isinstance(prop, datatypes.ExternalAttribute):
                    prop._isDirty = True
                    prop._eventHandler.on_create(item, prop)
            self.db.put_item(item)
        else:
            print('WARNING: Item "%s" already exists. Upgrading object...' %
                  item.displayName.value)
            item.displayName.value = old_item.displayName.value
            item.description.value = old_item.description.value
            item.inheritRoles = old_item.inheritRoles
            item.modifiedBy = old_item.modifiedBy
            item.modified = old_item.modified
            item._created = old_item._created
            item.security = old_item.security
            self.db.put_item(item)

    def _deltree(self, top):
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)
        
    def _addtree(self, path):
        self.package_files.append((
            self.package_file.gettarinfo(path, path), path))

    def _execute_script(self, filename, name):
        exec(compile(open(filename).read(), name, 'exec'))

    def install(self):
        print('INFO: installing [%s-%s] package...' % (self.name, self.version))
        contents = self.package_file.getnames()
        
        # pre-install script
        if '_pre.py' in contents:
            print('INFO: running pre installation script...')
            self.package_file.extract('_pre.py', self.tmp_folder)
            self._execute_script(self.tmp_folder + '/_pre.py',
                                 'Pre-installation script')
            os.remove(self.tmp_folder + '/_pre.py')
        
        # published directories
        if '_pubdir.xml' in contents:
            print('INFO: installing published directories...')
            dirsfile = self.package_file.extractfile('_pubdir.xml')
            _dom = minidom.parse(dirsfile)
            dirsConfig = configfiles.PubDirManager()
            dir_nodes = _dom.getElementsByTagName('dir')
            for dir_node in dir_nodes:
                dir_node = dir_node.cloneNode(True)
                dir_name = dir_node.getAttribute('name')
                print('INFO: installing published directory "%s"' % dir_name)
                old_node = dirsConfig.getDirNode(dir_name)
                if old_node:
                    dirsConfig.replaceDirNode(dir_node, old_node)
                else:
                    dirsConfig.addDirNode(dir_node)
            _dom.unlink()
            dirsConfig.close(True)
                
        # files and dirs
        for pfile in [x for x in contents if x[0] != '_']:
            print('INFO: extracting ' + pfile)
            self.package_file.extract(pfile)
                
        # database
        dbfiles = [x for x in contents if x[:4] == '_db/']
        if dbfiles:
            self.db = offlinedb.get_handle()

            @db.transactional(auto_commit=True)
            def _import_items():
                for dbfile in dbfiles:
                    print('INFO: importing object ' + os.path.basename(dbfile))
                    fn = '%s/%s' % (self.tmp_folder, dbfile)
                    self.package_file.extract(dbfile, self.tmp_folder)
                    objfile = None
                    try:
                        objfile = open(fn, 'rb')
                        self._import_item(objfile)
                    except Exception as e:
                        raise e
                        sys.exit(2)
                    finally:
                        if objfile:
                            objfile.close()

            # import objects
            try:
                _import_items()
            finally:
                offlinedb.close()
                if os.path.exists(self.tmp_folder + '/_db'):
                    self._deltree(self.tmp_folder + '/_db')
            
        # post-install script
        if '_post.py' in contents:
            print('INFO: running post installation script...')
            self.package_file.extract('_post.py', self.tmp_folder)
            self._execute_script(self.tmp_folder + '/_post.py',
                                 'Post-installation script')
            os.remove(self.tmp_folder + '/_post.py')
            
    def uninstall(self):
        print('INFO: uninstalling [%s-%s] package...'
              % (self.name, self.version))
        
        # database items
        items = self.config_file.options('items')
        itemids = [self.config_file.get('items', x) for x in items]
        
        if itemids:
            self.db = offlinedb.get_handle()
        
            @db.transactional(auto_commit=True)
            def _remove_items():
                try:
                    for itemid in itemids:
                        item = self.db.get_item(itemid)
                        if item is not None:
                            print('INFO: removing object %s' % itemid)
                            item.delete()
                except Exception as e:
                    raise e
                    sys.exit(2)

            try:
                _remove_items()
            finally:
                offlinedb.close()

        # uninstall script
        contents = self.package_file.getnames()
        if '_uninstall.py' in contents:
            print('INFO: running uninstallation script...')
            self.package_file.extract('_uninstall.py', self.tmp_folder)
            self._execute_script(self.tmp_folder + '/_uninstall.py',
                                 'Uninstall script')
            os.remove(self.tmp_folder + '/_uninstall.py')
        
        # files
        files = self.config_file.options('files')
        for fl in files:
            fname = self.config_file.get('files', fl)
            print('INFO: removing file ' + fname)
            if os.path.exists(fname):
                os.remove(fname)
            # check if it is a python file
            if fname[-3:] == '.py':
                [os.remove(fname + x)
                 for x in ('c', 'o')
                 if os.path.exists(fname + x)]
    
        # directories
        dirs = self.config_file.options('dirs')
        for dir in dirs:
            dirname = self.config_file.get('dirs', dir)
            if os.path.exists(dirname):
                print('INFO: removing directory ' + dirname)
                self._deltree(dirname)
                
        # published dirs
        if '_pubdir.xml' in contents:
            print('INFO: uninstalling web apps...')
            dirsfile = self.package_file.extractfile('_pubdir.xml')
            _dom = minidom.parse(dirsfile)
            dirsConfig = configfiles.PubDirManager()
            dir_nodes = _dom.getElementsByTagName('dir')
            for dir_node in dir_nodes:
                #app_node = app_node.cloneNode(True)
                dir_name = dir_node.getAttribute('name')
                print('INFO: uninstalling published directory "%s"' % dir_name)
                old_node = dirsConfig.getDirNode(dir_name)
                if old_node:
                    dirsConfig.removeDirNode(old_node)
                else:
                    print('WARNING: published directory "%s" does not exist'
                          % dir_name)
                dirname = dir_node.getAttribute('path')
                if os.path.exists(dirname):
                    self._deltree(dirname)

            _dom.unlink()
            dirsConfig.close(True)

    def create(self):
        # files
        files = self.config_file.options('files')
        for fl in files:
            fname = self.config_file.get('files', fl)
            print('INFO: adding file ' + fname)
            self.package_files.append((
                self.package_file.gettarinfo(fname, fname), fname))
    
        # directories
        dirs = self.config_file.options('dirs')
        for dir in dirs:
            dirname = self.config_file.get('dirs', dir)
            print('INFO: adding directory ' + dirname)
            self._addtree(dirname)
        
        # published directories
        if self.config_file.has_section('pubdir'):
            pubdirs = self.config_file.options('pubdir')
            dirsConfig = configfiles.PubDirManager()
            
            dir_nodes = []
            for dir in pubdirs:
                dirname = self.config_file.get('pubdir', dir)
                print('INFO: adding published directory "%s"' % dirname)
                dir_node = dirsConfig.getDirNode(dirname)
                if dir_node:
                        dir_nodes.append(dir_node)
                        dir_location = dir_node.getAttribute('path')
                        self._addtree(dir_location)
                else:
                    print('WARNING: published directory "%s" does not exist'
                          % appname)
            
            if dir_nodes:
                dirsFile = open(self.tmp_folder + '/_pubdir.xml', 'w')
                dirsFile.write('<?xml version="1.0" encoding="utf-8"?><dirs>')
                for dir_node in dir_nodes:
                    dirsFile.write(dir_node.toxml('utf-8'))
                dirsFile.write('</dirs>')
                dirsFile.close()
                self.package_files.append(
                    (
                        self.package_file.gettarinfo(
                            dirsFile.name, os.path.basename(dirsFile.name)
                        ),
                        dirsFile.name
                    )
                )
            dirsConfig.close(False)
        
        # database items
        items = self.config_file.options('items')
        itemids = [self.config_file.get('items', x) for x in items]
        self.db = offlinedb.get_handle()
        try:
            for itemid in itemids:
                item = self.db.get_item(itemid)
                self._export_item(item)
        finally:
            offlinedb.close()
                
        # scripts
        if self.config_file.has_option('scripts', 'preinstall'):
            preinstall = self.config_file.get('scripts', 'preinstall')
            print('INFO: adding pre-install script "%s"' % preinstall)
            self.package_files.append((
                self.package_file.gettarinfo(preinstall, '_pre.py'),
                preinstall))

        if self.config_file.has_option('scripts', 'postinstall'):
            postinstall = self.config_file.get('scripts', 'postinstall')
            print('INFO: adding post-install script "%s"' % postinstall)
            self.package_files.append((
                self.package_file.gettarinfo(postinstall, '_post.py'),
                postinstall))
                
        if self.config_file.has_option('scripts', 'uninstall'):
            uninstall = self.config_file.get('scripts', 'uninstall')
            print('INFO: adding uninstall script "%s"' % uninstall)
            self.package_files.append((
                self.package_file.gettarinfo(uninstall, '_uninstall.py'),
                uninstall))
            
        # definition file
        self.package_files.append((
                self.package_file.gettarinfo(definition, '_pkg.ini'),
                definition))

        # compact files
        print('INFO: compacting...')
        for tarinfo, fname in self.package_files:
            if tarinfo.isfile():
                self.package_file.addfile(tarinfo, file(fname, 'rb'))
                # remove temporary
                if fname[:len(self.tmp_folder)] == self.tmp_folder:
                    os.remove(fname)
            else:
                if type(fname) == unicode:
                    fname = str(fname)
                self.package_file.add(fname)

def usage():
    print(__usage__)
    sys.exit(2)

if __name__ == '__main__':
    freeze_support()

    # get arguments
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            argv, "iucp:d:", ["install","uninstall","create","package=","def="]
        )
    except getopt.GetoptError:
        usage()
        
    command = None
    package = None
    definition = None

    if opts:
        for opt, arg in opts:                
            if opt in ('-i', '--install'):
                command = 'INSTALL'
            elif opt in ('-u', '--uninstall'):
                command = 'UNINSTALL'
            elif opt in ('-c', '--create'):
                command = 'CREATE'
            elif opt in ('-p', '--package'):
                package = arg
            elif opt in ('-d', '--def'):
                definition = arg
    else:
        usage()
    
    if not command:
        usage()
        
    my_pkg = None
    
    try:
        if command in ('INSTALL', 'UNINSTALL'):
            if not(package):
                usage()
            my_pkg = Package(package_file = package)
            if command == 'INSTALL':
                my_pkg.install()
            else:
                my_pkg.uninstall()
        else:
            if not definition:
                usage()
            my_pkg = Package(ini_file = definition)
            my_pkg.create()
    finally:
        if my_pkg is not None:
            my_pkg.close()
