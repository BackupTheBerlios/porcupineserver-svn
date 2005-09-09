filetrack.getLogEntries = function(w) {
	if (!(w instanceof ListView))
		w = w.getWidgetsByType(ListView)[0];
	var page_num = w.attributes.page;
	var page_size = w.getParentByType(Window).getWidgetById('clientarea').attributes.pagesize;
	var page_control = w.getParentByType(Splitter).getWidgetById("page_num");
    var query = "select id, __image__ as image, entryType, displayName, " +
        "sender.displayName as sender, receiver.displayName as receiver, " +
        "entryDate as received from '" + w.attributes.protocolID + "'";
    
    if (w.attributes.filter != -1)
        query += " where entryType=" + w.attributes.filter;
    
    if (w.orderby)
        query += " order by " + w.orderby + " " + w.sortorder;

    var offset = (page_num-1)*page_size;
    var range = [offset, offset + page_size];
    var xmlrpc = new XMLRPCRequest(QuiX.root);
    xmlrpc.oncomplete = function(req) {
	    w.dataSet = req.response[0];
	    total = req.response[1];
	    w.attributes.maxpage = Math.ceil(total/page_size) || 1;
	    page_control.setCaption(page_num + '/' + w.attributes.maxpage);
	    w.refresh();
    }
    xmlrpc.callmethod('executeOqlCommand', query, range);
}

filetrack.pcontext_show = function(menu) {
	var oEntryList = menu.owner.getWidgetsByType(ListView)[0];
	menu.options[2].disabled = (!(oEntryList.selection.length == 1 && oEntryList.getSelection().entryType==1));
	menu.options[3].disabled = !(oEntryList.selection.length == 1);
}

filetrack.reply = function(evt, w) {
	var plist = w.parent.owner.getWidgetById('log_list');
	var pid = plist.getSelection().id;
	document.desktop.parseFromUrl(QuiX.root + pid + '?cmd=reply',
		function(req) {
			req.widget.attributes.refreshlist = function() {
				filetrack.getLogEntries(plist);
			}
		}
	);
}
