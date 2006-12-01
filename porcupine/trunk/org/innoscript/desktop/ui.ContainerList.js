var containerList = function() {}

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
		var newOption1 = w.getWidgetById('menubar').menus[0].contextMenu.options[0];
		var newOption2 = w.getWidgetsByType(Box)[0].widgets[3].contextMenu.options[0];
		var containment = req.response.containment;
		newOption1.options = [];
		newOption1.subMenu = null;
		newOption2.options = [];
		newOption2.subMenu = null;
		if (req.response.user_role > 1 && containment.length>0) {
			var params, mo1, mo2;
			newOption1.enable();
			newOption2.enable();
			for (var i=0; i<containment.length; i++) {
				params = {
					caption: containment[i][0],
					img: containment[i][2],
					onclick: containerList.createItem
				}
				mo1 = newOption1.addOption(params);
				mo1.attributes.cc = containment[i][1];
				mo2 = newOption2.addOption(params);
				mo2.attributes.cc = containment[i][1];
			}
		}
		else {
			newOption1.disable();
			newOption2.disable();
		}
		if (w.attributes.history[w.attributes.history.length-1] != w.attributes.FolderID)
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
	if (oItemList.selection.length == 0) {
		menu.options[2].disable();//cut
		menu.options[3].disable();//copy
		menu.options[5].disable();//delete
		menu.options[7].disable();//move to
		menu.options[8].disable();//copy to
		menu.options[9].disable();//rename
		menu.options[11].disable();//properties
	}
	else {
		menu.options[2].enable();//cut
		menu.options[3].enable();//copy
		menu.options[5].enable();//delete
		menu.options[7].enable();//move to
		menu.options[8].enable();//copy to
		menu.options[9].enable();//rename
		menu.options[11].enable();//properties
	}
	if (QuiX.clipboard.items.length>0 && QuiX.clipboard.contains=='objects')
		menu.options[4].enable();//paste
	else
		menu.options[4].disable();//paste
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
	generic.getProcessDialog(w.getCaption(), items.length, _startPasting);
}

containerList.copyMove = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var oList = win.getWidgetById("itemslist");
	var action = w.attributes.action;
	win.showWindow(QuiX.root + oList.getSelection().id  + '?cmd=selectcontainer&action=' + action,
		function(w) {
			w.attachEvent("onclose", containerList.doCopyMove);
			w.attributes.method = action;
		}
	);
}

containerList.doCopyMove = function(dlg) {
	if (dlg.buttonIndex == 0) {
		var method = (dlg.attributes.method=='copy')?'copyTo':'moveTo';
		var targetid = dlg.getWidgetById('tree').getSelection().getId();
		
		var xmlrpc = new XMLRPCRequest(QuiX.root + dlg.attributes.ID);
		xmlrpc.oncomplete = function(req) {
			if (method!='copyTo') {
				containerList.getContainerInfo(dlg.opener);
			}
		}
		xmlrpc.callmethod(method, targetid);
	}
}

containerList.rename = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var oList = win.getWidgetById("itemslist");
	win.showWindow(QuiX.root + oList.getSelection().id  + '?cmd=rename',
		function(w) {
			w.attachEvent("onclose", containerList.doRename);
		}
	);
}

containerList.doRename = function(dlg) {
	if (dlg.buttonIndex == 0) {
		var new_name = dlg.getWidgetById('new_name').getValue();
		
		var xmlrpc = new XMLRPCRequest(QuiX.root + dlg.attributes.ID);
		xmlrpc.oncomplete = function(req) {
			containerList.getContainerInfo(dlg.opener);
		}
		xmlrpc.callmethod('rename', new_name);
	}
}

containerList.deleteItem = function(evt, w) {
	var win = w.parent.owner.getParentByType(Window);
	var sCaption = w.getCaption();
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

	desktop.msgbox(w.getCaption(), 
		"Are you sure you want to delete the selected items?",
		[
			[desktop.attributes['YES'], 60, _deleteItem],
			[desktop.attributes['NO'], 60]
		],
		'desktop/images/messagebox_warning.gif', 'center', 'center', 260, 112);
}
