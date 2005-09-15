/************************
Labels & Buttons
************************/
function Label(params) {
	params = params || {};
	params.padding = params.padding || '2,2,2,2';
	params.onmousedown = QuiX.getEventWrapper(Label__onmousedown, params.onmousedown);
	
	this.base = Widget;
	this.base(params);

	this.div.className = 'label';	
	this.div.style.textAlign = params.align || 'left';
	this.div.style.color = params.color;

	this.canSelect = (params.canselect=="true" || params.canselect==true)?true:false;
	if (this.canSelect) {
		this.div.onselectstart = QuiX.stopPropag;
		this.div.style.cursor = 'text';
	}
	
	this.caption = params.caption || '';
	if (this.caption) this.div.innerHTML += '<span>' + this.caption + '</span>';
}

Label.prototype = new Widget;

Label.prototype.setCaption = function(s) {
	this.div.getElementsByTagName('SPAN')[0].innerHTML = s;
}

function Label__onmousedown(evt, w) {
	if (w.canSelect) QuiX.stopPropag(evt);
}

function Icon(params) {
	var imgalign;
	params = params || {};
	params.border = params.border || 0;
	params.canSelect = false;
	
	this.base = Label;
	this.base(params);
	this.div.style.textAlign = params.align || 'center';
	this.img = params.img || null;
	if (this.img)	{
		var img = QuiX.getImage(params.img);
		img.style.verticalAlign = 'middle';
		var oIcon = this;

		if (this.caption) {
			imgalign = params.imgalign || 'left';
			switch(imgalign) {
				case "left":
					img.style.marginRight = '2px';
					this.div.insertBefore(img, this.div.firstChild);
					break;
				case "right":
					img.style.marginLeft = '2px';
					this.div.appendChild(img);
					break;
				case "top":
					this.div.insertBefore(ce('BR'), this.div.firstChild);
					this.div.insertBefore(img, this.div.firstChild);
					break;
				case "bottom":
					this.div.appendChild(ce('BR'));
					this.div.appendChild(img);
			}
		 } else {
			img.style.verticalAlign = params.imgalign || 'middle';
			this.div.appendChild(img);
		}
	}
}

Icon.prototype = new Label;

Icon.prototype.changeImage = function(s) {
	this.div.firstChild.src = s;
}

//XButton class

function XButton(params) {
	params = params || {};

	this.base = Widget;
	this.base({
		border: 1,
		width: params.width,
		height: params.height,
		top: params.top,
		left: params.left,
		bgcolor: params.bgcolor || 'buttonface',
		overflow: 'hidden',
		onmouseover: QuiX.getEventWrapper(XButton__onmouseover, params.onmouseover),
		onmouseout: QuiX.getEventWrapper(XButton__onmouseout, params.onmouseout),
		onmouseup: QuiX.getEventWrapper(XButton__onmouseup, params.onmouseup),
		onmousedown: QuiX.getEventWrapper(XButton__onmousedown, params.onmousedown),
		onclick: params.onclick
	});
	
	delete params.onclick;
	delete params.onmouseover;
	delete params.onmousedown;
	delete params.onmouseup;
	delete params.onmousedown;
	
	this.div.className = 'btn';
	
	w2 = new Widget({border:1,width:'100%',height:'100%'});
	this.appendChild(w2);
	
	w2.div.className = 'l2';
	
	params.border = 0;
	params.width = '100%';
	params.height = (params.img)?16:14;
	delete params.bgcolor;
	params.padding = '0,0,0,0';
	params.top = 'center';
	params.left = 0;
	this.icon = new Icon(params);
	w2.appendChild(this.icon);
	this.div.style.cursor = 'pointer';
}

XButton.prototype = new Widget;

function XButton__onmouseover(evt, w) {
	w.div.className = 'btnover';
}

function XButton__onmouseout(evt, w) {
	w.div.className = 'btn';
	w.icon.padding[0] = 0;
	w.icon.padding[2] = 0;
	w.icon.repad();
}

function XButton__onmousedown(evt, w) {
	w.div.className = 'btndown';
	w.icon.padding[0] = 2;
	w.icon.padding[2] = 1;
	w.icon.repad();
}

function XButton__onmouseup(evt, w) {
	w.div.className = 'btn';
	w.icon.padding[0] = 0;
	w.icon.padding[2] = 0;
	w.icon.repad();
}

//FlatButton class

function FlatButton(params) {
	params = params || {};
	params.border = 0;
	params.padding = params.padding || '4,4,4,4';
	params.overflow = 'hidden';
	params.onmouseover = QuiX.getEventWrapper(FlatButton__onmouseover, params.onmouseover);
	params.onmouseout = QuiX.getEventWrapper(FlatButton__onmouseout, params.onmouseout);
	params.onmousedown = QuiX.getEventWrapper(FlatButton__onmousedown, params.onmousedown);
	params.onmouseup = QuiX.getEventWrapper(FlatButton__onmouseup, params.onmouseup);
	params.onclick = QuiX.getEventWrapper(FlatButton__onclick, params.onclick);

	this.base = Icon;
	this.base(params);
	this.div.className = 'flat';
	
	this.type = params.type || 'normal';
	this.value = (this.type=='toggle')?'off':'';
	
	this._ispressed = false;
	
	if (this.type=='menu') {
		var img = QuiX.getImage('images/desc8.gif');
		img.border = 0;
		img.align = 'absmiddle';
		this.div.appendChild(img);
		delete(params.height);
		delete(params.overflow);
		var oCMenu = new ContextMenu(params, this);
		this.contextmenu = oCMenu;
	}
}

FlatButton.prototype = new Icon;

FlatButton.prototype._addBorder = function() {
	if (this.borderWidth==0) {
		this.borderWidth = 1;
		for (var i=0; i<4; i++) this.padding[i] -= 1;
		this.repad();
	}
}

FlatButton.prototype._removeBorder = function() {
	if (this.borderWidth==1) {
		this.borderWidth = 0;
		for (var i=0; i<4; i++) this.padding[i] += 1;
		this.repad();
	}
}

FlatButton.prototype.toggle = function() {
	if (this.value=='off') {
		this._addBorder();
		this.div.className='flaton';
		for (var i=0; i<this.div.childNodes.length; i++) {
			this.div.childNodes[i].style.margin = '2px 0px 0px 2px';
		}
		this.value = 'on';
	}
	else {
		this._removeBorder();
		for (var i=0; i<this.div.childNodes.length; i++) {
			this.div.childNodes[i].style.margin = '0px 2px 0px 0px';
		}
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
			w.padding[0] -= 1;
			w.repad();
			w._ispressed = false;
		}
	}
}

function FlatButton__onmousedown(evt, w) {
	w.div.className='flaton';
	w._addBorder();
	if (w.type!='toggle') {
		w.padding[0] += 1;
		w._ispressed = true;
	}
	w.repad();
}

function FlatButton__onmouseup(evt, w) {
	w.div.className='flat';
	w._removeBorder();
	if (w.type!='toggle' && w._ispressed) {
		w.padding[0] -= 1;
		w.repad();
		w._ispressed = false;
	}
}

function FlatButton__onclick(evt, w) {
	if (w.type=='toggle')
		w.toggle();
	else if (w.type=='menu') {
		if (!w.contextmenu.isOpen) {
			w.div.className = 'btnmenu';
			showWidgetContextMenu(w, w.contextmenu);
		}
		else {
			w.div.className = 'btn';
			document.desktop.closeMenu(evt);
		}
	}
	QuiX.stopPropag(evt);
}


