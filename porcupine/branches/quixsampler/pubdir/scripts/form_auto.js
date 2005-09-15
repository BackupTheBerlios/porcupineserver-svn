function autoform() {}

autoform.submit = function(evt, w) {
	var oForm = w.getParentByType(Dialog).getWidgetsByType(Form)[0];
	oForm.submit(autoform.update);
}

autoform.update = function(response, form) {
	var dlg = form.getParentByType(Dialog);
	dlg.attributes.refreshlist();
	dlg.close();
}

autoform.displayRelated = function (evt, w) {
	generic.showObjectProperties(null, null, {id : w.value});
}