function selectPersons() {}

selectPersons.CONTACT_FOLDER = 'j0Cft3a6';

selectPersons.selectPersons = function(evt, w) {
	var oDialog = w.getParentByType(Dialog);
	oDialog.showWindow(QuiX.root + '?cmd=selectpersons');
	QuiX.stopPropag(evt);
}

selectPersons.searchPersons = function(evt, w) {
	var query;
	var search_for = w.parent.getWidgetById('search_for').getValue();
	var search_results = w.parent.parent.getWidgetById('search_results');
	var sFrom = "deep('" + selectPersons.CONTACT_FOLDER + "'),'users'";
	search_results.clear();
    query = "select id as value, __image__ as img, displayName as caption " +
		"from " + sFrom + " where '" + search_for + "' in caption " +
		"and contentclass in ['schemas.org.innoscript.collab.Contact'," +
		"'schemas.org.innoscript.security.User'] " +
		"order by caption asc";
    var xmlrpc = new XMLRPCRequest(QuiX.root);
    xmlrpc.oncomplete = function(req) {
		for (var i=0; i<req.response.length; i++) {
			search_results.addOption(req.response[i]);
		}
    }
    xmlrpc.callmethod('executeOqlCommand', query);
}

selectPersons.setPerson = function(evt, w) {
	var fname = w.attributes.field_name;
	var dlg = w.getParentByType(Dialog);
	var select = dlg.getWidgetById('search_results');
	var field = dlg.opener.getWidgetById(fname);
	var field_name = dlg.opener.getWidgetById(fname + '_name');
	for (var i=0; i<select.options.length; i++) {
		if (select.options[i].isSelected) {
			field.setValue(select.options[i].value);
			field_name.setValue(select.options[i].caption);
			break;
		}
	}
}

selectPersons.setCC = function(evt, w) {
	var dlg = w.getParentByType(Dialog);
	var select = dlg.getWidgetById('search_results');
	var field = dlg.opener.getWidgetById('cc');
	for (var i=0; i<select.options.length; i++) {
		if (select.options[i].isSelected) {
			field.addOption({
				value: select.options[i].value,
				img: select.options[i].img,
				caption: select.options[i].caption
			});
		}
	}
}