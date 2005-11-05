var desktop = function() {}

desktop.logoff = function(evt, w) {
	var desktop = document.desktop;
	desktop.msgbox(w.attributes.logoff, 
		w.attributes.ask_logoff,
		[
			[desktop.attributes['YES'], 60, 'desktop.do_logoff'],
			[desktop.attributes['NO'], 60]
		],
		'images/shutdown.gif', 'center', 'center', 260, 112)
}

desktop.showAbout = function (evt, w) {
	var desktop = document.desktop;
	desktop.parseFromUrl(QuiX.root + '?cmd=about');
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
	menu.options = menu.options.slice(0,2);
	for (var i=0; i<oWindows.length; i++) {
		if (oWindows[i].parent == document.desktop) {
			menu_option = menu.addOption({
				caption: oWindows[i].getTitle(),
				img: oWindows[i].icon,
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
		if (oWindows[i].parent == document.desktop && oWindows[i].canMini)
			if (!oWindows[i].isMinimized) oWindows[i].minimize();
	}
}

desktop.displayTime = function(timer) {
	timer.div.innerHTML = new Date().format("time");	
}

desktop.check = function(t) {
	alert('timeout');
}