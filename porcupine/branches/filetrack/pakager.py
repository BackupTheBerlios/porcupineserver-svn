#!/usr/bin/env python
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
"Porcupine Server Package Manager"

import getopt, sys, os, cPickle, tarfile, ConfigParser, imp
from xml.dom import minidom

from porcupine import datatypes
from porcupine import serverExceptions
from porcupine.administration import offlinedb
from porcupine.config import serverSettings

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
    def __init__(self, package_file=None, ini_file=None):
        self.package_files = []
        self.db = None
        self.name = None
        self.version = None
        self.package_file = None
        
        if package_file:
            self.package_file = tarfile.open(package_file, 'r:gz')
            ini_file = self.package_file.extractfile('_pkg.ini')
        elif ini_file:
            ini_file = file(ini_file)
        
        if ini_file:
            self.config_file = ConfigParser.RawConfigParser()
            self.config_file.readfp(ini_file)
            self.name = self.config_file.get('package', 'name')
            self.version = self.config_file.get('package', 'version')
            if not package_file:
                self.package_file = tarfile.open(self.name + '-' + \
                                                 self.version + '.ppf', 'w:gz')
    
    def close(self):
        if self.package_file:
            self.package_file.close()
    
    
    def _exportItem(self, id, clearRolesInherited=True):
        it_file = file(serverSettings.temp_folder + '/' + id, 'wb')
        item = self.db.getItem(id)
        if clearRolesInherited:
            item.inheritRoles = False
        
        # load external attributes
        for prop in [getattr(item, x) for x in item.__props__]:
            if isinstance(prop, datatypes.ExternalAttribute):
                prop.getValue()
        
        it_file.write( cPickle.dumps(item, 2) )
        it_file.close()
        self.package_files.append(
            (
                self.package_file.gettarinfo(
                    it_file.name,
                    '_db/' + os.path.basename(it_file.name)
                ), it_file.name
            )
        ) 
        if item.isCollection:
            dummy = [
                self._exportItem(childid, False)
                for childid in item._subfolders.values() + item._items.values()
            ]
    
    def _importItem(self, fileobj, txn):
        sItem = fileobj.read()
        oItem = cPickle.loads(sItem)
        oParent = self.db.getItem(oItem.parentid, txn)
        #check if the item already exists
        try:
            oOldItem = self.db.getItem(oItem.id, txn)
        except serverExceptions.DBItemNotFound:
            # write external attributes
            for prop in [getattr(oItem, x) for x in oItem.__props__]:
                if isinstance(prop, datatypes.ExternalAttribute):
                    prop._isDirty = True
                    prop._eventHandler.on_create(oItem, prop, txn)
    
            if oParent and not(oItem._id in oParent._items.values() + \
                                           oParent._subfolders.values()):
                if oItem.isCollection:
                    oParent._subfolders[oItem.displayName.value] = oItem._id
                else:
                    oParent._items[oItem.displayName.value] = oItem._id
                self.db.putItem(oParent, txn)
            self.db.putItem(oItem, txn)
        else:
            print 'WARNING: Item "%s" already exists. Upgrading object...' % \
                oItem.displayName.value
            oItem.displayName.value = oOldItem.displayName.value
            oItem.description.value = oOldItem.description.value
            oItem.inheritRoles = oOldItem.inheritRoles
            oItem.modifiedBy = oOldItem.modifiedBy
            oItem.modified = oOldItem.modified
            oItem._created = oOldItem._created
            oItem.security = oOldItem.security
            if oItem.isCollection:
                oItem._subfolders = oOldItem._subfolders
                oItem._items = oOldItem._items
            self.db.putItem(oItem, txn)
        
    def _deltree(self, top):
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)
        
    def _addtree(self, path):
        self.package_files.append(
            (self.package_file.gettarinfo(path, path), path)
        )
        for subdir in [f for f in os.listdir(path)
             if os.path.isdir(os.path.join(path, f))]:
             self._addtree(path + '/' + subdir)

    def install(self):
        print 'INFO: installing [%s-%s] package...' % (self.name, self.version)
        contents = self.package_file.getnames()
        
        # pre-install script
        if '_pre.py' in contents:
            print 'INFO: running pre installation script...'
            self.package_file.extract('_pre.py', serverSettings.temp_folder)
            execfile(serverSettings.temp_folder + '/_pre.py')
            os.remove(serverSettings.temp_folder + '/_pre.py')
        
        # registrations
        if '_regs.xml' in contents:
            print 'INFO: installing package registrations...'
            regsfile = self.package_file.extractfile('_regs.xml')
            _dom = minidom.parse(regsfile)
            package_node = _dom.getElementsByTagName('package')[0]
            package_node = package_node.cloneNode(True)
            conf_file = ConfigFile('conf/store.xml')
            old_node = conf_file.getPackageNode(self.name)
            if old_node:
                conf_file.replacePackageNode(package_node, old_node)
            else:
                conf_file.addPackageNode(package_node)
            _dom.unlink()
            conf_file.close()

        # registrations
        if '_resources.xml' in contents:
            print 'INFO: installing package resources...'
            resfile = self.package_file.extractfile('_resources.xml')
            _dom = minidom.parse(resfile)
            package_node = _dom.getElementsByTagName('package')[0]
            package_node = package_node.cloneNode(True)
            conf_file = ConfigFile('conf/stringresources.xml')
            old_node = conf_file.getPackageNode(self.name)
            if old_node:
                conf_file.replacePackageNode(package_node, old_node)
            else:
                conf_file.addPackageNode(package_node)
            _dom.unlink()
            conf_file.close()
            
        # web apps
        if '_pubdir.xml' in contents:
            print 'INFO: installing published directories...'
            appsfile = self.package_file.extractfile('_pubdir.xml')
            _dom = minidom.parse(appsfile)
            appsConfig = AppConfigFile()
            app_nodes = _dom.getElementsByTagName('dir')
            for app_node in app_nodes:
                app_node = app_node.cloneNode(True)
                app_name = app_node.getAttribute('name')
                print 'INFO: installing published directory "%s"' % app_name
                old_node = appsConfig.getAppNode(app_name)
                if old_node:
                    appsConfig.replaceAppNode(app_node, old_node)
                else:
                    appsConfig.addAppNode(app_node)
            _dom.unlink()
            appsConfig.close(True)
                
        # files and dirs
        for pfile in [x for x in contents if x[0] != '_']:
            print 'INFO: extracting ' + pfile
            self.package_file.extract(pfile)
                
        # database
        dbfiles = [x for x in contents if x[:4] == '_db/']
        if dbfiles:
            self.db = offlinedb.getHandle()
            txn = offlinedb.OfflineTransaction()
            try:
                for dbfile in dbfiles:
                    print 'INFO: importing object ' + os.path.basename(dbfile)
                    actual_fn = serverSettings.temp_folder + '/' + dbfile
                    objfile = None
                    try:
                        try:
                            self.package_file.extract(dbfile, serverSettings.temp_folder)
                            objfile = file(actual_fn, 'rb')
                            self._importItem(objfile, txn)
                        except Exception, e:
                            txn.abort()
                            raise e
                            sys.exit(2)
                    finally:
                        if objfile:
                            objfile.close()
                        if os.path.exists(actual_fn):
                            os.remove(actual_fn)
                txn.commit()
            finally:
                offlinedb.close()
                if os.path.exists(serverSettings.temp_folder + '/_db'):
                    os.rmdir(serverSettings.temp_folder + '/_db')
            
        # post-install script
        if '_post.py' in contents:
            print 'INFO: running post installation script...'
            self.package_file.extract('_post.py', serverSettings.temp_folder)
            execfile(serverSettings.temp_folder + '/_post.py')
            os.remove(serverSettings.temp_folder + '/_post.py')
            
    def uninstall(self):
        print 'INFO: uninstalling [%s-%s] package...' % (self.name, self.version)
        
        # Registrations
        conf_file = ConfigFile('conf/store.xml')
        pkgnode = conf_file.getPackageNode(self.name)
        if pkgnode:
            print 'INFO: removing package registrations'
            conf_file.removePackageNode(pkgnode)
            conf_file.close()
        
        # Resources
        conf_file = ConfigFile('conf/stringresources.xml')
        pkgnode = conf_file.getPackageNode(self.name)
        if pkgnode:
            print 'INFO: removing package resources'
            conf_file.removePackageNode(pkgnode)
            conf_file.close()
            
        # Database Items
        items = self.config_file.options('items')
        itemids = [self.config_file.get('items', x) for x in items]
        self.db = offlinedb.getHandle()
        txn = offlinedb.OfflineTransaction()
        try:
            try:
                for itemid in itemids:
                    print 'INFO: removing object %s' % itemid
                    try:
                        oItem = self.db.getItem(itemid, txn)
                    except:
                        pass
                    else:
                        oItem.delete(txn)
                txn.commit()
            except Exception, e:
                txn.abort()
                raise e
                sys.exit(2)
        finally:
            offlinedb.close()
            
        # uninstall script
        contents = self.package_file.getnames()
        if '_uninstall.py' in contents:
            print 'INFO: running uninstallation script...'
            self.package_file.extract('_uninstall.py', serverSettings.temp_folder)
            execfile(serverSettings.temp_folder + '/_uninstall.py')
            os.remove(serverSettings.temp_folder + '/_uninstall.py')
        
        # Files
        files = self.config_file.options('files')
        for fl in files:
            fname = self.config_file.get('files', fl)
            print 'INFO: removing file ' + fname
            if os.path.exists(fname):
                os.remove(fname)
            # check if it is a python file
            if fname[-3:] == '.py':
                dummy = [
                    os.remove(fname + x)
                    for x in ('c', 'o')
                    if os.path.exists(fname + x)
                ]
    
        # Directories
        dirs = self.config_file.options('dirs')
        for dir in dirs:
            dirname = self.config_file.get('dirs', dir)
            if os.path.exists(dirname):
                print 'INFO: removing directory ' + dirname
                self._deltree(dirname)
                
        # web apps
        if '_pubdir.xml' in contents:
            print 'INFO: uninstalling web apps...'
            appsfile = self.package_file.extractfile('_pubdir.xml')
            _dom = minidom.parse(appsfile)
            appsConfig = AppConfigFile()
            app_nodes = _dom.getElementsByTagName('dir')
            for app_node in app_nodes:
                #app_node = app_node.cloneNode(True)
                app_name = app_node.getAttribute('name')
                print 'INFO: uninstalling published directory "%s"' % app_name
                old_node = appsConfig.getAppNode(app_name)
                if old_node:
                    appsConfig.removeAppNode(old_node)
                else:
                    print 'WARNING: published directory "%s" does not exist' % app_name
                dirname = 'pubdir/' + app_name
                if os.path.exists(dirname):
                    self._deltree(dirname)

            _dom.unlink()
            appsConfig.close(True)

    def create(self):
        # Registrations
        conf_file = ConfigFile('conf/store.xml')
        pkgnode = conf_file.getPackageNode(self.name)
        if pkgnode:
            print 'INFO: extracting package registrations'
            regsFile = file(serverSettings.temp_folder + '/_regs.xml', 'w')
            regsFile.write('<config>\n' + pkgnode.toxml('utf-8') + '\n</config>')
            regsFile.close()
            self.package_files.append(
                (
                    self.package_file.gettarinfo(
                        regsFile.name, os.path.basename(regsFile.name)
                    ),
                    regsFile.name
                )
            )
        else:
            print 'WARNING: Package "' + self.name + '" has no registrations'
        
        # Resources
        conf_file = ConfigFile('conf/stringresources.xml')
        pkgnode = conf_file.getPackageNode(self.name)
        if pkgnode:
            print 'INFO: extracting package resources'
            resFile = file(serverSettings.temp_folder + '/_resources.xml', 'w')
            resFile.write('<?xml version="1.0" encoding="utf-8"?>' + \
                '<resources>\n' + pkgnode.toxml('utf-8') + '\n</resources>')
            resFile.close()
            self.package_files.append(
                (
                    self.package_file.gettarinfo(
                        resFile.name, os.path.basename(resFile.name)
                    ),
                    resFile.name
                )
            )
        else:
            print 'WARNING: Package "' + self.name + '" has no resources'
        
        # Files
        files = self.config_file.options('files')
        for fl in files:
            fname = self.config_file.get('files', fl)
            print 'INFO: adding file ' + fname
            self.package_files.append(
                (self.package_file.gettarinfo(fname, fname), fname)
            )
    
        # Directories
        dirs = self.config_file.options('dirs')
        for dir in dirs:
            dirname = self.config_file.get('dirs', dir)
            print 'INFO: adding directory ' + dirname
            self._addtree(dirname)
        
        # pub dirs
        if self.config_file.has_section('pubdir'):
            webapps = self.config_file.options('pubdir')
            appsConfig = AppConfigFile()
            
            app_nodes = []
            for app in webapps:
                appname = self.config_file.get('pubdir', app)
                print 'INFO: adding published directory "%s"' % appname
                app_node = appsConfig.getAppNode(appname)
                if app_node:
                        app_nodes.append(app_node)
                        app_dir = 'pubdir/' + app_node.getAttribute('path')
                        self._addtree(app_dir)
                else:
                    print 'WARNING: webapp "%s" does not exist' % appname
            
            if app_nodes:
                appsFile = file(serverSettings.temp_folder + '/_pubdir.xml', 'w')
                appsFile.write('<?xml version="1.0" encoding="utf-8"?><dirs>')
                for app_node in app_nodes:
                    appsFile.write(app_node.toxml('utf-8'))
                appsFile.write('</dirs>')
                appsFile.close()
                self.package_files.append(
                    (
                        self.package_file.gettarinfo(
                            appsFile.name, os.path.basename(appsFile.name)
                        ),
                        appsFile.name
                    )
                )
            appsConfig.close(False)
        
        # Database Items
        items = self.config_file.options('items')
        itemids = [self.config_file.get('items', x) for x in items]
        self.db = offlinedb.getHandle()
        try:
            for itemid in itemids:
                self._exportItem(itemid)
        finally:
            offlinedb.close()
                
        # Scripts
        if self.config_file.has_option('scripts', 'preinstall'):
            preinstall = self.config_file.get('scripts', 'preinstall')
            print 'INFO: adding pre-install script "%s"' % preinstall
            self.package_files.append(
                (
                    self.package_file.gettarinfo(preinstall, '_pre.py'),
                    preinstall
                )
            )

        if self.config_file.has_option('scripts', 'postinstall'):
            postinstall = self.config_file.get('scripts', 'postinstall')
            print 'INFO: adding post-install script "%s"' % postinstall
            self.package_files.append(
                (
                    self.package_file.gettarinfo(postinstall, '_post.py'),
                    postinstall
                )
            )
                
        if self.config_file.has_option('scripts', 'uninstall'):
            uninstall = self.config_file.get('scripts', 'uninstall')
            print 'INFO: adding uninstall script "%s"' % uninstall
            self.package_files.append(
                (
                    self.package_file.gettarinfo(uninstall, '_uninstall.py'),
                    uninstall
                )
            )
            
        # Definition file
        self.package_files.append(
            (
                self.package_file.gettarinfo(definition, '_pkg.ini'),
                definition
            )
        )
    
        # Compact files
        print 'INFO: compacting...'
        for tarinfo, fname in self.package_files:
            if tarinfo.isfile():
                self.package_file.addfile(tarinfo, file(fname, 'rb'))
                # remove temporary
                if fname[:len(serverSettings.temp_folder)] == \
                serverSettings.temp_folder:
                    os.remove(fname)
            else:
                self.package_file.add(fname)
                
class AppConfigFile(object):
    def __init__(self):
        self._xmlfile = minidom.parse('conf/pubdir.xml')
        
    def getAppNode(self, appName):
        applist = self._xmlfile.getElementsByTagName('dir')
        for appnode in applist:
            if appName==appnode.getAttribute('name'):
                return appnode
    
    def addAppNode(self, appNode):
        apps_node = self._xmlfile.getElementsByTagName('dirs')[0]
        apps_node.appendChild(appNode)
    
    def removeAppNode(self, appNode):
        apps_node = self._xmlfile.getElementsByTagName('dirs')[0]
        apps_node.removeChild(appNode)

    def replaceAppNode(self, new_node, old_node):
        apps_node = self._xmlfile.getElementsByTagName('dirs')[0]
        apps_node.replaceChild(new_node, old_node)

    def close(self, commitChanges):
        if commitChanges:
            configfile = file('conf/pubdir.xml', 'w')
            configfile.write(self._xmlfile.toxml('utf-8'))
            configfile.close()
        self._xmlfile.unlink()

class ConfigFile(object):
    def __init__(self, configfile):
        self._fn = configfile
        self._xmlfile = minidom.parse(configfile)
        
    def getPackageNode(self, pkgname):
        packagelist = self._xmlfile.getElementsByTagName('package')
        for pkgnode in packagelist:
            if pkgname==pkgnode.getAttribute('name'):
                return pkgnode
    
    def addPackageNode(self, package_node):
        packages_node = self._xmlfile.getElementsByTagName('packages')[0]
        packages_node.appendChild(package_node)
        
    def removePackageNode(self, package_node):
        packages_node = self._xmlfile.getElementsByTagName('packages')[0]
        packages_node.removeChild(package_node)
        
    def replacePackageNode(self, new_node, old_node):
        packages_node = self._xmlfile.getElementsByTagName('packages')[0]
        packages_node.replaceChild(new_node, old_node)
        
    def close(self):
        configfile = file(self._fn, 'w')
        configfile.write(self._xmlfile.toxml('utf-8'))
        configfile.close()
        self._xmlfile.unlink()

def usage():
    print __usage__
    sys.exit(2)

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

if __name__=='__main__':
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

    if main_is_frozen():
        sys.path.insert(0, '')

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
        if my_pkg:
            my_pkg.close()

