function login() {}

login.login = function (evt, w) {
	var sUser = document.getWidgetById('user').getValue();
	var sPassword = document.getWidgetById('password').getValue();
	var login_dialog = document.getWidgetById('logindialog');
	var sLoginServiceUrl = login_dialog.attributes.ServiceURI;
	var xmlrpc = new XMLRPCRequest(sLoginServiceUrl);
	xmlrpc.oncomplete = login.login_oncomplete;
	xmlrpc.callback_info = w;
	xmlrpc.onerror = login.login_onerror;
	xmlrpc.callmethod('login', sUser, sPassword);
	login_dialog.setStatus('Please wait...');
	w.disable();
	document.body.style.cursor = 'wait';
}

login.login_oncomplete = function (req) {
	if (req.response) {
		var root_ui = QuiX.root;
		document.desktop.clear();
		document.desktop.parseFromUrl(root_ui);
	}
	else {
		req.callback_info.enable();
		var oDialog = req.callback_info.getParentByType(Dialog);
		document.desktop.msgbox("Login failed", 
			oDialog.attributes.FailMsg,
			document.desktop.attributes.CLOSE,
			'images/error32.gif', 'center', 'center', 260, 120);
		oDialog.setStatus('');
	}
	document.body.style.cursor = '';
}

login.login_onerror = function(req) {
	req.callback_info.enable();
	req.callback_info.getParentByType(Dialog).setStatus('');
}