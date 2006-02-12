/************************
Menus
************************/
//menu option
function MenuOption(params) {
	params.height = params.height || 21;
	params.align = 'left';
	params.imgalign = 'left';
	params.width = '100%';
	params.padding = '4,0,3,2';
	params.onmouseover = MenuOption__onmouseover;
	params.onmouseout = MenuOption__onmouseout;
	params.onclick = QuiX.getEventWrapper(MenuOption__onclick, params.onclick);

	this.base = Icon;
	this.base(params);

	this.div.style.whiteSpace = 'nowrap';
	if (QuiX.browser == 'moz')
		this.setDisplay('table');
	this.setPosition('relative');

	this.subMenu = null;
	this.type = params.type;
	this.selected = (params.selected=='true' || params.selected==true)?true:false;
}

MenuOption.prototype = new Icon;

MenuOption.prototype.addOption = function(params) {
	if (!this.subMenu)
		this.subMenu = new ContextMenu({}, this);
	return this.subMenu.addOption(params);
}

MenuOption.prototype.redraw = function(bForceAll) {
	if (this.subMenu) {
		this.addPaddingOffset('Right', 16)
		var w = new Icon({
			left: 'this.parent.getWidth(true) - 12',
			top: 'center',
			padding: '0,0,0,0',
			overflow: 'hidden',
			width: 12,
			height: 12,
			img: 'images/submenu.gif'
		});
		this.appendChild(w);
	}
	if (this.type) {
		if (this.selected) {
			switch (this.type) {
				case 'radio':
					this.img = 'images/menu_radio.gif';
					break;
				case 'check':
					this.img = 'images/menu_check.gif';
			}
		}
		else
			this.img = null;
		bForceAll = true;
	}
	if (!this.img)
		this.setPadding([22,8,3,2]);
	else
		this.setPadding([4,8,3,2]);
	Icon.prototype.redraw(bForceAll, this);
}

MenuOption.prototype.select = function() {
	switch (this.type) {
		case 'radio':
			if (!this.selected) {
				if (this.id) {
					var oOptions = this.parent.getWidgetById(this.id);
					if (oOptions.length) {
						for(var i=0; i<oOptions.length; i++)
							oOptions[i].selected = false;
					}
					else
						oOptions.selected = false;
				}
				this.selected = true;
			}
			break;
		case 'check':
			this.selected = !this.selected;
	}
}


function MenuOption__onmouseout(evt, w) {
	w.div.className = 'option';
}

function MenuOption__onmouseover(evt, w) {
	if (w.parent.activeSub) {
		w.parent.activeSub.close();
		w.parent.activeSub = null;
	}
	w.div.className = 'option over';
	if (w.subMenu) {
		w.parent.activeSub = w.subMenu;
		w.subMenu.show(w.parent, w.getWidth(true), w.getTop(true)-w.parent.getPadding()[2]);
		
		if (w.subMenu.getScreenTop() + w.subMenu.height > document.desktop.getHeight(true)) {
			w.subMenu.top -= w.subMenu.getScreenTop() + w.subMenu.height - document.desktop.getHeight(true);
			w.subMenu.redraw();
		}

		if (w.subMenu.getScreenLeft() + w.subMenu.width > document.desktop.getWidth(true)) {
			w.subMenu.left = - w.subMenu.width;
			w.subMenu.redraw();
		}
	}
}

function MenuOption__onclick(evt, w) {
	if (w.type) w.select();
	w.div.className = 'option';
	QuiX.cleanupOverlays();
}

//context menu
function ContextMenu(params, owner) {
	this.id = params.id;
	this.base = Widget;
	this.onshow = getEventListener(params.onshow);
	this.isOpen = false;
	
	if (this.id) {
		if (owner._id_widgets[this.id])
			owner._id_widgets[this.id].push(this);
		else
			owner._id_widgets[this.id] = [this];
	}

	this.base({
		width: 80,
		border:1,
		onmousedown: QuiX.stopPropag
	});
	var rect = new Widget({
		width: '22',
		height: '100%',
		bgcolor: 'silver',
		overflow: 'hidden'
	});
	this.appendChild(rect);
	this.div.className = 'contextmenu';

	this.options = [];
	this.owner = owner;
	this.activeSub = null;
}

ContextMenu.prototype = new Widget;

ContextMenu.prototype.show = function(w, x, y) {
	var oOption, optionWidth;
	var iHeight = 0;
	
	if (!this.isOpen) {
		if (this.onshow) this.onshow(this);
		this.left = x;
		this.top = y;
		w.appendChild(this);

		for (var i=0; i<this.options.length; i++) {
			oOption = this.options[i];
			optionWidth = oOption.div.clientWidth;
			iHeight += oOption.div.offsetHeight;
			if (optionWidth > this.width)
				this.width = optionWidth + 16;
		}
		
		this.height = iHeight + 2;
		
		if (this.top + this.height > document.desktop.getHeight(true))
			this.top = y - this.height;
		if (this.left + this.width > document.desktop.getWidth(true))
			this.left = x - this.width;
		
		this.redraw();
		this.bringToFront();
		
		if (w==document.desktop)
			document.desktop.overlays.push(this);
		
		this.isOpen = true;
	}
}

ContextMenu.prototype.close = function() {
	if (this.parent == document.desktop)
		document.desktop.overlays.removeItem(this);
	this.detach();
	this.isOpen = false;
}

ContextMenu.prototype.addOption = function(params) {
	var oOption;
	if (params != -1) { //not a separator
		oOption = new MenuOption(params);
	}
	else {
		oOption = new Widget({
			width : 'this.parent.getWidth()-22',
			height : 2,
			left : 22,
			border : 1,
			overflow : 'hidden'
		});
		oOption.div.className = 'separator';
		oOption.setPosition('relative');
	}
	this.appendChild(oOption);
	this.options.push(oOption);
	return oOption;
}

// Menu Bar
function MBar(params) {
	params = params || {};
	params.border=1;
	params.padding = '2,4,1,1';
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'menubar';
	var iSpacing = params.spacing || 8;
	this.spacing = parseInt(iSpacing);
	this.contextmenus = [];
}

MBar.prototype = new Widget;

MBar.prototype.addRootMenu = function(params) {
	var oMenubar = this;
	var ind = this.contextmenus.length;
	var oMenu = new Widget({
		border: 0,padding: '4,4,3,3',
		onclick: function(evt){oMenubar._menuclick(evt, oMenu, ind)},
		onmouseover: function(){oMenubar._menuover(oMenu)},
		onmouseout: function(){oMenubar._menuout(oMenu)}
	});
	this.appendChild(oMenu);
	oMenu.setDisplay('inline');
	oMenu.setPosition();
	oMenu.div.className = 'menu';
	oMenu.div.style.marginRight = this.spacing + 'px';
	
	oMenu.div.innerHTML = params.caption;
	var oCMenu = new ContextMenu(params, oMenu);
	this.contextmenus.push(oCMenu);
	return(oCMenu);
}

MBar.prototype._menuover = function(oMenu) {
	oMenu.setBorderWidth(1);
	oMenu.setPadding([3,3,2,2]);
	oMenu.div.className = 'menu over';
}

MBar.prototype._menuout = function(oMenu) {
	oMenu.setBorderWidth(0);
	oMenu.setPadding([4,4,3,3]);
	oMenu.div.className = 'menu';
}

MBar.prototype._menuclick = function(evt, oMenu, ind) {
	oMenu.div.className = 'menu selected';
	var oCMenu = this.contextmenus[ind];
	showWidgetContextMenu(oMenu, oCMenu);
	QuiX.stopPropag(evt);
}

function showWidgetContextMenu(w, menu) {
	var nx = w.getScreenLeft();
	var ny = w.getScreenTop() + w.div.offsetHeight;

	menu.show(document.desktop, nx, ny);
	

	if (ny + menu.height > document.desktop.getHeight(true)) {
		menu.top = menu.owner.getScreenTop() - menu.getHeight(true);
		menu.redraw();
	}

	if (nx + menu.width > document.desktop.getWidth(true)) {
		menu.left = menu.owner.getScreenLeft() + menu.owner.padding[0] - menu.getWidth(true);
		menu.redraw();
	}
}