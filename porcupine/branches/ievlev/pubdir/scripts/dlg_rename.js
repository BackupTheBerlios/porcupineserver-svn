function rename() {}

rename.rename = function(evt, w) {
	var dlg = w.getParentByType(Dialog);
	var new_name = dlg.getWidgetById('new_name').getValue();
	
	var xmlrpc = new XMLRPCRequest(QuiX.root + dlg.attributes.ID);
	xmlrpc.oncomplete = function(req) {
		if (dlg.attributes.refreshlist) dlg.attributes.refreshlist();
		dlg.close();
	}
	xmlrpc.callmethod('rename', new_name);
}