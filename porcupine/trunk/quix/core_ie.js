//===============================================================================
//    Copyright 2005, 2006 Tassos Koutsovassilis and Contributors
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
	window.moveTo(0,0);
	window.resizeTo(screen.availWidth,screen.availHeight);

	var root = document.getElementById("xul");
	var parser = new XULParser();
	parser.parse(root.XMLDocument);
}

QuiX.browser = 'ie';
QuiX.root = (new RegExp("https?://[^/]+(?:/[^/\?]+)?(?:/\{[0-9a-f]{32}\})?", "i")).exec(document.location.href) + '/';

QuiX.modules = [
	new Module('Windows and Dialogs', '__quix/windows.js', [3]),
	new Module('Menus', '__quix/menus.js', [3]),
	new Module('Splitter', '__quix/splitter.js', [3]),
	new Module('Labels & Buttons', '__quix/buttons.js', []),
	new Module('Tab Pane', '__quix/tabpane.js', []),
	new Module('List View', '__quix/listview.js', []),
	new Module('Tree', '__quix/tree.js', []),
	new Module('Toolbars', '__quix/toolbars.js', [3]),
	new Module('Forms & Fields', '__quix/formfields.js', [3]),
	new Module('Common Widgets', '__quix/common.js', [3]),
	new Module('Datagrid', '__quix/datagrid.js', [5,8]),
	new Module('File Control', '__quix/file.js', [1,3,8]),
	new Module('Date Picker', '__quix/datepicker.js', [14]),
	new Module('Timers', '__quix/timers.js', []),
	new Module('Forms & Fields 2', '__quix/formfields2.js', [3]),
	new Module('VBox & HBox', '__quix/box.js', []),
];

QuiX.removeWidget = function(w) {
	while (w.widgets.length>0)
		QuiX.removeWidget(w.widgets[0]);
	
	if (w.parent) {
		w.parent.widgets.removeItem(w);
		if (w._id)
			w._removeIdRef();
	}
	
	w._detachEvents();
	w.div.removeNode(true);

	w._registry = null;
	w._customRegistry = null;
	w.div = null;
	w = null;
}

// xul parser
function XULParser() {
	this.__modulesToLoad = [];
	this.__imagesToLoad = [];
	this.activeForm = null;
	this.dom = null;
	this.progressWidget = null;
	this.oncomplete = null;
}

XULParser.prototype.detectModules = function(oNode) {
	var dependency;
	var sTag = oNode.tagName
	if (sTag) sTag = sTag.split(':')[1];
	var iMod = QuiX.tags[sTag];
	if (iMod>-1 && !QuiX.modules[iMod].isLoaded) {
		var oMod = QuiX.modules[iMod];
		if(!this.__modulesToLoad.hasItem(oMod)) {
			for (var i=0; i<oMod.dependencies.length; i++) {
				dependency = QuiX.modules[oMod.dependencies[i]];
				if (!this.__modulesToLoad.hasItem(dependency) && !dependency.isLoaded) {
					this.__modulesToLoad.push(QuiX.modules[oMod.dependencies[i]]);
				}
			}
			this.__modulesToLoad.push(oMod);
		}
	}
	if (iMod && oNode.getAttribute('img')) {
		src = oNode.getAttribute('img');
		if (src!='' && !QuiX.images.hasItem(src)) {
			this.__imagesToLoad.push(src);
		}
	}

	if (sTag == 'script') {
		params = this.getNodeParams(oNode);
		if (!document.getElementById(params.src)) {
			var oMod = new Module(params.name, params.src, []);
			this.__modulesToLoad.push(oMod);
		}
	}
	for (var i=0; i<oNode.childNodes.length; i++) {
		this.detectModules(oNode.childNodes[i]);
	}
}

XULParser.prototype.loadModules= function(w) {
	var oModule, imgurl, img;
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
		oModule.load(this);
	} else if (this.__imagesToLoad.length > 0) {
		imgurl = this.__imagesToLoad.pop();
		img = new QImage(imgurl);
		if (this.progressWidget) {
			this.progressWidget.getWidgetById('pb').increase(1);
			this.progressWidget.div.getElementsByTagName('SPAN')[0].innerHTML = 'image "' + imgurl + '"';
		}
		img.load(this);
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
	var widget = this.render();
	if (this.oncomplete) this.oncomplete(widget);
	widget.redraw(true);
}

XULParser.prototype.render = function() {
	window.status = '';
	var parentW = this.parentWidget;
	var frag = document.createDocumentFragment();
	if (parentW) {
		var root = parentW.div;
		frag.appendChild(root.cloneNode(true));
		parentW.div = frag.firstChild;
		widget = this.parseXul(this.dom.documentElement, parentW);
		root.appendChild(widget.div);
		parentW.div = root;
	}
	else {
		widget = this.parseXul(this.dom.documentElement, frag);
		document.body.appendChild(frag);
		widget.redraw();
	}
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
	var checkForChilds = true;
	var appendIt = true;
	var oWidget=null;
	var params = this.getNodeParams(oNode);
	var fparams = {};
	var sLocalName;
	if (oNode.namespaceURI == QuiX.namespace) {
		sLocalName = oNode.tagName.split(':')[1];
		switch(sLocalName) {
			case 'desktop':
				oWidget = new Desktop(params, parentW);
				appendIt = false;
				break;
			case 'label':
				oWidget = new Label(params);
				break;
			case 'icon':
				oWidget = new Icon(params);
				break;
			case 'button':
				oWidget = new XButton(params);
				break;
			case 'flatbutton':
				oWidget = new FlatButton(params);
				if (params.type=='menu') {
					parentW.appendChild(oWidget);
					oWidget = oWidget.contextMenu;
					appendIt = false;
				}
				break;
			case 'form':
				oWidget = new Form(params);
				this.activeForm = oWidget;
				break;
			case 'field':
				if (params.type=='textarea') params.value = oNode.text;
				oWidget = new Field(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'selectlist':
				oWidget = new SelectList(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'file':
				oWidget = new File(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'multifile':
				oWidget = new MultiFile(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'mfile':
				checkForChilds = false;
				parentW.addFile(params);
				appendIt = false;
				break;
			case 'option':
				checkForChilds = false;
				oWidget = parentW.addOption(params);
				appendIt = false;
				break;
			case 'combo':
				oWidget = new Combo(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'spinbutton':
				oWidget = new Spin(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'dialog':
				oWidget = new Dialog(params);
				break;
			case 'dlgbutton':
				oWidget = parentW.addButton(params);
				appendIt = false;
				break;
			case 'window':
				oWidget = new Window(params);
				break;
			case 'wbody':
				oWidget = parentW.body;
				appendIt = false;
				break;
			case 'splitter':
				oWidget = new Splitter(params);
				break;
			case 'pane':
				oWidget = parentW.addPane(params);
				appendIt = false;
				break;
			case 'tabpane':
				oWidget = new TabPane(params);
				break;
			case 'tab':
				oWidget = parentW.addTab(params);
				appendIt = false;
				break;
			case 'listview':
				oWidget = new ListView(params);
				break;
			case 'listheader':
				oWidget = parentW.addHeader(params);
				appendIt = false;
				break;
			case 'column':
				checkForChilds = false;
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
			case 'datagrid':
				oWidget = new DataGrid(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'datepicker':
				oWidget = new Datepicker(params);
				if (this.activeForm) this.activeForm.elements.push(oWidget);
				break;
			case 'progressbar':
				oWidget = new ProgressBar(params);
				break;
			case 'tree':
				oWidget = new Tree(params);
				break;
			case 'foldertree':
				oWidget = new FolderTree(params);
				break;
			case 'treenode':
				oWidget = new TreeNode(params);
				break;
			case 'toolbar':
				oWidget = new Toolbar(params);
				break;
			case 'tbbutton':
				oWidget = parentW.addButton(params);
				if (params.type=='menu') oWidget = oWidget.contextMenu;
				appendIt = false;
				break;
			case 'tbsep':
				checkForChilds = false;
				oWidget = parentW.addSeparator();
				appendIt = false;
				break;
			case 'outlookbar':
				oWidget = new OutlookBar(params);
				break;
			case 'tool':
				oWidget = parentW.addPane(params);
				appendIt = false;
				break;
			case 'menubar':
				oWidget = new MBar(params);
				break;
			case 'menu':
				oWidget = parentW.addRootMenu(params);
				appendIt = false;
				break;
			case 'contextmenu':
				oWidget = new ContextMenu(params, parentW);
				parentW.contextMenu = oWidget;
				parentW.attachEvent('oncontextmenu', Widget__contextmenu);
				appendIt = false;
				break;
			case 'menuoption':
				oWidget = parentW.addOption(params);
				appendIt = false;
				break;
			case 'sep':
				checkForChilds = false;
				oWidget = parentW.addOption(-1);
				appendIt = false;
				break;
			case 'hr':
				checkForChilds = false;
				oWidget = new HR(params);
				break;
			case 'iframe':
				checkForChilds = false;
				oWidget = new IFrame(params);
				break;
			case 'groupbox':
				oWidget = new GroupBox(params);
				parentW.appendChild(oWidget);
				oWidget = oWidget.body;
				appendIt = false;
				break;
			case 'rect':
				oWidget = new Widget(params);
				break;
			case 'timer':
				oWidget = new Timer(params);
				break;
			case 'box':
				oWidget = new Box(params);
				break;
			case 'prop':
				var attr_value = params['value'] || '';
				checkForChilds = false;
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
				checkForChilds = false;
				parentW.div.innerHTML = oNode.xml;
		}
		
		if (oWidget && parentW && !oWidget.parent && appendIt)
			parentW.appendChild(oWidget);
		
		if (checkForChilds) {
			for (var i=0; i<oNode.childNodes.length; i++) {
				this.parseXul(oNode.childNodes[i], oWidget, fparams);
			}
		}

		if (oNode.localName == 'form') this.activeForm = null;
		
		if (oWidget) { 
			if (oWidget._customRegistry.onload)
				oWidget._customRegistry.onload(oWidget);
		}
	}
	return oWidget;
}

function Module(sName, sFile, d) {
	this.isLoaded = false;
	this.name = sName;
	this.file = sFile;
	this.dependencies = d;
}

Module.prototype.load = function(parser) {
	this.parser = parser;
	var oScript = document.createElement('SCRIPT');
	oScript.type = 'text/javascript';
	oScript.defer = true;
	oScript.src = this.file;
	oScript.resource = this;
	oScript.id = this.file;
	oScript.onreadystatechange = Resource_onstatechange;
	document.getElementsByTagName('head')[0].appendChild(oScript);
}

function QImage(url) {
	this.url = url;
	this.isLoaded = false;
}

QImage.prototype.load = function(parser) {
	this.parser = parser;
	var img = new Image;
	QuiX.images.push(this.url);
	img.resource = this;
	img.onload = Resource_onstatechange;
	img.src = this.url;
	img.style.display = 'none';
	if (document.desktop) document.body.appendChild(img);
}

Resource_onstatechange = function() {
	if (this.readyState=='loaded' || this.readyState=='complete') {
		this.resource.isLoaded = true;
		this.resource.parser.loadModules();
	}
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
	this.widgets = [];
	this._id_widgets = {};
	this.attributes = params.attributes || {};
	this.maxz = 0;
	this._isDisabled = false;
	this.contextMenu = null;
	
	if (params.style) {
		var tmp = document.createDocumentFragment();
		tmp.appendChild(ce('DIV'));
		tmp.firstChild.innerHTML = '<div style="' + params.style + '"></div>';
		this.div = tmp.firstChild.firstChild.cloneNode();
	}
	else
		this.div = ce('DIV');
	this.div.style.visibility = params.hidden?'hidden':'';

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
		this.setPadding([0,0,0,0]);

	if (params.display)
		this.setDisplay(params.display);
	if (params.overflow)
		this.setOverflow(params.overflow);
	this.setPosition('absolute');

	this._buildEventRegistry(params);
	this._attachEvents();

	if (params.disabled=='true' || params.disabled==true)
		this.disable();
}

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
	var w = w || this;
	if (!w._isDisabled) {
		w._statecolor = w.div.style.color;
		w.div.style.color = 'GrayText';
		w._statecursor = w.div.style.cursor;
		w.div.style.cursor = 'default';
		w._isDisabled = true;
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

Widget.prototype.detach = function() {
	this.parent.widgets.removeItem(this);
	if (this._id)
		this._removeIdRef();
	this.parent = null;
	this.div = this.div.removeNode(true);
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
	xmlhttp.send('');
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
	ws = [];
	for (var i=0; i<this.widgets.length; i++) {
		w = this.widgets[i];
		if (w instanceof wtype) ws.push(w);
		ws = ws.concat(w.getWidgetsByType(wtype));
	}
	return ws;
}

Widget.prototype._setAbsProps = function () {
	this.div.style.left = this._calcLeft() + 'px';
	this.div.style.top = this._calcTop() + 'px';
}

Widget.prototype._setCommonProps = function (w) {
	var w = w || this;
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
	var w = w || this;
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
		ofs = parseInt(this.div.style.paddingTop) + parseInt(this.div.style.paddingBottom) + 2 * this.getBorderWidth();
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
		ofs = parseInt(this.div.style.paddingLeft) + parseInt(this.div.style.paddingRight) + 2*this.getBorderWidth();
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
	var height=(typeof(this[height])=='function')?this[height](this):this[height];
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
	var left = (typeof(this[left])=='function')?this[left](this):this[left];
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
			return parseInt((this.parent[getWidth]()/2) - (this[getWidth](true)/2)) || 0;
	}
}

Widget.prototype._calcHeight = function(b) {
	var offset = 0;
	if (!b)	offset = parseInt(this.div.style.paddingTop) + parseInt(this.div.style.paddingBottom) + 2*this.getBorderWidth();
	var s = this._calcSize("height", offset, "getHeight");
	var ms=((typeof(this.minh)=='function')?this.minh(this):this.minh) - offset;
	if (s < ms) s = ms;
	return s>0?s:0;
}

Widget.prototype._calcWidth = function(b) {
	var offset = 0;
	if (!b)	offset = parseInt(this.div.style.paddingLeft) + parseInt(this.div.style.paddingRight) + 2*this.getBorderWidth();
	var s = this._calcSize("width", offset, "getWidth");
	var ms=((typeof(this.minw)=='function')?this.minw(this):this.minw) - offset;
	if (s < ms) s = ms;
	return s>0?s:0;
}

Widget.prototype._calcLeft = function() {
	return this._calcPos("left", (this.parent?this.parent.getPadding()[0]:0), "getWidth");
}

Widget.prototype._calcTop = function() {
	return this._calcPos("top", (this.parent?this.parent.getPadding()[2]:0), "getHeight");
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
	this.div.style.left = this._calcLeft() + 'px';
	this.div.style.top = this._calcTop() + 'px';
}

Widget.prototype.resize = function(x,y) {
	var minw = (typeof this.minw == "function")?this.minw(this):this.minw;
	var minh = (typeof this.minh == "function")?this.minh(this):this.minh;
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

Widget.prototype.hide = function() {
	this.div.style.visibility = 'hidden';
}

Widget.prototype.show = function() {
	this.div.style.visibility = '';
	this.redraw();
}

Widget.prototype.isHidden = function() {
	return (this.div.style.visibility == 'hidden');
}

Widget.prototype._startResize = function (evt) {
	var oWidget = this;
	var evt = evt || event;
	QuiX.startX = evt.clientX;
	QuiX.startY = evt.clientY;

	QuiX.tmpWidget = QuiX.createOutline(this);
	QuiX.tmpWidget.bringToFront();

	document.desktop.attachEvent('onmouseup', function(evt){oWidget._endResize(evt)});
	document.desktop.attachEvent('onmousemove', function(evt){oWidget._resizing(evt)});
	this.parent.div.style.cursor = 'se-resize';
}

Widget.prototype._resizing = function(evt) {
	var evt = evt || event;
	offsetX = evt.clientX - QuiX.startX;
	offsetY = evt.clientY - QuiX.startY;
	QuiX.tmpWidget.resize(this.getWidth(true) + offsetX,
				this.getHeight(true) + offsetY);
}

Widget.prototype._endResize = function(evt) {
	var evt = evt || event;
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
	var evt = evt || event;
	QuiX.startX = evt.clientX;
	QuiX.startY = evt.clientY;

	QuiX.tmpWidget = QuiX.createOutline(this);
	QuiX.tmpWidget.bringToFront();

	document.desktop.attachEvent('onmouseup', function(evt){oWidget._endMove(evt)});
	document.desktop.attachEvent('onmousemove', function(evt){oWidget._moving(evt)});
	this.parent.div.style.cursor = 'move';
}

Widget.prototype._moving = function(evt) {
	var evt = evt || event;
	offsetX = evt.clientX - QuiX.startX;
	offsetY = evt.clientY - QuiX.startY;
	QuiX.tmpWidget.moveTo(this.getLeft() + offsetX,
				this.getTop() + offsetY);	
}

Widget.prototype._endMove = function(evt) {
	var evt = evt || event;
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

Widget.prototype.redraw = function(bForceAll, w) {
	var w = w || this;
	var sOverflow;
	if (w.div.parentElement) {
		if (w.div.style.visibility == '') {
			sOverflow = w.getOverflow();
			if (sOverflow != 'hidden') w.setOverflow('hidden');
			w._setCommonProps();
			if (w.getPosition()!='') w._setAbsProps();
			for (var i=0; i<w.widgets.length; i++) {
				if (bForceAll || w.widgets[i]._mustRedraw()) w.widgets[i].redraw(bForceAll);
			}
			if (sOverflow != 'hidden') w.setOverflow(sOverflow);
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
	'onkeypress','onkeyup',
	'onclick','ondblclick',
	'oncontextmenu'
];

Widget.prototype.customEvents = ['onload'];

Widget.prototype._registerHandler = function(evt_type, handler, isCustom, w) {
	var w = w || this;
	var chr = (w._isDisabled)?'*':'';
	if (!isCustom)
		w._registry[chr + evt_type] = function(evt){return handler(evt || event, w)};
	else
		w._customRegistry[chr + evt_type] = handler;
}

Widget.prototype._buildEventRegistry = function(params) {
	this._registry = {};
	this._customRegistry = {};
	var i;
	// register DOM events
	for (i=0; i<this.supportedEvents.length; i++) {
		var evt_type = this.supportedEvents[i];
		if (params[evt_type])
			this._registerHandler(evt_type, getEventListener(params[evt_type]), false);
	}
	//register custom events
	for (i=0; i<this.customEvents.length; i++) {
		var evt_type = this.customEvents[i];
		if (params[evt_type])
			this._registerHandler(evt_type, getEventListener(params[evt_type]), true);
	}
}

Widget.prototype._attachEvents = function() {
	for (var evt_type in this._registry) {
		if (evt_type!='toXMLRPC' && evt_type.slice(0,1)!='_') {
			if (evt_type.slice(0,1)=='*') evt_type=evt_type.slice(1, evt_type.length);
			this.attachEvent(evt_type, null);//restore events directly from registry
		}
	}
}

Widget.prototype._detachEvents = function(w) {
	var w = w || this;
	var first_char;
	for (var evt_type in w._registry) {
		first_char = evt_type.slice(0,1);
		if (evt_type!='toXMLRPC' && first_char!='_' && first_char!='*')
			w.detachEvent(evt_type, '*');
	}
}

Widget.prototype._getHandler = function(eventType, f) {
	var f = getEventListener(f);
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
	var w = w || this;
	var isCustom = w.customEvents.hasItem(eventType);
	var registry = (isCustom)?w._customRegistry:w._registry;
	var f = w._getHandler(eventType, f);
	
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
	var chr = chr || '_';
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

function Widget__contextmenu(evt, w) {
	w.contextMenu.show(document.desktop, evt.clientX, evt.clientY);
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

Desktop.prototype = new Widget;

Desktop.prototype.msgbox = function(mtitle, message, buttons, image, mleft, mtop, mwidth, mheight) {
	var sButtons = '';
	var handler;
	var oButton;
	var dlg;
	
	mwidth = mwidth || 240;
	mheight = mheight || 120;
	if (image)
		innHTML = '<td><img src="' + image + '"></img></td><td>' + message + '</td>';
	else
		innHTML = '<td>' + message + '</td>';
		
	if (typeof buttons=='object') {
		for (var i=0; i<buttons.length; i++) {
			oButton = buttons[i];
			sButtons += '<a:dlgbutton width="' + oButton[1] + '" height="22" caption="' + oButton[0] + '"></a:dlgbutton>';
		}
	}
	else
		sButtons = '<a:dlgbutton onclick="__closeDialog__" caption="' + buttons + '" width="80" height="22"></a:dlgbutton>';

	this.parseFromString('<a:dialog xmlns:a="http://www.innoscript.org/quix"' +
		' title="' + mtitle + '" resizable="false" close="true"' +
		' width="' + mwidth + '" height="' + mheight + '" left="' + mleft +'" top="' + mtop + '">' +
		'<a:wbody><a:xhtml><table cellpadding="4"><tr>' + innHTML +
		'</tr></table></a:xhtml></a:wbody>' + sButtons + '</a:dialog>',
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

