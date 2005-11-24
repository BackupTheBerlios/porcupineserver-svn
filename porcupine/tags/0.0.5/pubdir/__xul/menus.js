/************************
Menus
************************/
//menu option
function MenuOption(params) {
	this.caption = params.caption;
	this.id = params.id;
	this.height = params.height || 21;
	this.img = params.img;
	this.onclick = getEventListener(params.onclick);
	this.type = params.type;
	this.disabled = (params.disabled=='true' || params.disabled==true)?true:false;
	delete params.disabled;
	this.options = [];
	this.isSelected = (params.selected=='true')?true:false;
	this.attributes = params.attributes || {};
	this.base = Widget;
}

MenuOption.prototype = new Widget;

MenuOption.prototype.show = function(contextMenu) {
	var lpadding, rpadding, oOption = this;
	lpadding = 24;
	rpadding = (this.options.length==0)?8:24;
	this.base({
		id : this.id,
		height : this.height,
		top : contextMenu._top,
		padding : lpadding + ',' + rpadding + ',3,2',
		width : '100%',
		disabled: this.disabled,
		onmouseover: MenuOption__onmouseover,
		onmouseout: MenuOption__onmouseout,
		onclick: MenuOption__onclick,
		attributes : this.attributes
	});
	contextMenu.appendChild(this);
	this.setDisplay('inline');
	this.setPos();
	this.div.appendChild( document.createTextNode(this.caption));
	this.div.style.whiteSpace = 'nowrap';
	if (this.options.length>0) {
		var w = new Icon({
			left: 'this.parent.getWidth(true) - 12',
			top: 'center',
			padding: '0,0,0,0',
			width: 8,
			height: 8,
			img: 'images/submenu.gif'
		});
		this.appendChild(w);
		var oSubOptions = this.options;
		var oSubMenu = new ContextMenu({}, this);
		oSubMenu.options = oSubOptions;
		this.subMenu = oSubMenu;
	}
	
	if (this.type && this.isSelected) {
		this._addIndicator();
	} else if (this.img) {
		var img = QuiX.getImage(this.img);
		img.border=0;
		img.align='absmiddle';
		img.style.marginRight='4px';
		img.width=16;
		img.height=16;
		this.padding[0] -= 20;
		this.repad();
		this.div.insertBefore(img, this.div.firstChild);
	}
}

MenuOption.prototype._addIndicator = function() {
	var img;
	switch (this.type) {
		case 'radio':
			img = QuiX.getImage('images/menu_radio.gif');
			break;
		case 'check':
			img = QuiX.getImage('images/menu_check.gif');
	}
	img.width=16;
	img.height=16;
	img.border=0;
	img.align='absmiddle';
	img.style.marginRight='4px';

	this.padding[0] -= 20;
	this.repad();
	this.div.insertBefore(img, this.div.firstChild);
}

MenuOption.prototype.select = function () {
	switch (this.type) {
		case 'radio':
			if (!this.isSelected) {
				if (this.id) {
					var oOptions = this.parent.getWidgetById(this.id);
					if (oOptions.length) {
						for(var i=0; i<oOptions.length; i++)
							oOptions[i].isSelected = false;
					}
					else
						oOptions.isSelected = false;
				}
				this.isSelected = true;
			}
			break;
		case 'check':
			this.isSelected = !this.isSelected;
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
		w.subMenu.show(w.parent, w.getWidth(true), w.getTop(true)-w.parent.padding[2]);
		
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
	QuiX.cleanupOverlays();
	if (w.onclick) {
		w.onclick(evt, w);
	}
}

//context menu
function ContextMenu(params, owner) {
	this.options = [];
	this.owner = owner;
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
}

ContextMenu.prototype = new Widget;

ContextMenu.prototype.show = function(w,x,y) {
	var oOption, optionWidth, max_width=0;
	if (!this.isOpen) {
		this._top = 0;
		if (this.onshow) this.onshow(this);
		this.base({
			left:x,
			top:y,
			width: 60,
			border:1,
			padding:'1,1,1,1',
			onmousedown: QuiX.stopPropag
		});
		w.appendChild(this);
		
		var rect = new Widget({
			width: '22',
			height: '100%',
			bgcolor: 'silver',
			overflow: 'hidden'
		});
		
		this.appendChild(rect);
		
		this.div.className = 'contextmenu';
		for (var i=0; i<this.options.length; i++) {
			oOption = this.options[i];
			if (oOption!=-1) {
				oOption.show(this);
				optionWidth = oOption.div.offsetWidth;
				if (QuiX.browser == 'ie' && !oOption.img)
					optionWidth += oOption.padding[0];
				if (optionWidth > max_width) max_width = optionWidth;
				oOption.setDisplay();
				oOption.setPos('absolute');
			}
			else {
				oOption = new Widget({
					width:'this.parent.getWidth()-24',
					height:2, top:this._top, left:24,
					border:1, overflow:'hidden'
				});
				this.appendChild(oOption);
				oOption.div.className = 'separator';
			}
			this._top += oOption.height;
	
		}
		this.activeSub = null;
	
		if (!this.fixedheight) this.height = this._top + 4;
	
		if (this.top + this.height > document.desktop.getHeight(true))
			this.top = y - this.height;
		if (this.left + this.width > document.desktop.getWidth(true))
			this.left = x - this.width;
		
		this.width=max_width + 8;
		
		this.redraw();
		this.bringToFront();
		
		if (w==document.desktop) document.desktop.overlays.push(this);
		this.isOpen = true;
	}
}

ContextMenu.prototype.close = function() {
	if (this.parent == document.desktop)
		document.desktop.overlays.removeItem(this);
	this.destroy();
	this.isOpen = false;
}

ContextMenu.prototype.addOption = function(params) {
	var oOpt = new MenuOption(params);
	this.options.push(oOpt);
	return(oOpt);
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
	var oMenu = new Widget(
		{
			border: 0,padding: '4,4,3,3',
			onclick: function(evt){oMenubar._menuclick(evt, oMenu, ind)},
			onmouseover: function(){oMenubar._menuover(oMenu)},
			onmouseout: function(){oMenubar._menuout(oMenu)}
		});
	this.appendChild(oMenu);
	oMenu.setDisplay('inline');
	oMenu.setPos();
	oMenu.div.className = 'menu';
	oMenu.div.style.marginRight = this.spacing + 'px';
	
	oMenu.div.innerHTML = params.caption;
	var oCMenu = new ContextMenu(params, oMenu);
	this.contextmenus.push(oCMenu);
	return(oCMenu);
}

MBar.prototype._menuover = function(oMenu) {
	oMenu.borderWidth = 1;
	oMenu.padding = [3,3,2,2];
	oMenu.div.className = 'menu over';
	oMenu.repad();
}

MBar.prototype._menuout = function(oMenu) {
	oMenu.borderWidth = 0;
	oMenu.padding = [4,4,3,3];
	oMenu.div.className = 'menu';
	oMenu.repad();
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