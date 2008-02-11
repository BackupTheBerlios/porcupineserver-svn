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
	params.border = 1;
	params.padding = '1,1,1,1';
	params.onmousedown = QuiX.getEventWrapper(Window__onmousedown, params.onmousedown);
	params.oncontextmenu = QuiX.getEventWrapper(Window__oncontextmenu, params.oncontextmenu);

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

	//title
	this.title = new Widget({
		width:'100%',
		height:22,
		padding:'4,0,4,2',
		border:0,
		overflow:'hidden'
	});
	this.appendChild(this.title);
	this.title.div.className = 'header';
	this.title.div.innerHTML = '<span style="margin-top:8px"></span>';
	this.title.attachEvent('onmousedown', WindowTitle__onmousedown);
	this.setTitle(params.title || "Untitled");

	//icon
	if (params.img)
		this.setIcon(params.img);

	//client area
	this.body = new Widget({
		top:22,width:'100%',
		height:"this.parent.getHeight()-22",
		border:0,overflow:'auto'
	});
	this.body.div.className = 'body';
	this.appendChild(this.body);
	
	//status
	var status = (params.status=="true"||params.status==true)?true:false;
	if (status) {
		this.addStatusBar();
	}

	// resize handle
	var isResizable = (params.resizable=="true"||params.resizable==true)?true:false;
	if (isResizable) {
		this.setResizable(true);
	}
	
	// control buttons
	var canClose = (params.close=='true'||params.close==true)?true:false;
	var canMini = (params.minimize=='true'||params.minimize==true)?true:false;
	var canMaxi = (params.maximize=='true'||params.maximize==true)?true:false;
	if (canClose)
		this.addControlButton(0);
	if (canMaxi)
		this.addControlButton(1);
	if (canMini)
		this.addControlButton(2);
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
	var icon = this.title.div.firstChild;
	if (icon.tagName == 'IMG')
		QuiX.removeNode(icon);
	if (sUrl) {
		var icon = QuiX.getImage(sUrl);
		icon.align = 'absmiddle';
		icon.style.marginRight = '2px';
		this.title.div.insertBefore(icon, this.title.div.firstChild);
	}
}

Window.prototype.getIcon = function() {
	var icon = this.title.div.firstChild;
	if (icon.tagName == 'IMG')
		return icon.src;
	return '';
}

Window.prototype.setResizable = function(bResizable) {
	var oWindow = this;
	if (bResizable && !this.resizeHandle) {
		this.resizeHandle = new Widget({
			left:"this.parent.getWidth()-16",
			top:"this.parent.getHeight()-16",
			width:16,
			height:16,
			border:0,
			overflow:'hidden'
		});
		this.appendChild(this.resizeHandle);
		this.resizeHandle.div.className = 'resize';
		this.resizeHandle.attachEvent('onmousedown', function(evt){oWindow._startResize(evt)});
	}
	else if (!bResizable && this.resizeHandle) {
		this.resizeHandle.destroy();
		this.resizeHandle = null;
	}
}

Window.prototype.addControlButton = function(iWhich) {
	var oControl, img, iOffset;
	var oWindow = this;
	if (iWhich>-1 && iWhich<3) {
		iOffset = (iWhich + 1) * 17;
		oControl = new Widget({
			id:iWhich.toString(),
			left:"this.parent.getWidth()-" + iOffset,top:-1,padding:'0,0,0,0',
			onmouseover:function(){oWindow._mouseoverControl(iWhich)},
			onmouseout:function(){oWindow._mouseoutControl(iWhich)}
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
					oWindow.close()
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

Window.prototype.removeControlButton = function(iWhich) {
	var oButton = this.title.getWidgetById(iWhich.toString());
	if (oButton)
		oButton.destroy();
}

Window.prototype.close = function() {
	if (this._customRegistry.onclose)
		QuiX.getEventListener(this._customRegistry.onclose)(this);
	while (this.childWindows.length != 0)
		this.childWindows[0].close();
	if (this.opener)
		this.opener.childWindows.removeItem(this);
	this.destroy();
}

Window.prototype.setTitle = function(s) {
	this.title.div.getElementsByTagName('SPAN')[0].innerHTML = s;
}

Window.prototype.getTitle = function() {
	return this.title.div.getElementsByTagName('SPAN')[0].innerHTML;
}

Window.prototype.addStatusBar = function(w) {
	w = w || this;
	if (!this.statusBar) {
		w.body.height = 'this.parent.getHeight()-42';
		w.body.redraw();
		
		w.statusBar = new Widget({
			top: "this.parent.getHeight()-20",
			width: '100%',
			left: 0,
			height: 20,
			padding: '4,0,0,0',
			border: 1,
			overflow: 'hidden'
		});
		w.statusBar.div.className = 'status';
		w.appendChild(w.statusBar);
		if (w.resizeHandle)
			w.resizeHandle.bringToFront();
	}
}

Window.prototype.removeStatusBar = function(w) {
	w = w || this;
	if (w.statusBar) {
		w.statusBar.destroy();
		w.statusBar = null;
		w.body.height = 'this.parent.getHeight()-22';
		w.body.redraw();
	}
}

Window.prototype.setStatus = function(s) {
	if (this.statusBar)
		this.statusBar.div.innerHTML = s;
}

Window.prototype.getStatus = function() {
	if (this.statusBar)
		return this.statusBar.div.innerHTML;
}

Window.prototype._mouseoverControl = function(iWhich) {
	this.title.getWidgetById(iWhich.toString()).div.childNodes[0].src = this.images[iWhich + 3].src;
}

Window.prototype._mouseoutControl = function(iWhich) {
	this.title.getWidgetById(iWhich.toString()).div.childNodes[0].src = this.images[iWhich].src;
}

Window.prototype.minimize = function(w) {
	w = w || this;
	var maxControl = w.title.getWidgetById('1');
	var minControl = w.title.getWidgetById('2');
	var childWindow;
	
	if (minControl) {
		if (!w.isMinimized) {
			var padding = w.getPadding();
			w.body.hide();
			if (w.statusBar)
				w.statusBar.hide();
			if (w.resizeHandle)
				w.resizeHandle.hide();
			w._stateh = w.getHeight(true);
			w.height = w.title.getHeight(true) + 2*w.getBorderWidth() + padding[2] + padding[3];
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
		}
		else {
			w.body.show();
			if (w.statusBar)
				w.statusBar.show();
			if (w.resizeHandle)
				w.resizeHandle.show();
			w.height = w._stateh;
			if (maxControl)
				maxControl.enable();
				
			while (w._childwindows.length > 0) {
				childWindow = w._childwindows.pop();
				childWindow.show();
			}
			w.isMinimized = false;
		}
		w.redraw();
	}
}

Window.prototype.maximize = function(w) {
	w = w || this;
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
			if (w.isResizable)
				w.resz.disable();
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
			if (w.isResizable)
				w.resz.enable();
			w.title.attachEvent('onmousedown');
			w.isMaximized = false;
		}
		w.redraw();
	}
}

Window.prototype.bringToFront = function() {
	Widget.prototype.bringToFront(this);
	for (var i=0; i<this.childWindows.length; i++)
		this.childWindows[i].bringToFront();
}

Window.prototype.showWindow = function(sUrl, oncomplete) {
	var oWin = this;
	document.desktop.parseFromUrl(
		sUrl,
		function(w) {
			oWin.childWindows.push(w);
			w.opener = oWin;
			if (oncomplete) oncomplete(w);
		}
	);
}

Window.prototype.showWindowFromString = function(s, oncomplete) {
	var oParent = this;
	document.desktop.parseFromString(s, 
		function(w) {
			oParent.childWindows.push(w);
			w.opener = oParent;
			if (oncomplete) oncomplete(w);
		}
	);
}

WindowTitle__onmousedown = function(evt, w) {
	w.parent._startMove(evt);
	QuiX.stopPropag(evt);
	QuiX.cancelDefault(evt);
}

Window__onmousedown = function(evt, w) {
	w.bringToFront();
}

Window__oncontextmenu = function(evt, w) {
	QuiX.stopPropag(evt);
	return false;
}

//Dialog class
function Dialog(params) {
	params.onkeypress = Dialog__keypress;
	this.base = Window;
	this.base(params);

	iOffset = this.statusBar?20:0;
	this.body.height = "this.parent.getHeight()-56-" + iOffset.toString();
	this.footer = new Widget({
		top:"this.parent.getHeight()-32-" + iOffset.toString(),
		width:'100%', height:32,padding:'0,0,0,0', overflow:'hidden',
		onclick: QuiX.stopPropag
	});
	this.appendChild(this.footer);
	
	this.buttonHolder = new Widget({
		top: 0, height: '100%',
		width: 0, border:0, overflow:'hidden'
	});
	this.buttonHolder.redraw = Dialog__buttonHolderRedraw;
	
	this.setButtonsAlign(params.align);
	this.footer.appendChild(this.buttonHolder);
	this.buttons = this.buttonHolder.widgets;
	this.buttonIndex = -1;
	this.defaultButton = null;
	if (this.resizeHandle)
		this.resizeHandle.bringToFront();
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

Dialog.prototype.addStatusBar = function() {
	Window.prototype.addStatusBar(this);
	this.body.height = 'this.parent.getHeight()-76';
	this.body.redraw();
	if (this.footer) {
		this.footer.top = 'this.parent.getHeight()-52';
		this.footer.redraw();
	}
}

Dialog.prototype.removeStatusBar = function() {
	Window.prototype.removeStatusBar(this);
	this.body.height = 'this.parent.getHeight()-56';
	this.body.redraw();
	this.footer.top = 'this.parent.getHeight()-32';
	this.footer.redraw();
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

Dialog.prototype.minimize = function() {
	Window.prototype.minimize(this);
	if (this.isMinimized)
		this.footer.hide();
	else {
		this.footer.show();
		this.redraw();
	}
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
