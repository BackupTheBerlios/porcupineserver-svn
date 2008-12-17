#!/usr/bin/env python
"Utility for initializing the server database"
import sys
import time
import imp

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

if main_is_frozen():
    sys.path.insert(0, '')

from porcupine.administration import offlinedb

answer = raw_input('''WARNING: Please ensure that Porcupine Server is stopped!
All objects will be erased!
Are you sure you want to initialize the database(Y/N)?''')

if (answer.upper() == 'Y'):
    import org.innoscript.desktop.schema.common
    import org.innoscript.desktop.schema.security

    # create system user
    system = org.innoscript.desktop.schema.security.SystemUser()
    system._id = 'system'
    system.displayName.value = 'SYSTEM'
    system._isSystem = True
    system.description.value = 'System account'
    
    try:
        # get offline db handle
        db = offlinedb.getHandle(system)
    except Exception, e:
        sys.exit(e)
    
    # truncate database
    sys.stdout.write('Deleting existing database...')
    db.db_handle._truncate()
    sys.stdout.write('[OK]\n')
    
    # modify containment at run-time
    org.innoscript.desktop.schema.common.RootFolder.containment = (
        'org.innoscript.desktop.schema.common.Category',
        'org.innoscript.desktop.schema.common.PersonalFolders',
        'org.innoscript.desktop.schema.common.AdminTools'
    )
    org.innoscript.desktop.schema.common.AdminTools.containment = (
        'org.innoscript.desktop.schema.security.UsersFolder',
        'org.innoscript.desktop.schema.security.PoliciesFolder',
        'org.innoscript.desktop.schema.common.AppsFolder'
    )
    org.innoscript.desktop.schema.security.UsersFolder.containment = \
        list(org.innoscript.desktop.schema.security.UsersFolder.containment) + \
        ['org.innoscript.desktop.schema.security.SystemUser',
         'org.innoscript.desktop.schema.security.GuestUser',
         'org.innoscript.desktop.schema.security.EveryoneGroup',
         'org.innoscript.desktop.schema.security.AuthUsersGroup']
    
    # create top level objects
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
    
    txn = offlinedb.OfflineTransaction()
    
    sys.stdout.write('Creating Categories folder...')
    catFolder = org.innoscript.desktop.schema.common.Category()
    catFolder._id = 'categories'
    catFolder.displayName.value = 'Categories'
    catFolder._isSystem = True
    catFolder.appendTo('', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating container for users\' personal storage...')
    perFolder = org.innoscript.desktop.schema.common.PersonalFolders()
    perFolder._id = 'personal'
    perFolder.displayName.value = 'Personal folders'
    perFolder._isSystem = True
    perFolder.appendTo('', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating admin\'s personal storage...')
    adminFolder = org.innoscript.desktop.schema.common.PersonalFolder()
    adminFolder._id = 'adminstorage'
    adminFolder.displayName.value = 'admin'
    adminFolder._isSystem = True
    adminFolder.inheritRoles = False
    adminFolder.security = {'admin':2, 'administrators':8}
    adminFolder.appendTo('personal', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Administrative Tools folder...')
    adminFolder = org.innoscript.desktop.schema.common.AdminTools()
    adminFolder._id = 'admintools'
    adminFolder.displayName.value = 'Administrative Tools'
    adminFolder._isSystem = True
    adminFolder.inheritRoles = False
    adminFolder.security = {'administrators':8}
    adminFolder.appendTo('', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Users folder...')
    userFolder = org.innoscript.desktop.schema.security.UsersFolder()
    userFolder._id = 'users'
    userFolder.displayName.value = 'Users and Groups'
    userFolder._isSystem = True
    userFolder.inheritRoles = False
    userFolder.security = {'authusers':1, 'administrators':8}
    userFolder.description.value = 'Users and Groups container'
    userFolder.appendTo('admintools', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Admin user...')
    admin = org.innoscript.desktop.schema.security.User()
    admin._id = 'admin'
    admin.displayName.value = 'admin'
    admin.personalFolder.value = 'adminstorage'
    admin._isSystem = True
    admin.description.value = 'Administrator account'
    admin.password.value = 'admin'
    admin.settings.value = {'TASK_BAR_POS' : 'bottom'}
    admin.appendTo('users', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating SYSTEM user...')
    system.appendTo('users', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating GUEST user...')
    guest = org.innoscript.desktop.schema.security.GuestUser()
    guest._id = 'guest'
    guest.displayName.value = 'GUEST'
    guest._isSystem = True
    guest.description.value = 'Guest account'
    guest.appendTo('users', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Everyone group...')
    everyone = org.innoscript.desktop.schema.security.EveryoneGroup()
    everyone._id = 'everyone'
    everyone.displayName.value = 'Everyone'
    everyone._isSystem = True
    everyone.description.value = 'Everyone group'
    everyone.appendTo('users', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Authenticated Users group...')
    auth = org.innoscript.desktop.schema.security.AuthUsersGroup()
    auth._id = 'authusers'
    auth.displayName.value = 'Authenticated Users'
    auth._isSystem = True
    auth.description.value = 'Authenticated Users group'
    auth.appendTo('users', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Administrators Group...')
    admins = org.innoscript.desktop.schema.security.Group()
    admins._id = 'administrators'
    admins.displayName.value = 'Administrators'
    admins._isSystem = True
    admins.members.value = ['admin']
    admins.description.value = 'Administrators group'
    admins.appendTo('users', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Server Policies folder...')
    polFolder = org.innoscript.desktop.schema.security.PoliciesFolder()
    polFolder._id = 'policies'
    polFolder.displayName.value = 'Policies'
    polFolder._isSystem = True
    polFolder.description.value = 'Server Security Policies '
    polFolder.appendTo('admintools', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Upload Policy...')
    policy = org.innoscript.desktop.schema.security.Policy()
    policy._id = 'uploadpolicy'
    policy.displayName.value = 'Upload Documents'
    policy._isSystem = True
    policy.policyGranted.value = ['authusers']
    policy.description.value = 'Policy for uploading documents to server temporary folder'
    policy.appendTo('policies', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating QuiX Applications folder...')
    appFolder = org.innoscript.desktop.schema.common.AppsFolder()
    appFolder._id = 'apps'
    appFolder.displayName.value = 'Applications'
    appFolder._isSystem = True
    appFolder.inheritRoles = False
    appFolder.security = {'authusers':1, 'administrators':8}
    appFolder.description.value = 'Installed applications container'
    appFolder.appendTo('admintools', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating Users and Groups Management application...')
    app = org.innoscript.desktop.schema.common.Application()
    app._id = 'appusrmgmnt'
    app.displayName.value = 'Users and Groups Management'
    app._isSystem = True
    app.launchUrl.value = 'usermgmnt/usermgmnt.quix'
    app.icon.value = 'usermgmnt/images/icon.gif'
    app.inheritRoles = False
    app.security = {'administrators': 8}
    app.appendTo('apps', txn)
    sys.stdout.write('[OK]\n')
    
    sys.stdout.write('Creating OQL Query Performer application...')
    app = org.innoscript.desktop.schema.common.Application()
    app._id = 'oqlqueryperf'
    app.displayName.value = 'OQL Query Performer'
    app._isSystem = True
    app.launchUrl.value = 'queryperformer/queryperformer.quix'
    app.icon.value = 'queryperformer/images/icon.gif'
    app.inheritRoles = False
    app.security = {'administrators': 8}
    app.appendTo('apps', txn)
    sys.stdout.write('[OK]\n')
    
    txn.commit()
    db.close()
    
    sys.stdout.write('Store initialization completed successfully.\n')
    sys.exit()