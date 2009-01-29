//==============================================================================
//  Copyright 2005-2008 Tassos Koutsovassilis and Contributors
//
//  This file is part of Porcupine.
//  Porcupine is free software; you can redistribute it and/or modify
//  it under the terms of the GNU Lesser General Public License as published by
//  the Free Software Foundation; either version 2.1 of the License, or
//  (at your option) any later version.
//  Porcupine is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Lesser General Public License for more details.
//  You should have received a copy of the GNU Lesser General Public License
//  along with Porcupine; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//==============================================================================

QuiX.browser = 'moz';

//Widget class
function Widget(params) {
	params = params || {};
	this.left = params.left || 0;
	this.top = params.top || 0;
	this.width = params.width || null;
	this.height = params.height || null;
	this.minw = params.minw || 0;
	this.minh = params.minh || 0;
	this.tooltip = params.tooltip;
	this.widgets = [];
	this.attributes = params.attributes || {};
	this.maxz = 0;
	this._isDisabled = false;
	this._isContainer = true;
	this.contextMenu = null;

	this.div = ce('DIV');
	if (params.style)
		this.div.setAttribute('style', params.style);
	this.div.widget = this;

	this._id = undefined;
	if (params.id) {
		this.setId(params.id)
	}
	
	if (params.bgcolor)
		this.setBgColor(params.bgcolor);
	this.setBorderWidth(parseInt(params.border) || 0);
	if (params.padding) {
		var padding = params.padding.split(',');
		this.setPadding(padding);
	}
	else
		this.div.style.padding = '0px 0px 0px 0px';

	if (params.display)
		this.setDisplay(params.display);
	if (params.overflow)
		this.setOverflow(params.overflow);
	this.setPosition('absolute');

	if (params.tooltip) {
		params.onmouseover = QuiX.getEventWrapper(Widget__tooltipover,
			params.onmouseover);
		params.onmouseout = QuiX.getEventWrapper(Widget__tooltipout,
			params.onmouseout);
	}
	
	if (typeof params.opacity != 'undefined') {
		this.setOpacity(parseFloat(params.opacity));
	}
	
	this.dragable = (params.dragable == 'true' || params.dragable == true);
	if (this.dragable){
		params.onmousedown = QuiX.getEventWrapper(Widget__startdrag,
			params.onmousedown);
	}
	this.dropable = (params.dropable == 'true' || params.dropable == true);
	
	this._buildEventRegistry(params);
	this._attachEvents();

	if (params.disabled=='true' || params.disabled==true)
		this.disable();
}

QuiX.constructors['rect'] = Widget;

Widget.prototype.appendChild = function(w, p) {
	p = p || this;
	p.widgets.push(w);
	w.parent = p;
	w.div = p.div.appendChild(w.div);

	w.bringToFront();
	if (p._isDisabled)
		w.disable();
}

Widget.prototype.disable = function() {
	if (!this._isDisabled) {
		this._statecolor = this.div.style.color;
		this.div.style.color = 'GrayText';
		this._statecursor = this.div.style.cursor;
		this.div.style.cursor = 'default';
		this._isDisabled = true;
		if (this.__tooltip || this.__tooltipID)
			Widget__tooltipout(null, this);
		this._detachEvents();
		for (var i=0; i<this.widgets.length; i++) {
			this.widgets[i].disable();
		}
	}
}

Widget.prototype.enable = function() {
	if (this._isDisabled) {
		this.div.style.color = this._statecolor;
		this.div.style.cursor = this._statecursor;
		this._isDisabled = false;
		this._attachEvents();
		for (var i=0; i<this.widgets.length; i++) {
			this.widgets[i].enable();
		}
	}
}

Widget.prototype.detach = function() {
	this.parent.widgets.removeItem(this);
	this.parent = null;
	this.div = QuiX.removeNode(this.div);
}

Widget.prototype.parse = function(dom, callback) {
	var parser = new QuiX.Parser();
	parser.oncomplete = callback;
	parser.parse(dom, this);
}

Widget.prototype.parseFromString = function(s, oncomplete) {
	this.parse(QuiX.domFromString(s), oncomplete);
}

Widget.prototype.parseFromUrl = function(url, oncomplete) {
	var xmlhttp = QuiX.XHRPool.getInstance();
	var oWidget = this;
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp != null && xmlhttp.readyState==4) {
			QuiX.removeLoader();
			oWidget.parse(xmlhttp.responseXML, oncomplete);
			QuiX.XHRPool.release(xmlhttp);
		}
	}
	QuiX.addLoader();
	xmlhttp.open('GET', url, true);
	xmlhttp.send('');
}

Widget.prototype.getParentByType = function(wtype) {
	var w = this.parent;
	while (w) {
		if (w instanceof wtype) return w;
		w = w.parent;
	}
	return null;
}

Widget.prototype.getWidgetById = function(sid) {
	var ws = this.query('w._id==param', sid);
	if (ws.length==0)
		return null;
	else if (ws.length==1)
		return ws[0];
	else
		return ws;
}

Widget.prototype.query = function(eval_condition, param, shallow) {
	var w;
	var ws = [];
	for (var i=0; i<this.widgets.length; i++) {
		w = this.widgets[i];
		if (eval(eval_condition)) ws.push(w);
		if (!shallow)
			ws = ws.concat(w.query(eval_condition, param, shallow));
	}
	return ws;
}

Widget.prototype.getWidgetsByType = function(wtype, shallow) {
	return this.query('w instanceof param', wtype, shallow);
}

Widget.prototype.getWidgetsByClassName = function(cssName, shallow) {
	return this.query('w.div.className == param', cssName, shallow);
} 

Widget.prototype.getWidgetsByAttribute = function(attr_name, shallow) {
	return this.query('w[param] != undefined', attr_name, shallow);
}

Widget.prototype.getWidgetsByAttributeValue = function(attr_name, value, shallow) {
	return this.query('w[param[0]] == param[1]', [attr_name, value], shallow);
}

Widget.prototype._setAbsProps = function() {
	this.div.style.left = this._calcLeft() + 'px';
	this.div.style.top = this._calcTop() + 'px';
}

Widget.prototype._setCommonProps = function() {
	if (this.height!=null)
		this.div.style.height = this._calcHeight() + 'px';
	if (this.width!=null)
		this.div.style.width = this._calcWidth() + 'px';
}

// id attribute
Widget.prototype.setId = function(id) {
	this._id = id;
	this.div.id = id;
}
Widget.prototype.getId = function() {
	return this._id;
}

// bgColor attribute
Widget.prototype.setBgColor = function(color) {
	this.div.style.backgroundColor = color;
}
Widget.prototype.getBgColor = function() {
	return this.div.style.backgroundColor;
}

//borderWidth attribute
Widget.prototype.setBorderWidth = function(iWidth) {
	this.div.style.borderWidth = iWidth + 'px';
}
Widget.prototype.getBorderWidth = function() {
	return parseInt(this.div.style.borderWidth);
}

//display attribute
Widget.prototype.setDisplay = function(sDispl) {
	this.div.style.display = sDispl || '';
}
Widget.prototype.getDisplay = function() {
	return this.div.style.display;
}

//overflow attribute
Widget.prototype.setOverflow = function(sOverflow) {
	this.div.style.overflow = sOverflow;
	this._overflow = sOverflow;
}
Widget.prototype.getOverflow = function() {
	return this.div.style.overflow;
}

//position attribute
Widget.prototype.setPosition = function(sPos) {
	this.div.style.position = sPos || '';
}
Widget.prototype.getPosition = function() {
	return this.div.style.position;
}

//opacity attribute
Widget.prototype.setOpacity = function(fOpacity) {
	this.div.style.MozOpacity = fOpacity;
}

Widget.prototype.getOpacity = function() {
	return parseFloat(this.div.style.MozOpacity);
}

//padding attribute
Widget.prototype.setPadding = function(arrPadding) {
	this.div.style.paddingLeft = arrPadding[0] + 'px';
	this.div.style.paddingRight = arrPadding[1] + 'px';
	this.div.style.paddingTop = arrPadding[2] + 'px';
	this.div.style.paddingBottom = arrPadding[3] + 'px';
}
Widget.prototype.getPadding = function() {
	var padding = [
		parseInt(this.div.style.paddingLeft),
		parseInt(this.div.style.paddingRight),
		parseInt(this.div.style.paddingTop),
		parseInt(this.div.style.paddingBottom)
	];
	return padding;
}

Widget.prototype.addPaddingOffset = function(where, iOffset) {
	var old_offset = parseInt(this.div.style['padding' + where]);
	var new_offset = old_offset + iOffset;
	if (new_offset < 0)
		new_offset = 0;
    this.div.style['padding' + where] = new_offset + 'px';
}

Widget.prototype._mustRedraw = function () {
	return(isNaN(this.left)||isNaN(this.top)||isNaN(this.height)||isNaN(this.width));
}

Widget.prototype.getHeight = function(b) {
	var ofs, hg;
	b = b || false;
	hg = parseInt(this.div.style.height);
	if (isNaN(hg)) return 0;
	if (b) {
		ofs = parseInt(this.div.style.paddingTop) +
			  parseInt(this.div.style.paddingBottom) +
			  2 * this.getBorderWidth();
		hg += ofs;
	}
	return hg;
}

Widget.prototype.getWidth = function(b) {
	var ofs, wd;
	b = b || false;
	wd = parseInt(this.div.style.width);
	if (isNaN(wd)) return 0;
	if (b) {
		ofs = parseInt(this.div.style.paddingLeft) +
			  parseInt(this.div.style.paddingRight) +
			  2*this.getBorderWidth();
		wd += ofs;
	}
	return wd;
}

Widget.prototype.getLeft = function() {
	var ofs, lf;
	lf = parseInt(this.div.style.left);
	if (isNaN(lf)) return 0;
	ofs = this.parent.getPadding()[0];
	lf -= ofs
	return lf;
}

Widget.prototype.getTop = function() {
	var ofs, rg;
	rg = parseInt(this.div.style.top);
	if (isNaN(rg)) return 0;
	ofs = this.parent.getPadding()[2];
	rg -= ofs
	return rg;
}

Widget.prototype._calcSize = function(height, offset, getHeight) {
	height=(typeof(this[height])=='function')?this[height](this):this[height];
	if (height == null)
		return height;
	if (!isNaN(height))
		return parseInt(height)-offset;
	else if (height.slice(height.length-1) == '%') {
		var perc = parseInt(height)/100;
		return (parseInt(this.parent[getHeight]()*perc)-offset) || 0;
	}
	else
		return (eval(height) - offset) || 0;
}

Widget.prototype._calcPos = function(left, offset, getWidth) {
	left = (typeof(this[left])=='function')?this[left](this):this[left];
	if (!isNaN(left))
		return parseInt(left) + offset;
	else if (left.slice(left.length-1)=='%') {
		var perc = parseInt(left)/100;
		return (this.parent[getWidth]() * perc) || 0;
	}
	else {
		if (left!='center')
			return( (eval(left) + offset) || 0 );
		else 
			return parseInt((this.parent[getWidth]()/2) -
							(this[getWidth](true)/2)) + offset || 0;
	}
}

Widget.prototype._calcHeight = function(b) {
	var offset = 0;
	if (!b)	offset = parseInt(this.div.style.paddingTop) +
					 parseInt(this.div.style.paddingBottom) +
					 2*this.getBorderWidth();
	var s = this._calcSize("height", offset, "getHeight");
	var ms = this._calcMinHeight() - offset;
	if (s < ms) s = ms;
	return s>0?s:0;
}

Widget.prototype._calcWidth = function(b) {
	var offset = 0;
	if (!b)	offset = parseInt(this.div.style.paddingLeft) +
					 parseInt(this.div.style.paddingRight) +
					 2*this.getBorderWidth();
	var s = this._calcSize("width", offset, "getWidth");
	var ms = this._calcMinWidth() - offset;
	if (s < ms) s = ms;
	return s>0?s:0;
}

Widget.prototype._calcLeft = function() {
	return this._calcPos("left",
		(this.parent? this.parent.getPadding()[0]:0), "getWidth");
}

Widget.prototype._calcTop = function() {
	return this._calcPos("top",
		(this.parent? this.parent.getPadding()[2]:0), "getHeight");
}

Widget.prototype._calcMinWidth = function() {
	return (typeof(this.minw)=='function')?this.minw(this):this.minw;
}

Widget.prototype._calcMinHeight = function() {
	return (typeof(this.minh)=='function')?this.minh(this):this.minh;
}

Widget.prototype.getScreenLeft = function() {
	var oElement = this.div;
	var iX = 0, b;
	while(oElement && oElement.tagName && oElement.tagName!='HTML')
	{
		if (oElement.tagName!='TR')
			iX += oElement.offsetLeft - oElement.scrollLeft;
		b = parseInt(oElement.style.borderWidth);
		if (b)
			iX += b;
		oElement = oElement.parentNode;
	}
	return(iX);
}

Widget.prototype.getScreenTop = function() {
	var oElement = this.div;
	var iY = 0, b;
	while(oElement && oElement.tagName && oElement.tagName!='HTML') {
		if (oElement.tagName!='TR')
			iY += oElement.offsetTop - oElement.scrollTop;
		b = parseInt(oElement.style.borderWidth);
		if (b)
			iY += b;
		oElement = oElement.parentNode;
	}
	return(iY);
}

Widget.prototype.bringToFront = function() {
	if (this.div.style.zIndex==0 || this.div.style.zIndex < this.parent.maxz) {
		this.div.style.zIndex = ++this.parent.maxz;
	}
}

Widget.prototype.click = function() {
	QuiX.sendEvent(this.div, 'MouseEvents', 'onclick');
}

Widget.prototype.moveTo = function(x,y) {
	this.left = x;
	this.top = y;
	var padding = this.parent.getPadding();
	x = (isNaN(x))? this._calcLeft() : x + padding[0];
	y = (isNaN(y))? this._calcTop() : y + padding[2];
	this.div.style.left = x + 'px';
	this.div.style.top = y + 'px';
}

Widget.prototype.resize = function(x,y) {
	var minw = this._calcMinWidth();
	var minh = this._calcMinHeight();
	this.width = (x>minw)?x:minw;
	this.height = (y>minh)?y:minh;
	this.redraw();
}

Widget.prototype.destroy = function() {
	if (this._customRegistry.onunload)
		this._customRegistry.onunload(this);
	QuiX.removeWidget(this);
}

Widget.prototype.clear = function() {
	while (this.widgets.length > 0) this.widgets[0].destroy();
}

Widget.prototype.hide = function() {
	if (!this.isHidden()) {
		QuiX.detachFrames(this);
		this._statedisplay = this.div.style.display;
		this.div.style.display = 'none';
	}
}

Widget.prototype.show = function() {
	QuiX.attachFrames(this);
	this.div.style.display = this._statedisplay || '';
}

Widget.prototype.isHidden = function() {
	return (this.div.style.display == 'none');
}

Widget.prototype._startResize = function (evt) {
	var oWidget = this;
	evt = evt || event;
	QuiX.startX = evt.clientX;
	QuiX.startY = evt.clientY;

	QuiX.tmpWidget = QuiX.createOutline(this);
	QuiX.tmpWidget.bringToFront();

	document.desktop.attachEvent('onmouseup',
		function(evt){oWidget._endResize(evt)});
	document.desktop.attachEvent('onmousemove',
		function(evt){oWidget._resizing(evt)});
	this.parent.div.style.cursor = 'se-resize';
}

Widget.prototype._resizing = function(evt) {
	evt = evt || event;
	var offsetX = evt.clientX - QuiX.startX;
	var offsetY = evt.clientY - QuiX.startY;
	QuiX.tmpWidget.resize(this.getWidth(true) + offsetX,
				this.getHeight(true) + offsetY);
}

Widget.prototype._endResize = function(evt) {
	evt = evt || event;
	var offsetX = evt.clientX - QuiX.startX;
	var offsetY = evt.clientY - QuiX.startY;
	this.resize(this.getWidth(true) + offsetX,
				this.getHeight(true) + offsetY);
	this.bringToFront();
	QuiX.tmpWidget.destroy();
	document.desktop.detachEvent('onmouseup');
	document.desktop.detachEvent('onmousemove');
	this.parent.div.style.cursor = '';
}

Widget.prototype._startMove = function(evt) {
	var oWidget = this;
	evt = evt || event;
	QuiX.startX = evt.clientX;
	QuiX.startY = evt.clientY;

	QuiX.tmpWidget = QuiX.createOutline(this);
	QuiX.tmpWidget.bringToFront();

	document.desktop.attachEvent('onmouseup',
		function(evt){oWidget._endMove(evt)});
	document.desktop.attachEvent('onmousemove',
		function(evt){oWidget._moving(evt)});
	this.parent.div.style.cursor = 'move';
}

Widget.prototype._moving = function(evt) {
	evt = evt || event;
	var offsetX = evt.clientX - QuiX.startX;
	var offsetY = evt.clientY - QuiX.startY;
	QuiX.tmpWidget.moveTo(this.getLeft() + offsetX,
				this.getTop() + offsetY);	
}

Widget.prototype._endMove = function(evt) {
	evt = evt || event;
	QuiX.tmpWidget.destroy();
	document.desktop.detachEvent('onmouseup');
	document.desktop.detachEvent('onmousemove');
	var offsetX = evt.clientX - QuiX.startX;
	var offsetY = evt.clientY - QuiX.startY;
	this.moveTo(this.getLeft() + offsetX,
				this.getTop() + offsetY);
	this.bringToFront();
	this.parent.div.style.cursor = '';
}

Widget.prototype._startDrag = function(x, y) {
	var dragable = QuiX.getDraggable(this);
	dragable.left = x + 2;
	dragable.top = y + 2;
	dragable.setOpacity(.5);
	
	document.desktop.appendChild(dragable);
	dragable.div.style.zIndex = QuiX.maxz;
	dragable.redraw();
	
	QuiX.tmpWidget = dragable;
	QuiX.dragable = this;

	document.desktop.attachEvent('onmouseover', Widget__detecttarget);
	document.desktop.attachEvent('onmousemove', Widget__drag);
}

Widget.prototype.redraw = function(bForceAll) {
	var container = this.div.parentNode;
	if (container && this.div.style.display != 'none') {
		var wdth = this.div.style.width;
		var hght = this.div.style.height;
		if (this.div.clientWidth > 0) {
			var frag = document.createDocumentFragment();
			frag.appendChild(QuiX.removeNode(this.div));
		}
		try {
			this._setCommonProps();
			if (this.getPosition() != '')
				this._setAbsProps();
			for (var i=0; i<this.widgets.length; i++) {
				if (bForceAll || this.widgets[i]._mustRedraw())
					this.widgets[i].redraw(bForceAll);
			}
		}
		finally {
			container.appendChild(this.div);
			if (frag) frag = null;
		}
		if ((wdth && wdth != this.div.style.width) ||
			(hght && hght != this.div.style.height)) {
			if (this._customRegistry.onresize)
				this._customRegistry.onresize(this,
                                              parseInt(wdth),
                                              parseInt(hght));
		}
	}
}

Widget.prototype.print = function(expand) {
	var oWidget = this;
	expand = expand || false;
	var iframe = document.getElementById('_print');
	if (!iframe) {
		iframe = ce('IFRAME');
		iframe.id = '_print';
		iframe.onload = function() {
			var n;
			var doc = iframe.contentWindow.document;
			n = oWidget.div.cloneNode(true);
			n.style.position = '';
			if (expand) {
				n.style.width = '';
				n.style.height = '';
			}
			doc.body.appendChild(n);
			iframe.contentWindow.print();
		}
		document.body.appendChild(iframe);
		iframe.src = QuiX.baseUrl + 'ui/print.htm';
	}
	else {
		iframe.contentWindow.location.reload();
	}
}

Widget.prototype.nextSibling = function() {
	var p = this.parent;
	var ns = null;
	if (p) {
		var idx = p.widgets.indexOf(this);
		if (idx < p.widgets.length - 1)
			ns = p.widgets[idx + 1];
	}
	return ns;
}

Widget.prototype.previousSibling = function() {
	var p = this.parent;
	var ns = null;
	if (p) {
		var idx = p.widgets.indexOf(this);
		if (idx > 0)
			ns = p.widgets[idx - 1];
	}
	return ns;
}

//events sub-system
Widget.prototype.supportedEvents = [
	'onmousedown','onmouseup',
	'onmousemove','onmouseover','onmouseout',
	'onkeypress','onkeyup','onkeydown',
	'onclick','ondblclick',
	'oncontextmenu', 'onscroll'
];

Widget.prototype.customEvents = ['onload','onunload','onresize','ondrop'];

Widget.prototype._registerHandler = function(evt_type, handler, isCustom) {
    var self = this;
	var chr = (this._isDisabled)?'*':'';
	if (!isCustom)
		this._registry[chr + evt_type] = function(evt) {
            return handler(evt || event, self);
        };
	else
		this._customRegistry[chr + evt_type] = handler;
}

Widget.prototype._buildEventRegistry = function(params) {
	var i, evt_type;
	this._registry = {};
	this._customRegistry = {};
	// register DOM events
	for (i=0; i<this.supportedEvents.length; i++) {
		evt_type = this.supportedEvents[i];
		if (params[evt_type])
			this._registerHandler(evt_type,
				QuiX.getEventListener(params[evt_type]), false);
	}
	//register custom events
	for (i=0; i<this.customEvents.length; i++) {
		evt_type = this.customEvents[i];
		if (params[evt_type])
			this._registerHandler(evt_type,
				QuiX.getEventListener(params[evt_type]), true);
	}
}

Widget.prototype._attachEvents = function() {
	for (var evt_type in this._registry) {
		if (evt_type.slice(0,1)!='_') {
			if (evt_type.slice(0,1)=='*')
				evt_type=evt_type.slice(1, evt_type.length);
			this.attachEvent(evt_type, null);//restore events directly from registry
		}
	}
}

Widget.prototype._detachEvents = function() {
	var first_char;
	for (var evt_type in this._registry) {
		first_char = evt_type.slice(0,1);
		if (first_char!='_' && first_char!='*')
			this.detachEvent(evt_type, '*');
	}
}

Widget.prototype._getHandler = function(eventType, f) {
	f = QuiX.getEventListener(f);
	if (!f) {//restore from registry
		f = this._registry[eventType] ||
			this._registry['_' + eventType] ||
			this._registry['*' + eventType] ||
			this._customRegistry[eventType] ||
			this._customRegistry['_' + eventType] ||
			this._customRegistry['*' + eventType];
	}
	return f;
}

Widget.prototype.attachEvent = function(eventType, f) {
	var isCustom = this.customEvents.hasItem(eventType);
	var registry = (isCustom)?this._customRegistry:this._registry;
	f = this._getHandler(eventType, f);
	
	if (f) {
		if (!this._isDisabled && !isCustom)
			this.detachEvent(eventType);
		if (f!=registry[eventType])
			this._registerHandler(eventType, f, isCustom);
	}

	if (registry['_' + eventType])
		delete registry['_' + eventType];

	if (!this._isDisabled && registry['*' + eventType])
		delete registry['*' + eventType];

	if (!this._isDisabled && !isCustom)
		QuiX.addEvent(this.div, eventType, this._registry[eventType]);
}

Widget.prototype.detachEvent = function(eventType, chr) {
	var registry = null;
	chr = chr || '_';
	if (this._registry[eventType]) {
		QuiX.removeEvent(this.div, eventType, this._registry[eventType]);
		registry = this._registry;
	}
	else if (this._customRegistry[eventType]) {
		registry = this._customRegistry;
	}
	if (registry) {
		registry[chr + eventType] = registry[eventType];
		delete registry[eventType];
	}
}

function Widget__tooltipover(evt, w) {
	if (!QuiX.dragging) {
		var x1 = evt.clientX;
		var y1 = evt.clientY + 18;
		if (!w.__tooltipID) {
			w.__tooltipID = window.setTimeout(
				function _tooltiphandler() {
					Widget__showtooltip(w, x1, y1);
				}, 1000);
		}
	}
}

function Widget__tooltipout(evt, w) {
	window.clearTimeout(w.__tooltipID);
	w.__tooltipID = 0;
	if (w.__tooltip) {
		w.__tooltip.destroy();
		w.__tooltip = null;
	}	
}

function Widget__showtooltip(w, x, y) {
	var tooltip = new Label({
		left : x,
		top : y,
		caption : w.tooltip,
		border : 1,
		bgcolor : 'lightyellow',
		wrap : true
	});
	tooltip.div.className = 'tooltip';
	document.desktop.appendChild(tooltip);
	tooltip.redraw();
	w.__tooltip  = tooltip;
}

function Widget__startdrag(evt, w) {
	if (QuiX.getMouseButton(evt) == 0) {
		var x = evt.clientX;
		var y = evt.clientY;
		var el = QuiX.getTarget(evt);
		document.desktop.attachEvent('onmouseup', Widget__enddrag);
		QuiX.dragTimer = window.setTimeout(
			function _draghandler() {w._startDrag(x, y, el)}, 200);
		QuiX.cancelDefault(evt);
		QuiX.stopPropag(evt);
		QuiX.cleanupOverlays();
		QuiX.dragging = true;
	}
}

function Widget__drag(evt, desktop) {
	QuiX.tmpWidget.moveTo(evt.clientX + 2, evt.clientY + 2);
}

function Widget__enddrag(evt, desktop) {
	if (QuiX.dragTimer != 0) {
		window.clearTimeout(QuiX.dragTimer);
		QuiX.dragTimer = 0;
	}
	desktop.detachEvent('onmouseup');
	QuiX.dragging = false;
	if (QuiX.dragable) {
		desktop.detachEvent('onmouseover');
		desktop.detachEvent('onmousemove');
		QuiX.tmpWidget.destroy();
		QuiX.tmpWidget = null;
		
		try {
			if (QuiX.dropTarget && QuiX.dropTarget._customRegistry['ondrop']) {
				QuiX.dropTarget._customRegistry['ondrop'](evt, QuiX.dropTarget,
														  QuiX.dragable);
			}
		}
		finally {
			QuiX.dropTarget = null;
			QuiX.dragable = null;
		}
	}
}

function Widget__detecttarget(evt, desktop) {
	var w = QuiX.getTargetWidget(evt);
	while (w && !w.dropable)
		w = w.parent;
	if (w && w != QuiX.dragable && w != QuiX.dragable.parent) {
		QuiX.tmpWidget.div.style.borderColor = 'red';
		QuiX.dropTarget = w;
	}
	else {
		QuiX.tmpWidget.div.style.borderColor = 'transparent';
		QuiX.dropTarget = null;
	}
}

//Desktop class
function Desktop(params, root) {
	this.base = Widget;
	params.id = 'desktop';
	params.width = 'document.documentElement.clientWidth';
	params.height = 'document.documentElement.clientHeight';
	params.overflow = 'hidden';
	params.onmousedown = Desktop__onmousedown;
	params.oncontextmenu = Desktop__oncontextmenu;
	this.base(params);
	this._setCommonProps();
	this.div.innerHTML = '<p align="right" style="color:#666666;margin:0px;">QuiX v' + QuiX.version + '</p>';
	root.appendChild(this.div);
	this.div.className = 'desktop';
	document.desktop = this;
	window.onresize = function() {document.desktop.redraw()};
	this.overlays = [];
	this.parseFromString(QuiX.progress,
		function(loader){
			loader.div.style.zIndex = QuiX.maxz + 1;
			document.desktop._loader = loader;
		});
}

QuiX.constructors['desktop'] = Desktop;
Desktop.prototype = new Widget;

Desktop.prototype.msgbox = function(mtitle, message, buttons, image,
                                    mleft, mtop, mwidth, mheight) {
	var sButtons = '';
	var handler;
	var oButton;
	var innHTML;
	
	mwidth = mwidth || 240;
	mheight = mheight || 120;
	if (image) {
		QuiX.getImage(image);
		innHTML = '<td><img src="' + image + '"></img></td><td>' +
                  message + '</td>';
	}
	else
		innHTML = '<td>' + message + '</td>';
		
	if (typeof buttons=='object') {
		for (var i=0; i<buttons.length; i++) {
			oButton = buttons[i];
			sButtons += '<dlgbutton width="' + oButton[1] +
						'" height="22" caption="' + oButton[0] + '"/>';
		}
	}
	else
		sButtons = '<dlgbutton onclick="__closeDialog__" caption="' +
				   buttons + '" width="80" height="22"/>';

	this.parseFromString('<dialog xmlns="http://www.innoscript.org/quix"' +
		' title="' + mtitle + '" close="true"' +
		' width="' + mwidth + '" height="' + mheight + '" left="' + mleft +
        '" top="' + mtop + '">' +
		'<wbody><xhtml><![CDATA[<table cellpadding="4"><tr>' + innHTML +
		'</tr></table>]]></xhtml></wbody>' + sButtons + '</dialog>',
		function(w) {
			//attach buttons click events
			if (typeof buttons=='object') {
				for (var i=0; i<buttons.length; i++) {
					oButton = buttons[i];
					handler = '__closeDialog__';
					if (oButton.length>2) handler = oButton[2];
					w.buttons[i].attachEvent('onclick', handler);
				}
			}
		}
	);
}

function Desktop__onmousedown(evt, w) {
	QuiX.cleanupOverlays();
	QuiX.cancelDefault(evt);
	return false;
}

function Desktop__oncontextmenu(evt, w) {
	QuiX.cancelDefault(evt);
}
