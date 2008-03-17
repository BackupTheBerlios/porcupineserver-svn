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
	params.onclick = QuiX.getEventWrapper(params.onclick, MenuOption__onclick);

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
	if (this.subMenu)
		this.div.className = 'submenu';
	else
		this.div.className = '';

	if (this.type) {
		if (this.selected) {
			switch (this.type) {
				case 'radio':
					this.img = '__quix/images/menu_radio.gif';
					break;
				case 'check':
					this.img = '__quix/images/menu_check.gif';
			}
		}
		else
			this.img = null;
		bForceAll = true;
	}
	if (!this.img)
		this.setPadding([24,8,3,2]);
	else
		this.setPadding([5,8,3,2]);
	
	Icon.prototype.redraw(bForceAll, this);
}

MenuOption.prototype.destroy = function() {
	var parent = this.parent;
	parent.options.removeItem(this);

	if (this.base)
		this.base.prototype.destroy(this);
	else
		Widget.prototype.destroy(this);

	if (parent.options.length==0 && parent.owner instanceof MenuOption) {
		parent.owner.subMenu = null;
		parent.close();
		parent.destroy();
		parent = null;
	}
	
	if (parent) parent.redraw();
}

MenuOption.prototype.select = function() {
	switch (this.type) {
		case 'radio':
			if (!this.selected) {
				var id = this.getId();
				if (id) {
					var oOptions = this.parent.getWidgetById(id);
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

MenuOption.prototype.expand = function() {
	if (this.parent.activeSub && this.parent.activeSub != this.subMenu) {
		this.parent.activeSub.close();
	}
	if (this.subMenu && !this.subMenu.isOpen) {
		this.parent.activeSub = this.subMenu;
		this.subMenu.show(
			this.parent,
			this.getWidth(true),
			this.getScreenTop() - this.parent.getScreenTop() );
		
		if (this.subMenu.getScreenTop() + this.subMenu.height > document.desktop.getHeight(true)) {
			this.subMenu.top -= this.subMenu.getScreenTop() + this.subMenu.height - document.desktop.getHeight(true);
			this.subMenu.redraw();
		}
		
		if (this.subMenu.getScreenLeft() + this.subMenu.width > document.desktop.getWidth(true)) {
			this.subMenu.left = - this.subMenu.width;
			this.subMenu.redraw();
		}
	}
}

function MenuOption__onmouseout(evt, w) {
	if (w.subMenu)
		w.div.className = 'submenu';
	else
		w.div.className = '';
}

function MenuOption__onmouseover(evt, w) {
	w.expand();
	w.div.className += ' over';
}

function MenuOption__onclick(evt, w) {
	if (w.type) w.select();
	w.div.className = 'option';
	QuiX.cleanupOverlays();
}

//context menu
function ContextMenu(params, owner) {
	this.base = Widget;
	this.base({
		id : params.id,
		width : 100,
		border : 1,
		onmousedown : QuiX.stopPropag,
		onshow : params.onshow,
		onclose : params.onclose
	});
	this.div.className = 'contextmenu';
	if (QuiX.browser == 'moz' && QuiX.getOS() == 'MacOS')
	{
		var c = new Widget({
			width : '100%',
			height : '100%',
			overflow : 'auto'
		});
		this.appendChild(c);
		c = new Widget({
			width : '100%',
			height : '100%',
			overflow : 'hidden'
		});
		this.appendChild(c);
	}
	
	var rect = new Widget({
		width: '22',
		height: '100%',
		bgcolor: 'silver',
		overflow: 'hidden'
	});
	this.appendChild(rect);
	
	this.options = [];
	this.owner = owner;
	this.target = null;
	
	owner.contextMenu = this;
	owner.attachEvent('oncontextmenu', Widget__contextmenu);
	
	this.activeSub = null;
	this.isOpen = false;
}

QuiX.constructors['contextmenu'] = ContextMenu;
ContextMenu.prototype = new Widget;

ContextMenu.prototype.customEvents =
	Widget.prototype.customEvents.concat(['onshow', 'onclose']);

ContextMenu.prototype.destroy = function() {
	this.owner.detachEvent('oncontextmenu');
	this.owner.contextMenu = null;
	Widget.prototype.destroy(this);
}

ContextMenu.prototype.redraw = function(bForceAll) {
	var oOption, optionWidth;
	var iHeight = 0;
	
	for (var i=0; i<this.options.length; i++) {
		oOption = this.options[i];
		if (oOption instanceof Icon && QuiX.browser == 'ie')
			optionWidth = oOption.div.getElementsByTagName('SPAN')[0].offsetWidth + 26;
		else
			optionWidth = oOption.div.offsetWidth;
		if (optionWidth + 2 > this.width)
			this.width = optionWidth + 16;
		iHeight += oOption.div.offsetHeight;
	}
	
	this.height = iHeight + 2;
	
	if (this.top + this.height > document.desktop.getHeight(true))
		this.top = this.top - this.height;
	if (this.left + this.width > document.desktop.getWidth(true))
		this.left = this.left - this.width;

	Widget.prototype.redraw(bForceAll, this);
}

ContextMenu.prototype.show = function(w, x, y) {
	if (!this.isOpen) {
		var bShow = true;
		if (this._customRegistry.onshow) {
			var r = this._customRegistry.onshow(this);
			bShow = (r==false)?false:true;
		}
		if (bShow) {
			this.left = x;
			this.top = y;
			w.appendChild(this);
			this.redraw();
			if (w==document.desktop)
				document.desktop.overlays.push(this);
			this.isOpen = true;
		}
	}
}

ContextMenu.prototype.close = function() {
	if (this.activeSub) {
		this.activeSub.close();
	}
	if (this.owner.parent.activeSub)
		this.owner.parent.activeSub = null;
	if (this.parent == document.desktop)
		document.desktop.overlays.removeItem(this);
	this.detach();
	this.isOpen = false;
	if (this._customRegistry.onclose)
		this._customRegistry.onclose(this);
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
		oOption.destroy = MenuOption.prototype.destroy;
		oOption.div.className = 'separator';
		oOption.setPosition('relative');
	}
	this.appendChild(oOption);
	oOption.redraw();
	
	this.options.push(oOption);
	return oOption;
}

function Widget__contextmenu(evt, w) {
	w.contextMenu.target = QuiX.getTargetWidget(evt);
	w.contextMenu.show(document.desktop, evt.clientX, evt.clientY);
}

// Menu Bar
function MBar(params) {
	params = params || {};
	params.border = params.border || 1;
	params.padding = '2,4,0,1';
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'menubar';
	var iSpacing = params.spacing || 2;

	this.spacing = parseInt(iSpacing);
	this.menus = [];
}

QuiX.constructors['menubar'] = MBar;
MBar.prototype = new Widget;

MBar.prototype.redraw = function(bForceAll) {
	for (var i=0; i<this.menus.length; i++) {
		 this.menus[i].div.style.marginRight = this.spacing + 'px';
	}
	Widget.prototype.redraw(bForceAll, this);
}

MBar.prototype.addRootMenu = function(params) {
	var oMenu = new Label({
		top : 'center',
		border : 0,
		padding : '8,8,3,4',
		caption : params.caption,
		onclick : Menu__click,
		onmouseover : Menu__mouseover,
		onmouseout : Menu__mouseout
	});
	this.appendChild(oMenu);
	oMenu.div.className = 'menu';
	oMenu.setPosition();
	oMenu.destroy = Menu__destroy;
	oMenu.div.style.marginRight = this.spacing + 'px';
	
	this.menus.push(oMenu);

	var oCMenu = new ContextMenu(params, oMenu);
	oMenu.contextMenu = oCMenu;
	return(oCMenu);
}

function Menu__destroy() {
	this.parent.menus.removeItem(this);
	Label.prototype.destroy(this);	
}

function Menu__click(evt, w) {
	w.div.className = 'menu selected';
	showWidgetContextMenu(w, w.contextMenu);
	QuiX.stopPropag(evt);
}

function Menu__mouseover(evt, w) {
	w.setBorderWidth(1);
	w.setPadding([7,7,2,3]);
	w.div.className = 'menu over';
}

function Menu__mouseout(evt, w) {
	w.setBorderWidth(0);
	w.setPadding([8,8,3,4]);
	w.div.className = 'menu';
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
		menu.left = menu.owner.getScreenLeft() - menu.getWidth(true);
		menu.redraw();
	}
}