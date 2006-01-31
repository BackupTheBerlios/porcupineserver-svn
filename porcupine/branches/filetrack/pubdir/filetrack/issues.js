filetrack.getIssues = function(w) {
	if (!(w instanceof ListView))
		w = w.getWidgetsByType(ListView)[0];
	var page_num = w.attributes.page;
	var page_size = w.getParentByType(Window).getWidgetById('clientarea').attributes.pagesize;
	var page_control = w.getParentByType(Splitter).getWidgetById("page_num");
    var query = "select id, __image__ as image, displayName, " +
        "(if issueClosed then 'filetrack/images/issue_closed.gif' " +
        "else 'filetrack/images/issue_open.gif') as issueStatus, " +
        "modified from deep('" + filetrack.ISSUES_FOLDER + "')";
    
    if (w.attributes.filter != '')
        query += " where issueClosed=" + w.attributes.filter;
    
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

filetrack.searchIssues = function(evt, w) {
	var query;
	var cont = w.parent;
	var scope = [filetrack.ISSUES_FOLDER];
	var search_results = cont.parent.parent.getWidgetById('search_results');
	var maxresults = cont.getParentByType(Window).getWidgetById('clientarea').attributes.max_results;
	
    query = filetrack.getIssuesSearchQuery(w, scope);
    
    var xmlrpc = new XMLRPCRequest(QuiX.root);
    xmlrpc.oncomplete = function(req) {
	    search_results.dataSet = req.response[0];
	    total = req.response[1];
	    search_results.refresh();
	    if (total > maxresults) {
			document.desktop.msgbox("%(WARNING)s", "%(DISPLAYING)s " + maxresults + "/" + total,
				[['%(CLOSE)s', 60]], '/images/messagebox_warning.gif',
				'center', 'center', 260, 112);
	    }
    }
    xmlrpc.callmethod('executeOqlCommand', query, [0, maxresults]);
}

filetrack.issuescontext_show = function(menu) {
	var oEntryList = menu.owner.getWidgetsByType(ListView)[0];
	menu.options[2].disabled = !(oEntryList.selection.length == 1);
}
