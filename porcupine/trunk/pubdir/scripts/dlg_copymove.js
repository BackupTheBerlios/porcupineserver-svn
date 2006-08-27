function copyMove() {}

copyMove.copyMove = function(evt, w) {
	var dlg = w.getParentByType(Dialog);
	var method = dlg.attributes.method;
	var targetid = dlg.getWidgetById('tree').getSelection().getId();
	
	if (method!='select_folder') {
		var xmlrpc = new XMLRPCRequest(QuiX.root + dlg.attributes.ID);
		xmlrpc.oncomplete = function(req) {
			if (method!='copyTo') {
				dlg.attributes.refreshFunc(dlg.attributes.window);
			}
			dlg.close();
		}
		xmlrpc.callmethod(method, targetid);
	}
	else {
		dlg.attributes.refreshFunc(dlg.attributes.window, dlg);
		dlg.close();
	}
}