#!/usr/bin/env python
"Utility for initializing the server database"
import sys, time

from porcupine.db import db
from porcupine import serverExceptions

answer = raw_input('''WARNING: all objects will be erased!
Are you sure you want to initialize the database(Y/N)?''')

if (answer == 'Y'):
    try:
        from porcupine.config import dbparams
        db.open(dbparams.db_class)
    except serverExceptions.ConfigurationError, e:
        sys.exit(e.info)
    
    import schemas.org.innoscript.common
    import schemas.org.innoscript.security
    import porcupine.systemObjects

    # truncate database
    sys.stdout.write('Deleting existing database...')
    db.db_handle._truncate()
    sys.stdout.write('[OK]\n')

    sOwner = 'SYSTEM'
    ftime = time.time()

    sys.stdout.write('Creating root folder...')
    rootFolder = schemas.org.innoscript.common.RootFolder()
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
        'Administrative Tools':'admintools'
    }
    rootFolder.security = {'everyone':1, 'administrators':8}
    db.putItem(rootFolder, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating recycle bin...')
    rb = schemas.org.innoscript.common.RecycleBin()
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
    catFolder = schemas.org.innoscript.common.Category()
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
    
    sys.stdout.write('Creating Administrative Tools folder...')
    adminFolder = schemas.org.innoscript.common.AdminTools()
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
    userFolder = schemas.org.innoscript.security.UsersFolder()
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
    admin = schemas.org.innoscript.security.User()
    admin._id = 'admin'
    admin._parentid = 'users'
    admin.displayName.value = 'admin'
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
    system = schemas.org.innoscript.security.SystemUser()
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
    guest = schemas.org.innoscript.security.GuestUser()
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
    everyone = schemas.org.innoscript.security.EveryoneGroup()
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
    auth = schemas.org.innoscript.security.AuthUsersGroup()
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
    admins = schemas.org.innoscript.security.Group()
    admins._id = 'administrators'
    admins._parentid = 'users'
    admins.displayName.value = 'Administrators'
    admins._isSystem = True
    admins._created = ftime
    admins.modified = ftime
    admins._owner = sOwner
    admin.modifiedBy = sOwner
    admins.members.value = ['admin']
    admins.description.value = 'Administrators group'
    admins.security = userFolder.security
    db.putItem(admins, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating Server Policies folder...')
    polFolder = schemas.org.innoscript.security.PoliciesFolder()
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
    policy = schemas.org.innoscript.security.Policy()
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
    appFolder = schemas.org.innoscript.common.AppsFolder()
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
    app = schemas.org.innoscript.common.Application()
    app._id = 'appusrmgmnt'
    app._parentid = 'apps'
    app.displayName.value = 'Users and Groups Management'
    app._isSystem = True
    app._owner = sOwner
    app.modifiedBy = sOwner
    app._created = ftime
    app.modified = ftime
    app.interface.value = '''
<a:splitter orientation="h" spacing="0" width="100%%" height="100%%">
    <a:pane length="24">
        <a:menubar width="100%%" height="100%%">
            <a:menu caption="File">
                <a:menuoption img="images/filenew.gif" caption="New">
                    <a:menuoption img="images/user.gif" caption="User" onclick="usermgmnt.newUser"></a:menuoption>
                    <a:menuoption img="images/group.gif" caption="Group" onclick="usermgmnt.newGroup"></a:menuoption>
                </a:menuoption>
                <a:sep></a:sep>
                <a:menuoption img="images/exit.gif" caption="Exit" onclick="usermgmnt.exitApp"></a:menuoption>
            </a:menu>
            <a:menu caption="About">
                <a:menuoption img="images/about16.gif" caption="About Users and Groups Management" onclick="usermgmnt.about"></a:menuoption>
            </a:menu>
        </a:menubar>
    </a:pane>
    <a:pane length="34">
        <a:toolbar width="100%%" height="100%%">
            <a:tbbutton width="30" img="images/reload22.gif" onclick="usermgmnt.refreshUsersList">
            </a:tbbutton>
            <a:tbbutton width="38" id="filter" img="images/colorpicker22.gif" type="menu">
                    <a:menuoption id="fv" type="radio" caption="Show all" selected="true" onclick="usermgmnt.applyFilter"></a:menuoption>
                    <a:menuoption id="fv" type="radio" caption="Show users" onclick="usermgmnt.applyFilter">
                        <a:prop name="CC" value="schemas.org.innoscript.security.User"></a:prop>
                    </a:menuoption>
                    <a:menuoption id="fv" type="radio" caption="Show groups" onclick="usermgmnt.applyFilter">
                        <a:prop name="CC" value="schemas.org.innoscript.security.Group"></a:prop>
                    </a:menuoption>
            </a:tbbutton>
        </a:toolbar>
    </a:pane>
    <a:pane length="-1">
        <a:contextmenu onshow="usermgmnt.usersListMenu_show">
            <a:menuoption img="images/filenew.gif" caption="New">
                    <a:menuoption img="images/user.gif" caption="User" onclick="usermgmnt.newUser"></a:menuoption>
                    <a:menuoption img="images/group.gif" caption="Group" onclick="usermgmnt.newGroup"></a:menuoption>
            </a:menuoption>
            <a:menuoption img="images/editdelete.gif" caption="Delete" onclick="usermgmnt.deleteItem"></a:menuoption>
            <a:sep></a:sep>
            <a:menuoption img="images/change_password.gif" caption="Reset password" onclick="usermgmnt.showResetPasswordDialog"></a:menuoption>
            <a:menuoption caption="Properties" onclick="usermgmnt.showProperties"></a:menuoption>
        </a:contextmenu>
        <a:listview id="userslist" multiple="true" width="100%%" height="100%%" ondblclick="usermgmnt.loadItem" onload="usermgmnt.getUsers">
            <a:prop name="FolderID" value="users"></a:prop>
            <a:prop name="filter" value=""></a:prop>
            <a:listheader>
                <a:column width="24" caption="" type="img" name="image" resizable="false"></a:column>
                <a:column width="24" caption="S" type="bool" name="issystem" resizable="false" sortable="true"></a:column>
                <a:column width="140" caption="Name" name="displayName" bgcolor="#EFEFEF" sortable="true"></a:column>
                <a:column width="140" caption="Full Name" name="fname" sortable="true"></a:column>
                <a:column width="220" caption="Description" name="description" sortable="true"></a:column>
            </a:listheader>
        </a:listview>
    </a:pane>
</a:splitter>
    '''
    app.script.value = '''
function usermgmnt() {}

usermgmnt.getUsers = function(w) {
    var folderUri = w.attributes.FolderID;
    var query = "select id, __image__ as image, displayName, description," +
        "isNone(fullName,'') as fname, isSystem as issystem, hasattr('password') as haspsw " +
        "from '" + folderUri + "'";
    if (w.attributes.filter)
        query += " where contentclass='" + w.attributes.filter + "'";
    if (w.orderby)
        query += " order by " + w.orderby + " " + w.sortorder;
    var xmlrpc = new XMLRPCRequest(QuiX.root);
    xmlrpc.oncomplete = usermgmnt.users_loaded;
    xmlrpc.callback_info = w;
    xmlrpc.callmethod('executeOqlCommand', query);
}

usermgmnt.users_loaded = function(req) {
    req.callback_info.dataSet = req.response;
    req.callback_info.refresh();
}

usermgmnt.refreshUsersList = function(evt, w) {
    oUserList = w.getParentByType(Window).body.getWidgetsByType(ListView)[0];
    usermgmnt.getUsers(oUserList);
}

usermgmnt.newUser = function(evt, w) {
    var oWin = w.parent.owner.parent.owner.getParentByType(Window);
    var oUserList = w.parent.owner.parent.owner.parent.parent.parent.getWidgetById('userslist');
    var sFolder = QuiX.root + oUserList.attributes.FolderID;
    oWin.showWindow(sFolder + '?cmd=new&cc=schemas.org.innoscript.security.User',
        function(win) {
            win.attributes.refreshlist = function(){usermgmnt.getUsers(oUserList)}
        }
    );
}

usermgmnt.deleteItem = function(evt, w) {
    var win = w.parent.owner.getParentByType(Window);
    var sCaption = w.getCaption();
    var desktop = document.desktop;

    _deleteItem = function(evt, w) {
        w.getParentByType(Dialog).close();
        var items = win.getWidgetById("userslist").getSelection();
        if (!(items instanceof Array)) items = [items];
        items.reverse();
        var _startDeleting = function(w) {
            w = w.callback_info || w;
            if (items.length > 0 && !w.attributes.canceled) {
                var item = items.pop();
                var pb = w.getWidgetById("pb");
                pb.increase(1);
                pb.widgets[1].setCaption(item.displayName);
                var xmlrpc = new XMLRPCRequest(QuiX.root + item.id);
                xmlrpc.oncomplete = _startDeleting;
                xmlrpc.callback_info = w;
                xmlrpc.onerror = function(req) {
                    w.close();
                }
                xmlrpc.callmethod('delete');
            }
            else {
                w.close();
                usermgmnt.getUsers(win.getWidgetById("userslist"));
            }
        }
        var dlg = generic.getProcessDialog(sCaption, items.length, _startDeleting);
    }

    desktop.msgbox(sCaption, 
        "Are you sure you want to delete the selected users/groups?",
        [
            ['Yes', 60, _deleteItem],
            ['No', 60]
        ],
        'images/messagebox_warning.gif', 'center', 'center', 260, 112);
}

usermgmnt.newGroup = function(evt, w) {
    var oWin = w.parent.owner.parent.owner.getParentByType(Window);
    var oUserList = oWin.getWidgetById('userslist');
    var sFolder = QuiX.root + oUserList.attributes.FolderID;
    oWin.showWindow(sFolder + '?cmd=new&cc=schemas.org.innoscript.security.Group',
        function(win) {
            win.attributes.refreshlist = function(){usermgmnt.getUsers(oUserList)}
        }
    );
}

usermgmnt.applyFilter = function(evt, w) {
    var userlist = w.parent.owner.getParentByType(Window).getWidgetById('userslist');
    userlist.attributes.filter = w.attributes.CC;
    usermgmnt.getUsers(userlist);
}

usermgmnt.exitApp = function(evt, w) {
    w.parent.owner.getParentByType(Window).close();
}

usermgmnt.usersListMenu_show = function(menu) {
    var oUserList = menu.owner.getWidgetsByType(ListView)[0];
    menu.options[1].disabled = (oUserList.selection.length == 0); //delete
    menu.options[3].disabled = !(oUserList.selection.length == 1 && oUserList.getSelection().haspsw); //reset password
    menu.options[4].disabled = !(oUserList.selection.length == 1); //properties
} 

usermgmnt.showProperties = function(evt, w) {
    var oUserList = w.parent.owner.getWidgetsByType(ListView)[0];
    generic.showObjectProperties(null, null, oUserList.getSelection(),
        function(){usermgmnt.getUsers(oUserList);}
    );
}

usermgmnt.loadItem = function(evt, w) {
    var oUserList = w;
    generic.showObjectProperties(null, null, oUserList.getSelection(),
        function(){usermgmnt.getUsers(oUserList);}
    );
}

usermgmnt.showResetPasswordDialog = function(evt, w) {
    var oWindow = w.parent.owner.getParentByType(Window);
    var oUserList = w.parent.owner.getWidgetsByType(ListView)[0];
    var user_url = QuiX.root + oUserList.getSelection().id;
    oWindow.showWindow(user_url + '?cmd=resetpsw');
}

usermgmnt.resetPassword = function(evt, w) {
    var oDialog = w.getParentByType(Dialog);
    var user_uri = oDialog.attributes.UserURI;
    var sPass1 = oDialog.body.getWidgetById('password1').getValue();
    var sPass2 = oDialog.body.getWidgetById('password2').getValue();
    if (sPass1==sPass2) {
        var xmlrpc = new XMLRPCRequest(user_uri);
        xmlrpc.oncomplete = function(req){
            req.callback_info.close()
        }
        xmlrpc.callback_info = oDialog;
        xmlrpc.callmethod('resetPassword', sPass1);
    }
    else {
        document.desktop.msgbox("Error", 
            "Passwords are not identical!",
            "Close",
            "images/error.png", 'center', 'center', 260, 112);
    }
}

usermgmnt.about = function(evt, w) {
    document.desktop.msgbox(
        w.getCaption(),
        "User and Groups Management v0.1<br/>(c)2005 Innoscript",
        [['OK', 60]],
        'images/messagebox_info.gif', 'center', 'center', 260, 112
    );
}
    '''
    app.width.value = '600'
    app.height.value = '400'
    app.left.value = 'center'
    app.top.value = 'center'
    app.icon.value = 'images/group.gif'
    app.resourcesImportPath.value = 'resources.systemstrings.resources'
    app.isResizable.value = True
    app.canMaximize.value = True
    app.canMinimize.value = True
    app.inheritRoles = False
    app.security = {'administrators': 8}
    db.putItem(app, None)
    sys.stdout.write('[OK]\n')

    sys.stdout.write('Creating OQL Query Performer application...')
    app = schemas.org.innoscript.common.Application()
    app._id = 'oqlqueryperf'
    app._parentid = 'apps'
    app.displayName.value = 'OQL Query Performer'
    app._isSystem = True
    app._owner = sOwner
    app.modifiedBy = sOwner
    app._created = ftime
    app.modified = ftime
    app.interface.value = '''
<a:splitter orientation="h" spacing="0" width="100%%" height="100%%">
    <a:pane length="24">
        <a:menubar width="100%%" height="100%%">
            <a:menu caption="File">
                <a:menuoption caption="New query" onclick="queryPerformer.newQuery"></a:menuoption>
                <a:sep></a:sep>
                <a:menuoption img="images/exit.gif" caption="Exit" onclick="queryPerformer.exitApp"></a:menuoption>
            </a:menu>
            <a:menu caption="Edit">
                <a:menuoption img="images/configure.gif" caption="Options" onclick="queryPerformer.showSettings"></a:menuoption>
            </a:menu>
            <a:menu caption="About">
                <a:menuoption img="images/about16.gif" caption="About OQL Query Performer" onclick="queryPerformer.about"></a:menuoption>
            </a:menu>
        </a:menubar>
    </a:pane>
    <a:pane length="-1" overflow="auto" id="clientArea">
        <a:prop name="tree_caption" value="displayName"></a:prop>
        <a:prop name="use_image" type="bool" value="0"></a:prop>
        <a:prop name="tree_image" value="__image__"></a:prop>
        <a:file display="none"></a:file>
    </a:pane>
</a:splitter>
    '''
    app.script.value = '''
function queryPerformer() {}

queryPerformer.exitApp = function(evt, w) {
    w.parent.owner.getParentByType(Window).close();
}

queryPerformer.newQuery = function(evt, w) {
    var clientArea = w.parent.owner.getParentByType(Window).getWidgetById('clientArea');
    clientArea.parseFromString(
        '<a:window xmlns:a="http://www.innoscript.org/quix" ' +
            'width="480" height="300" status="true" ' +
            'resizable="true" close="true" minimize="true" maximize="true">' +
            '<a:wbody>' +
                '<a:splitter orientation="h" spacing="0" width="100%%" height="100%%">' +
                    '<a:pane length="34">' +
                        '<a:toolbar width="100%%" height="100%%">' +
                            '<a:tbbutton width="30" img="images/save22.gif" onclick="queryPerformer.saveQuery"></a:tbbutton>' +
                            '<a:tbbutton width="30" img="images/execute22.gif" onclick="queryPerformer.executeQuery"></a:tbbutton>' +
                        '</a:toolbar>' +
                    '</a:pane>' +
                    '<a:pane length="-1">' +
                        '<a:splitter bgcolor="white" orientation="h" interactive="true" width="100%%" height="100%%">' +
                            '<a:pane length="100">' +
                                '<a:field id="oqlquery" type="textarea" width="100%%" height="100%%" border="0">' +
                                '</a:field>' +
                            '</a:pane>' +
                            '<a:pane length="-1">' +
                                '<a:splitter orientation="v" interactive="true" width="100%%" height="100%%">' +
                                    '<a:pane id="resultsarea" length="50%%" overflow="auto" padding="4,4,4,4"></a:pane>' +
                                    '<a:pane length="-1">' +
                                        '<a:listview id="proplist" width="100%%" height="100%%" cellborder="1">' +
                                            '<a:listheader>' +
                                                '<a:column width="100" caption="Name" name="name"></a:column>' +
                                                '<a:column width="80" caption="Type" name="type"></a:column>' +
                                                '<a:column width="120" caption="Value" name="value"></a:column>' +
                                            '</a:listheader>' +
                                        '</a:listview>' +
                                    '</a:pane>' +
                                '</a:splitter>' +
                            '</a:pane>' +
                        '</a:splitter>' +
                    '</a:pane>' +
                '</a:splitter>' +
            '</a:wbody>' +
        '</a:window>'
    );
}

queryPerformer.saveQuery = function(evt, w) {
    var win = w.getParentByType(Window);
    var file = win.parent.widgets[0];
    file.saveTextFile( win.getTitle() + '.oql', win.getWidgetById('oqlquery').getValue() );
}

queryPerformer.executeQuery = function(evt, w) {
    var oWin = w.getParentByType(Window);
    var oPane = oWin.getWidgetById('resultsarea');
    sQuery = oWin.getWidgetById('oqlquery').getValue();
    
    var xmlrpc = new XMLRPCRequest(QuiX.root);
    xmlrpc.oncomplete = queryPerformer.executeQuery_oncomplete;
    xmlrpc.callback_info = oPane;
    xmlrpc.callmethod('executeOqlCommand', sQuery);
}

queryPerformer.executeQuery_oncomplete = function(req) {
    var oPane = req.callback_info;
    var oWin = oPane.getParentByType(Window);
    var oResults = req.response;
    oPane.clear();
    if (oResults.length > 0) {
        var treeNode, caption;
        var schema = req.response[0];
        
        var oTree = oPane.parseFromString(
            '<a:tree xmlns:a="http://www.innoscript.org/quix" onexpand="queryPerformer.expandNode" onselect="queryPerformer.showProps"></a:tree>',
            function (w) {
                queryPerformer.expandArray(w, oResults, oWin.getParentByType(Window).getWidgetById('clientArea').attributes);
            }
        );
        oWin.setStatus('Query returned ' + oResults.length + ' rows/objects.');
    } else {
        oPane.parseFromString('<a:rect xmlns:a="http://www.innoscript.org/quix"><a:xhtml>No results found</a:xhtml></a:rect>');
    }
}

queryPerformer.about = function(evt, w) {
    document.desktop.msgbox(
        w.getCaption(),
        "OQL Query Performer v0.1<br/>(c)2005 Innoscript",
        [['OK', 60]],
        'images/messagebox_info.gif', 'center', 'center', 260, 112
    );
}

queryPerformer.showProps = function(w) {
    var obj = w.attributes.obj;
    if (obj) {
        var oAttr, dataset = [];
        var oList = w.getParentByType(Splitter).getWidgetById('proplist');
        for (var attr in obj) {
            oAttr = obj[attr];
            if (typeof(oAttr) != 'function')
                dataset.push({
                    name: attr,
                    type: queryPerformer.getType(obj[attr]),
                    value: oAttr
                });
        }
        oList.dataSet = dataset;
        oList.refresh();
    }
}

queryPerformer.expandNode = function(w) {
    var oAttr, oNode;
    var obj = w.attributes.obj;
    if (w.childNodes.length==0) {
        if (obj instanceof Array) {
            queryPerformer.expandArray(w, obj, w.getParentByType(Window).parent.attributes);
        } else {
            for (var attr in obj) {
                oAttr = obj[attr];
                if (typeof(oAttr) != 'function' && (oAttr instanceof Array)) {
                    oNode = new TreeNode(
                        {haschildren:(oAttr.length>0), caption: attr, disabled:(oAttr.length==0)},
                        w
                    );
                    oNode.attributes.obj = oAttr;
                }
                else if (oAttr.constructor == Object) {
                    oNode = new TreeNode(
                        {haschildren:true, caption: attr},
                        w
                    );
                    oNode.attributes.obj = oAttr;
                }
            }
            if (w.childNodes.length == 0) {
                oNode = new TreeNode (
                    {haschildren:false, caption: 'Empty', disabled:true},
                    w
                );
            }
        }
    }    
}

queryPerformer.expandArray = function(w, array, options) {
    var caption, nodeimg;
    var tree_caption = options.tree_caption;
    for (var i=0; i<array.length; i++) {
        nodeimg = (options.use_image)?array[i][options.tree_image]:null;
        caption = (array[i][tree_caption])?array[i][tree_caption]:'Object ' + i.toString();
        treeNode = new TreeNode(
            {
                haschildren:(array.length>0),
                img: nodeimg,
                caption: caption, disabled:(array.length==0)
            }, w
        );
        treeNode.attributes.obj = array[i];
    }
}

queryPerformer.getType = function(obj) {
    var typ = 'Unknown';
    if (obj instanceof Date) {
        typ = 'Date';
    } else if (typeof(obj) == 'boolean') {
        typ = 'Boolean';
    } else if (obj instanceof Array) {
        typ = 'Array';
    } else if (obj instanceof String) {
        typ = 'String';
    } else if (obj instanceof Number) {
        typ = 'Number';
    }
    return typ;
}

queryPerformer.showSettings = function(evt, w) {
    var win = w.parent.owner.getParentByType(Window);
    var ca = win.getWidgetById("clientArea");
    win.showWindowFromString(
        '<a:dialog xmlns:a="http://www.innoscript.org/quix" width="300" height="160" ' +
            'title="' + w.getCaption() + '" img="images/configure.gif" left="center" top="center">' +
            '<a:wbody>' +
                '<a:label top="7" left="5" caption="Attribute for tree captions:" width="140"></a:label>' +
                '<a:field id="tree_caption" width="120" height="22" top="5" left="140" value="' + ca.attributes.tree_caption + '"></a:field>' +
                '<a:field id="use_image" type="checkbox" top="30" left="5" value="' + ca.attributes.use_image + '" onclick="queryPerformer.toggleUseImage"></a:field>' +
                '<a:label top="32" left="25" caption="Use image for tree nodes" width="200"></a:label>' +
                '<a:label top="62" left="5" caption="Image attribute:" width="120"></a:label>' +
                '<a:field id="tree_image" disabled="' + !(ca.attributes.use_image) + '" width="120" height="22" top="60" left="90" value="' + ca.attributes.tree_image + '"></a:field>' +
            '</a:wbody>' +
            '<a:dlgbutton width="60" height="22" caption="OK" onclick="queryPerformer.applyPreferences"></a:dlgbutton>' +
            '<a:dlgbutton width="60" height="22" onclick="__closeDialog__" caption="Cancel"></a:dlgbutton>' +
        '</a:dialog>'
    );
}

queryPerformer.toggleUseImage = function(evt, w) {
    if (w.getValue())
        w.parent.getWidgetById('tree_image').enable();
    else
        w.parent.getWidgetById('tree_image').disable();
}

queryPerformer.applyPreferences = function(evt, w) {
    var win = w.getParentByType(Window);
    var appWin = win.opener;
    var ca = appWin.getWidgetById('clientArea');
    ca.attributes.tree_caption = win.getWidgetById('tree_caption').getValue();
    ca.attributes.use_image = win.getWidgetById('use_image').getValue();
    ca.attributes.tree_image = win.getWidgetById('tree_image').getValue();
    win.close();
}
    '''
    app.width.value = '600'
    app.height.value = '400'
    app.left.value = 'center'
    app.top.value = 'center'
    app.icon.value = 'images/oql.gif'
    app.resourcesImportPath.value = 'resources.systemstrings.resources'
    app.isResizable.value = True
    app.canMaximize.value = True
    app.canMinimize.value = True
    app.inheritRoles = False
    app.security = {'administrators': 8}
    db.putItem(app, None)
    sys.stdout.write('[OK]\n')

    db.close()
    sys.stdout.write('Store initialization completed successfully.')

sys.exit()
