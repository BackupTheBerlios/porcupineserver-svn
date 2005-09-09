filetrack.gotopage = function(evt, w) {
	var dlg = w.getParentByType(Dialog);
	var list = dlg.attributes.list;
	list.attributes.page = dlg.getWidgetById("page_num").getValue();
	dlg.close();
	filetrack.refreshList(list);
}

filetrack.firstpage = function(evt, w) {
	var list = w.getParentByType(Splitter).getWidgetsByType(ListView)[0];
	if (list.attributes.page > 1) {
		list.attributes.page=1;
		filetrack.refreshList(list);
	}
}

filetrack.previouspage = function(evt, w) {
	var list = w.getParentByType(Splitter).getWidgetsByType(ListView)[0];
	if (list.attributes.page > 1) {
		list.attributes.page--;
		filetrack.refreshList(list);
	}
}

filetrack.nextpage = function(evt, w) {
	var list = w.getParentByType(Splitter).getWidgetsByType(ListView)[0];
	if (list.attributes.page < list.attributes.maxpage) {
		list.attributes.page++;
		filetrack.refreshList(list);
	}
}

filetrack.lastpage = function(evt, w) {
	var list = w.getParentByType(Splitter).getWidgetsByType(ListView)[0];
	if (list.attributes.page < list.attributes.maxpage) {
		list.attributes.page = plist.attributes.maxpage;
		filetrack.refreshList(list);
	}
}

filetrack.applyFilter = function(evt, w) {
    var list = w.parent.owner.getParentByType(Splitter).getWidgetsByType(ListView)[0];
    list.attributes.filter = w.attributes.filter;
    filetrack.refreshList(list);
}
