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
		var value = (option.value!=undefined)?option.value:option.getCaption();
		if (this.selection!=value) {
			this.selection = value;
			if (this.onchange) this.onchange(this);
		}
	}
	this.div.firstChild.value = option.caption || option.getCaption();
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
			bgcolor : oCombo.getBgColor(),
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
		opt.setPosition();
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
	params.onclick = QuiX.getEventWrapper(SelectOption__onclick, params.onclick);
	var w = new Icon(params);
	this.appendChild(w);
	w.isSelected = false;
	w.value = params.value;
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
		var w = this.selection[i];
		w.div.className = 'label';
		w.isSelected = false;
	}
	this.selection = [];
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
	function selectOption(option) {
		option.div.className = 'optionselected';
		option.isSelected = true;
		oSelectList.selection.push(option);
	}
	function deselectOption(option) {
		option.div.className = 'label';
		option.isSelected = false;
		oSelectList.selection.removeItem(option);
	}
	if (!oSelectList.multiple) {
		oSelectList.clearSelection();
		selectOption(option);
	}
	else {
		if (!evt.shiftKey) {
			oSelectList.clearSelection();
			selectOption(option);
		}
		else if (evt.shiftKey && !option.isSelected) {
			selectOption(option);
		}
		else {
			deselectOption(option);
		}
	}
}
