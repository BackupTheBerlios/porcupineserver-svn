/************************
Labels & Buttons
************************/
function Label(params) {
	params = params || {};
	params.padding = params.padding || '2,2,2,2';
	params.onmousedown = QuiX.getEventWrapper(Label__onmousedown,
		params.onmousedown);
	
	this.base = Widget;
	this.base(params);

	this.div.className = 'label';
	this.align = params.align || 'left';
	
	if (params.color) {
		if (!this._isDisabled)
			this.div.style.color = params.color;
		else
			this._statecolor = params.color;
	}

	this.canSelect = (params.canselect=="true" || params.canselect==true)?
					 true:false;
	if (this.canSelect) {
		this.div.onselectstart = QuiX.stopPropag;
		this.div.style.cursor = 'text';
	}
	this.wrap = (params.wrap=="true" || params.wrap==true);
	
	var sCaption = params.caption || '';
	this.div.innerHTML += '<span>' + sCaption + '</span>';
}

QuiX.constructors['label'] = Label;
Label.prototype = new Widget;

Label.prototype.setCaption = function(s) {
	this.div.getElementsByTagName('SPAN')[0].innerHTML = s;
}

Label.prototype.getCaption = function(s) {
	return(this.div.getElementsByTagName('SPAN')[0].innerHTML.xmlDecode());
}

Label.prototype.redraw = function(bForceAll, w) {
	var w = w || this;
	with (w.div.style) {
		if (!w.wrap)
			whiteSpace = 'nowrap';
		else
			whiteSpace = '';
		textAlign = w.align;
	}
	Widget.prototype.redraw(bForceAll, w);
}

function Label__onmousedown(evt, w) {
	if (!w.canSelect)
		QuiX.cancelDefault(evt);
	else
		QuiX.stopPropag(evt);
}

function Icon(params) {
	params = params || {};
	params.border = params.border || 0;
	params.canSelect = false;
	params.align = params.align || 'center';
	
	this.base = Label;
	this.base(params);
	this.img = params.img || null;
	this.imageElement = null;
	this.imgAlign = params.imgalign || 'left';
	this.imgHeight = params.imgheight;
	this.imgWidth = params.imgwidth;
	this.redraw(true);
}

QuiX.constructors['icon'] = Icon;
Icon.prototype = new Label;

Icon.prototype.setImageURL = function(s) {
	this.img = s;
	if (this.imageElement)
		this.imageElement.src = s;
}

Icon.prototype.getImageURL = function() {
	return (this.imageElement)?this.imageElement.src:'';
}

Icon.prototype._addDummyImage = function() {
	var img = QuiX.getImage('__quix/images/transp.gif');
	img.style.verticalAlign = 'middle';
	img.style.height = '100%';
	img.style.width = '1px';
	if (this.imgAlign=='right') {
		this.div.appendChild(img);
	}
	else if (this.imgAlign=='left') {
		this.div.insertBefore(img, this.div.firstChild);
	}
}

Icon.prototype.redraw = function(bForceAll, w) {
	var w = w || this;
	if (bForceAll) {
		var imgs = w.div.getElementsByTagName('IMG');
		while (imgs.length > 0)
			QuiX.removeNode(imgs[0]);
		var br = w.div.getElementsByTagName('BR')[0];
		if (br) QuiX.removeNode(br);

		if (this.imgAlign == 'left' || this.imgAling == 'right')
			w._addDummyImage();

		if (w.img) {
			var percentage, caption;
			img = QuiX.getImage(w.img);
			caption = w.getCaption();
			img.style.verticalAlign = (w.imgAlign=='top')?'top':'middle';
			img.ondragstart = QuiX.cancelDefault;
			
			if (caption != '') {
				switch(w.imgAlign) {
					case "left":
						img.style.marginRight = '3px';
						w.div.insertBefore(img, w.div.firstChild);
						break;
					case "right":
						img.style.marginLeft = '3px';
						w.div.appendChild(img);
						break;
					case "top":
						w.div.insertBefore(ce('BR'), w.div.firstChild);
						w.div.insertBefore(img, w.div.firstChild);
						break;
					case "bottom":
						w.div.appendChild(ce('BR'));
						w.div.appendChild(img);
				}
			}
			else {
				w.div.insertBefore(img, w.div.firstChild);
			}
			w.imageElement = img;
		}
		else
			w.imageElement = null;
	}
	if (w.imageElement && (w.imgHeight || w.imgWidth)) {
		if (w.imgHeight) {
			percentage = w.imgHeight.toString().charAt(w.imgHeight.length-1);
			w.imageElement.style.height =
				(percentage == '%')?w.imgHeight:w.imgHeight + 'px';
		}
		if (w.imgWidth) {
			percentage = w.imgWidth.toString().charAt(w.imgWidth.length-1);
			w.imageElement.style.width =
				(percentage == '%')?w.imgWidth:w.imgWidth + 'px';
		}
	}
	Label.prototype.redraw(bForceAll, w);
}

//XButton class

function XButton(params) {
	params = params || {};
	this.icon = null;
	this.base = Widget;
	this.base({
		id: params.id,
		border: 1,
		width: params.width,
		height: params.height,
		minw: params.minw,
		minh: params.minh,
		top: params.top,
		left: params.left,
		disabled: params.disabled,
		bgcolor: params.bgcolor || 'buttonface',
		padding: '0,0,0,0',
		overflow: 'hidden',
		onmouseover: QuiX.getEventWrapper(XButton__onmouseover,
						params.onmouseover),
		onmouseout: QuiX.getEventWrapper(XButton__onmouseout,
						params.onmouseout),
		onmouseup: QuiX.getEventWrapper(XButton__onmouseup,
						params.onmouseup),
		onmousedown: QuiX.getEventWrapper(XButton__onmousedown,
						params.onmousedown),
		onclick: params.onclick
	});
	this.div.className = 'btn';
	this.div.style.cursor = 'pointer';
	
	delete params.id; delete params.top; delete params.left;
	delete params.minw;	delete params.minh; delete params.onclick;
	delete params.onmouseover; delete params.onmousedown;
	delete params.onmouseup; delete params.onmousedown;
	delete params.bgcolor;
		
	params.width = '100%';
	params.height = '100%';
	params.border = 1;
	this.iconPadding = params.iconpadding || '0,0,0,0';
	params.padding = this.iconPadding;
	params.align = params.align || 'center';

	this.align = params.align;
	this.imgAlign = params.imgAlign || 'left';
	this.img = params.img || null;
	
	this.icon = new Icon(params);
	this.icon.div.className = 'l2';
	this.icon.setPosition();
	this.appendChild(this.icon);

	if (this._isDisabled)
		this._statecursor = 'pointer';
}

QuiX.constructors['button'] = XButton;
XButton.prototype = new Widget;

XButton.prototype.setCaption = function(s) {
	this.icon.setCaption(s);
}

XButton.prototype.getCaption = function() {
	return this.icon.getCaption();
}

XButton.prototype.redraw = function(bForceAll) {
	if (bForceAll) {
		this.icon.align = this.align;
		this.icon.img = this.img;
		this.icon.imgAlign = this.imgAlign;
		this.icon.setPadding(this.iconPadding.split(','));
		this.icon.redraw(true);
	}
	Widget.prototype.redraw(bForceAll, this);
}

function XButton__onmouseover(evt, w) {
	w.div.className = 'btnover';
}

function XButton__onmouseout(evt, w) {
	w.div.className = 'btn';
	if (w._isPressed) {
		w.icon.addPaddingOffset('Left', -1);
		w.icon.addPaddingOffset('Top', -1);
		w._isPressed = false;
	}
}

function XButton__onmousedown(evt, w) {
	w.div.className = 'btndown';
	w.icon.addPaddingOffset('Left', 1);
	w.icon.addPaddingOffset('Top', 1);
	w._isPressed = true;
}

function XButton__onmouseup(evt, w) {
	w.div.className = 'btn';
	w.icon.addPaddingOffset('Left', -1);
	w.icon.addPaddingOffset('Top', -1);
	w._isPressed = false;
}

//FlatButton class
function FlatButton(params) {
	params = params || {};
	params.border = 0;
	params.padding = params.padding || '4,4,4,4';
	params.overflow = 'hidden';
	params.align = params.align || 'center';
	params.onmouseover = QuiX.getEventWrapper(FlatButton__onmouseover,
							params.onmouseover);
	params.onmouseout = QuiX.getEventWrapper(FlatButton__onmouseout,
							params.onmouseout);
	params.onmousedown = QuiX.getEventWrapper(FlatButton__onmousedown,
							params.onmousedown);
	params.onmouseup = QuiX.getEventWrapper(FlatButton__onmouseup,
							params.onmouseup);
	params.onclick = QuiX.getEventWrapper(FlatButton__onclick,
							params.onclick);

	this.base = Icon;
	this.base(params);
	this.div.className = 'flat';
	
	this.type = params.type || 'normal';
	
	this._ispressed = false;
	
	if (this.type=='menu') {
		delete(params.height);
		delete(params.overflow);
		var oCMenu = new ContextMenu(params, this);
		this.contextMenu = oCMenu;
		this._menuImg = null;
	}
	
	if (this.type=='toggle') {
		this.value = params.value || 'off';
		if (this.value == 'on') {
			this.value = 'off';
			this.toggle();
		}
	}
}

QuiX.constructors['flatbutton'] = FlatButton;
FlatButton.prototype = new Icon;

FlatButton.prototype.redraw = function(bForceAll) {
	Icon.prototype.redraw(bForceAll, this);

	if (this.type == 'menu' && (!this._menuImg || bForceAll)) {
		this._menuImg = QuiX.getImage('__quix/images/desc8.gif');
		this._menuImg.border = 0;
		this._menuImg.align = 'absmiddle';
		this.div.appendChild(this._menuImg);
	}
}

FlatButton.prototype._addBorder = function() {
	if (this.getBorderWidth()==0) {
		this.setBorderWidth(1);
		var padding = this.getPadding();
		for (var i=0; i<4; i++) padding[i] -= 1;
		this.setPadding(padding);
	}
}

FlatButton.prototype._removeBorder = function() {
	if (this.getBorderWidth()==1) {
		this.setBorderWidth(0);
		var padding = this.getPadding();
		for (var i=0; i<4; i++) padding[i] += 1;
		this.setPadding(padding);
	}
}

FlatButton.prototype.toggle = function() {
	if (this.value=='off') {
		this._addBorder();
		this.div.className='flaton';
		this.addPaddingOffset('Left', 1);
		this.addPaddingOffset('Right', -1);
		this.value = 'on';
	}
	else {
		this._removeBorder();
		this.addPaddingOffset('Left', -1);
		this.addPaddingOffset('Right', 1);
		this.div.className = 'flat';
		this.value = 'off';
	}
}

function FlatButton__onmouseover(evt, w) {
	if (!(w.type=='toggle' && w.value=='on')) {
		w.div.className += ' flatover';
		w._addBorder();
	}
}

function FlatButton__onmouseout(evt, w) {
	if (!(w.type=='toggle' && w.value=='on')) {
		w.div.className = 'flat';
		w._removeBorder();
		if (w.type!='toggle' && w._ispressed) {
			w.addPaddingOffset('Left', -1);
			w._ispressed = false;
		}
	}
}

function FlatButton__onmousedown(evt, w) {
	w.div.className='flaton';
	w._addBorder();
	if (w.type == 'menu')
		QuiX.stopPropag(evt);
	if (w.type!='toggle') {
		w.addPaddingOffset('Left', 1);
		w._ispressed = true;
	}
}

function FlatButton__onmouseup(evt, w) {
	w.div.className='flat';
	w._removeBorder();
	if (w.type!='toggle' && w._ispressed) {
		w.addPaddingOffset('Left', -1);
		w._ispressed = false;
	}
}

function FlatButton__onclick(evt, w) {
	if (w.type=='toggle')
		w.toggle();
	else if (w.type=='menu') {
		if (!w.contextMenu.isOpen) {
			w.div.className = 'btnmenu';
			showWidgetContextMenu(w, w.contextMenu);
		}
		else {
			w.div.className = 'btn';
			w.contextMenu.close();
		}
	}
	QuiX.stopPropag(evt);
}


