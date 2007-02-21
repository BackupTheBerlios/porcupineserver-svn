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
	params.border = params.border || 1;
	params.overflow = 'hidden';
	this.type = params.type || 'text';
	if (this.type == 'radio') {
		this._value = params.value || '';
		params.onclick = QuiX.getEventWrapper(Radio__click, params.onclick);
		params.overflow = '';
	}
	params.height = params.height || 22;
	params.padding = '0,0,0,0';
	this.base(params);
	this.name = params.name;
	this.readonly = (params.readonly=='true' || params.readonly==true)?true:false;
	this.onchange = params.onchange;
	var e;
	switch (this.type) {
		case 'checkbox':
		case 'radio':
			var sChecked;
			if (this.type=='checkbox')
				sChecked = (params.value==true || params.value == 'true')?'checked':'';
			else
				sChecked = (params.checked==true || params.checked == 'true')?'checked':'';
			this.div.innerHTML = '<input type=' + this.type + ' ' + sChecked +
				' style="vertical-align:middle">';
			e = this.div.firstChild;
			if (this.readonly) e.disabled = true;
			if (params.caption) this.setCaption(params.caption);
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
			this.textPadding = params.textpadding || 0;
			if (this.type=='hidden') this.hide();
			this.div.appendChild(e);
	}

	e.onmousedown = QuiX.stopPropag;
	e.onselectstart = QuiX.stopPropag;
	
	var oField = this;
	e.onchange = function() {
		if (oField.onchange)
			getEventListener(oField.onchange)(oField);
	}

	this._adjustFieldSize();
	if (this._isDisabled) {
		e.disabled = true;
		e.style.backgroundColor = 'menu';
	}
}

Field.prototype = new Widget;

Field.prototype.getValue = function() {
	switch (this.type) {
	case 'checkbox':
		return this.div.firstChild.checked;
	case 'radio':
		var radio;
		var id = this.getId();
		if (id) {
			var radio_group = this.parent.getWidgetById(id);
			for (var i=0; i<radio_group.length; i++) {
				radio = radio_group[i].div.firstChild;
				if (radio.checked)
					return (radio_group[i]._value);
			}
		}
		break;
	default:
		return this.div.firstChild.value;
	}
}

Field.prototype.setValue = function(value) {
	switch (this.type) {
	case 'checkbox':
		this.div.firstChild.checked = value;
		break;
	case 'radio':
		var radio;
		var id = this.getId();
		if (id) {
			var radio_group = this.parent.getWidgetById(id);
			for (var i=0; i<radio_group.length; i++) {
				radio = radio_group[i].div.firstChild;
				if (radio_group[i]._value == value)
					radio.checked = true;
				else
					radio.checked = false;
			}
		}
		break;
	default:
		this.div.firstChild.value = value;
	}
}

Field.prototype.getCaption = function() {
	if (this.type=='radio' || this.type=='checkbox') {
		var oSpan = this.div.getElementsByTagName('SPAN')[0];
		if (oSpan)
			return oSpan.innerHTML;
		else
			return '';
	}
}

Field.prototype.setCaption = function(caption) {
	if (this.type=='radio' || this.type=='checkbox') {
		var textnode = this.div.getElementsByTagName('SPAN')[0];
		if (!textnode) {
			textnode =ce('SPAN');
			textnode.style.cursor = 'default';
			textnode.innerHTML = caption;
			textnode.style.verticalAlign = 'middle';
			this.div.appendChild(textnode);
		}
		else {
			textnode.innerHTML = caption;
		}
	}
}

Field.prototype.enable = function() {
	if (this.div.firstChild) {
		this.div.firstChild.disabled = false;
		this.div.firstChild.style.backgroundColor = this.getBgColor();
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

Field.prototype.setBgColor = function(color) {
	this.div.style.backgroundColor = color;
	if (this.type == 'text' || this.type == 'textarea' || this.type == 'password')
		this.div.firstChild.style.backgroundColor = color;
}

Field.prototype.redraw = function(bForceAll) {
	if (this.type == 'text' || this.type == 'textarea' || this.type == 'password')
		this.div.firstChild.style.padding = this.textPadding + 'px' + ' ' + this.textPadding + 'px'+ ' ' + this.textPadding + 'px'+ ' ' + this.textPadding + 'px';
	Widget.prototype.redraw(bForceAll, this);
}

Field.prototype._adjustFieldSize = function() {
	if (this.type!='checkbox' && this.type!='radio' && this.div.firstChild) {
		var nw = this.getWidth() || 0;
		var nh = this.getHeight() || 0;
		nw -= 1;
		nh -= 1;
		if (this.type=='textarea' && QuiX.browser=='moz')
			this.div.firstChild.style.top = '-1px';
		if (nw < 0) nw = 0;
		if (nh < 0) nh = 0;
		this.div.firstChild.style.width = nw + 'px';
		this.div.firstChild.style.height = nh + 'px';
	}
}

Field.prototype._setCommonProps = function() {
	this.base.prototype._setCommonProps(this);
	this._adjustFieldSize();
}

function Radio__click(evt, w) {
	var id = w.getId();
	if (id) {
		var radio_group = w.parent.getWidgetById(id);
		for (var i=0; i<radio_group.length; i++) {
			radio = radio_group[i].div.firstChild;
			radio.checked = false;
		}
		w.div.firstChild.checked = true;
	}
}

// spin button
function Spin(params) {
	params = params || {};
	params.bgcolor = params.bgcolor || 'white';
	params.border = params.border || 1;
	params.padding = '0,0,0,0';
	params.overflow = 'hidden';
	params.height = params.height || 22;

	this.base = Widget;
	this.base(params);

	this.div.className = 'combo';
		
	this.name = params.name;
	this.editable = (params.editable=='true' || params.editable==true)?true:false;
	this.min = params.min || 0;
	this.max = params.max;
	this.step = parseInt(params.step) || 1;
	this.div.className = 'field';

	var e = ce('INPUT');
	e.style.borderWidth = '1px';
	e.style.position='absolute';
	e.style.textAlign = 'right';
	this.div.appendChild(e);
	e.onmousedown = QuiX.stopPropag;
	e.onselectstart = QuiX.stopPropag;
	
	if (params.maxlength)
		e.maxLength = params.maxlength;
	
	var oSpin = this;

	upbutton = new XButton({
		left : "this.parent.getWidth()-16",
		height : '50%', width : 16,
		onclick : SpinUp__onclick
	});
	this.appendChild(upbutton);

	downbutton = new XButton({
		left : "this.parent.getWidth()-16",
		height : '50%', top : '50%', width : 16,
		onclick : SpinDown__onclick
	});
	this.appendChild(downbutton);

	if (!this.editable) {
		e.readOnly = true;
		e.style.cursor = 'default';
	} else {
		e.onblur = function() {oSpin.validate();}
	}
	
	this.attachEvent('onkeypress', Spin__onkeypress);
	
	if (params.value)
		this.setValue(params.value);

	this.onchange = params.onchange;
	var oField = this;
	e.onchange = function() {
		var v = oField.validate( oField.getValue() );
		if (v==0) {
			if (oField.onchange)
				getEventListener(oField.onchange)(oField);
		}
		else if (v==1)
			oField.setValue(oField.max);
		else if (v==-1)
			oField.setValue(oField.min);
	}
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

Spin.prototype.validate = function(val) {
	var min = this.min;
	var max = this.max;
	if (max && val > max )
		return 1;
	if (val < min)
		return -1;
	return 0;
}

Spin.prototype.setBgColor = function(color) {
	this.div.style.backgroundColor = color;
	if (this.div.firstChild)
		this.div.firstChild.style.backgroundColor = color;
}

Spin.prototype.getValue = function() {
	return( parseInt(this.div.firstChild.value) );
}

Spin.prototype.setValue = function(value) {
	if (value != this.getValue()) {
		this.div.firstChild.value = parseInt(value);
		if (this.onchange)
			getEventListener(this.onchange)(this);
	}
}

function Spin__onkeypress(evt, w) {
	var keycode = (QuiX.browser=='ie')? evt.keyCode:evt.charCode;
	if (!(keycode>47 && keycode<58) && keycode!=0)
		QuiX.cancelDefault(evt);
}

function SpinUp__onclick(evt, w) {
	var oSpin = w.parent;
	var val = oSpin.getValue() + oSpin.step;
	alert(val)
	if (!isNaN(val)) {
		if (oSpin.validate(val)==0)
			oSpin.setValue(val);
	}
}

function SpinDown__onclick(evt, w) {
	var oSpin = w.parent;
	var val = oSpin.getValue() - oSpin.step;
	if (!isNaN(val)) {
		if (oSpin.validate(val)==0)
			oSpin.setValue(val);
	}
}
