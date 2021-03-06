var desktop = function() {}

desktop.autoRun = true;

desktop.logoff = function(evt, w) {
	var desktop = document.desktop;
	desktop.msgbox(w.attributes.logoff, 
		w.attributes.ask_logoff,
		[
			[desktop.attributes['YES'], 60, 'desktop.do_logoff'],
			[desktop.attributes['NO'], 60]
		],
		'desktop/images/shutdown.gif', 'center', 'center', 260, 112)
}

desktop.loginAs = function(evt, w) {
	document.desktop.parseFromUrl(QuiX.root + '?cmd=loginas');
}

desktop.showAbout = function (evt, w) {
	document.desktop.parseFromUrl(QuiX.root + '?cmd=about');
}

desktop.showSettings = function(evt, w) {
	document.desktop.parseFromUrl(QuiX.root + '?cmd=user_settings');
}

desktop.do_logoff = function() {
	var xmlrpc = new XMLRPCRequest(QuiX.root);
	xmlrpc.oncomplete = function() {
		window.location.reload();
	}
	xmlrpc.callmethod('logoff');
}

desktop.getWindows = function(menu) {
	var menu_option;
	var oWindows = document.desktop.getWidgetsByType(Window);
	while (menu.options.length > 2)
		menu.options[2].destroy();
	for (var i=0; i<oWindows.length; i++) {
		if (oWindows[i].parent == document.desktop && !oWindows[i].opener) {
			menu_option = menu.addOption({
				caption: oWindows[i].getTitle(),
				img: oWindows[i].getIcon(),
				onclick: desktop.showWindow
			});
			menu_option.attributes.win = oWindows[i];
		}
	}
}

desktop.showWindow = function(evt, w) {
	var oWindow = w.attributes.win;
	oWindow.bringToFront();
	if (oWindow.isMinimized) oWindow.minimize();
}

desktop.minimizeAll = function() {
	var oWindows = document.desktop.getWidgetsByType(Window);
	for (var i=0; i<oWindows.length; i++) {
		if (oWindows[i].parent == document.desktop)
			if (!oWindows[i].isMinimized) oWindows[i].minimize();
	}
}

desktop.displayTime = function(timer) {
	timer.div.innerHTML = new Date().format("time");	
}

desktop.applyUserSettings = function(evt ,w) {
	var oDialog = w.getParentByType(Dialog);
	var oForm = oDialog.getWidgetsByType(Form)[0];
	oForm.submit(
		function(){
			if (oForm.getElements()[0].getValue() != oDialog.attributes.ORIGINAL_TASK_POS)
				document.location.reload();
			else
				oDialog.close();
		}
	);
}

desktop.runApplication = function(w) {
	var autoRun = w.parent.attributes.AUTO_RUN;
	var runMaximized = w.parent.attributes.RUN_MAXIMIZED;
	if (autoRun != '' && desktop.autoRun) {
		document.desktop.parseFromUrl(QuiX.root	+ autoRun,
			function(w) {
				if (runMaximized) {
					w.maximize();
				}
			}
		);
	}
}

desktop.launchHyperSearch = function(evt, w) {
	var query_string = '';
	var win;
	try {
		win = w.getParentByType(Window);
	}
	catch(e) {}
	if (win)
		query_string = '?id=' + win.attributes.FolderID;
	document.desktop.parseFromUrl('hypersearch/hypersearch.quix' + query_string);
}
