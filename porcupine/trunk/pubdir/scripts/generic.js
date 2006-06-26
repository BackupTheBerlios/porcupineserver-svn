function generic() {}

generic.showObjectProperties = function(evt, w, o, refresh_func) {
	document.desktop.parseFromUrl(QuiX.root	+ (o.id || o) + '?cmd=properties',
		function(w) {
			if (refresh_func) w.attributes.refreshlist = refresh_func;
		}
	);
}

generic.selectItems = function(evt, w) {
	var oDialog = w.getParentByType(Dialog);
	var oTarget = w.parent.parent.getWidgetsByType(SelectList)[0];
	var sFolderURI = oTarget.attributes.SelectFrom;
	var sCC = oTarget.attributes.RelatedCC;
	generic.selectObjects(oDialog, oTarget, generic.addSelectionToList, sFolderURI, sCC, 'true');
}

generic.selectItem = function(evt, w) {
	var oDialog = w.getParentByType(Dialog);
	var oTarget = w.parent;
	var sFolderURI = oTarget.attributes.SelectFrom;
	var sCC = oTarget.attributes.RelatedCC;
	generic.selectObjects(oDialog, oTarget, generic.addSelectionToField, sFolderURI, sCC, 'false');
}

generic.selectObjects = function(win, target, select_func, startFrom, contentclass, multiple) {
	win.showWindow(startFrom + '?cmd=selectobjects&cc=' + contentclass + '&multiple=' + multiple,
		function(win) {
			win.attributes['target'] = target;
			win.attributes['select_click'] = select_func;
		}
	);
}

generic.addSelectionToList = function(evt, w, source, target) {
	for (var i=0; i<source.options.length; i++) {
		var oOption = source.options[i];
		if (oOption.selected) {
			target.addOption(
				{
					img : oOption.img, 
					caption : oOption.getCaption(), 
					value : oOption.value
				}
			);
		}
	}
}

generic.addSelectionToField = function(evt, w, source, target) {
	for (var i=0; i<source.options.length; i++) {
		var oOption = source.options[i];
		if (oOption.selected) {
			target.getWidgetsByType(Field)[0].setValue(oOption.value);
			target.getWidgetsByType(Field)[1].setValue(oOption.getCaption());
			return;
		}
	}
}

generic.removeSelectedItems = function(evt, w) {
	var oSelectList = w.parent.parent.getWidgetsByType(SelectList)[0];
	oSelectList.removeSelected();
}

generic.clearReference1 = function(evt, w) {
	var fields = w.parent.getWidgetsByType(Field);
	fields[0].setValue('');
	fields[1].setValue('');
}

generic.updateItem = function(evt, w) {
	var oDialog = w.getParentByType(Dialog);
	var oForm = oDialog.getWidgetsByType(Form)[0];
	oForm.submit(
		function() {
			if (oDialog.attributes.refreshlist) oDialog.attributes.refreshlist();
			oDialog.close();
		}
	);
}

generic.openContainer = function(evt, w) {
	document.desktop.parseFromUrl(QuiX.root	+ w.attributes.folderID + '?cmd=list');
}

generic.runApp = function(evt,w) {
	var appID = w.attributes.ID;
	document.desktop.parseFromUrl(QuiX.root	+ appID + '?cmd=run');
}

generic.addSelectionToAclDataGrid = function(evt, w, source, target) {
	for (var i=0; i<source.options.length; i++) {
		var oOption = source.options[i];
		if (oOption.selected) {
			target.dataSet.push(
				{
					id : oOption.value, 
					displayName : oOption.getCaption(), 
					role: '1'
				}
			);
		}
	}
	target.refresh();
}

generic.rolesInherited_onclick = function(evt, w) {
	var _acl = w.parent.widgets[1];
	if (!w.getValue()) _acl.enable();
	else _acl.disable();
}

generic.getSecurity = function(tabcontrol, itab) {
	var acl_datagrid = tabcontrol.tabs[itab].getWidgetsByType(DataGrid)[0];
	var sObjectURI = tabcontrol.getParentByType(Form).action;
	var xmlrpc = new XMLRPCRequest(sObjectURI);
	xmlrpc.oncomplete = function(req) {
		acl_datagrid.dataSet = req.response;
		acl_datagrid.refresh();
	};
	xmlrpc.callmethod('getSecurity');
}

generic.addACLEntry = function(evt, w) {
	var oDialog = w.getParentByType(Dialog);
	var oDataGrid = w.parent.parent.getWidgetsByType(DataGrid)[0];
	var sFolderURI = QuiX.root + 'users';
	generic.selectObjects(oDialog, oDataGrid, generic.addSelectionToAclDataGrid, sFolderURI, '*');
}

generic.removeACLEntry = function(evt, w) {
	var oDataGrid = w.parent.parent.getWidgetsByType(DataGrid)[0];
	oDataGrid.removeSelected();
}

generic.computeSize = function(obj, value) {
	if (obj.size)
		return Math.round(obj.size/1024) + ' KB';
	else
		return '';
}

generic.getProcessDialog = function(title, steps, oncomplete) {
	var dlg = document.desktop.parseFromString('<a:dialog xmlns:a="http://www.innoscript.org/quix"'+
		' title="' + title + '" width="240" height="100" left="center" top="center">' +
		'<a:prop type="bool" name="canceled" value="0"></a:prop>' +
		'<a:wbody>' +
		'<a:progressbar id="pb" width="90%" height="24" left="center" top="center" ' +
		'maxvalue="' + steps + '">' +
		'<a:label align="center" width="100%" height="100%" caption="0%">' +
		'</a:label></a:progressbar></a:wbody>' +
		'<a:dlgbutton onclick="generic.cancelAction" width="70" height="22" caption="' + document.desktop.attributes.CANCEL + '"></a:dlgbutton>' +
		'</a:dialog>', oncomplete);
}

generic.cancelAction = function(evt, w) {
	w.getParentByType(Dialog).attributes.canceled = true;
}