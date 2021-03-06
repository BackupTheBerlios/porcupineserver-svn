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
	
	this.name = params.name;
	this.editable = (params.editable=='true' || params.editable==true)?true:false;
	this.readonly = (params.readonly=='true' || params.readonly==true)?true:false;
	this.menuHeight = parseInt(params.menuheight) || 100;
	this.div.className = 'field';
	this.selection = null;
	this.isExpanded = false;
	this.attachEvent('onmousedown', QuiX.stopPropag);
	
	var e = ce('INPUT');
	e.style.padding = '1px';
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
	cont.div.style.overflowX = 'hidden';
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
	resizer.attachEvent('onclick', QuiX.stopPropag);
	resizer.attachEvent('onmousedown', function(evt){
		oCombo.dropdown._startResize(evt);
		QuiX.cancelDefault(evt);
	});
	
	this.button = new XButton({
		left : 'this.parent.getWidth()-20',
		height : '100%', width : 20,
		img : params.img || '__quix/images/desc8.gif'
	});
	this.appendChild(this.button);
	if (!this.readonly)
		this.button.attachEvent('onclick', ComboBtn__onclick);
	
	if (this.editable) {
		e.value = (params.value)?params.value:'';
		if (!this.readonly) {
			e.onfocus = function() {
				oCombo._old_value = this.value;
			}
			e.onblur = function() {
				if (oCombo._old_value != this.value) {
					if (oCombo._customRegistry.onchange)
						QuiX.getEventListener(oCombo._customRegistry.onchange)(oCombo);
				}
			}
		}
		else
			e.readonly = true;
	}
	else {
		e.readOnly = true;
		e.style.cursor = 'default';
		this._set = false;
		if (!this.readonly) e.onclick = ComboBtn__onclick;
	}
	
	if (this._isDisabled)
		this.disable();
}

QuiX.constructors['combo'] = Combo;
Combo.prototype = new Widget;

Combo.prototype.customEvents = Widget.prototype.customEvents.concat(['onchange']);

Combo.prototype._adjustFieldSize = function() {
	if (this.div.firstChild) {
		var nh = this.getHeight() - 2;
		var nw = this.getWidth() - 22;
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
	if (this.editable){
		this.div.firstChild.value = value;
		if (this._old_value != value) {
			if (this._customRegistry.onchange)
				QuiX.getEventListener(this._customRegistry.onchange)(this);
		}		
		this._old_value = value;
	}
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
				if ((this._set || old_value == null) && (value != old_value))
					if (this._customRegistry.onchange)
						QuiX.getEventListener(this._customRegistry.onchange)(this);
				break;
			}
		}
		this._set = true;
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

Combo.prototype.clearOptions = function() {
	this.dropdown.widgets[0].clear();
	this.div.firstChild.value = '';
}

Combo.prototype.focus = function() {
	this.div.firstChild.focus();
}

Combo.prototype.showDropdown = function(w) {
	var w = w || this;
	var iLeft = w.getScreenLeft();
	var iTop = w.getScreenTop() + w.getHeight(true);

	if (iTop + w.menuHeight > document.desktop.getHeight(true))
		iTop = w.getScreenTop() - w.menuHeight;

	w.dropdown.top = iTop;
	w.dropdown.left = iLeft;
	if (!w.dropdown.width)
		w.dropdown.width = 'this.combo.getWidth(true)';
	w.dropdown.height = w.menuHeight;
	w.dropdown.setBgColor(w.getBgColor());

	document.desktop.appendChild(w.dropdown);
	w.dropdown.redraw();
	document.desktop.overlays.push(w.dropdown);
	w.isExpanded = true;
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

Combo.prototype.addOption = function(params, w) {
	var w = w || this;
	params.align = params.align || 'left';
	params.width = '100%';
	params.height = params.height || 24;
	params.overflow = 'hidden';
	var opt = new Icon(params);
	opt._isContainer = false;
	opt.selected = false;
	opt.value = params.value;
	w.dropdown.widgets[0].appendChild(opt);
	if ((params.selected=='true' || params.selected == true) && !w.editable) {
		w.selectOption(opt);
	}
	opt.attachEvent('onmouseover', ComboOption__mouseover);
	opt.attachEvent('onmouseout', ComboOption__mouseout);
	opt.attachEvent('onclick', ComboOption__onclick);
	opt.setPosition('relative');
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

// auto complete
function AutoComplete(params) {
	params = params || {};
	params.editable = true;
	this.base = Combo;
	this.base(params);
	this.textField = this.div.firstChild;
	this.url = params.url;
	this.method = params.method;
	if (this.url == '/')
		this.url = '';
	
	//hide combo button
	this.widgets[0].hide();
	
	//attach events
	var oAuto = this;
	this.textField.onkeyup = function(evt) {
		var evt = evt || event;
		oAuto._captureKey(evt);
	}
}

QuiX.constructors['autocomplete'] = AutoComplete;
AutoComplete.prototype = new Combo;

AutoComplete.prototype._getSelection = function(evt) {
	var sel = this.dropdown.widgets[0].getWidgetsByClassName('option over');
	var index = -1;
	if (sel.length > 0) {
		sel = sel[0];
		index = this.options.indexOf(sel);
		sel.div.className = 'option';
	}
	
	switch(evt.keyCode) {
		case 40: 
			if (index + 1 < this.options.length)
				return index + 1;
			return 0;
		case 38: 
			return (index == 0)?this.options.length-1:index-1;
		case 13:
			return index;
	}
}

AutoComplete.prototype._getResults = function() {
	var xmlrpc = new XMLRPCRequest(QuiX.root + this.url);
	xmlrpc.oncomplete = this._showResults;
	xmlrpc.callback_info = this;
	xmlrpc.callmethod(this.method, this.textField.value);
}

AutoComplete.prototype._showResults = function(oReq) {
	var oAuto = oReq.callback_info;
	oAuto.dropdown.widgets[0].clear();
	if (oReq.response.length > 0) {
		for (var i=0; i<oReq.response.length; i++)
			oAuto.addOption(oReq.response[i]);
		if (!oAuto.isExpanded)
			oAuto.showDropdown();
		oAuto.dropdown.redraw();
	}
	else {
		if (oAuto.isExpanded)
			oAuto.dropdown.close();
	}
}

AutoComplete.prototype._captureKey = function(evt) {
	var index;
	if (this.textField.value == '') {
		if (this.isExpanded)
			this.dropdown.close();
		this.dropdown.widgets[0].clear();
		return;
	}

	switch(evt.keyCode)
	{
		case 27: //ESC
		case 39: //Right Arrow
			if (this.isExpanded)
				this.dropdown.close();
			break;
		case 40: // Down Arrow
			if (this.options.length == 0) return;
			if (!this.isExpanded)
				this._getResults();
			else {
				index = this._getSelection(evt);
				var opt = this.options[index];
				this.dropdown.widgets[0].div.scrollTop = opt.div.offsetTop - 20;
				opt.div.className = 'option over';
			}
			break;
		case 38: //Up arrow
			index = this._getSelection(evt);
			if (index < 0)
				return;
			if (!this.isExpanded)
				this.showDropdown();
			var opt = this.options[index];
			this.dropdown.widgets[0].div.scrollTop = opt.div.offsetTop - 20;
			opt.div.className = 'option over';
			break;
		case 13: // enter
			index = this._getSelection(evt);
			if (!this.isExpanded || index < 0)
				return;
			this.dropdown.close();
			this.selectOption(this.options[index]);
			break;
		default:
			this._getResults();
	}
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
	this.div.style.overflowX = 'hidden';
	this.multiple = (params.multiple=="true")?true:false;
	this.posts = params.posts || "selected";
	this.options = [];
	this.selection = [];
}

QuiX.constructors['selectlist'] = SelectList;
SelectList.prototype = new Widget;

SelectList.prototype.addOption = function(params) {
	params.imgalign = 'left';
	params.align = 'left';
	params.width = '100%';
	params.height = params.height || 24;
	params.overflow = 'hidden';
	params.onmousedown = QuiX.getEventWrapper(SelectOption__onmousedown,
												params.onmousedown);
	var w = new Icon(params);
	this.appendChild(w);
	w.selected = false;
	w.value = params.value;
	if (params.selected == 'true' || params.selected == true) {
		this.selectOption(w);
	}
	w.setPosition('relative');
	w.redraw();
	
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

function SelectOption__onmousedown(evt, option) {
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
