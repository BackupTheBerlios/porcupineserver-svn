filetrack.getSearchScopes = function(w, ccs) {
	var sccs = "['" + ccs.join("','") + "']";
	w.clear();
    var query = "select id as value, __image__ as img, displayName as caption " +
        "from '" + filetrack.ROOT_FOLDER + "','" + filetrack.ARCHIVES_FOLDER + "' where " +
        "contentclass in " + sccs + " order by caption asc";

    var xmlrpc = new XMLRPCRequest(QuiX.root);
    xmlrpc.oncomplete = function(req) {
    	for (var i=0; i<req.response.length; i++) {
    		w.addOption(req.response[i]);
    	}
    }
    xmlrpc.callmethod('executeOqlCommand', query);
}

filetrack.getSearchQuery = function(w, scope) {
	var cont = w.parent.parent.parent;
	var query, conditions, fields, field_value;

	for (var i=0; i<scope.length; i++) {
		scope[i] = "'" + scope[i] + "'";
	}
    query = "select id, __image__ as image, displayName, sender.displayName as sender," +
        " receiver.displayName as receiver, entryDate as entrydate " +
        "from " + scope.join(',');
    
    fields = w.parent.attributes.fields;
    
    conditions = [];
	for (var i=0; i<fields.length; i++) {
		switch (fields[i]) {
			case 'displayName':
			case 'sender':
			case 'receiver':
				field_value = cont.getWidgetById(fields[i]).getValue();
				conditions.push("'" + field_value + "' in " + fields[i]);
				break;
			case 'entrydate':
				field_value = [
					cont.getWidgetById(fields[i] + '_from').getValue().toIso8601(),
					cont.getWidgetById(fields[i] + '_to').getValue().toIso8601()
				]
				conditions.push(fields[i] + " between date('" +
					field_value[0] + "') and date('" + field_value[1] + "')");
		}
	}
    
    if (conditions.length > 0) {
    	query += ' where ' + conditions.join(' and ');
    }
    
    query += ' order by entrydate desc';
    
    return(query);
}

filetrack.toggleSearchField = function(evt, w) {
	var cont = w.parent;
	var field_name = w.attributes.f;
	var field = cont.getWidgetById(field_name);
	if (w.getValue()) {
		if (field)
			field.enable();
		else {
			cont.getWidgetById('entrydate_from').enable();
			cont.getWidgetById('entrydate_to').enable();
		}
		cont.attributes.fields.push(field_name);
	}
	else {
		if (field)
			field.disable();
		else {
			cont.getWidgetById('entrydate_from').disable();
			cont.getWidgetById('entrydate_to').disable();
		}
		cont.attributes.fields.removeItem(field_name);
	}
}
