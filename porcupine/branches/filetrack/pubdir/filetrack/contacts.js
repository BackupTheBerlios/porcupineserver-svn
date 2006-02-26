filetrack.showContactProps = function(evt, w) {
	var oList = w.parent.owner.getWidgetsByType(ListView)[0];
	document.desktop.parseFromUrl(QuiX.root	+ oList.getSelection().id + '?cmd=filetrackprops',
		function(w) {
			w.attributes.refreshlist = function(){filetrack.refreshList(oList)}
		}
	);
}

filetrack.selectletter = function(evt, w) {
	var clist = w.getParentByType(Window).getWidgetById('contact_list');
	var cheader = w.getParentByType(Window).getWidgetById('contacts_header');
	var letters = w.attributes.letters;
	cheader.div.getElementsByTagName('SPAN')[1].innerHTML = letters;
	clist.attributes.letters = letters;
	filetrack.getContacts(clist);
}

filetrack.getContacts = function(w) {
	var clist = w;
	var letters = clist.attributes.letters;

    var query = "select id, __image__ as image, displayName, company, email " +
        "from deep('" + filetrack.CONTACT_FOLDER + "') " +
        "where slice(displayName,0,1) in '" + letters + "' and " +
        "contentclass = 'schemas.org.innoscript.collab.Contact' " +
        "order by displayName asc";

    var xmlrpc = new XMLRPCRequest(QuiX.root);
    xmlrpc.oncomplete = function(req) {
	    clist.dataSet = req.response;
	    clist.refresh();
    }
    xmlrpc.callmethod('executeOqlCommand', query);
}

filetrack.ccontext_show = function(menu) {
	var oList = menu.owner.getWidgetsByType(ListView)[0];
	if (oList.selection.length == 0) {
		menu.options[2].disable();//delete
		menu.options[3].disable();//properties
	}
	else {
		menu.options[2].enable();//delete
		menu.options[3].enable();//properties
	}
}