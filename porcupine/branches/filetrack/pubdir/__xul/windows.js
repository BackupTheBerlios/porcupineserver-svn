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
	params.onclick = QuiX.getEventWrapper(Window__onclick, params.onclick);
	params.oncontextmenu = QuiX.getEventWrapper(Window__oncontextmenu, params.oncontextmenu);

	this.base = Widget;
	this.base(params);
	this.minw = 140;
	this.minh = 120;
	this.isMinimized = false;
	this.isMaximized = false;
	this.childWindows = [];
	this.opener = null;
	this.statex = 0;
	this.statey = 0;
	this.statew = 0;
	this.stateh = 0;
	this.div.className = 'window';

	var oWindow = this;
	//title
	this.title = new Widget(
		{
			width:'100%',
			height:22,
			padding:'4,0,4,2',
			border:0,
			overflow:'hidden'
		}
	);
	this.appendChild(this.title);
	this.title.div.className = 'header';
	this.title.div.innerHTML = '<span style="margin-top:8px"></span>';
	this.title.attachEvent('onmousedown', WindowTitle__onmousedown);
	this.setTitle(params.title || "Untitled");
	if (params.img) {
		var icon = QuiX.getImage(params.img);
		icon.align = 'absmiddle';
		icon.style.marginRight = '2px';
		this.title.div.insertBefore(icon, this.title.div.firstChild);
		this.icon = params.img;
	}

	this.status = (params.status=="true")?true:false;
	this.isResizable = (params.resizable=="true")?true:false;
	
	iOffset = this.status?20:0;
	//main area
	this.body = new Widget(
		{
			top:22,width:'100%', height:"this.parent.getHeight()-22-" + iOffset.toString(),
			border:0,overflow:'auto'
		}
	);
	this.body.div.className = 'body';
	this.appendChild(this.body);
	
	//status
	if (this.status) {
		this.stat = new Widget(
			{
				top:"this.parent.getHeight()-19",
				width: '100%',
				left: 0,
				height:20,
				padding:'4,0,0,0',
				border:1,
				overflow:'hidden'
			});
		this.stat.div.className = 'status';
		this.appendChild(this.stat);
	}
	// resize handle
	if (this.isResizable) {
		this.resz = new Widget(
			{
				left:"this.parent.getWidth()-15",
				top:"this.parent.getHeight()-15",
				width:16,
				height:16,
				border:0,
				overflow:'hidden'
			});
		this.appendChild(this.resz);
		this.resz.div.className = 'resize';
		this.resz.attachEvent('onmousedown', function(evt){oWindow._startResize(evt)});
	}
	// controls
	this.canClose = (params["close"]=='true')?true:false;
	this.canMini = (params["minimize"]=='true')?true:false;
	this.canMaxi = (params["maximize"]=='true')?true:false;

	var img;
	if (this.canClose) {
		this.clos = new Widget(
			{
				left:"this.parent.getWidth()-16",top:-1,padding:"0,0,0,0",
				onclick:function(){oWindow.close()},
				onmouseover:function(){oWindow._mouseoverControl(0)},
				onmouseout:function(){oWindow._mouseoutControl(0)}
			});
		this.title.appendChild(this.clos);
		img = QuiX.getImage("images/win_close.gif");
		this.clos.div.appendChild(img);
		this.clos.div.style.cursor = 'default';
		this.clos.attachEvent('onmousedown', QuiX.stopPropag);
	}
	if (this.canMini) {
		this.mini = new Widget(
			{
				left:"this.parent.getWidth()-50",top:-1,padding:"0,0,0,0",
				onclick:function(){oWindow.minimize()},
				onmouseover:function(){oWindow._mouseoverControl(1)},
				onmouseout:function(){oWindow._mouseoutControl(1)}
			});
		this.title.appendChild(this.mini);
		img = QuiX.getImage("images/win_min.gif");
		this.mini.div.appendChild(img);
		this.mini.div.style.cursor = 'default';
		this.mini.attachEvent('onmousedown', QuiX.stopPropag);
	}
	if (this.canMaxi) {
		this.maxi = new Widget(
			{
				left:"this.parent.getWidth()-34",top:-1,padding:"0,0,0,0",
				onclick:function(evt, w){oWindow.maximize()},
				onmouseover:function(){oWindow._mouseoverControl(2)},
				onmouseout:function(){oWindow._mouseoutControl(2)}
			});
		this.title.appendChild(this.maxi);
		img = QuiX.getImage("images/win_max.gif");
		this.maxi.div.appendChild(img);
		this.maxi.div.style.cursor = 'default';
		this.title.attachEvent('ondblclick', function(evt, w){oWindow.maximize()});
		this.maxi.attachEvent('onmousedown', QuiX.stopPropag);
	}
}

Window.prototype = new Widget;

Window.prototype.close = function() {
	while (this.childWindows.length != 0) this.childWindows[0].close();
	if (this.opener) this.opener.childWindows.removeItem(this);
	this.destroy();
}

Window.prototype.setTitle = function(s) {
	this.title.div.getElementsByTagName('SPAN')[0].innerHTML = s;
}

Window.prototype.getTitle = function() {
	return this.title.div.getElementsByTagName('SPAN')[0].innerHTML;
}

Window.prototype.setStatus = function(s) {
	if (this.status) {
		this.stat.div.innerHTML = s;
	}
}

Window.prototype._mouseoverControl = function(iWhich) {
	switch (iWhich) {
		case 0: //close
			this.clos.div.childNodes[0].src = 'images/win_close_over.gif';
			break;
		case 1: //mini
			this.mini.div.childNodes[0].src = 'images/win_min_over.gif';
			break;
		case 2: //maxi
			this.maxi.div.childNodes[0].src = 'images/win_max_over.gif';
	}
}

Window.prototype._mouseoutControl = function(iWhich) {
	switch (iWhich) {
		case 0: //close
			this.clos.div.childNodes[0].src = 'images/win_close.gif';
			break;
		case 1: //mini
			this.mini.div.childNodes[0].src = 'images/win_min.gif';
			break;
		case 2: //maxi
			this.maxi.div.childNodes[0].src = 'images/win_max.gif';
	}
}

Window.prototype.minimize = function(w) {
	w = w || this;
	if (!w.isMinimized) {
		w.body.hide();
		if (w.status) w.stat.hide();
		if (w.isResizable) w.resz.hide();
		w.stateh = w.getHeight(true);
		w.height = w.title.getHeight(true) + 2*w.borderWidth + w.padding[2]+ w.padding[3];
		if (w.canMaxi) w.maxi.disable();
		w.isMinimized = true;
	}
	else {
		w.body.show();
		if (w.status) w.stat.show();
		if (w.isResizable) w.resz.show();
		w.height = w.stateh;
		if (w.canMaxi) w.maxi.enable();
		w.isMinimized = false;
	}
	w.redraw();
}

Window.prototype.maximize = function(w) {
	w = w || this;
	if (!w.isMaximized) {
		w.statex = w._calcLeft();
		w.statey = w._calcTop();
		w.statew = w.getWidth(true);
		w.stateh = w.getHeight(true);
		w.top = 0; w.left = 0;
		w.height = '100%';
		w.width = '100%';
		if (w.canMini) w.mini.disable();
		if (w.isResizable) w.resz.disable();
		w.title.detachEvent('onmousedown');
		w.isMaximized = true;
	}
	else {
		w.top = w.statey;
		w.left = w.statex;
		w.width = w.statew;
		w.height = w.stateh;
		if (w.canMini) w.mini.enable();
		if (w.isResizable) w.resz.enable();
		w.title.attachEvent('onmousedown');
		w.isMaximized = false;
	}
	w.redraw();
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
}

Window__onclick = function(evt, w) {
	w.bringToFront();
}

Window__oncontextmenu = function(evt, w) {
	QuiX.stopPropag(evt);
	return false;
}

//Dialog class

function Dialog(params) {
	var sLeft;

	params.onkeypress = function(evt, w) {
		if (evt.keyCode==13 && w.defaultButton) {
			w.defaultButton.click();
		}
		else if (evt.keyCode==27 && w.canClose) {
			w.close();
		}
	}

	this.base = Window;
	this.base(params);

	iOffset = this.status?20:0;

	this.body.height = "this.parent.getHeight()-56-" + iOffset.toString();

	this.footer = new Widget(
		{
			top:"this.parent.getHeight()-32-" + iOffset.toString(),
			width:'100%', height:32,padding:'0,0,0,0', overflow:'hidden',
			onclick: QuiX.stopPropag
		});
	this.appendChild(this.footer);
	sLeft = (params.align=='center')?'center':'this.parent.getWidth()-this.getWidth(true)';
	this.buttonHolder = new Widget(
		{
			left: sLeft, top: 0, height: '100%',
			//** width: Dialog__getButtonHolderWidth
			width: 0, border:1, overflow:'hidden'
		}
	);
	this.footer.appendChild(this.buttonHolder);
	//this.buttonHolder.div.style.borderStyle = 'solid';
	this.buttons = this.buttonHolder.widgets;
	this.defaultButton = null;
	if (this.isResizable) this.resz.bringToFront();
	//this.redraw();
}

Dialog.prototype = new Window;

Dialog.prototype.addButton = function(params) {

	params.left = this.buttonHolder._calcWidth(true);
	params.top = 'center';
	var oWidget = new XButton(params)
	this.buttonHolder.appendChild(oWidget, true);
	this.buttonHolder.width += oWidget.getWidth(true) + 8;
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

