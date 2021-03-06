// horizontal rule
QuiX.ui.HR = function(params) {
	params = params || {};
	this.base = QuiX.ui.Widget;
	params.border = params.border || 1;
	params.height = params.height || 2;
	params.overflow = 'hidden';
	this.base(params);
	this._isContainer = false;
	this.div.className = 'separator';
}

QuiX.constructors['hr'] = HR;
QuiX.ui.HR.prototype = new QuiX.ui.Widget;
// backwards compatibility
var HR = QuiX.ui.HR;

// iframe
QuiX.ui.IFrame = function(params) {
	params = params || {};
	params.overflow = 'hidden';
	this.base = QuiX.ui.Widget;
	this.base(params);
	this._isContainer = false;
	this.div.className = 'ifrm';
	this.frame = ce("IFRAME");
	this.frame.frameBorder = 0;
	QuiX.addEvent(this.frame, 'onload', IFrame.prototype._onload);
	this.frame.src = params.src || "";
	this.frame.style.width = "100%";
	this.frame.style.height = "100%";
	
	this.div.appendChild(this.frame);
}

QuiX.constructors['iframe'] = QuiX.ui.IFrame;
QuiX.ui.IFrame.prototype = new QuiX.ui.Widget;
QuiX.ui.IFrame.prototype.customEvents =
	QuiX.ui.Widget.prototype.customEvents.concat(['ondocumentload']);
// backwards compatibility
var IFrame = QuiX.ui.IFrame;

QuiX.ui.IFrame.prototype.redraw = function(bForceAll, memo) {
	this.frame.style.visibility = 'hidden';
	QuiX.ui.Widget.prototype.redraw.apply(this, arguments);
	this.frame.style.visibility = '';
}

QuiX.ui.IFrame.prototype.setSource = function(src) {
	this.frame.src = src;
}

QuiX.ui.IFrame.prototype.getSource = function() {
	return this.frame.src;
}

QuiX.ui.IFrame.prototype.getDocument = function() {
	return this.frame.contentDocument || this.frame.contentWindow.document;
}

QuiX.ui.IFrame.prototype._onload = function(evt) {
	evt = evt || event;
	var w = QuiX.getTargetWidget(evt);
	if (w._customRegistry.ondocumentload)
		w._customRegistry.ondocumentload(w);
}

// GroupBox
QuiX.ui.GroupBox = function(params) {
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
	
	this.base = QuiX.ui.Widget;
	this.base(params);
	this.div.className = 'groupbox';
	
	this.border = new QuiX.ui.Widget({
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

	this.body = new QuiX.ui.Widget({
		width: "100%",
		height: "100%",
		disabled: !v
	});
	this.border.appendChild(this.body);
}

QuiX.constructors['groupbox'] = QuiX.ui.GroupBox;
QuiX.ui.GroupBox.prototype = new QuiX.ui.Widget;
// backwards compatibility
var GroupBox = QuiX.ui.GroupBox;

QuiX.ui.GroupBox.prototype.customEvents =
    QuiX.ui.Widget.prototype.customEvents.concat(['onstatechange']);

QuiX.ui.GroupBox.prototype.setBgColor = function(color) {
	QuiX.ui.Widget.prototype.setBgColor.apply(this, arguments);
	this.caption.setBgColor(color);
}

QuiX.ui.GroupBox.prototype.getValue = function() {
	return (this.caption.getValue)?this.caption.getValue():true;
}

QuiX.ui.GroupBox.prototype.setValue = function(value) {
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
QuiX.ui.Slider = function(params) {
	params = params || {};
	
	params.padding = '0,0,0,0',
	params.height = params.height || 26;
	params.overflow = 'visible';

	this.base = QuiX.ui.Widget;
	this.base(params);
	this.div.className = 'slider';

	this.min = parseInt(params.min) || 0;
	this.max = parseInt(params.max) || 100;
	this.name = params.name;
	
	var slot = new QuiX.ui.Widget({
		top : 'center',
		left : 4,
		width : 'this.parent.getWidth() - 8',
		height : 2,
		bgcolor : 'silver',
		border : 1,
		overflow : 'hidden'
	});
	slot.div.className = 'slot';
	this.appendChild(slot);
	
	var handle = new QuiX.ui.Icon({
		img : '$THEME_URL$images/slider.gif',
		top : 'center',
		width : 10,
		height : 18,
		border : 0,
		padding : '0,0,0,0',
		overflow : 'visible'
	});
	handle.div.className = 'handle';
	this.appendChild(handle);
	this.handle = handle;
	
	this.handle.attachEvent('onmousedown', Slider__mousedown)
	
	var lbl = new Label({
		top : 10,
		left : 10
	});
	this.handle.appendChild(lbl);
	this.label = lbl;

	this.setValue(params.value || this.min);
}

QuiX.constructors['slider'] = QuiX.ui.Slider;
QuiX.ui.Slider.prototype = new QuiX.ui.Widget;
// backwards compatibility
var Slider = QuiX.ui.Slider;

QuiX.ui.Slider.prototype.customEvents =
    QuiX.ui.Widget.prototype.customEvents.concat(['onchange']);

QuiX.ui.Slider.prototype.getValue = function() {
	return this._value;
}

QuiX.ui.Slider.prototype.setValue = function(val) {
	this._value = Math.round(parseFloat(val) * 100) / 100;
	if (this._value > this.max)
		this._value = this.max;
	if (this._value < this.min)
		this._value = this.min;
	this._update();
}

QuiX.ui.Slider.prototype._update = function() {
	var x = '((this.parent._value - this.parent.min)/' +
            '(this.parent.max - this.parent.min))*' +
            '(this.parent.getWidth() - 8)';
	this.handle.moveTo(x ,'center');
	this.label.setCaption(this._value);
}

function Slider__mousedown(evt, handle) {
	QuiX.startX = evt.clientX;
	QuiX.tmpWidget = handle;
	handle.attributes.__startx = handle.getLeft();
	document.desktop.attachEvent('onmousemove', Slider__mousemove);
	document.desktop.attachEvent('onmouseup', Slider__mouseup);
	QuiX.cancelDefault(evt);
}

function Slider__mousemove(evt, desktop) {
	var offsetX = evt.clientX - QuiX.startX;
	var new_x = QuiX.tmpWidget.attributes.__startx + offsetX;
	var slider = QuiX.tmpWidget.parent;
	var range_length = slider.max - slider.min;
		
	new_x = (new_x<0)?0:new_x;
	new_x = (new_x>QuiX.tmpWidget.parent.getWidth()-8)?QuiX.tmpWidget.parent.getWidth()-8:new_x;
	
	var new_value = slider.min + (QuiX.tmpWidget.getLeft() / (slider.getWidth() - 8)) * range_length;
	slider.label.setCaption(Math.round(new_value * 100) / 100);
	
	QuiX.tmpWidget.moveTo(new_x, 'center');
}

function Slider__mouseup(evt, desktop) {
	document.desktop.detachEvent('onmousemove');
	document.desktop.detachEvent('onmouseup');
	
	var slider = QuiX.tmpWidget.parent;
	var range_length = slider.max - slider.min;
	var old_value = slider._value;
	var new_value = slider.min + (QuiX.tmpWidget.getLeft() / (slider.getWidth() - 8)) * range_length;
	slider._value = Math.round(new_value * 100) / 100;
	
	slider._update();
	if (slider._customRegistry.onchange && old_value != slider._value)
		slider._customRegistry.onchange(slider);
}

// progress bar
QuiX.ui.ProgressBar = function(params) {
	params = params || {};
	this.base = QuiX.ui.Widget;
	params.border = 1;
	params.overflow = 'hidden';
	this.base(params);
	this.div.className = 'progressbar';
	this.bar = new QuiX.ui.Widget({height:"100%",overflow:'hidden'});
	this.appendChild(this.bar);
	this.bar.div.className = 'bar';
	this.maxvalue = parseInt(params.maxvalue) || 100;
	this.value = parseInt(params.value) || 0;
	this.setValue(this.value);
}

QuiX.constructors['progressbar'] = QuiX.ui.ProgressBar;
QuiX.ui.ProgressBar.prototype = new QuiX.ui.Widget;
// backwards compatibility
var ProgressBar = QuiX.ui.ProgressBar;

QuiX.ui.ProgressBar.prototype._update = function() {
	this.bar.width = parseInt((this.value/this.maxvalue)*100) + '%';
	this.bar.redraw();
}

QuiX.ui.ProgressBar.prototype.setValue = function(v) {
	this.value = parseInt(v);
	if (this.value>this.maxvalue) this.value=this.maxvalue;
	this._update();
}

QuiX.ui.ProgressBar.prototype.increase = function(amount) {
	this.setValue(this.value + parseInt(amount));
}
