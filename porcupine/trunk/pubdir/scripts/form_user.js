function formUser() {}

formUser.createUser = function(evt, w) {
	var oForm = w.getParentByType(Dialog).getWidgetsByType(Form)[0];
	var sPass1 = oForm.getWidgetById('password').getValue();
	var sPass2 = oForm.getWidgetById('password2').getValue();
	if (sPass1 != sPass2) {
		document.desktop.msgbox("Error", 
			"Passwords are not identical!",
			document.desktop.attributes['CLOSE'],
			"images/error32.gif", 'center', 'center', 260, 112);
	}
	else
		oForm.submit(formUser.update);
}

formUser.update = function(response, form) {
	var dlg = form.getParentByType(Dialog);
	dlg.attributes.refreshlist();
	dlg.close();
}