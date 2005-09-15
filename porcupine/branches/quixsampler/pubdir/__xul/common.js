// horizontal rule
function HR(params) {
	params = params || {};
	this.base = Widget;
	params.border = params.border || 1;
	params.height = params.height || 2;
	params.overflow = 'hidden';
	this.base(params);
	this.div.className = 'separator';
}

HR.prototype = new Widget;

// combo box
function Combo(params) {
	params = params || {};
	params.bgcolor = params.bgcolor || 'white';
	params.border = params.border || 1;
	params.overflow = 'hidden';
	params.height = params.height || 22;

	this.base = Widget;
	this.base(params);

	this.div.className = 'combo';
		
	this.name = params.name;
	this.editable = (params.editable=='true' || params.editable==true)?true:false;
	this.readonly = (params.readonly=='true' || params.readonly==true)?true:false;
	this.menuHeight = parseInt(params.menuheight) || 100;
	this.div.className = 'field';
	this.options = [];
	this.selection = null;
	this.isExpanded = false;
	this.attachEvent('onmousedown', QuiX.stopPropag);
	this.onchange = getEventListener(params.onchange);

	var e = ce('INPUT');
	e.style.borderWidth = '1px';
	e.style.position='absolute';
	this.div.appendChild(e);
	e.onselectstart = QuiX.stopPropag;
	var oCombo = this;

	this.button = new XButton(
		{
			left : "this.parent.getWidth()-20",
			height : '100%', width : 20, bgcolor : 'silver',
			img : params.img || 'images/desc8.gif'
		});
	this.appendChild(this.button);
	if (!this.readonly) this.button.attachEvent('onclick', ComboBtn__onclick);
	
	if (this.editable) {
		e.value = (params.value)?params.value:'';
		if (!this.readonly)
			if (this.onchange) e.onchange = this.onchange(this);
		else
			e.readonly = true
		this.getValue = function() { return e.value; }
		this.setValue = function(value) { e.value=value; }
	}
	else {
		e.readOnly = true;
		e.style.cursor = 'default';
		if (!this.readonly) e.onclick = ComboBtn__onclick;
		this.getValue = function() { return oCombo.selection; }
		this.setValue = function(value) {
			for (var i=0; i<oCombo.options.length; i++) {
				if (oCombo.options[i].value == value && oCombo.getValue()!=value) {
					this.selection = value;
					this.div.firstChild.value = oCombo.options[i].caption;
				}
			}
		}
	}
}

Combo.prototype = new Widget;

Combo.prototype._adjustFieldSize = function() {
	if (this.div.firstChild) {
		var nh = this.getHeight();
		this.div.firstChild.style.width = (this.getWidth()-21) + 'px';
		this.div.firstChild.style.height = nh + 'px';
	}
}

Combo.prototype._setCommonProps = function() {
	Widget.prototype._setCommonProps(this);
	this._adjustFieldSize();
}

Combo.prototype.enable = function() {
	if (this.div.firstChild) {
		this.div.firstChild.disabled = false;
		this.div.firstChild.style.backgroundColor = '';
	}
	Widget.prototype.enable(this);
}

Combo.prototype.disable = function() {
	if (this.div.firstChild) {
		this.div.firstChild.disabled = true;
		this.div.firstChild.style.backgroundColor = 'menu';
	}
	Widget.prototype.disable(this);
}

Combo.prototype.selectOption = function(option) {
	if (!this.editable) {
		var value = (option.value!=undefined)?option.value:option.caption;
		if (this.selection!=value) {
			this.selection = value;
			if (this.onchange) this.onchange(this);
		}
	}
	this.div.firstChild.value = option.caption;
}

Combo.prototype.showDropdown = function(w) {
	var oCombo = w || this;

	oCombo.isExpanded = true;

	var iLeft = oCombo.getScreenLeft() + 2;
	var iTop = oCombo.getScreenTop() + oCombo.getHeight(true) + 2;

	if (iTop + oCombo.menuHeight > document.desktop.getHeight(true))
		iTop = oCombo.getScreenTop() - oCombo.menuHeight;

	this.dropdown = new Widget(
		{
			top : iTop,
			left : iLeft,
			width : oCombo.getWidth(),
			bgcolor : oCombo.bgColor,
			border : 1,
			overflow : 'hidden',
			height : oCombo.menuHeight,
			onclick : function(evt, w) {
				w.close();
			},
			onmousedown : QuiX.stopPropag
		});
	
	this.dropdown.combo = this;
	this.dropdown.minw = 60;
	this.dropdown.minh = 50;
	this.dropdown.div.className = 'combodropdown';
	this.dropdown.close = function() {
		document.desktop.overlays.removeItem(this);
		oCombo.isExpanded = false;
		this.destroy();
	};
	
	var cont = new Widget(
		{
			width : '100%',
			height: '100%',
			overflow: 'auto',
			onmousedown : QuiX.cancelDefault
		});	
	this.dropdown.appendChild(cont);

	var opt;
	for (var i=0; i<oCombo.options.length; i++) {
		opt = new Icon(oCombo.options[i]);
		cont.appendChild(opt);
		opt.value = oCombo.options[i].value;
		opt.attachEvent('onmouseover', ComboOption__mouseover);
		opt.attachEvent('onmouseout', ComboOption__mouseout);
		opt.attachEvent('onclick', function(evt, w){
			oCombo.selectOption(w);
		});
		opt.setPos();
	}
	var resizer = new Widget(
		{
			left:"this.parent.getWidth()-15",
			top:"this.parent.getHeight()-15",
			width:16,
			height:16,
			border:0,
			overflow:'hidden'
		});
	this.dropdown.appendChild(resizer);
	resizer.div.className = 'resize';
	resizer.attachEvent('onmousedown', function(evt){
		oCombo.dropdown._startResize(evt);
	});
	
	document.desktop.appendChild(this.dropdown, true);
	document.desktop.overlays.push(this.dropdown);
}

Combo.prototype.destroy = function() {
	if (this.isExpanded) this.dropdown.close();
	Widget.prototype.destroy(this);
}

Combo.prototype.addOption = function(params) {
	params.align = params.align || 'left';
	if ((params.selected=='true' || params.selected == true) && !this.editable) {
		this.selectOption(params);
	}
	this.options.push(params);
}

function ComboOption__mouseover(evt, w) {
	w.div.className = 'option over';
}

function ComboOption__mouseout(evt, w) {
	w.div.className = 'option';
}

function ComboBtn__onclick(evt, w) {
	var oCombo;
	if (w)
		oCombo = w.parent
	else
		oCombo = (this.parentNode || this.parentElement).widget;
	if (!oCombo.isExpanded) {
		QuiX.cleanupOverlays();
		oCombo.showDropdown();
	}
	else
		oCombo.dropdown.close();
	QuiX.stopPropag(evt);
}

// spin button
function Spin(params) {
	params = params || {};
	params.bgcolor = params.bgcolor || 'white';
	params.border = params.border || 1;
	params.overflow = 'hidden';
	params.height = params.height || 24;

	this.base = Widget;
	this.base(params);

	this.div.className = 'combo';
		
	this.name = params.name;
	this.editable = (params.editable=='true' || params.editable==true)?true:false;
	this.min = params.min || 0;
	this.max = params.max;
	this.div.className = 'field';
	this.onchange = getEventListener(params.onchange);

	var e = ce('INPUT');
	e.style.borderWidth = '1px';
	e.style.position='absolute';
	e.style.textAlign = 'right';
	this.div.appendChild(e);
	e.onmousedown = QuiX.stopPropag;
	e.onselectstart = QuiX.stopPropag;
	
	if (params.maxlength) e.maxLength = params.maxlength;
	
	var oSpin = this;

	upbutton = new XButton(
		{
			left : "this.parent.getWidth()-16",
			height : '50%', width : 16, bgcolor : 'silver',
			onclick : SpinUp__onclick
		});
	this.appendChild(upbutton);

	downbutton = new XButton(
		{
			left : "this.parent.getWidth()-16",
			height : '50%', top : '50%', width : 16, bgcolor : 'silver',
			onclick : SpinDown__onclick
		});
	this.appendChild(downbutton);

	if (!this.editable) {
		e.readOnly = true;
		e.style.cursor = 'default';
	} else {
		e.onblur = function() {oSpin.validate();}
	}
	
	this.attachEvent('onkeypress', Spin__onkeypress );
	
	if (params.value)
		this.setValue(parseInt(params.value));
}

Spin.prototype = new Widget;

Spin.prototype._adjustFieldSize = function() {
	if (this.div.firstChild) {
		var nh = this.getHeight();
		var offset = (QuiX.browser=='ie')?20:18;
		this.div.firstChild.style.width = (this.getWidth()-offset) + 'px';
		this.div.firstChild.style.height = nh + 'px';
	}
}

Spin.prototype._setCommonProps = function() {
	Widget.prototype._setCommonProps(this);
	this._adjustFieldSize();
}

Spin.prototype.validate = function() {
	var min = this.min;
	var max = this.max;
	var val = this.getValue();
	if (max && val > max ) this.setValue(max);
	if (val < min) this.setValue(min);
}

Spin.prototype.getValue = function() {
	return( parseInt(this.div.firstChild.value) );
}

Spin.prototype.setValue = function(value) {
	if (value != this.getValue()) {
		this.div.firstChild.value = parseInt(value);
		if (this.onchange) this.onchange(this);
	}
}

function Spin__onkeypress(evt, w) {
	var keycode = (QuiX.browser=='ie')? evt.keyCode:evt.charCode;
	if (!(keycode>47 && keycode<58) && keycode!=0)
		QuiX.cancelDefault(evt);
}

function SpinUp__onclick(evt, w) {
	var oSpin = w.parent;
	var val = oSpin.getValue() + 1;
	if (!isNaN(val)) {
		oSpin.setValue(val);
		oSpin.validate();
	}
}

function SpinDown__onclick(evt, w) {
	var oSpin = w.parent;
	var val = oSpin.getValue() - 1;
	if ( !isNaN(val)) {
		oSpin.setValue(val);
		oSpin.validate();
	}
}

