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

// iframe
function IFrame(params) {
	params = params || {};
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'ifrm';
	var frame = ce("IFRAME");
	frame.frameBorder = 0;
	frame.src = params.src || "";
	frame.style.width = "100%";
	frame.style.height = "100%";
	this.div.appendChild(frame);
}

IFrame.prototype = new Widget;

IFrame.prototype.setSource = function(src)
{
	this.div.firstChild.src = src;
}

IFrame.prototype.getSource = function() {
	return this.div.firstChild.src;
}

// GroupBox
function GroupBox(params) {
	params = params || {};
	params.overflow = 'hidden';
	
	var v = true;
	if (params.checked) {
		v = params.value || true;
		this.caption = new Field({
			left: 5,
			bgcolor: params.bgcolor,
			caption: params.caption,
			border: "thin",
			value: v,
			onclick: GroupBox__checkBody,
			type: "checkbox"
		});
	}
	else
		this.caption = new Label({
			left:5,
			bgcolor: params.bgcolor,
			caption: params.caption
		});
	
	this.base = Widget;
	this.base(params);
	this.div.className = 'groupbox';
	
	this.border = new Widget({
		top: 8,
		width:"100%",
		padding:"12,12,12,12",
		height: "this.parent.getHeight()-this.top",
		border: params.border || 2
	});
	this.border.div.className = "groupboxframe";
	this.appendChild(this.border);

	this.appendChild(this.caption);
	this.caption.div.className = this.div.className;

	this.body = new Widget({
		width: "100%",
		height: "100%",
		disabled: !v
	});
	this.border.appendChild(this.body);
}

GroupBox.prototype = new Widget;

GroupBox.prototype.customEvents = Widget.prototype.customEvents.concat(['onstatechange']);

GroupBox.prototype.setBgColor = function(color) {
	Widget.prototype.setBgColor(color,this);
	this.caption.setBgColor(color);
}

GroupBox.prototype.getValue = function() {
	return (this.caption.getValue)?this.caption.getValue():true;
}

GroupBox.prototype.setValue = function(value) {
	if (this.caption.setValue) {
		this.caption.setValue(value);
		GroupBox__checkBody(null, this.caption);
	}
}

function GroupBox__checkBody(evt ,w) {
	var box = w.parent;
	if (w.getValue())
		box.body.enable();
	else
		box.body.disable();
	if (box._customRegistry.onstatechange)
		box._customRegistry.onstatechange(evt, box);
	if (evt)
		QuiX.stopPropag(evt);
}

// slider
function Slider(params) {
	params = params || {};
	
	params.padding = '0,0,0,0',
	params.height = params.height || 26;
	params.overflow = 'hidden';

	this.base = Widget;
	this.base(params);
	this.div.className = 'slider';

	this.min = parseInt(params.min) || 0;
	this.max = parseInt(params.max) || 100;
	this.name = params.name;
	
	var slot = new Widget({
		top : 'center',
		left : 4,
		width : 'this.parent.getWidth() - 8',
		height : 2,
		bgcolor : 'silver',
		border : 1
	});
	slot.div.className = 'slot';
	this.appendChild(slot);
	
	var handle = new Icon({
		img : '__quix/images/slider.gif',
		top : 'center',
		width : 10,
		height : 18,
		border : 0,
		padding : '0,0,0,0'
	});
	handle.div.className = 'handle';
	this.appendChild(handle);
	this.handle = handle;
	
	this.handle.attachEvent('onmousedown', Slider__mousedown)
	
	this.setValue(params.value || this.min);
}

Slider.prototype = new Widget;

Slider.prototype.customEvents = Widget.prototype.customEvents.concat(['onchange']);

Slider.prototype.getValue = function() {
	return this._value;
}

Slider.prototype.setValue = function(val) {
	this._value = parseFloat(val);
	if (this._value > this.max)
		this._value = this.max;
	if (this._value < this.min)
		this._value = this.min;
	this._update();
}

Slider.prototype._update = function() {
	var x = '((this.parent._value - this.parent.min) / (this.parent.max - this.parent.min)) * (this.parent.getWidth() - 8)';
	this.handle.moveTo(x ,'center');
}

function Slider__mousedown(evt, handle) {
	QuiX.startX = evt.clientX;
	QuiX.tmpWidget = handle;
	handle.attributes.__startx = handle.getLeft();
	document.desktop.attachEvent('onmousemove', Slider__mousemove);
	document.desktop.attachEvent('onmouseup', Slider__mouseup);
}

function Slider__mousemove(evt, desktop) {
	var offsetX = evt.clientX - QuiX.startX;
	var new_x = QuiX.tmpWidget.attributes.__startx + offsetX;
	new_x = (new_x<0)?0:new_x;
	new_x = (new_x>QuiX.tmpWidget.parent.getWidth()-8)?QuiX.tmpWidget.parent.getWidth()-8:new_x;
	QuiX.tmpWidget.moveTo(new_x, 'center');
}

function Slider__mouseup(evt, desktop) {
	document.desktop.detachEvent('onmousemove');
	document.desktop.detachEvent('onmouseup');
	
	var slider = QuiX.tmpWidget.parent;
	var range_length = slider.max - slider.min;
	var old_value = slider._value;
	slider._value =  slider.min + (QuiX.tmpWidget.getLeft() / (slider.getWidth() - 8)) * range_length;
	slider._update();
	if (slider._customRegistry.onchange && old_value != slider._value)
		box._customRegistry.onchange(slider);
}