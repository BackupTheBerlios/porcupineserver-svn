//===============================================================================
//    Copyright 2005, Tassos Koutsovassilis
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

//QuiX generic functions

function __init__() {
	var root = document.getElementById("xul");
	var parser = new XULParser();
	parser.parse(root.XMLDocument);
}

function Clipboard() {
	this.contains = '';
	this.action = '';
	this.items = [];
}

var QuiX = function() {}
QuiX.version = '0.3 build 20051117';
QuiX.namespace = 'http://www.innoscript.org/quix';
QuiX.browser = 'ie';
QuiX.startX = 0;
QuiX.startY = 0;
QuiX.clipboard = new Clipboard();
QuiX.tmpWidget = null;
QuiX.images = [];
QuiX.root = (new RegExp("https?://[^/]+/[^/]+/\{[0-9a-f]{32}\}", "i")).exec(document.location.href) + '/';
QuiX.progress = '<a:rect xmlns:a="http://www.innoscript.org/quix" ' +
		'width="240" height="48" overflow="hidden" top="center" left="center" ' +
		'border="2" bgcolor="white" style="border-color:#999999;border-style:solid" '+
		'padding="1,1,1,1"><a:xhtml><center>Please wait...<br/><br/>' +
		'<span></span></center></a:xhtml>' +
		'<a:progressbar id="pb" width="150" maxvalue="1" height="4" ' +
		'top="center" left="center"></a:progressbar></a:rect>';
QuiX.modules = [
	new Module('Windows and Dialogs', '__xul/windows.js', [3]),
	new Module('Menus', '__xul/menus.js', [3]),
	new Module('Splitter', '__xul/splitter.js', [3]),
	new Module('Labels & Buttons', '__xul/buttons.js', [1]),
	new Module('Tab Pane', '__xul/tabpane.js', []),
	new Module('List View', '__xul/listview.js', []),
	new Module('Tree', '__xul/tree.js', []),
	new Module('Toolbars', '__xul/toolbars.js', [3]),
	new Module('Forms & Fields', '__xul/formfields.js', [3]),
	new Module('Common Widgets', '__xul/common.js', [3]),
	new Module('Datagrid', '__xul/datagrid.js', [5,8]),
	new Module('File Control', '__xul/file.js', [3,8]),
	new Module('Date Picker', '__xul/datepicker.js', [9]),
	new Module('Timers', '__xul/timers.js', []),
];
QuiX.tags = {
	'desktop':-1,'xhtml':-1,'script':-1,'prop':-1,'rect':-1,'progressbar':-1,
	'window':0,'dialog':0,
	'menubar':1,'menu':1,'menuoption':1,'contextmenu':1,
	'splitter':2,
	'dlgbutton':3,'button':3,'flatbutton':3,'label':3,'icon':3,
	'tabpane':4,'tab':4,
	'listview':5,
	'tree':6,'treenode':6,'foldertree':6,
	'toolbar':7,'tbbutton':7,'outlookbar':7,'tool':7,
	'field':8,'selectlist':8,'form':8,
	'hr':9,'combo':9,'spinbutton':9,
	'datagrid':10,
	'file':11,'multifile':11,
	'datepicker':12,
	'timer':13
};
QuiX.Exception = function(name, msg) {
	this.name = name;
	this.message = msg;
}
QuiX.getWidgetsById = function(w, sid) {
	var ws = [];
	if (w._id_widgets[sid]) ws = ws.concat(w._id_widgets[sid]);
	for (var i=0; i<w.widgets.length; i++) {
		ws = ws.concat(QuiX.getWidgetsById(w.widgets[i], sid));
	}
	return ws;
}
QuiX.removeWidget = function(w) {
	while (w.widgets.length>0)
		QuiX.removeWidget(w.widgets[0]);
	
	if (w.parent) {
		w.parent.widgets.removeItem(w);
		if (w.id) delete(w.parent._id_widgets[w.id]);
	}
	
	w._detachEvents();
	w.div.removeNode(true);

	w._registry = null;
	w.div = null;
	w = null;
}
QuiX.createOutline = function(w) {
	var oW = new Widget(
		{
			left:w._calcLeft(),
			top:w._calcTop(),
			width:w.getWidth(true),
			height:w.getHeight(true),
			border:2,
			overflow:'hidden'
		});
	w.parent.appendChild(oW, true);	
	oW.minw = w.minw;
	oW.minh = w.minh;
	oW.div.className = 'outline';
	return(oW);
}
QuiX.cleanupOverlays = function() {
	var ovr = document.desktop.overlays;
	while (ovr.length>0) ovr[0].close();
}
QuiX.stopPropag = function(evt) {
	evt = window.event || evt;
	evt.cancelBubble=true;
}
QuiX.cancelDefault = function(evt) {
	evt.returnValue = false;
}
QuiX.getTarget = function(evt) {
	return evt.srcElement;
}
QuiX.removeNode = function(node) {
	node.removeNode(true);
}
QuiX.getEventWrapper = function(f1, f2) {
	var wrapper;
	f1 = getEventListener(f1);
	f2 = getEventListener(f2);
	wrapper = function(evt, w) {
		var r1, r2 = null;
		r1 = f1(evt, w);
		if (f2) r2 = f2(evt, w);
		return((typeof(r1)!='undefined')?r1:r1||r2);
	}
	return(wrapper);
}
QuiX.getImage = function(url) {
		var img = new Image();
		img.src = url;
		return img;
}

// xml document
function XmlDocument() {}
XmlDocument.create = function(s) {
	var dom = new ActiveXObject("msxml2.domdocument");
	if (s) dom.loadXML(s);
	return(dom);
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

XULParser.prototype.parseXul = function(oNode, parentW, prm) {
	if (oNode.nodeType!=1) return;
	prm = prm || {};
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
					oWidget = oWidget.contextmenu;
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
				oWidget = new TreeNode(params, parentW);
				appendIt = false;
				break;
			case 'toolbar':
				oWidget = new Toolbar(params);
				break;
			case 'tbbutton':
				oWidget = parentW.addButton(params);
				if (params.type=='menu') oWidget = oWidget.contextmenu;
				appendIt = false;
				break;
			case 'tbsep':
				checkForChilds = false;
				parentW.addSeparator();
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
				parentW.attachEvent('oncontextmenu', function(){
					oWidget.show(document.desktop, event.clientX, event.clientY);
				});
				appendIt = false;
				break;
			case 'menuoption':
				if (prm.option) {
					fparams.option = new MenuOption(params);
					prm.option.options.push(fparams.option);
				}
				else {
					fparams.option = parentW.addOption(params);
				}
				appendIt = false;
				oWidget = fparams.option;
				break;
			case 'sep':
				checkForChilds = false;
				if (prm.option)
					prm.option.options.push(-1);
				else
					parentW.options.push(-1);
				appendIt = false;
				break;
			case 'hr':
				checkForChilds = false;
				oWidget = new HR(params);
				break;
			case 'rect':
				oWidget = new Widget(params);
				break;
			case 'timer':
				oWidget = new Timer(params);
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
		
		if (oWidget && parentW && !oWidget.parent && appendIt) {
			parentW.appendChild(oWidget);
		}
		
		if (checkForChilds) {
			for (var i=0; i<oNode.childNodes.length; i++) {
				this.parseXul(oNode.childNodes[i], oWidget, fparams);
			}
		}

		if (oNode.localName == 'form') this.activeForm = null;
		
		if (oWidget) { 
			if (oWidget.onload) oWidget.onload(oWidget);
			if (params.disabled=='true' || params.disabled==true) oWidget.disable();
		}
	}
	return(oWidget);
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
	var img = new Image();
	QuiX.images.push(this.url);
	img.resource = this;
	img.onload = Resource_onstatechange;
	img.src = this.url;
	if (document.desktop) document.body.appendChild(img);
}

Resource_onstatechange = function() {
	if (this.readyState=='loaded' || this.readyState=='complete') {
		if (this.tagName=='IMG') this.removeNode();
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
	this.borderWidth = params.border || 0;
	this.style = params.style || '';
	this.bgColor = params.bgcolor || '';
	this.overflow = params.overflow || '';
	if (params.padding) {
		this.padding = params.padding.split(',');
		for (var i=0; i<this.padding.length; i++) this.padding[i]=parseInt(this.padding[i]);
	}
	else
		this.padding = [0,0,0,0];
	this.minw = 0;
	this.minh = 0;
	this.isHidden = false;
	this.widgets = [];
	this._id_widgets = {};
	this.attributes = params.attributes || {};
	this.isAbs = true;
	this.maxz = 0;
	this.display = '';
	this._isDisabled = false;

	if (this.style != '') {
		var tmp = document.createDocumentFragment();
		tmp.appendChild(ce('DIV'));
		tmp.firstChild.innerHTML = '<div style="' + this.style + '"></div>';
		this.div = tmp.firstChild.firstChild.cloneNode();
	}
	else
		this.div = ce('DIV');

	this.div.widget = this;
	
	if (params.id) {
		this.id = params.id;
		this.div.id = this.id;
	}

	if (params.display) this.setDisplay(params.display);
	this.div.style.position = 'absolute';
	this.div.style.overflow = this.overflow;
	this.div.style.backgroundColor = this.bgColor;

	this._buildEventRegistry(params)
	this._attachEvents();
	if (params.onload) this.onload = getEventListener(params.onload);
	if (params.disabled=='true' || params.disabled==true) this.disable();
}

Widget.prototype.appendChild = function(w) {
	this.widgets.push(w);
	if (w.id) {
		if (this._id_widgets[w.id])
			this._id_widgets[w.id].push(w);
		else
			this._id_widgets[w.id] = [w];
	}
	w.parent = this;
	
	this.div.appendChild(w.div);

	if (w.height=='100%' && w.width=='100%') {
		this.overflow = 'hidden';
		this.div.style.overflow='hidden';
	}
	w.repad();
	w.redraw();
	w.bringToFront();
}

Widget.prototype.repad = function () {
	this.div.style.paddingLeft = this.padding[0] + 'px';
	this.div.style.paddingRight = this.padding[1] + 'px';
	this.div.style.paddingTop = this.padding[2] + 'px';
	this.div.style.paddingBottom = this.padding[3] + 'px';
	this.div.style.borderWidth = this.borderWidth + 'px';
}

Widget.prototype.supportedEvents = [
	'onmousedown','onmouseup',
	'onmousemove','onmouseover','onmouseout',
	'onselectstart',
	'onkeypress','onkeyup',
	'onclick','ondblclick',
	'oncontextmenu'
];

Widget.prototype._buildEventRegistry = function(params) {
	var evt_type;
	this._registry = {};
	for (var i=0; i<this.supportedEvents.length; i++) {
		evt_type = this.supportedEvents[i];
		if (params[evt_type])
			this._registry[evt_type] = getEventListener(params[evt_type]);
	}
}

Widget.prototype._attachEvents = function() {
	for (var evt_type in this._registry) {
		this.attachEvent(
			evt_type,
			this._registry[evt_type]
		);
	}
}

Widget.prototype._detachEvents = function(w) {
	var w = w || this;
	for (var evt_type in w._registry) {
		w.detachEvent(
			evt_type,
			w._registry[evt_type]
		);
	}
}

Widget.prototype.disable = function(w) {
	w = w || this;
	w.statecolor = w.div.style.color;
	w.div.style.color = 'GrayText';
	w.statecursor = w.div.style.cursor;
	w.div.style.cursor = '';
	if (!w._isDisabled) w._detachEvents();
	w._isDisabled = true;
	for (var i=0; i<w.widgets.length; i++) {
		w.widgets[i].disable();
	}
}

Widget.prototype.enable = function(w) {
	w = w || this;
	w.div.style.color = w.statecolor || '';
	w.div.style.cursor = w.statecursor || '';
	if (w._isDisabled) w._attachEvents();
	w._isDisabled = false;
	for (var i=0; i<w.widgets.length; i++) {
		w.widgets[i].enable();
	}
}

Widget.prototype.parse = function(dom, callback) {
	var parser = new XULParser();
	parser.oncomplete = callback;
	parser.parse(dom, this);
}

Widget.prototype.parseFromString = function(s, oncomplete) {
	var oDom = XmlDocument.create(s);
	this.parse(oDom, oncomplete);
}

Widget.prototype.parseFromUrl = function(url, oncomplete) {
	var xmlhttp = new ActiveXObject("microsoft.xmlhttp");
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
	if (w.height!=null) w.div.style.height = w._calcHeight() + 'px';
	if (w.width!=null) w.div.style.width = w._calcWidth() + 'px';
	w.div.style.backgroundColor = this.bgColor;
}

Widget.prototype.setDisplay = function (sDispl) {
	this.display = sDispl || '';
	this.div.style.display = sDispl || '';
}

Widget.prototype.setPos = function (sPos) {
	this.isAbs = (sPos=='absolute')? true:false;
	this.div.style.position = sPos || '';
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
		ofs = this.padding[2] + this.padding[3] + 2*this.borderWidth;
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
		ofs = this.padding[0]+this.padding[1]+2*this.borderWidth;
		wd += ofs;
	}
	return wd;
}

Widget.prototype.getLeft = function(b)
{
	var ofs, lf;
	b = b || false;
	lf = parseInt(this.div.style.left);
	if (isNaN(lf)) return 0;
	if (b) {
		ofs = this.padding[0]+this.borderWidth;
		lf -= ofs
	}
	return lf;
}

Widget.prototype.getTop = function(b)
{
	var ofs, rg;
	b = b || false;
	rg = parseInt(this.div.style.top);
	if (isNaN(rg)) return 0;
	if (b) {
		ofs = this.padding[2]+this.borderWidth;
		rg -= ofs
	}
	return rg;
}

Widget.prototype._calcHeight = function(b)
{
	var offset = 0;
	if (!b)	offset = this.padding[2]+this.padding[3]+2*this.borderWidth;
	if (!isNaN(this.height)) {
		return(parseInt(this.height)-offset);
	}
	else if (typeof(this.height)=='function') {
		var w = this.height(this)-offset;
		return(w>0?w:0)
	}
	else if (this.height.slice(this.height.length-1)=='%') {
		var perc = parseInt(this.height)/100;
		var nh = parseInt(this.parent.getHeight()*perc) - offset;
		return(nh>0?nh:0);
	}
	else {
		var w = eval(this.height) - offset;
		return(w>0?w:0);
	}
}

Widget.prototype._calcWidth = function(b)
{
	var offset = 0;
	if (!b) offset = this.padding[0]+this.padding[1]+2*this.borderWidth;
	if (!isNaN(this.width)) {
		return(parseInt(this.width)-offset);
	}
	else if (typeof(this.width)=='function') {
		var w = this.width(this)-offset;
		return(w>0?w:0)
	}
	else if (this.width.slice(this.width.length-1)=='%') {
		var perc = parseInt(this.width)/100;
		var nw = parseInt(this.parent.getWidth()*perc) - offset;
		return(nw>0?nw:0);
	}
	else {
		var w = eval(this.width)-offset;
		return(w>0?w:0);
	}
}

Widget.prototype._calcLeft = function()
{
	if (!isNaN(this.left)) {
		var l = parseInt(this.left);
		if (this.parent) l+= this.parent.padding[0];
		return(l);
	}
	else if (typeof(this.left)=='function') {
		var w = this.left(this);
		return(w>0?w:0)
	}
	else if (this.left.slice(this.left.length-1)=='%') {
		var perc = parseInt(this.left)/100;
		return(this.parent.getWidth() * perc);
	}
	else {
		if (this.left!='center')
			return(eval(this.left));
		else
			return parseInt((this.parent.getWidth()/2) - (this.getWidth(true)/2));
	}
}

Widget.prototype._calcTop = function()
{
	if (!isNaN(this.top)) {
		var t = parseInt(this.top);
		if (this.parent) t+= this.parent.padding[2];
		return(t);
	}
	else if (typeof(this.top)=='function') {
		var w = this.top(this);
		return(w>0?w:0)
	}
	else if (this.top.slice(this.top.length-1)=='%') {
		var perc = parseInt(this.top)/100;
		return(this.parent.getHeight() * perc);
	}
	else {
		if (this.top!='center')
			return(eval(this.top));
		else
			return parseInt((this.parent.getHeight()/2) - (this.getHeight(true)/2));
	}
}


Widget.prototype.getScreenLeft = function()
{
	var oElement = this.div;
	iX = 0
	while(oElement) {
		if (oElement.tagName!='TR') iX += oElement.offsetLeft - oElement.scrollLeft;
		oElement = oElement.parentElement;
	}
	return(iX);
}

Widget.prototype.getScreenTop = function()
{
	var oElement = this.div;
	iY = 0
	while(oElement) {
		if (oElement.tagName!='TR') iY += oElement.offsetTop - oElement.scrollTop;
		oElement = oElement.parentElement;
	}
	return(iY);
}

Widget.prototype.bringToFront = function(w)
{
	w = w || this;
	if (w.div.style.zIndex==0 || w.div.style.zIndex < w.parent.maxz) {
		w.div.style.zIndex = ++w.parent.maxz;
	}
}

Widget.prototype.click = function() {
	this.div.click();
}

Widget.prototype.moveTo = function(x,y) {
	this.left = x>0?x:0;
	this.top = y>0?y:0;
	this.redraw();
}

Widget.prototype.resize = function(x,y) {
	this.width = (x>this.minw)?x:this.minw;
	this.height = (y>this.minh)?y:this.minh;
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
	this.isHidden = true;
}

Widget.prototype.show = function() {
	this.div.style.visibility = '';
	this.isHidden = false;
	this.redraw();
}

Widget.prototype._startResize = function (evt)
{
	var oWidget = this;
	QuiX.startX = event.clientX;
	QuiX.startY = event.clientY;

	QuiX.tmpWidget = QuiX.createOutline(this);
	QuiX.tmpWidget.bringToFront();

	document.desktop.attachEvent('onmouseup', function(evt){oWidget._endResize(evt)});
	document.desktop.attachEvent('onmousemove', function(evt){oWidget._resizing(evt)});
	this.parent.div.style.cursor = 'se-resize';
}

Widget.prototype._resizing = function(evt)
{
	offsetX = event.clientX - QuiX.startX;
	offsetY = event.clientY - QuiX.startY;
	QuiX.tmpWidget.resize(this.getWidth(true) + offsetX,
				this.getHeight(true) + offsetY);
}

Widget.prototype._endResize = function(evt)
{
	offsetX = event.clientX - QuiX.startX;
	offsetY = event.clientY - QuiX.startY;
	this.resize(this.getWidth(true) + offsetX,
				this.getHeight(true) + offsetY);
	this.bringToFront();
	QuiX.tmpWidget.destroy();
	document.desktop.detachEvent('onmouseup');
	document.desktop.detachEvent('onmousemove');
	this.parent.div.style.cursor = '';
}

Widget.prototype._startMove = function(evt)
{
	var oWidget = this;
	QuiX.startX = event.clientX;
	QuiX.startY = event.clientY;

	QuiX.tmpWidget = QuiX.createOutline(this);
	QuiX.tmpWidget.bringToFront();

	document.desktop.attachEvent('onmouseup', function(evt){oWidget._endMove(evt)});
	document.desktop.attachEvent('onmousemove', function(evt){oWidget._moving(evt)});
	this.parent.div.style.cursor = 'move';
}

Widget.prototype._moving = function(evt)
{
	offsetX = event.clientX - QuiX.startX;
	offsetY = event.clientY - QuiX.startY;
	QuiX.tmpWidget.moveTo(this._calcLeft() + offsetX,
				this._calcTop() + offsetY);	
}

Widget.prototype._endMove = function(evt)
{
	QuiX.tmpWidget.destroy();
	document.desktop.detachEvent('onmouseup');
	document.desktop.detachEvent('onmousemove');
	offsetX = event.clientX - QuiX.startX;
	offsetY = event.clientY - QuiX.startY;
	this.moveTo(this.div.offsetLeft + offsetX,
				this.div.offsetTop + offsetY);
	this.bringToFront();
	this.parent.div.style.cursor = '';
}

Widget.prototype.redraw = function(bForceAll) {
	if (!this.isHidden) {
		if (this.overflow != 'hidden') this.div.style.overflow = 'hidden';

		this._setCommonProps();
		if (this.isAbs) this._setAbsProps();
		for (var i=0; i<this.widgets.length; i++) {
			if (this.widgets[i]._mustRedraw() || bForceAll) this.widgets[i].redraw(bForceAll);
		}
		
		if (this.overflow!='hidden') this.div.style.overflow = this.overflow;
	}
}

Widget.prototype.print = function(expand) {
	var oWidget = this;
	var iframe = document.getElementById('_print');
	expand = expand || false;
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
		iframe.src = '__xul/print.htm';
	}
	else {
		iframe.contentWindow.location.reload();
	}
}

Widget.prototype.attachEvent = function(eventType, f) {
	var oWidget = this;
	if (this._registry[eventType]) {
		this.detachEvent(eventType);
	}
	if (f) {
		if (typeof f=='string')
			f = getEventListener(f);
		var handler = function(e){return f(e, oWidget)};
		this._registry[eventType] = handler;
	}
	else
		handler = this._registry[eventType];
	this.div.attachEvent(eventType, handler);
}

Widget.prototype.detachEvent = function(eventType) {
	this.div.detachEvent(eventType, this._registry[eventType]);
}

//Desktop class
function Desktop(params, root) {
	this.base = Widget;
	params.id = 'desktop';
	params.width = 'document.documentElement.clientWidth';
	params.height = 'document.documentElement.clientHeight';
	params.onmousedown = QuiX.getEventWrapper(Desktop__onmousedown, params.onmousedown);
	params.oncontextmenu = function() {return false}
	this.base(params);
	this.setPos();
	this.div.onselectstart = function(){return(false)};
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
	this.value += parseInt(amount);
	if (this.value>this.maxvalue) this.value=this.maxvalue;
	this._update();	
}

