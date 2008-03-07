//===============================================================================
//    Copyright 2005-2008 Tassos Koutsovassilis and Contributors
//
//    This file is part of Porcupine.
//    Porcupine is free software; you can redistribute it and/or modify
//    it under the terms of the GNU Lesser General Public License as published by
//    the Free Software Foundation; either version 2.1 of the License, or
//    (at your option) any later version.
//    Porcupine is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Lesser General Public License for more details.
//    You should have received a copy of the GNU Lesser General Public License
//    along with Porcupine; if not, write to the Free Software
//    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//===============================================================================

function __init__() {
	try {
		window.moveTo(0,0);
		window.resizeTo(screen.availWidth,screen.availHeight);
	} catch(e) {}

	var root = document.getElementById("xul");
	var parser = new XULParser();
	parser.parse(root.XMLDocument);
}

QuiX.browser = 'ie';
QuiX.root = (new RegExp("https?://[^/]+(?:/[^/\?]+)?(?:/\{[0-9a-f]{32}\})?", "i")).exec(document.location.href) + '/';

// xul parser
function XULParser() {
	this.__modulesToLoad = [];
	this.__imagesToLoad = [];
	this.__onload = [];
	this.dom = null;
	this.progressWidget = null;
	this.oncomplete = null;
}

XULParser.prototype.detectModules = function(oNode) {
	var sTag = oNode.tagName;
	var arrTokens;
	if (sTag) {
		arrTokens = oNode.tagName.split(':');
		sTag = (arrTokens.length==1) ? arrTokens[0]:arrTokens[1];
	}
	var iMod = QuiX.tags[sTag];
	this._addModule(iMod);
	
	if (iMod && oNode.getAttribute('img')) {
		src = oNode.getAttribute('img');
		if (src!='' && !QuiX.images.hasItem(src)) {
			this.__imagesToLoad.push(src);
		}
	}

	if (sTag == 'script' || sTag == 'module' || sTag == 'stylesheet') {
		params = this.getNodeParams(oNode);
		if (!document.getElementById(params.src)) {
			var oMod = new QModule(params.name, params.src, []);
			if (sTag == 'stylesheet')
				oMod.type = 'stylesheet';
			else if (params.depends) {
				var depends = params.depends.split(",");
				for (var i=0; i<depends.length; i++) {
					this._addModule(parseInt(depends[i]));
				}
			}
			this.__modulesToLoad.push(oMod);
		}
	}
	for (var i=0; i<oNode.childNodes.length; i++) {
		this.detectModules(oNode.childNodes[i]);
	}
}

XULParser.prototype._addModule = function(iMod) {
	var dependency;
	if (iMod>-1 && !QuiX.modules[iMod].isLoaded) {
		var oMod = QuiX.modules[iMod];
		if(!this.__modulesToLoad.hasItem(oMod)) {
			for (var i=0; i<oMod.dependencies.length; i++) {
				dependency = QuiX.modules[oMod.dependencies[i]];
				if (!this.__modulesToLoad.hasItem(dependency) && !dependency.isLoaded) {
					this._addModule(oMod.dependencies[i]);
				}
			}
			this.__modulesToLoad.push(oMod);
		}
	}
}

XULParser.prototype.loadModules= function(w) {
	var oModule, imgurl, img;
	var oParser = this;
	if (w) {
		this.progressWidget = w;
		w.getWidgetById('pb').maxvalue = this.__modulesToLoad.length + this.__imagesToLoad.length;
	}
	if (this.__modulesToLoad.length > 0) {
		oModule = this.__modulesToLoad.pop();
		if (this.progressWidget) {
			this.progressWidget.getWidgetById('pb').increase(1);
			this.progressWidget.div.getElementsByTagName('SPAN')[0].innerHTML = oModule.name;
		}
		oModule.load(function(){oParser.loadModules()});
	} else if (this.__imagesToLoad.length > 0) {
		imgurl = this.__imagesToLoad.pop();
		img = new QImage(imgurl);
		if (this.progressWidget) {
			this.progressWidget.getWidgetById('pb').increase(1);
			this.progressWidget.div.getElementsByTagName('SPAN')[0].innerHTML = 'image "' + imgurl + '"';
		}
		img.load(function(){oParser.loadModules()});
	} else {
		if (this.progressWidget) this.progressWidget.destroy();
		widget = this.beginRender();
	}
}

XULParser.prototype.parse = function(oDom, parentW) {
	var widget, parser;
	this.dom = oDom;
	this.parentWidget = parentW;
	this.detectModules(oDom.documentElement);
	if (this.__modulesToLoad.length + this.__imagesToLoad.length > 0) {
		this.__modulesToLoad.reverse();
		parser = this;
		if (parentW) {
			parentW.parseFromString(QuiX.progress, function(w){parser.loadModules(w);});
		} else {
			this.loadModules();
		}
	} else {
		this.beginRender();
	}
}

XULParser.prototype.beginRender = function() {
	var on_load;
	var widget = this.render();
	widget.redraw(true);	

	while (this.__onload.length > 0) {
		on_load = this.__onload.pop();
		on_load[0](on_load[1]);
	}

	if (this.oncomplete)
		this.oncomplete(widget);
}

XULParser.prototype.render = function() {
	var parentW = this.parentWidget;
	var frag = document.createDocumentFragment();
	if (parentW) {
		var root = parentW.div;
		frag.appendChild(root.cloneNode(false));
		parentW.div = frag.firstChild;
		widget = this.parseXul(this.dom.documentElement, parentW);
		root.appendChild(widget.div);
		parentW.div = root;
	}
	else {
		widget = this.parseXul(this.dom.documentElement, frag);
		document.body.appendChild(frag);
	}
	frag = null;
	return(widget);
}

XULParser.prototype.getNodeParams = function(oNode) {
	var params = {};
	for (var i=0; i<oNode.attributes.length; i++)
		params[oNode.attributes[i].name] = oNode.attributes[i].value;
	return(params);
}

XULParser.prototype.parseXul = function(oNode, parentW) {
	if (oNode.nodeType!=1) return;
	var oWidget = null;
	var params = this.getNodeParams(oNode);
	var sLocalName, arrTokens;
	if (oNode.namespaceURI == QuiX.namespace) {
		arrTokens = oNode.tagName.split(':');
		sLocalName = (arrTokens.length==1) ? arrTokens[0]:arrTokens[1];
		switch(sLocalName) {
			case 'flatbutton':
				oWidget = new FlatButton(params);
				if (params.type=='menu') {
					parentW.appendChild(oWidget);
					oWidget = oWidget.contextMenu;
				}
				break;
			case 'field':
				if (params.type=='textarea')
					params.value = oNode.text;
				oWidget = new Field(params);
				break;
			case 'mfile':
				parentW.addFile(params);
				break;
			case 'option':
				oWidget = parentW.addOption(params);
				break;
			case 'dlgbutton':
				oWidget = parentW.addButton(params);
				break;
			case 'wbody':
				oWidget = parentW.body;
				break;
			case 'tab':
				oWidget = parentW.addTab(params);
				break;
			case 'listheader':
				oWidget = parentW.addHeader(params);
				break;
			case 'column':
				var oCol = parentW.parent.addColumn(params);
				if (params.type=='optionlist') {
					var options, p;
					options = oNode.childNodes;
					oCol.options = [];
					for (var k=0; k<options.length; k++) {
						p = this.getNodeParams(options[k]);
						oCol.options.push(p);
					}
				}
				break;
			case 'tbbutton':
				oWidget = parentW.addButton(params);
				if (params.type=='menu') oWidget = oWidget.contextMenu;
				break;
			case 'tbsep':
				oWidget = parentW.addSeparator();
				break;
			case 'tool':
				oWidget = parentW.addPane(params);
				break;
			case 'menu':
				oWidget = parentW.addRootMenu(params);
				break;
			case 'menuoption':
				oWidget = parentW.addOption(params);
				break;
			case 'sep':
				oWidget = parentW.addOption(-1);
				break;
			case 'groupbox':
				oWidget = new GroupBox(params);
				parentW.appendChild(oWidget);
				oWidget = oWidget.body;
				break;
			case 'custom':
				oWidget = eval('new ' + params.classname + '(params)');
				break;
			case 'prop':
				var attr_value = params['value'] || '';
				switch (params.type) {
					case 'int':
						attr_value = parseInt(attr_value);
						attr_value = (isNaN(attr_value))?null:attr_value;
						break;
					case 'bool':
						attr_value = new Boolean(parseInt(attr_value)).valueOf();
						break;
					case 'float':
						attr_value = parseFloat(attr_value);
						attr_value = (isNaN(attr_value))?null:attr_value;
						break;
					case 'strlist':
						var delimeter = params['delimeter'] || ';';
						if (attr_value != '')
							attr_value = attr_value.split(delimeter);
						else
							attr_value = [];
				}
				if (attr_value!=null)
					parentW.attributes[params['name']] = attr_value;
				else
					throw new QuiX.Exception('Illegal custom property value',
						' ' + params['name'] + '=' + params['value']);
				break;
			case 'xhtml':
				parentW.div.innerHTML = oNode.text;
				break;
			default:
				var widget_contructor = QuiX.constructors[sLocalName];
				if (widget_contructor != null)
					oWidget = new widget_contructor(params, parentW);
		}

		if (oWidget) {
			if (parentW && !oWidget.parent &&
					!oWidget.owner && oWidget != document.desktop)
				parentW.appendChild(oWidget);
			
			if (oWidget._isContainer)
				for (var i=0; i<oNode.childNodes.length; i++)
					this.parseXul(oNode.childNodes[i], oWidget);

			if (oWidget._customRegistry.onload)
				this.__onload.push([oWidget._customRegistry.onload, oWidget]);
		}
	}
	return oWidget;
}

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
	this._id_widgets = {};
	this.attributes = params.attributes || {};
	this.maxz = 0;
	this._isDisabled = false;
	this._isContainer = true;
	this.contextMenu = null;
	
	this.div = ce('DIV');
	if (params.style)
		this.div.style.cssText = params.style;
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
	
	if (typeof(params.opacity) != 'undefined') {
		this.setOpacity(parseFloat(params.opacity));
	}
	
	this.dragable = (params.dragable == 'true' || params.dragable == true);
	if  (this.dragable){
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
	if (w._id)
		w._addIdRef();
	p.div.appendChild(w.div);
	if (w.height=='100%' && w.width=='100%')
		p.setOverflow('hidden');

	w.bringToFront();
	if (p._isDisabled)
		w.disable();
}

Widget.prototype.disable = function(w) {
	w = w || this;
	if (!w._isDisabled) {
		w._statecolor = w.div.style.color;
		w.div.style.color = 'GrayText';
		w._statecursor = w.div.style.cursor;
		w.div.style.cursor = 'default';
		w._isDisabled = true;
		if (w.__tooltip || w.__tooltipID)
			Widget__tooltipout(null, w);
		w._detachEvents();
		for (var i=0; i<w.widgets.length; i++) {
			w.widgets[i].disable();
		}
	}
}

Widget.prototype.enable = function(w) {
	w = w || this;
	if (w._isDisabled) {
		w.div.style.color = w._statecolor;
		w.div.style.cursor = w._statecursor;
		w._isDisabled = false;
		w._attachEvents();
		for (var i=0; i<w.widgets.length; i++) {
			w.widgets[i].enable();
		}
	}
}

Widget.prototype.detach = function(w) {
	var w = w || this;
	w.parent.widgets.removeItem(w);
	if (w._id)
		w._removeIdRef();
	w.parent = null;
	w.div = QuiX.removeNode(w.div);
}

Widget.prototype.parse = function(dom, callback) {
	var parser = new XULParser();
	parser.oncomplete = callback;
	parser.parse(dom, this);
}

Widget.prototype.parseFromString = function(s, oncomplete) {
	this.parse(QuiX.domFromString(s), oncomplete);
}

Widget.prototype.parseFromUrl = function(url, oncomplete) {
	var xmlhttp = QuiX.XMLHttpRequest();
	var oWidget = this;
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp != null && xmlhttp.readyState==4) {
			oWidget.parse(xmlhttp.responseXML, oncomplete);
			xmlhttp = null;
		}
	}
	xmlhttp.open('GET', url, true);
	xmlhttp.send();
}

Widget.prototype.getParentByType = function(wtype) {
	w = this.parent;
	while (w) {
		if (w instanceof wtype) return w;
		w = w.parent;
	}
	return null;
}

Widget.prototype.getWidgetById = function(sid) {
	ws = QuiX.getWidgetsById(this, sid);
	if (ws.length==0)
		return null;
	else if (ws.length==1)
		return ws[0];
	else
		return ws;
}

Widget.prototype.getWidgetsByType = function(wtype) {
	var w;
	var ws = [];
	for (var i=0; i<this.widgets.length; i++) {
		w = this.widgets[i];
		if (w instanceof wtype) ws.push(w);
		ws = ws.concat(w.getWidgetsByType(wtype));
	}
	return ws;
}

Widget.prototype.getWidgetsByAttribute = function(attr_name) {
	var w;
	var ws = [];
	for (var i=0; i<this.widgets.length; i++) {
		w = this.widgets[i];
		if (w[attr_name] != undefined) ws.push(w);
		ws = ws.concat(w.getWidgetsByAttribute(attr_name));
	}
	return ws;
}

Widget.prototype.getWidgetsByAttributeValue = function(attr_name, value) {
	var w;
	var ws = [];
	for (var i=0; i<this.widgets.length; i++) {
		w = this.widgets[i];
		if (w[attr_name] == value) ws.push(w);
		ws = ws.concat(w.getWidgetsByAttributeValue(attr_name, value));
	}
	return ws;
}

Widget.prototype._setAbsProps = function () {
	this.div.style.left = this._calcLeft() + 'px';
	this.div.style.top = this._calcTop() + 'px';
}

Widget.prototype._setCommonProps = function (w) {
	w = w || this;
	if (w.height!=null)
		w.div.style.height = w._calcHeight() + 'px';
	if (w.width!=null)
		w.div.style.width = w._calcWidth() + 'px';
}

Widget.prototype._removeIdRef = function()
{
	this.parent._id_widgets[this._id].removeItem(this);
	if (this.parent._id_widgets[this._id].length == 0)
		delete this.parent._id_widgets[this._id];
}

Widget.prototype._addIdRef = function()
{
	if (this.parent._id_widgets[this._id])
		this.parent._id_widgets[this._id].push(this);
	else
		this.parent._id_widgets[this._id] = [this];
}

// id attribute
Widget.prototype.setId = function(id) {
	if (this.parent && this._id)
		this._removeIdRef();
	this._id = id;
	this.div.id = id;
	if (this.parent)
		this._addIdRef();
}
Widget.prototype.getId = function() {
	return this._id;
}

// bgColor attribute
Widget.prototype.setBgColor = function(color,w) {
	w = w || this;
	w.div.style.backgroundColor = color;
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
	this.div.style.filter = 'alpha(opacity=' + fOpacity * 100 + ')';
}

Widget.prototype.getOpacity = function() {
	var re = /alpha\(opacity=(\d+)\)/;
	var arrOpacity = re.exec(this.div.style.filter);
	if (arrOpacity.length > 1)
		return parseInt(arrOpacity[1]) / 100;
	else
		return 1;
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
	var old_offset = eval('parseInt(this.div.style.padding' + where + ')');
	var new_offset = old_offset + iOffset;
	if (new_offset < 0)
		new_offset = 0;
	eval('this.div.style.padding' + where + '="' + new_offset + 'px"');
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
	while(oElement) {
		if (oElement.tagName!='TR') {
			iX += oElement.offsetLeft - oElement.scrollLeft;
			b = parseInt(oElement.style.borderWidth);
			if (b)
				iX += b;
		}
		oElement = oElement.parentElement;
	}
	return(iX - 1);
}

Widget.prototype.getScreenTop = function() {
	var oElement = this.div;
	var iY = 0, b=0;
	while(oElement) {
		if (oElement.tagName!='TR') {
			iY += oElement.offsetTop - oElement.scrollTop;
			b = parseInt(oElement.style.borderWidth);
			if (b)
				iY += b;
		}
		oElement = oElement.parentElement;
	}
	return(iY - 1);
}

Widget.prototype.bringToFront = function(w) {
	w = w || this;
	if (w.div.style.zIndex==0 || w.div.style.zIndex < w.parent.maxz) {
		w.div.style.zIndex = ++w.parent.maxz;
	}
}

Widget.prototype.click = function() {
	QuiX.sendEvent(this.div,'MouseEvents','onclick');
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

Widget.prototype.destroy = function(w) {
	w = w || this;
	QuiX.removeWidget(w);
}

Widget.prototype.clear = function() {
	while (this.widgets.length > 0) this.widgets[0].destroy();
}

Widget.prototype.hide = function(w) {
	var w = w || this;
	if (!w.isHidden()) {
		QuiX.detachFrames(w);
		this._statedisplay = w.div.style.display;
		w.div.style.display = 'none';
	}
}

Widget.prototype.show = function(w) {
	var w = w || this;
	QuiX.attachFrames(w);
	w.div.style.display = w._statedisplay || '';
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
	offsetX = evt.clientX - QuiX.startX;
	offsetY = evt.clientY - QuiX.startY;
	QuiX.tmpWidget.resize(this.getWidth(true) + offsetX,
				this.getHeight(true) + offsetY);
}

Widget.prototype._endResize = function(evt) {
	evt = evt || event;
	offsetX = evt.clientX - QuiX.startX;
	offsetY = evt.clientY - QuiX.startY;
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
	offsetX = evt.clientX - QuiX.startX;
	offsetY = evt.clientY - QuiX.startY;
	QuiX.tmpWidget.moveTo(this.getLeft() + offsetX,
				this.getTop() + offsetY);	
}

Widget.prototype._endMove = function(evt) {
	evt = evt || event;
	QuiX.tmpWidget.destroy();
	document.desktop.detachEvent('onmouseup');
	document.desktop.detachEvent('onmousemove');
	offsetX = evt.clientX - QuiX.startX;
	offsetY = evt.clientY - QuiX.startY;
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
	dragable.redraw();
		
	QuiX.tmpWidget = dragable;
	QuiX.dragable = this;

	document.desktop.attachEvent('onmouseover', Widget__detecttarget);
	document.desktop.attachEvent('onmousemove', Widget__drag);
}

Widget.prototype.redraw = function(bForceAll, w) {
	w = w || this;
	var container = w.div.parentElement;
	if (container &&  w.div.style.display != 'none') {
		var wdth = w.div.style.width;
		var hght = w.div.style.height;
		if (w.div.clientWidth > 0)
		{
			var frag = document.createDocumentFragment();
			frag.appendChild(QuiX.removeNode(w.div));
		}
		try {
			w._setCommonProps();
			if (w.div.style.position != '')
				w._setAbsProps();
			for (var i=0; i<w.widgets.length; i++) {
				if (bForceAll || w.widgets[i]._mustRedraw())
					w.widgets[i].redraw(bForceAll);
			}
		}
		finally {
			container.appendChild(w.div);
		}
		if ((wdth && wdth != w.div.style.width) ||
			(hght && hght != w.div.style.height)) {
			if (w._customRegistry.onresize)
				w._customRegistry.onresize(this);
		}
	}
}

Widget.prototype.print = function(expand) {
	var oWidget = this;
	expand = expand || false;
	var iframe = document.getElementById('_print');
	if (!iframe) {
		var iframe = ce('IFRAME');
		iframe.name = '_print';
		iframe.id = '_print';
		document.body.appendChild(iframe);
		iframe.attachEvent('onload', function() {
			var n;
			var frame = document.frames('_print');
			var fbody = frame.document.body;
			n = oWidget.div.cloneNode(true);
			n.style.position = '';
			if (expand) {
				n.style.width = '';
				n.style.height = '';
			}
			fbody.innerHTML = n.outerHTML;
			frame.focus();
			frame.print();
		});
		iframe.src = '__quix/print.htm';
	}
	else {
		iframe.contentWindow.location.reload();
	}
}

//events sub-system
Widget.prototype.supportedEvents = [
	'onmousedown','onmouseup',
	'onmousemove','onmouseover','onmouseout',
	'onkeypress','onkeyup','onkeydown',
	'onclick','ondblclick',
	'oncontextmenu', 'onscroll'
];

Widget.prototype.customEvents = ['onload','onresize','ondrop'];

Widget.prototype._registerHandler = function(evt_type, handler, isCustom, w) {
	w = w || this;
	var chr = (w._isDisabled)?'*':'';
	if (!isCustom)
		w._registry[chr + evt_type] = function(evt){return handler(evt || event, w)};
	else
		w._customRegistry[chr + evt_type] = handler;
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
		if (evt_type!='toXMLRPC' && evt_type.slice(0,1)!='_') {
			if (evt_type.slice(0,1)=='*')
				evt_type=evt_type.slice(1, evt_type.length);
			this.attachEvent(evt_type, null);//restore events directly from registry
		}
	}
}

Widget.prototype._detachEvents = function(w) {
	w = w || this;
	var first_char;
	for (var evt_type in w._registry) {
		first_char = evt_type.slice(0,1);
		if (evt_type!='toXMLRPC' && first_char!='_' && first_char!='*')
			w.detachEvent(evt_type, '*');
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

Widget.prototype.attachEvent = function(eventType, f, w) {
	w = w || this;
	var isCustom = w.customEvents.hasItem(eventType);
	var registry = (isCustom)?w._customRegistry:w._registry;
	f = w._getHandler(eventType, f);
	
	if (f) {
		if (!w._isDisabled && !isCustom)
			w.detachEvent(eventType);
		if (f!=registry[eventType])
			w._registerHandler(eventType, f, isCustom);
	}

	if (registry['_' + eventType])
		delete registry['_' + eventType];

	if (!w._isDisabled && registry['*' + eventType])
		delete registry['*' + eventType];

	if (!w._isDisabled && !isCustom)
		QuiX.addEvent(w.div, eventType, w._registry[eventType]);
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
		document.desktop.attachEvent('onmouseup', Widget__enddrag);
		QuiX.dragTimer = window.setTimeout(
			function _draghandler() {w._startDrag(x, y)}, 150);
		QuiX.cancelDefault(evt);
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
	params.onmousedown = Desktop__onmousedown;
	params.oncontextmenu = Desktop__oncontextmenu;
	this.base(params);
	this.setPosition();
	this.div.onselectstart = function(){return false};
	this._setCommonProps();
	this.div.innerHTML = '<p align="right" style="color:#666666;margin:0px;">QuiX v' + QuiX.version + '</p>';
	root.appendChild(this.div);
	this.div.className = 'desktop';
	document.desktop = this;
	window.onresize = function() {document.desktop.redraw()};
	this.overlays = [];
}

QuiX.constructors['desktop'] = Desktop;
Desktop.prototype = new Widget;

Desktop.prototype.msgbox = function(mtitle, message, buttons, image, mleft, mtop, mwidth, mheight) {
	var sButtons = '';
	var handler;
	var oButton;
	var dlg;
	
	mwidth = mwidth || 240;
	mheight = mheight || 120;
	if (image) {
		QuiX.getImage(image);
		innHTML = '<td><img src="' + image + '"></img></td><td>' + message + '</td>';
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
		' width="' + mwidth + '" height="' + mheight + '" left="' + mleft +'" top="' + mtop + '">' +
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

// progress bar
function ProgressBar(params) {
	params = params || {};
	this.base = Widget;
	params.border = 1;
	params.overflow = 'hidden';
	this.base(params);
	this.div.className = 'progressbar';
	this.bar = new Widget({height:"100%",overflow:'hidden'});
	this.appendChild(this.bar);
	this.bar.div.className = 'bar';
	this.maxvalue = parseInt(params.maxvalue) || 100;
	this.value = parseInt(params.value) || 0;
	this.setValue(this.value);
}

QuiX.constructors['progressbar'] = ProgressBar;
ProgressBar.prototype = new Widget;

ProgressBar.prototype._update = function() {
	this.bar.width = parseInt((this.value/this.maxvalue)*100) + '%';
	this.bar.redraw();
}

ProgressBar.prototype.setValue = function(v) {
	this.value = parseInt(v);
	if (this.value>this.maxvalue) this.value=this.maxvalue;
	this._update();
}

ProgressBar.prototype.increase = function(amount) {
	this.setValue(this.value + parseInt(amount));
}

