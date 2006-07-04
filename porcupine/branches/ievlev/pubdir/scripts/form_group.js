function formGroup() {}

formGroup.createGroup = function(evt, w) {
	var oForm = w.getParentByType(Dialog).getWidgetsByType(Form)[0];
	oForm.submit(formGroup.update);
}

formGroup.update = function(response, form) {
	var dlg = form.getParentByType(Dialog);
	dlg.attributes.refreshlist();
	dlg.close();
}