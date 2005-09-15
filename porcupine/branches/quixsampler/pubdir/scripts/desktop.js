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