/************************
Windows & Dialogs
************************/
// generic event handlers
function __closeDialog__(evt, w) {
	w.getParentByType(Window).close();
}

//Window class
function Window(params) {
	params = params || {};
	var overflow = params.oveflow;
	params.border = 1;
	params.padding = '1,1,1,1';
	params.opacity = (QuiX.effectsEnabled)?0:1;
	params.onmousedown = QuiX.getEventWrapper(Window__onmousedown,
												params.onmousedown);
	params.oncontextmenu = QuiX.getEventWrapper(Window__oncontextmenu,
												params.oncontextmenu);
	params.overflow = (QuiX.browser == 'moz' && QuiX.getOS() == 'MacOS')?
						'auto':'hidden';
	this.base = Widget;
	this.base(params);
	this.minw = params.minw || 120;
	this.minh = params.minh || 26;
	this.isMinimized = false;
	this.isMaximized = false;
	this.childWindows = [];
	this.opener = null;
	this._statex = 0;
	this._statey = 0;
	this._statew = 0;
	this._stateh = 0;
	this._childwindows = [];
	this.div.className = 'window';
	var box = new Box({
		width : '100%',
		height : '100%',
		orientation : 'v',
		spacing : 0
	});
	this.appendChild(box);
	//title
	this.title = new Box({
		height : 22,
		padding :'1,1,1,1',
		childrenalign : 'center',
		onmousedown : WindowTitle__onmousedown
	});
	this.title.div.className = 'header';
	box.appendChild(this.title);
	var t = new Icon({
		id : '_t',
		caption : params.title || 'Untitled',
		img : params.img,
		align : 'left',
		style : 'cursor:move'
	});
	this.title.appendChild(t);
	// control buttons
	this._addControlButtons();
	var canClose = (params.close=='true'||params.close==true)?true:false;
	var canMini = (params.minimize=='true'||params.minimize==true)?true:false;
	var canMaxi = (params.maximize=='true'||params.maximize==true)?true:false;
	if (!canMini)
		this.title.getWidgetById('2').hide();
	if (!canMaxi) {
		this.title.getWidgetById('1').hide();
		this.title.detachEvent('ondblclick');
	}
	if (!canClose)
		this.title.getWidgetById('0').hide();
	//client area
	this.body = new Widget({
		border : 0,
		overflow : overflow
	});
	this.body.div.className = 'body';
	box.appendChild(this.body);
	//status
	var stat = (params.status=="true"||params.status==true)?true:false;
	if (stat)
		this.addStatusBar();
	// resize handle
	var resizable = (params.resizable=="true"||params.resizable==true)?true:false;
	this.setResizable(resizable);
	if (QuiX.effectsEnabled) {
		var effect = new Effect({
			type : 'fade-in',
			auto : true,
			steps : 4
		});
		this.appendChild(effect);
		var mini_effect = new Effect({
			id : '_eff_mini',
			type : 'wipe-out',
			interval : 10,
			end : 0.1,
			steps : 5,
			oncomplete : Window__onminimize
		});
		this.appendChild(mini_effect);
		var maxi_effect = new Effect({
			id : '_eff_maxi',
			type : 'wipe-in',
			interval : 10,
			steps : 5,
			oncomplete : Window__onmaximize
		});
		this.appendChild(maxi_effect);
	}
}

QuiX.constructors['window'] = Window;
Window.prototype = new Widget;

Window.prototype.customEvents = Widget.prototype.customEvents.concat(['onclose']);

Window.prototype.images = [
	QuiX.getImage('__quix/images/win_close.gif'),
	QuiX.getImage('__quix/images/win_max.gif'),
	QuiX.getImage('__quix/images/win_min.gif'),
	QuiX.getImage('__quix/images/win_close_over.gif'),
	QuiX.getImage('__quix/images/win_max_over.gif'),
	QuiX.getImage('__quix/images/win_min_over.gif')
];

Window.prototype.setIcon = function(sUrl) {
	var icon = this.title.getWidgetById('_t');
	icon.setImageURL(sUrl);
	icon.redraw(true);
}

Window.prototype.getIcon = function() {
	var icon = this.title.getWidgetById('_t');
	return icon.getImageURL();
}

Window.prototype.setResizable = function(bResizable) {
	var oWindow = this;
	if (bResizable && !this._resizer) {
		this._resizer = new Widget({
			left : 'this.parent.getWidth()-16',
			top : 'this.parent.getHeight()-16',
			width : 16,
			height : 16,
			border : 0,
			overflow : 'hidden'
		});
		this.appendChild(this._resizer);
		this._resizer.div.className = 'resize';
		this._resizer.div.style.zIndex = 10000; //stay on top
		this._resizer.attachEvent('onmousedown',
			function(evt){
				oWindow._startResize(evt);
				QuiX.cancelDefault(evt);
				QuiX.stopPropag(evt);
			});
	}
	else if (!bResizable && this._resizer) {
		this._resizer.destroy();
		this._resizer = null;
	}
}

Window.prototype._addControlButtons = function() {
	var oControl, img;
	var oWindow = this;
	for (var iWhich=2; iWhich>-1; iWhich--) {
		oControl = new Widget({
			id : iWhich.toString(),
			width : 16,
			height : 16,
			onmouseover : oWindow._mouseoverControl,
			onmouseout : oWindow._mouseoutControl
		});
		img = this.images[iWhich].cloneNode(true);
		oControl.div.appendChild(img);
		oControl.div.style.cursor = 'default';
		oControl.attachEvent('onmousedown', QuiX.stopPropag);
		this.title.appendChild(oControl);
		switch(iWhich) {
			case 0:
				oControl.attachEvent('onclick', function(){
					if (oWindow.buttonIndex)
						oWindow.buttonIndex = -1;
					oWindow.close();
				});
				break;
			case 1:
				oControl.attachEvent('onclick', function(){oWindow.maximize()});
				this.title.attachEvent('ondblclick', 
					function(){
						if (!oWindow.isMinimized)
							oWindow.maximize();
					});
				break;
			case 2:
				oControl.attachEvent('onclick', function(){oWindow.minimize()});
		}
	}
}

Window.prototype.addControlButton = function(iWhich) {
	var oButton = this.title.getWidgetById(iWhich.toString());
	oButton.show();
	this.title.redraw();
}

Window.prototype.removeControlButton = function(iWhich) {
	var oButton = this.title.getWidgetById(iWhich.toString());
	oButton.hide();
	this.title.redraw();
}

Window.prototype.close = function() {
	QuiX.cleanupOverlays();
	if (this._customRegistry.onclose)
		QuiX.getEventListener(this._customRegistry.onclose)(this);
	while (this.childWindows.length != 0)
		this.childWindows[0].close();
	if (this.opener)
		this.opener.childWindows.removeItem(this);
	if (QuiX.effectsEnabled) {
		var oWindow = this;
		var effect = new Effect({
			type : 'fade-out',
			auto : true,
			steps : 4,
			oncomplete : function() {
				oWindow.destroy();
			}
		});
		this.appendChild(effect);
	}
	else	
		this.destroy();
}

Window.prototype.setTitle = function(s) {
	var icon = this.title.getWidgetById('_t');
	icon.setCaption(s);
}

Window.prototype.getTitle = function() {
	var icon = this.title.getWidgetById('_t');
	return icon.getCaption();
}

Window.prototype.addStatusBar = function() {
	if (!this.statusBar) {
		this.statusBar = new Label({
			height: 20,
			padding: '4,0,0,0',
			border: 1,
			overflow: 'hidden'
		});
		this.statusBar.div.className = 'status';
		this.widgets[0].appendChild(this.statusBar);
	}
}

Window.prototype.removeStatusBar = function() {
	if (this.statusBar) {
		this.statusBar.destroy();
		this.statusBar = null;
		this.redraw();
	}
}

Window.prototype.setStatus = function(s) {
	if (this.statusBar)
		this.statusBar.setCaption(s);
}

Window.prototype.getStatus = function() {
	if (this.statusBar)
		return this.statusBar.getCaption();
}

Window.prototype._mouseoverControl = function(evt, btn) {
	var id = btn.getId();
	btn.div.childNodes[0].src = Window.prototype.images[parseInt(id) + 3].src;
}

Window.prototype._mouseoutControl = function(evt, btn) {
	var id = btn.getId();
	btn.div.childNodes[0].src = Window.prototype.images[parseInt(id)].src;
}

Window.prototype.minimize = function() {
	var w = this;
	var maxControl = w.title.getWidgetById('1');
	var minControl = w.title.getWidgetById('2');
	var childWindow;
	var effect;
	if (minControl) {
		if (!w.isMinimized) {
			var padding = w.getPadding();
			for (var i=1; i<w.widgets[0].widgets.length; i++)
				w.widgets[0].widgets[i].hide();
			if (w._resizer)
				w._resizer.hide();
			w._stateh = w.getHeight(true);
			w.height = w.title.getHeight(true) + 2*w.getBorderWidth() +
						padding[2] + padding[3];
			if (maxControl)
				maxControl.disable();
			for (var i=0; i<w.childWindows.length; i++) {
				childWindow = w.childWindows[i];
				if (!childWindow.isHidden()) {
					childWindow.hide();
					w._childwindows.push(childWindow);
				}
			}
			w.isMinimized = true;
			if (QuiX.effectsEnabled) {
				effect = w.getWidgetById('_eff_mini');
				effect.play();
			}
			else
				w.redraw();
		}
		else {
			w.bringToFront();
			w.height = w._stateh;
			w.isMinimized = false;
			if (QuiX.effectsEnabled) {
				effect = w.getWidgetById('_eff_maxi');
				effect.play();
			}
			else
				Window__onmaximize(w);
			w.redraw();
			
			if (maxControl)
				maxControl.enable();
			while (w._childwindows.length > 0) {
				childWindow = w._childwindows.pop();
				childWindow.show();
			}
		}
	}
}

Window.prototype.maximize = function() {
	var w = this;
	var maxControl = w.title.getWidgetById('1');
	var minControl = w.title.getWidgetById('2');
	if (maxControl) {
		if (!w.isMaximized) {
			w._statex = w._calcLeft();
			w._statey = w._calcTop();
			w._statew = w._calcWidth(true);
			w._stateh = w._calcHeight(true);
			w.top = 0; w.left = 0;
			w.height = '100%';
			w.width = '100%';
			if (minControl)
				minControl.disable();
			if (w._resizer)
				w._resizer.disable();
			w.title.detachEvent('onmousedown');
			w.isMaximized = true;
		}
		else {
			w.top = w._statey;
			w.left = w._statex;
			w.width = w._statew;
			w.height = w._stateh;
			if (minControl)
				minControl.enable();
			if (w._resizer)
				w._resizer.enable();
			w.title.attachEvent('onmousedown');
			w.isMaximized = false;
		}
		w.redraw();
	}
}

Window.prototype.bringToFront = function() {
	QuiX.cleanupOverlays();
	if (this.div.style.zIndex < this.parent.maxz) {
		var sw, dt;
		var macff = QuiX.browser == 'moz' && QuiX.getOS() == 'MacOS';
		Widget.prototype.bringToFront(this);
		if (macff) {
			var dt = document.desktop;
			//hide scrollbars
			sw = dt.getWidgetsByAttributeValue('_overflow', 'auto');
			sw = sw.concat(dt.getWidgetsByAttributeValue('_overflow', 'scroll'));
			for (var i=0; i<sw.length; i++) {
				if (sw[i] != this.parent)
					sw[i].div.style.overflow = 'hidden';
			}
			//restore scrollbars
			sw = this.getWidgetsByAttributeValue('_overflow', 'auto');
			sw = sw.concat(this.getWidgetsByAttributeValue('_overflow', 'scroll'));
			for (var i=0; i<sw.length; i++)
				sw[i].div.style.overflow = sw[i]._overflow;
		}
	}
}

Window.prototype.showWindow = function(sUrl, oncomplete) {
	var oWin = this;
	document.desktop.parseFromUrl(sUrl,
		function(w) {
			oWin.childWindows.push(w);
			w.opener = oWin;
			if (oncomplete) oncomplete(w);
		}
	);
}

Window.prototype.showWindowFromString = function(s, oncomplete) {
	var oWin = this;
	document.desktop.parseFromString(s, 
		function(w) {
			oWin.childWindows.push(w);
			w.opener = oWin;
			if (oncomplete) oncomplete(w);
		}
	);
}

WindowTitle__onmousedown = function(evt, w) {
	QuiX.cleanupOverlays();
	QuiX.stopPropag(evt);
	QuiX.cancelDefault(evt);
	w.parent.parent._startMove(evt);
}

Window__onmousedown = function(evt, w) {
	if (QuiX.getMouseButton(evt) == 0) {
		w.bringToFront();
		QuiX.stopPropag(evt);
	}
	QuiX.cleanupOverlays();
}

Window__oncontextmenu = function(evt, w) {
	QuiX.stopPropag(evt);
	return false;
}

Window__onminimize = function(eff) {
	eff.parent.div.style.clip = 'rect(auto,auto,auto,auto)';
	eff.parent.redraw();
}

Window__onmaximize = function(w) {
	if (!(w instanceof Window))
		w = w.parent;
	for (var i=1; i<w.widgets[0].widgets.length; i++)
		w.widgets[0].widgets[i].show();
	if (w._resizer)
		w._resizer.show();
}

//Dialog class
function Dialog(params) {
	var stat = params.status || false;
	var resizable = params.resizable || false;
	
	params.status = false;
	params.resizable = false;
	params.onkeypress = Dialog__keypress;
		
	this.base = Window;
	this.base(params);

	this.footer = new Widget({
		height : 32,
		padding : '0,0,0,0',
		overflow : 'hidden',
		onclick : QuiX.stopPropag
	});
	this.widgets[0].appendChild(this.footer);
	
	this.buttonHolder = new Widget({
		top : 0,
		height : '100%',
		width : 0,
		border : 0,
		overflow:'hidden'
	});
	this.buttonHolder.redraw = Dialog__buttonHolderRedraw;
	
	this.setButtonsAlign(params.align);
	this.footer.appendChild(this.buttonHolder);
	this.buttons = this.buttonHolder.widgets;
	
	//status
	if (stat.toString()=='true')
		this.addStatusBar();

	// resize handle
	if (resizable.toString()=='true')
		this.setResizable(true);
	
	this.buttonIndex = -1;
	this.defaultButton = null;
}

QuiX.constructors['dialog'] = Dialog;
Dialog.prototype = new Window;

Dialog.prototype.setButtonsAlign = function(sAlign) {
	var left;
	switch (sAlign) {
		case 'left':
			left = 0;
			break;
		case 'center':
			left = 'center';
			break;
		default:
			left = 'this.parent.getWidth()-this.getWidth(true)';
	}
	this.buttonHolder.left = left;
	this.buttonHolder.redraw();
}

Dialog.prototype.addButton = function(params) {
	params.top = 'center';
	var oWidget = new DialogButton(params, this);
	this.buttonHolder.appendChild(oWidget);
	this.buttonHolder.redraw();
	if (params['default'] == 'true') {
		this.defaultButton = oWidget;
		this.defaultButton.widgets[0].div.className='l2default';
	}
	return oWidget;
}

function Dialog__keypress(evt, w) {
	if (evt.keyCode==13 && w.defaultButton)
		w.defaultButton.click();
	else if (evt.keyCode==27 && w.title.getWidgetById('0'))
		w.close();
}

function Dialog__buttonHolderRedraw(bForceAll) {
	var iOffset = 0;
	for (var i=0; i<this.widgets.length; i++) {
		this.widgets[i].left = iOffset;
		iOffset += this.widgets[i].getWidth(true) + 8;
	}
	this.width = iOffset;
	Widget.prototype.redraw(bForceAll, this);
}

function DialogButton(params, dialog) {
	this.base = XButton;
	this.base(params);
	this.dialog = dialog;
}

DialogButton.prototype = new XButton;

DialogButton.prototype._registerHandler = function(eventType, handler, isCustom) {
	var wrapper;
	if(handler && handler.toString().lastIndexOf('return handler(evt || event, w)')==-1)
		wrapper = function(evt, w) {
			for (var i=0; i<w.dialog.buttons.length; i++) {
				if (w.dialog.buttons[i] == w) {
					w.dialog.buttonIndex = i;
					break;
				}
			}
			handler(evt, w);
		}
	wrapper = wrapper || handler;
	Widget.prototype._registerHandler(eventType, wrapper, isCustom, this);
}
