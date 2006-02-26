var recycleBin= function() {}

recycleBin.loadItem = function(evt, w, o) {
	var oWin;
	if (o.isCollection) {
		oWin = w.getParentByType(Window);
		oWin.attributes.FolderID = o.id;
		containerList.getContainerInfo(oWin);
	}
	else {
		generic.showObjectProperties(null, null, o);
	}
}

recycleBin.listMenu_show = function(menu) {
	var oItemList = menu.owner.getWidgetsByType(ListView)[0];
	if (oItemList.selection.length == 0) {
		menu.options[0].disable();//restore
		menu.options[1].disable();//restore to
		menu.options[2].disable();//delete
		menu.options[4].disable();//empty
		menu.options[6].disable();//properties
	}
	else {
		menu.options[0].enable();//restore
		menu.options[1].enable();//restore to
		menu.options[2].enable();//delete
		menu.options[4].enable();//empty
		menu.options[6].enable();//properties
	}
}

recycleBin.getContainerInfo = function(w) {
	var folderUri = QuiX.root + w.attributes.FolderID;
	var xmlrpc = new XMLRPCRequest(folderUri);
	xmlrpc.oncomplete = function(req) {
		var itemlist;
		w.setTitle(req.response.displayName);
		w.attributes.ParentID = req.response.parentid;

		itemlist = w.getWidgetById('itemslist');

		itemlist.dataSet = req.response.contents;
		itemlist.refresh();
	}
	xmlrpc.callmethod('getInfo');
}

recycleBin.showProperties = function(evt, w) {
	var oWindow = w.parent.owner.getParentByType(Window);
	var oItemList = w.parent.owner.getWidgetsByType(ListView)[0];
	generic.showObjectProperties(null, null, oItemList.getSelection());
}

recycleBin.refresh = function(evt, w) {
	var win = w.getParentByType(Window);
	recycleBin.getContainerInfo(win);
}

recycleBin.restoreTo = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var oList = win.getWidgetById("itemslist");
	var action = w.attributes.action;
	document.desktop.parseFromUrl(QuiX.root + 
		oList.getSelection().id  + '?cmd=selectcontainer&action=' + action,
		function(w) {
			w.attributes.window = win;
			w.attributes.refreshFunc = recycleBin.getContainerInfo;
		}
	);
}

recycleBin.empty = function(evt, w) {
	var desktop = document.desktop;
	var win;
	var win_elem = (w.parent.owner)?w.parent.owner:w;
	win = win_elem.getParentByType(Window);
	var rbid = win.attributes.FolderID;
	
	var _empty = function(evt, w) {
		w.getParentByType(Dialog).close();
		var xmlrpc = new XMLRPCRequest(QuiX.root + rbid);
		xmlrpc.oncomplete = function(req) {
			recycleBin.getContainerInfo(win);
		}
		xmlrpc.callmethod('empty');
	}
	
	desktop.msgbox(w.getCaption(), 
		"Are you sure you want to empty the recycle bin?",
		[
			[desktop.attributes['YES'], 60, _empty],
			[desktop.attributes['NO'], 60]
		],
		'images/messagebox_warning.gif', 'center', 'center', 260, 112);
}

recycleBin.restoreItem = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var items = win.getWidgetById("itemslist").getSelection();
	if (!(items instanceof Array)) items = [items];
	items.reverse();
	var _startRestoring = function(w) {
		w = w.callback_info || w;
		if (items.length > 0) {
			var item = items.pop();
			var pb = w.getWidgetById("pb");
			pb.increase(1);
			pb.widgets[1].setCaption(item.displayName);
			var xmlrpc = new XMLRPCRequest(QuiX.root + item.id);
			xmlrpc.oncomplete = _startRestoring;
			xmlrpc.callback_info = w;
			xmlrpc.callmethod('restore');
		}
		else {
			w.close();
			recycleBin.getContainerInfo(win);
		}
	}
	var dlg = generic.getProcessDialog(w.getCaption(), items.length, _startRestoring);
}

recycleBin.deleteItem = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var sCaption = w.getCaption();
	var desktop = document.desktop;

	var _deleteItem = function(evt, w) {
		w.getParentByType(Dialog).close();
		var items = win.getWidgetById("itemslist").getSelection();
		if (!(items instanceof Array)) items = [items];
		items.reverse();
		var _startDeleting = function(w) {
			w = w.callback_info || w;
			if (items.length > 0) {
				var item = items.pop();
				var pb = w.getWidgetById("pb");
				pb.increase(1);
				pb.widgets[1].setCaption(item.displayName);
				var xmlrpc = new XMLRPCRequest(QuiX.root + item.id);
				xmlrpc.oncomplete = _startDeleting;
				xmlrpc.callback_info = w;
				xmlrpc.onerror = function(req) {
					w.close();
				}
				xmlrpc.callmethod('delete');
			}
			else {
				w.close();
				recycleBin.getContainerInfo(win);
			}
		}
		generic.getProcessDialog(sCaption, items.length, _startDeleting);
	}
	
	desktop.msgbox(w.getCaption(), 
		"Are you sure you want to PERMANENTLY delete the selected items?",
		[
			[desktop.attributes['YES'], 60, _deleteItem],
			[desktop.attributes['NO'], 60]
		],
		'images/messagebox_warning.gif', 'center', 'center', 280, 112);
}
