#!/usr/bin/env python
"Utility for initializing the server database"
import sys, time, imp

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

if main_is_frozen():
    sys.path.insert(0, '')

from porcupine.db import db
from porcupine import serverExceptions

answer = raw_input('''WARNING: Please ensure that Porcupine Server is stopped!
All objects will be erased!
Are you sure you want to initialize the database(Y/N)?''')

if (answer == 'Y'):
    try:
        from porcupine.config import dbparams
        db.open(dbparams.db_class)
    except serverExceptions.ConfigurationError, e:
        sys.exit(e.info)

    import porcupine.systemObjects
    import org.innoscript.desktop.schema.common
    import org.innoscript.desktop.schema.security

    # truncate database
    sys.stdout.write('Deleting existing database...')
    db.db_handle._truncate()
    sys.stdout.write('[OK]\n')

    sOwner = 'SYSTEM'
    ftime = time.time()

    sys.stdout.write('Creating root folder...')
    rootFolder = org.innoscript.desktop.schema.common.RootFolder()
    rootFolder._id = ''
    rootFolder.description.value = 'Root Folder'
    rootFolder.displayName.value = 'Porcupine Server'
    rootFolder._isSystem = True
    rootFolder._owner = sOwner
    rootFolder.modifiedBy = sOwner
    rootFolder._created = ftime
    rootFolder.modified = ftime
    rootFolder._subfolders = {
        'Categories':'categories',
        'Administrative Tools':'admintools',
        'Personal folders':'personal'
    }
    rootFolder.security = {'everyone':1, 'administrators':8}
    db.putItem(rootFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating recycle bin...')
    rb = org.innoscript.desktop.schema.common.RecycleBin()
    rb._id = 'rb'
    rb.description.value = 'Deleted items container'
    rb.displayName.value = 'Recycle Bin'
    rb._isSystem = True
    rb._owner = sOwner
    rb.modifiedBy = sOwner
    rb._created = ftime
    rb.modified = ftime
    rb.inheritRoles = False
    rb.security = {'administrators':8}
    db.putItem(rb, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Categories folder...')
    catFolder = org.innoscript.desktop.schema.common.Category()
    catFolder._id = 'categories'
    catFolder.displayName.value = 'Categories'
    catFolder._isSystem = True
    catFolder._owner = sOwner
    catFolder.modifiedBy = sOwner
    catFolder._created = ftime
    catFolder.modified = ftime
    catFolder.security = {'everyone':1, 'administrators':8}
    db.putItem(catFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating container for users\' personal storage...')
    perFolder = org.innoscript.desktop.schema.common.PersonalFolders()
    perFolder._id = 'personal'
    perFolder.displayName.value = 'Personal folders'
    perFolder._isSystem = True
    perFolder._owner = sOwner
    perFolder.modifiedBy = sOwner
    perFolder._created = ftime
    perFolder.modified = ftime
    perFolder._subfolders = {
        'admin':'adminstorage',
    }
    perFolder.security = {'everyone':1, 'administrators':8}
    db.putItem(perFolder, None)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating admin\'s personal storage...')
    adminFolder = org.innoscript.desktop.schema.common.PersonalFolder()
    adminFolder._id = 'adminstorage'
    adminFolder._parentid = 'personal'
    adminFolder.displayName.value = 'admin'
    adminFolder._isSystem = True
    adminFolder._owner = sOwner
    adminFolder.modifiedBy = sOwner
    adminFolder._created = ftime
    adminFolder.modified = ftime
    adminFolder.inheritRoles = False
    adminFolder.security = {'admin':2, 'administrators':8}
    db.putItem(adminFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Administrative Tools folder...')
    adminFolder = org.innoscript.desktop.schema.common.AdminTools()
    adminFolder._id = 'admintools'
    adminFolder.displayName.value = 'Administrative Tools'
    adminFolder._isSystem = True
    adminFolder._owner = sOwner
    adminFolder.modifiedBy = sOwner
    adminFolder._created = ftime
    adminFolder.modified = ftime
    adminFolder.inheritRoles = False
    adminFolder._subfolders = {
        'Users and Groups':'users',
        'Applications':'apps',
        'Policies':'policies'
    }
    adminFolder.security = {'administrators':8}
    db.putItem(adminFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Users folder...')
    userFolder = org.innoscript.desktop.schema.security.UsersFolder()
    userFolder._id = 'users'
    userFolder._parentid = 'admintools'
    userFolder.displayName.value = 'Users and Groups'
    userFolder._isSystem = True
    userFolder._owner = sOwner
    userFolder.modifiedBy = sOwner
    userFolder._created = ftime
    userFolder.modified = ftime
    userFolder.inheritRoles = 0
    userFolder._items = {
        'admin':'admin',
        'Everyone':'everyone',
        'Authenticated Users':'authusers',
        'SYSTEM':'system',
        'GUEST':'guest',
        'Administrators':'administrators'
    }
    userFolder.security = {'authusers':1, 'administrators':8}
    userFolder.description.value = 'Users and Groups container'
    db.putItem(userFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Admin user...')
    admin = org.innoscript.desktop.schema.security.User()
    admin._id = 'admin'
    admin._parentid = 'users'
    admin.displayName.value = 'admin'
    admin.personalFolder.value = 'adminstorage'
    admin._isSystem = True
    admin._owner = sOwner
    admin.modifiedBy = sOwner
    admin._created = ftime
    admin.modified = ftime
    admin.memberof.value = ['administrators']
    admin.description.value = 'Administrator account'
    admin.password.value = 'admin'
    admin.security = userFolder.security
    admin.settings.value = {'TASK_BAR_POS' : 'bottom'}
    db.putItem(admin, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating SYSTEM user...')
    system = org.innoscript.desktop.schema.security.SystemUser()
    system._id = 'system'
    system._parentid = 'users'
    system.displayName.value = 'SYSTEM'
    system._isSystem = True
    system.modifiedBy = sOwner
    system._owner = sOwner
    system._created = ftime
    system.modified = ftime
    system.description.value = 'System account'
    system.security = userFolder.security
    db.putItem(system, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating GUEST user...')
    guest = org.innoscript.desktop.schema.security.GuestUser()
    guest._id = 'guest'
    guest._parentid = 'users'
    guest.displayName.value = 'GUEST'
    guest._isSystem = True
    guest.modifiedBy = sOwner
    guest._owner = sOwner
    guest._created = ftime
    guest.modified = ftime
    guest.description.value = 'Guest account'
    guest.security = userFolder.security
    db.putItem(guest, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Everyone group...')
    everyone = org.innoscript.desktop.schema.security.EveryoneGroup()
    everyone._id = 'everyone'
    everyone._parentid = 'users'
    everyone.displayName.value = 'Everyone'
    everyone._isSystem = True
    everyone.modifiedBy = sOwner
    everyone._owner = sOwner
    everyone._created = ftime
    everyone.modified = ftime
    everyone.description.value = 'Everyone group'
    everyone.security = userFolder.security
    db.putItem(everyone, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Authenticated Users group...')
    auth = org.innoscript.desktop.schema.security.AuthUsersGroup()
    auth._id = 'authusers'
    auth._parentid = 'users'
    auth.displayName.value = 'Authenticated Users'
    auth._isSystem = True
    auth.modifiedBy = sOwner
    auth._owner = sOwner
    auth._created = ftime
    auth.modified = ftime
    auth.description.value = 'Authenticated Users group'
    auth.security = userFolder.security
    db.putItem(auth, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Administrators Group...')
    admins = org.innoscript.desktop.schema.security.Group()
    admins._id = 'administrators'
    admins._parentid = 'users'
    admins.displayName.value = 'Administrators'
    admins._isSystem = True
    admins._created = ftime
    admins.modified = ftime
    admins._owner = sOwner
    admins.modifiedBy = sOwner
    admins.members.value = ['admin']
    admins.description.value = 'Administrators group'
    admins.security = userFolder.security
    db.putItem(admins, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Server Policies folder...')
    polFolder = org.innoscript.desktop.schema.security.PoliciesFolder()
    polFolder._id = 'policies'
    polFolder._parentid = 'admintools'
    polFolder.displayName.value = 'Policies'
    polFolder._isSystem = True
    polFolder._owner = sOwner
    polFolder.modifiedBy = sOwner
    polFolder._created = ftime
    polFolder.modified = ftime
    #appFolder.inheritRoles = 0
    polFolder._items = {
        'Upload Documents' : 'uploadpolicy'
    }
    polFolder.security = adminFolder.security
    polFolder.description.value = 'Server Security Policies '
    db.putItem(polFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Upload Policy...')
    policy = org.innoscript.desktop.schema.security.Policy()
    policy._id = 'uploadpolicy'
    policy._parentid = 'policies'
    policy.displayName.value = 'Upload Documents'
    policy._isSystem = True
    policy._created = ftime
    policy.modified = ftime
    policy._owner = sOwner
    policy.modifiedBy = sOwner
    policy.policyGranted.value = ['authusers']
    policy.description.value = 'Policy for uploading documents to server temporary folder'
    policy.security = polFolder.security
    db.putItem(policy, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating QuiX Applications folder...')
    appFolder = org.innoscript.desktop.schema.common.AppsFolder()
    appFolder._id = 'apps'
    appFolder._parentid = 'admintools'
    appFolder.displayName.value = 'Applications'
    appFolder._isSystem = True
    appFolder._owner = sOwner
    appFolder.modifiedBy = sOwner
    appFolder._created = ftime
    appFolder.modified = ftime
    appFolder.inheritRoles = 0
    appFolder._items = {
        'Users and Groups Management' : 'appusrmgmnt',
        'OQL Query Performer': 'oqlqueryperf'
    }
    appFolder.security = {'authusers':1, 'administrators':8}
    appFolder.description.value = 'Installed applications container'
    db.putItem(appFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Users and Groups Management application...')
    app = org.innoscript.desktop.schema.common.Application()
    app._id = 'appusrmgmnt'
    app._parentid = 'apps'
    app.displayName.value = 'Users and Groups Management'
    app._isSystem = True
    app._owner = sOwner
    app.modifiedBy = sOwner
    app._created = ftime
    app.modified = ftime
    app.launchUrl.value = 'usermgmnt/usermgmnt.quix'
    app.icon.value = 'usermgmnt/images/icon.gif'
    app.inheritRoles = False
    app.security = {'administrators': 8}
    db.putItem(app, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating OQL Query Performer application...')
    app = org.innoscript.desktop.schema.common.Application()
    app._id = 'oqlqueryperf'
    app._parentid = 'apps'
    app.displayName.value = 'OQL Query Performer'
    app._isSystem = True
    app._owner = sOwner
    app.modifiedBy = sOwner
    app._created = ftime
    app.modified = ftime
    app.launchUrl.value = 'queryperformer/queryperformer.quix'
    app.icon.value = 'queryperformer/images/icon.gif'
    app.inheritRoles = False
    app.security = {'administrators': 8}
    db.putItem(app, None)
    sys.stdout.write('[OK]\n')

    db.close()
    sys.stdout.write('Store initialization completed successfully.')

    sys.exit()
