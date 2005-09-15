/************************
Form & Field controls
************************/
function Form(params) {
	params = params || {};
	params.width = params.width || '100%';
	params.height = params.height || '100%';
	this.base = Widget;
	this.base(params);
	this.files = [];
	this.action = params.action;
	this.method = params.method;
	this.elements = [];
}

Form.prototype = new Widget;

Form.prototype.getElementByName = function(name) {
	for (var i=0; i<this.elements.length; i++) {
		if (this.elements[i].name==name) return(this.elements[i]);
	}
}

Form.prototype.submit = function(f_callback) {
	function submit_oncomplete(req) {
		var form = req.callback_info;
		f_callback(req.response, form);
	}
	
	var formData = {};
	// build form data
	for (var i=0; i<this.elements.length; i++) {
		if (this.elements[i].name && !this.elements[i]._isDisabled)
			formData[this.elements[i].name] = this.elements[i].getValue();
	}
	// send data
	var xmlrpc = new XMLRPCRequest(this.action);
	xmlrpc.oncomplete = submit_oncomplete;
	xmlrpc.callback_info = this;
	xmlrpc.callmethod(this.method, formData);
}

function Field(params) {
	params = params || {};
	this.base = Widget;
	params.height = params.height || 22;
	params.border = params.border || 1;
	params.overflow = 'hidden';
	this.type = params.type || 'text';
	this.base(params);
	this.name = params.name;
	this.readonly = (params.readonly=='true')?true:false;
	this.onchange = getEventListener(params.onchange);
	var e;
	switch (this.type) {
		case 'checkbox':
			var sChecked = (params.value==true || params.value == 'true')?'checked':'';
			this.div.innerHTML = '<input type=checkbox ' + sChecked + '>';
			e = this.div.firstChild;
			if (this.readonly) e.disabled = true;
			this.getValue = function() { return e.checked; }
			this.setValue = function(value) { e.checked = value; }
			break;
		case 'file':
			throw new QuiX.Exception("Invalid field type.\nUse the file control instead.")
			break;
		default:
			this.div.className = 'field';
			e = (this.type=='textarea')?ce('TEXTAREA'):ce('INPUT');
			e.style.borderWidth = '1px';
			e.style.position='absolute';
			if (this.readonly) e.readOnly = true;
			//fixme: wait for MS to fix it
			//e.style.width = '100%';
			//e.style.height = '100%';
			if (this.type!='textarea') e.type = this.type;
			e.value = (params.value)?params.value:'';
			this.getValue = function() { return e.value; }
			this.setValue = function(value) { e.value = value; }
			if (this.type=='hidden') this.hide();
			this.div.appendChild(e);
	}

	e.onmousedown = QuiX.stopPropag;
	e.onselectstart = QuiX.stopPropag;
	var oField = this;
	e.onchange = function() {
		if (oField.onchange) oField.onchange(oField);
	}

	if (params.onclick) this.attachEvent('onclick', params.onclick);
	this._adjustFieldSize();
}

Field.prototype = new Widget;

Field.prototype._adjustFieldSize = function() {
	if (this.type!='checkbox' && this.div.firstChild) {
		var nw = this.getWidth();
		var nh = this.getHeight();
		if (this.type=='textarea' && QuiX.browser=='ie') {
			nw -= 3;
			nh -= 3;
		} else if (this.type=='textarea' && QuiX.browser=='moz') {
			this.div.firstChild.style.top = '-1px';
		}
		if (nw < 0) nw = 0;
		if (nh < 0) nh = 0;
		this.div.firstChild.style.width = nw + 'px';
		this.div.firstChild.style.height = nh + 'px';
	}
}

Field.prototype.enable = function() {
	if (this.div.firstChild) {
		this.div.firstChild.disabled = false;
		this.div.firstChild.style.backgroundColor = '';
	}
	Widget.prototype.enable(this);
}

Field.prototype.disable = function() {
	if (this.div.firstChild) {
		this.div.firstChild.disabled = true;
		this.div.firstChild.style.backgroundColor = 'menu';
	}
	Widget.prototype.disable(this);
}

Field.prototype._setCommonProps = function() {
	this.base.prototype._setCommonProps(this);
	this._adjustFieldSize();
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
	params.onclick = function(evt, w){oSelectList._optionSelected(evt, w)};
	var w = new Icon(params);
	this.appendChild(w);
	w.isSelected = false;
	w.value = params.value;
	w.setPos();
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

SelectList.prototype._optionSelected = function(evt, option) {
	var oSelectList = this;
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
	if (!this.multiple) {
		this.clearSelection();
		selectOption(option);
	}
	else {
		if (!evt.shiftKey) {
			this.clearSelection();
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