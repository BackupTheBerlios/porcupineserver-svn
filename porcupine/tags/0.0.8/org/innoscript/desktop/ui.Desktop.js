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

desktop.showAbout = function (evt, w) {
	var desktop = document.desktop;
	desktop.parseFromUrl(QuiX.root + '?cmd=about');
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
		if (oWindows[i].parent == document.desktop) {
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
	oDialog.getWidgetsByType(Form)[0].submit(
		function(){
			oDialog.close();
			document.desktop.clear();
			desktop.autoRun = false;
			document.desktop.parseFromUrl(QuiX.root);
		}
	);
}

desktop.runApplication = function(w) {
	var autoRun = w.attributes.AUTO_RUN;
	var runMaximized = w.attributes.RUN_MAXIMIZED;
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
	var win = w.getParentByType(Window);
	if (win)
		query_string = '?id=' + win.attributes.FolderID;
	document.desktop.parseFromUrl('hypersearch/hypersearch.quix' + query_string);
}
