function queryPerformer() {}

queryPerformer.exitApp = function(evt, w) {
    w.parent.owner.getParentByType(Window).close();
}

queryPerformer.newQuery = function(evt, w) {
    var clientArea = w.parent.owner.getParentByType(Window).getWidgetById('clientArea');
    clientArea.parseFromUrl('queryperformer/newquery.quix');
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
	var treeNode, caption;
	var oPane = req.callback_info;
	var oWin = oPane.getParentByType(Window);
	var oResults = req.response;
	oPane.clear();
    if (oResults.length > 0) {
        var schema = req.response[0];
        oPane.parseFromString(
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
        "OQL Query Performer v0.1<br/>(c)2005-2006 Innoscript",
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
                    oNode = new TreeNode({
                         haschildren:(oAttr.length>0),
                         caption: attr,
                         disabled:(oAttr.length==0)
                    });
                    oNode.attributes.obj = oAttr;
                    w.appendChild(oNode);
                }
                else if (oAttr.constructor == Object) {
                    oNode = new TreeNode({
                        haschildren:true,
                        caption: attr
                    });
                    oNode.attributes.obj = oAttr;
                    w.appendChild(oNode);
                }
            }
            if (w.childNodes.length == 0) {
                oNode = new TreeNode ({
                    haschildren:false,
                    caption: 'Empty',
                    disabled:true
                });
                w.appendChild(oNode);
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
        treeNode = new TreeNode({
            haschildren:(array.length>0),
            img: nodeimg,
            caption: caption, disabled:(array.length==0)
        });
        treeNode.attributes.obj = array[i];
        w.appendChild(treeNode);
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