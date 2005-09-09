filetrack.applyPreferences = function(evt, w) {
	var options_dlg = w.getParentByType(Dialog);
	var app_win = options_dlg.attributes.win;
	var clientarea = app_win.getWidgetById('clientarea');
	
	var new_page_size = parseInt(options_dlg.getWidgetById('pagesize').getValue());
	var maxresults = parseInt(options_dlg.getWidgetById('max_results').getValue());
	
	if (isNaN(new_page_size) || new_page_size < 1) {
		document.desktop.msgbox("%(ERROR)s", "%(INVALID_PAGE_SIZE)s",
			[['%(CLOSE)s', 60]], '/images/error32.gif', 'center', 'center', 260, 112);
		return;
	}
	
	if (isNaN(maxresults)) {
		document.desktop.msgbox("%(ERROR)s", "%(INVALID_MAX_RESULTS)s",
			[['%(CLOSE)s', 60]], '/images/error32.gif', 'center', 'center', 260, 112);
		return;
	}

	if (new_page_size!=clientarea.attributes.pagesize) {
		clientarea.attributes.pagesize = new_page_size;
		filetrack.getLogEntries(app_win.getWidgetById('log_list'));
		var ilist = app_win.getWidgetById('issue_list');
		if (ilist) filetrack.getIssues(ilist);
	}

	clientarea.attributes.max_results = maxresults;

	options_dlg.close();
}

filetrack.getArchiveSets = function(w) {
	var archive_sets = w.getWidgetById('archive_sets');
	filetrack.getSearchScopes(
		archive_sets,
		['schemas.org.innoscript.filetrack.LogArchiveSet']);
}

filetrack.archiveEntries = function(evt, w) {
	var dlg = w.getParentByType(Dialog);
	var destination = dlg.getWidgetById('archive_sets').getValue();
	var date_range = [dlg.getWidgetById('entryDate_from').getValue(),
		dlg.getWidgetById('entryDate_to').getValue()];
	if (!destination) {
		document.desktop.msgbox("%(ERROR)s", "%(WARN_SELECT_DEST_SET)s",
			[['%(CLOSE)s', 60]], '/images/messagebox_warning.gif', 'center', 'center', 260, 112);
		return;
	}
	var xmlrpc = new XMLRPCRequest(QuiX.root + dlg.attributes.PID);
    xmlrpc.oncomplete = function(req) {
    	dlg.close();
		document.desktop.msgbox("%(INFO)s", req.response + " %(ENTRIES_ARCHIVED)s",
			[['%(CLOSE)s', 60]], '/images/messagebox_info.gif', 'center', 'center', 260, 112);
    }
    xmlrpc.callmethod('archive', destination, date_range);
}

filetrack.newArchive = function(evt, w) {
	var dlg = w.getParentByType(Dialog);
	document.desktop.parseFromUrl(QuiX.root + filetrack.ARCHIVES_FOLDER +
		'?cmd=new&cc=schemas.org.innoscript.filetrack.LogArchiveSet',
		function(w) {
			w.attributes.refreshlist = function() {
				filetrack.getArchiveSets(dlg);
			}
		}
	);
}

filetrack.renameArchive = function(evt, w) {
	var dlg = w.getParentByType(Dialog);
	var destination = dlg.getWidgetById('archive_sets').getValue();
	if (destination) {
		document.desktop.parseFromUrl(QuiX.root + destination + '?cmd=rename',
			function(req) {
				req.widget.attributes.refreshlist = function() {
					filetrack.getArchiveSets(dlg);
				}
			}
		);
	}
}
