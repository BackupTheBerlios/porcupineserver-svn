var containerList= function() {}

containerList.loadItem = function(evt, w, o) {
	var oWin = w.getParentByType(Window);
	if (o.isCollection) {
		oWin.attributes.FolderID = o.id;
		containerList.getContainerInfo(oWin);
	}
	else {
		generic.showObjectProperties(null, null, o,
			function() {
				containerList.getContainerInfo(oWin);
			}
		);
	}
}

containerList.closeWindow = function (evt, w) {
	w.parent.owner.getParentByType(Window).close();
}

containerList.getContainerInfo = function(w, bAddPath) {
	var folderUri = QuiX.root + w.attributes.FolderID;
	var xmlrpc = new XMLRPCRequest(folderUri);
	xmlrpc.oncomplete = function(req) {
		var itemlist;
		w.setTitle(req.response.displayName);
		w.attributes.ParentID = req.response.parentid;
		var sFullPath = req.response.path;
		w.getWidgetById('path').setValue(sFullPath);
		itemlist = w.getWidgetById('itemslist');
		if (w.attributes.FolderID=='')
			w.getWidgetById('btn_up').disable();
		else
			w.getWidgetById('btn_up').enable();
		itemlist.dataSet = req.response.contents;
		itemlist.refresh();
		if (bAddPath) {
			var cmb_path = w.getWidgetById('path');
			var pathExists = false;
			for (var i=0; i<cmb_path.options.length; i++) {
				if (cmb_path.options[i].value.toString() == sFullPath) {
					pathExists = true;
					break;
				}
			}
			if (!pathExists) cmb_path.addOption({ caption: sFullPath, value: sFullPath });
		}
		var newOption1 = w.getWidgetById('menubar').contextmenus[0].options[0];
		var newOption2 = w.getWidgetById('contextmenu').options[0];
		var containment = req.response.containment;
		newOption1.options = [];
		newOption2.options = [];
		if (req.response.user_role > 1 && containment.length>0) {
			var mo;
			newOption1.disabled=false;
			newOption2.disabled=false;
			for (var i=0; i<containment.length; i++) {
				mo = new MenuOption ({
					caption: containment[i][0],
					img: containment[i][2],
					onclick: containerList.createItem
				});
				mo.attributes.cc = containment[i][1];
				newOption1.options.push(mo);
				newOption2.options.push(mo);
			}
		}
		else {
			newOption1.disabled=true;
			newOption2.disabled=true;
		}
		w.attributes.history.push(w.attributes.FolderID);
	}
	xmlrpc.callmethod('getInfo');
}

containerList.createItem = function(evt, w) {
	var cc = w.attributes.cc;
	var owin = w.parent.owner.parent.owner.getParentByType(Window);
	document.desktop.parseFromUrl(QuiX.root + owin.attributes.FolderID + '?cmd=new&cc=' + cc,
		function(w) {
			w.attributes.refreshlist = function() {
				containerList.getContainerInfo(owin);
			}
		}
	);
}

containerList.upOneFolder = function(evt, w) {
	var win = w.getParentByType(Window);
	win.attributes.FolderID = win.attributes.ParentID;
	containerList.getContainerInfo(win);
}

containerList.goBack = function(evt, w) {
	var win = w.getParentByType(Window);
	var win_history = win.attributes.history;
	if (win_history.length > 1) {
		win_history.pop();
		win.attributes.FolderID = win_history.pop();
		containerList.getContainerInfo(win);
	}
}

containerList.refresh = function(evt, w) {
	var win = w.getParentByType(Window);
	containerList.getContainerInfo(win);
}

containerList.navigateTo = function(evt, w) {
	var folder_id = w.parent.parent.getWidgetById('path').getValue();
	var win = w.getParentByType(Window);
	win.attributes.FolderID = folder_id;
	containerList.getContainerInfo(win, true);
}

containerList.listMenu_show = function(menu) {
	var oItemList = menu.owner.getWidgetsByType(ListView)[0];
	menu.options[2].disabled = (oItemList.selection.length == 0);//cut
	menu.options[3].disabled = (oItemList.selection.length == 0);//copy
	menu.options[4].disabled = QuiX.clipboard.items.lenth==0 || QuiX.clipboard.contains!='objects';//paste
	menu.options[5].disabled = (oItemList.selection.length == 0);//delete
	menu.options[7].disabled = !(oItemList.selection.length == 1);//move to
	menu.options[8].disabled = !(oItemList.selection.length == 1);//copy to
	menu.options[9].disabled = !(oItemList.selection.length == 1);//rename
	menu.options[11].disabled = !(oItemList.selection.length == 1);//properties
}

containerList.showProperties = function(evt, w) {
	var oWindow = w.parent.owner.getParentByType(Window);
	var oItemList = w.parent.owner.getWidgetsByType(ListView)[0];
	generic.showObjectProperties(null, null, oItemList.getSelection(),
		function() {
			containerList.getContainerInfo(oWindow);
		}
	);
}

containerList.updateCliboard = function(evt, w) {
	var oList = w.parent.owner.getParentByType(Window).getWidgetById("itemslist");
	var selection = oList.getSelection();
	QuiX.clipboard.action = w.attributes.action;
	QuiX.clipboard.contains = 'objects';
	if (selection instanceof Array)
		QuiX.clipboard.items = selection;
	else
		QuiX.clipboard.items = [selection];
}

containerList.paste = function(evt, w) {
	var items = [].concat(QuiX.clipboard.items);
	items.reverse();
	var win = w.parent.owner.getParentByType(Window);
	var target = win.attributes.FolderID;
	var method = (QuiX.clipboard.action=='copy')?'copyTo':'moveTo';
	
	var _startPasting = function(w) {
		w = w.callback_info || w;
		if (items.length > 0 && !w.attributes.canceled) {
			var item = items.pop();
			var pb = w.getWidgetById("pb");
			pb.increase(1);
			pb.widgets[1].setCaption(item.displayName);
			var xmlrpc = new XMLRPCRequest(QuiX.root + item.id);
			xmlrpc.oncomplete = _startPasting;
			xmlrpc.callback_info = w;
			xmlrpc.onerror = function(req) {
				w.close();
			}
			xmlrpc.callmethod(method, target);
		} else {
			w.close();
			containerList.getContainerInfo(win);
		}
	}
	generic.getProcessDialog(w.caption, items.length, _startPasting);
}

containerList.copyMove = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var oList = win.getWidgetById("itemslist");
	var action = w.attributes.action;
	document.desktop.parseFromUrl(QuiX.root + oList.getSelection().id  + '?cmd=selectcontainer&action=' + action,
		function(w) {
			w.attributes.window = win;
			w.attributes.refreshFunc = containerList.getContainerInfo;
		}
	);
}

containerList.rename = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var oList = win.getWidgetById("itemslist");
	document.desktop.parseFromUrl(QuiX.root + oList.getSelection().id  + '?cmd=rename',
		function(w) {
			w.attributes.refreshlist = function() {
				containerList.getContainerInfo(win);
			}
		}
	);
}

containerList.deleteItem = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var sCaption = w.caption;
	var desktop = document.desktop;

	var _deleteItem = function(evt, w) {
		w.getParentByType(Dialog).close();
		var items = win.getWidgetById("itemslist").getSelection();
		if (!(items instanceof Array)) items = [items];
		items.reverse();
		var _start = function(w) {
			w = w.callback_info || w;
			if (items.length > 0 && !w.attributes.canceled) {
				var item = items.pop();
				var pb = w.getWidgetById("pb");
				pb.increase(1);
				pb.widgets[1].setCaption(item.displayName);
				var xmlrpc = new XMLRPCRequest(QuiX.root + item.id);
				xmlrpc.oncomplete = _start;
				xmlrpc.callback_info = w;
				xmlrpc.onerror = function(req) {
					w.close();
				}
				xmlrpc.callmethod('delete');
			}
			else {
				w.close();
				containerList.getContainerInfo(win);
			}
		}
		generic.getProcessDialog(sCaption, items.length, _start);
	}

	desktop.msgbox(w.caption, 
		"Are you sure you want to delete the selected items?",
		[
			[desktop.attributes['YES'], 60, _deleteItem],
			[desktop.attributes['NO'], 60]
		],
		'images/messagebox_warning.gif', 'center', 'center', 260, 112);
}
