function selectObjectsDialog() {}

selectObjectsDialog.showFolders = function(evt, w) {
	var dialog = w.getParentByType(Dialog);
	var main_splitter = dialog.body.getWidgetById('spl_main');
	var btn_search = dialog.body.getWidgetById('btn_search');

	if (w.value == 'off') {
		main_splitter.panes[0].height = 0;
	}
	else {
		if (btn_search.value == 'on')
			btn_search.toggle();
		else
			if (main_splitter.panes[0].height==0) main_splitter.panes[0].height = '50%';
		main_splitter.panes[0].getWidgetById("search").hide();
		main_splitter.panes[0].getWidgetById("folders").show();
	}
	main_splitter.redraw();
}

selectObjectsDialog.showSearch = function(evt, w) {
	var dialog = w.getParentByType(Dialog);
	var main_splitter = dialog.body.getWidgetById('spl_main');
	var btn_folders = dialog.body.getWidgetById('btn_folders');

	if (w.value == 'off') {
		main_splitter.panes[0].height = 0;
	}
	else {
		if (btn_folders.value == 'on')
			btn_folders.toggle();
		else
			if (main_splitter.panes[0].height==0) main_splitter.panes[0].height = '50%';
		main_splitter.panes[0].getWidgetById("folders").hide();
		main_splitter.panes[0].getWidgetById("search").show();
	}
	main_splitter.redraw();
}

selectObjectsDialog.search = function(evt, w) {
	var oDialog = w.getParentByType(Dialog);
	var cc = oDialog.attributes.CC;
	var oRect = w.parent;
	var oTree = w.getParentByType(Splitter).getWidgetById('tree');
	var sName = oRect.getWidgetById('displayName').getValue();
	var sDesc = oRect.getWidgetById('description').getValue();
	var isDeep = oRect.getWidgetById('deep').getValue();
	var sID = oTree.getSelection().getId();
	var sFrom;
	
	if (isDeep)
		sFrom = "deep('" + sID + "')";
	else
		sFrom = "'" + sID + "'";

	var sCommand = "select id as value, __image__ as img, displayName as caption " +
		"from " + sFrom;
	var conditions = [];
	if (cc!='*') conditions.push(selectObjectsDialog.getConditions(cc));
	if (sName!='') conditions.push("'" + sName + "' in displayName");
	if (sDesc!='') conditions.push("'" + sDesc + "' in description");
	if (conditions.length>0) {
		sCommand += ' where ' + conditions.join(' and ');
	}

	var xmlrpc = new XMLRPCRequest(QuiX.root);
	xmlrpc.oncomplete = selectObjectsDialog.refreshList_oncomplete;
	xmlrpc.callback_info = w;
	xmlrpc.callmethod('executeOqlCommand', sCommand);
}

selectObjectsDialog.select = function(evt, w) {
	var oDialog = w.getParentByType(Dialog);
	var source = oDialog.getWidgetById("selection");
	var target = oDialog.attributes.target;
	oDialog.attributes.select_click(evt, w, source, target);
}

selectObjectsDialog.refreshList = function(treeNodeSelected) {
	var oDialog = treeNodeSelected.tree.getParentByType(Dialog);
	var xmlrpc = new XMLRPCRequest(QuiX.root);
	var cc = oDialog.attributes.CC;
	var sOql = "select id as value, __image__ as img, displayName as caption " +
		"from '" + treeNodeSelected.getId() + "'";
	if (cc != '*') sOql += " where " + selectObjectsDialog.getConditions(cc);
	xmlrpc.oncomplete = selectObjectsDialog.refreshList_oncomplete;
	xmlrpc.callback_info = treeNodeSelected.tree;
	xmlrpc.callmethod('executeOqlCommand', sOql);
}

selectObjectsDialog.getConditions = function(s) {
	lst = s.split('|');
	for (var i=0; i<lst.length; i++) lst[i] = "contentclass='" + lst[i] + "'";
	return "(" + lst.join(' or ') + ")"
}

selectObjectsDialog.refreshList_oncomplete = function(req) {
	var oDialog = req.callback_info.getParentByType(Dialog);
	var oSelect = oDialog.getWidgetById("selection");
	var oItems = req.response;
	oSelect.clear();
	for (var i=0; i<oItems.length; i++) {
		oSelect.addOption(oItems[i]);
	}
}
