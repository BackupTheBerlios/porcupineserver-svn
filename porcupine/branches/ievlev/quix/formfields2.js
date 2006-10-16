/************************
Field controls 2
************************/
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
	this.selection = null;
	this.isExpanded = false;
	this.attachEvent('onmousedown', QuiX.stopPropag);

	var e = ce('INPUT');
	e.style.borderWidth = '1px';
	e.style.position = 'absolute';
	this.div.appendChild(e);
	e.onselectstart = QuiX.stopPropag;
	
	var oCombo = this;

	this.dropdown = new Widget({
		border : 1,
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
		this.detach();
	};

	var cont = new Widget({
		width : '100%',
		height: '100%',
		overflow: 'auto',
		onmousedown : QuiX.cancelDefault
	});
	this.dropdown.appendChild(cont);
	this.options = cont.widgets;

	var resizer = new Widget({
		left : 'this.parent.getWidth()-16',
		top : 'this.parent.getHeight()-16',
		width : 16,
		height : 16,
		border : 0,
		overflow : 'hidden'
	});
	this.dropdown.appendChild(resizer);
	resizer.div.className = 'resize';
	resizer.attachEvent('onmousedown', function(evt){
		oCombo.dropdown._startResize(evt);
	});

	this.button = new XButton({
		left : 'this.parent.getWidth()-20',
		height : '100%', width : 20,
		img : params.img || 'images/desc8.gif'
	});
	this.appendChild(this.button);
	if (!this.readonly)
		this.button.attachEvent('onclick', ComboBtn__onclick);
	
	if (this.editable) {
		e.value = (params.value)?params.value:'';
		if (!this.readonly) {
			e.onchange = function() {
				if (oCombo._customRegistry.onchange)
					getEventListener(oCombo._customRegistry.onchange)(oCombo);
			}
		}
		else
			e.readonly = true
	}
	else {
		e.readOnly = true;
		e.style.cursor = 'default';
		if (!this.readonly) e.onclick = ComboBtn__onclick;
	}
}

Combo.prototype = new Widget;

Combo.prototype.customEvents = Widget.prototype.customEvents.concat(['onchange']);

Combo.prototype._adjustFieldSize = function() {
	if (this.div.firstChild) {
		var nh = this.getHeight();
		var nw = this.getWidth()-21;
		this.div.firstChild.style.width = (nw>0?nw:0) + 'px';
		this.div.firstChild.style.height = nh + 'px';
	}
}

Combo.prototype._setCommonProps = function() {
	Widget.prototype._setCommonProps(this);
	this._adjustFieldSize();
}

Combo.prototype.getValue = function() {
	if (this.editable)
		return this.div.firstChild.value;
	else {
		if (this.selection)
			return this.selection.value;
		else
			return null;
	}
}

Combo.prototype.setValue = function(value) {
	if (this.editable)
		this.div.firstChild.value = value;
	else {
		var opt, opt_value;
		var old_value = this.getValue();
		this.selection = null;
		this.div.firstChild.value = '';
		for (var i=0; i<this.options.length; i++) {
			this.options[i].selected = false;
		}
		for (i=0; i<this.options.length; i++) {
			opt = this.options[i];
			opt_value = (opt.value!=undefined)?opt.value:opt.getCaption();
			if (opt_value == value) {
				this.selection = opt;
				opt.selected = true;
				this.div.firstChild.value = opt.getCaption();
				if (value != old_value)
					if (this._customRegistry.onchange)
						getEventListener(this._customRegistry.onchange)(this);
				return;
			}
		}
	}
}

Combo.prototype.enable = function() {
	if (this.div.firstChild) {
		this.div.firstChild.disabled = false;
		this.div.firstChild.style.backgroundColor = '';
		if (!this.readonly) this.div.firstChild.onclick = ComboBtn__onclick;
	}
	Widget.prototype.enable(this);
}

Combo.prototype.disable = function() {
	if (this.div.firstChild) {
		this.div.firstChild.disabled = true;
		this.div.firstChild.style.backgroundColor = 'menu';
		if (!this.readonly) this.div.firstChild.onclick = null;
	}
	Widget.prototype.disable(this);
}

Combo.prototype.selectOption = function(option) {
	var value = (option.value!=undefined)?option.value:option.getCaption();
	this.setValue(value);
}

Combo.prototype.reset = function() {
	if (this.editable)
		this.div.firstChild.value = '';
	else {
		for (var i=0; i<this.options.length; i++) {
			this.options[i].selected = false;
		}
		this.selection = null;
		this.div.firstChild.value = '';
	}	
}

Combo.prototype.showDropdown = function(w) {
	var oCombo = w || this;

	var iLeft = oCombo.getScreenLeft();
	var iTop = oCombo.getScreenTop() + oCombo.getHeight(true);

	if (iTop + oCombo.menuHeight > document.desktop.getHeight(true))
		iTop = oCombo.getScreenTop() - oCombo.menuHeight;

	oCombo.dropdown.top = iTop;
	oCombo.dropdown.left = iLeft;
	if (!oCombo.dropdown.width)
		oCombo.dropdown.width = 'this.combo.getWidth(true)';
	oCombo.dropdown.height = oCombo.menuHeight;
	oCombo.dropdown.setBgColor(oCombo.getBgColor());

	document.desktop.appendChild(oCombo.dropdown);
	document.desktop.overlays.push(oCombo.dropdown);
	oCombo.isExpanded = true;
}

Combo.prototype.destroy = function() {
	if (this.isExpanded) this.dropdown.close();
	Widget.prototype.destroy(this);
}

Combo.prototype.setBgColor = function(color) {
	this.div.style.backgroundColor = color;
	if (this.div.firstChild)
		this.div.firstChild.style.backgroundColor = color;
}

Combo.prototype.addOption = function(params) {
	params.align = params.align || 'left';
	params.width = params.width || '100%';
	var opt = new Icon(params);
	opt.selected = false;
	opt.value = params.value;
	this.dropdown.widgets[0].appendChild(opt);
	if ((params.selected=='true' || params.selected == true) && !this.editable) {
		this.selectOption(opt);
	}
	opt.attachEvent('onmouseover', ComboOption__mouseover);
	opt.attachEvent('onmouseout', ComboOption__mouseout);
	opt.attachEvent('onclick', ComboOption__onclick);
	opt.setDisplay();
	opt.setPosition();
	return opt;
}

function ComboOption__mouseover(evt, w) {
	w.div.className = 'option over';
}

function ComboOption__mouseout(evt, w) {
	w.div.className = 'option';
}

function ComboOption__onclick(evt, w) {
	w.parent.parent.combo.selectOption(w);
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


// Select list
function SelectList(params) {
	params = params || {};
	params.bgcolor = params.bgcolor || 'white';
	params.border = params.border || 1;
	params.overflow = 'auto';
	this.base = Widget;
	this.base(params);
	this.name = params.name;
	this.div.className = 'field';
	this.multiple = (params.multiple=="true")?true:false;
	this.posts = params.posts || "selected";
	this.options = [];
	this.selection = [];
}

SelectList.prototype = new Widget;

SelectList.prototype.addOption = function(params) {
	var oSelectList = this;
	params.imgalign = 'left';
	params.align = 'left';
	params.width = '100%';
	params.onclick = QuiX.getEventWrapper(SelectOption__onclick, params.onclick);
	var w = new Icon(params);
	this.appendChild(w);
	w.selected = false;
	w.value = params.value;
	if (params.selected == 'true' || params.selected == true) {
		this.selectOption(w);
	}
	w.setDisplay();
	w.setPosition();
	w.div.style.whiteSpace = 'nowrap';
	this.options.push(w);
	return(w);
}

SelectList.prototype.clear = function() {
	for (var i=this.options.length-1; i>=0; i--) {
		this.options[i].destroy();
	}
	this.options = [];
	this.selection = [];
}

SelectList.prototype.removeSelected = function() {
	for (var i=0; i<this.selection.length; i++) {
		this.options.removeItem(this.selection[i]);
		this.selection[i].destroy();
	}
	this.selection = [];
}

SelectList.prototype.clearSelection = function() {
	for (var i=0; i<this.selection.length; i++) {
		this.deSelectOption(this.selection[i]);
	}
	//this.selection = [];
}

SelectList.prototype.selectOption = function(option) {
	if (!option.selected) {
		if (!this.multiple)
			this.clearSelection();
		option.div.className = 'optionselected';
		option.selected = true;
		this.selection.push(option);
	}
}

SelectList.prototype.deSelectOption = function(option) {
	//var oSelectList = this;
	if (option.selected) {
		option.div.className = 'label';
		option.selected = false;
		this.selection.removeItem(option);
	}
}

SelectList.prototype.getValue = function() {
	vs = [];
	if (this.posts == 'all') {
		for (var i=0; i<this.options.length; i++) {
			vs.push(this.options[i].value);
		}
		return vs;
	}
	else {
		for (var i=0; i<this.selection.length; i++) {
			vs.push(this.selection[i].value);
		}
		if (this.multiple)
			return vs;
		else
			return vs[0];
	}
}

function SelectOption__onclick(evt, option) {
	var oSelectList = option.parent;
	if (!oSelectList.multiple)
		oSelectList.selectOption(option);
	else {
		if (!evt.shiftKey) {
			oSelectList.clearSelection();
			oSelectList.selectOption(option);
		}
		else
			if (option.selected)
				oSelectList.deSelectOption(option);
			else
				oSelectList.selectOption(option);
	}
}
