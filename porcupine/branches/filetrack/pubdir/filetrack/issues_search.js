filetrack.getIssuesSearchQuery = function(w, scope) {
	var cont = w.parent.parent.parent;
	var query, conditions, fields, field_value;

	for (var i=0; i<scope.length; i++) {
		scope[i] = "'" + scope[i] + "'";
	}
    query = "select id, __image__ as image, displayName, " +
        "(if issueClosed then 'filetrack/images/issue_closed.gif' " +
        "else 'filetrack/images/issue_open.gif') as issueStatus, " +
        "modified from " + scope.join(',');
    
    fields = w.parent.attributes.fields;
    
    conditions = [];
	for (var i=0; i<fields.length; i++) {
		switch (fields[i]) {
			case 'displayName':
			case 'description':
				field_value = cont.getWidgetById(fields[i]).getValue();
				conditions.push("'" + field_value + "' in " + fields[i]);
				break;
			case 'issueClosed':
				field_value = (cont.getWidgetById(fields[i]).getValue()=='1')?'true':'false';
				conditions.push(fields[i] + '=' + field_value);
				break;
			case 'modified':
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
    
    query += ' order by modified desc';
    
    return(query);
}