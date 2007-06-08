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

//QuiX compatibility layer

function Clipboard() {
	this.contains = '';
	this.action = '';
	this.items = [];
}

var QuiX = {};
QuiX.version = '0.8 build 20070519';
QuiX.namespace = 'http://www.innoscript.org/quix';
QuiX.startX = 0;
QuiX.startY = 0;
QuiX.clipboard = new Clipboard();
QuiX.tmpWidget = null;
QuiX.images = [];

QuiX.progress = '<a:rect xmlns:a="http://www.innoscript.org/quix" ' +
	'width="240" height="48" overflow="hidden" top="center" left="center" ' +
	'border="2" bgcolor="white" style="border-color:#999999;border-style:solid" '+
	'padding="1,1,1,1"><a:xhtml><![CDATA[<center>Please wait...<br/><br/>' +
	'<span></span></center>]]></a:xhtml>' +
	'<a:progressbar id="pb" width="150" maxvalue="1" height="4" ' +
	'top="center" left="center"></a:progressbar></a:rect>';

QuiX.modules = [
	new QModule('Windows and Dialogs', '__quix/windows.js', [3]),
	new QModule('Menus', '__quix/menus.js', [3]),
	new QModule('Splitter', '__quix/splitter.js', [3]),
	new QModule('Labels & Buttons', '__quix/buttons.js', []),
	new QModule('Tab Pane', '__quix/tabpane.js', []),
	new QModule('List View', '__quix/listview.js', []),
	new QModule('Tree', '__quix/tree.js', []),
	new QModule('Toolbars', '__quix/toolbars.js', [3]),
	new QModule('Forms & Fields', '__quix/formfields.js', [3]),
	new QModule('Common Widgets', '__quix/common.js', [3]),
	new QModule('Datagrid', '__quix/datagrid.js', [5,8]),
	new QModule('File Control', '__quix/file.js', [1,3,8]),
	new QModule('Date Picker', '__quix/datepicker.js', [14]),
	new QModule('Timers', '__quix/timers.js', []),
	new QModule('Forms & Fields 2', '__quix/formfields2.js', [3]),
	new QModule('VBox & HBox', '__quix/box.js', []),
];

QuiX.tags = {
	'desktop':-1,'xhtml':-1,'script':-1,'prop':-1,'stylesheet':-1,
	'rect':-1,'progressbar':-1,'module':-1,'custom':-1,
	'window':0,'dialog':0,
	'menubar':1,'menu':1,'menuoption':1,'contextmenu':1,
	'splitter':2,
	'dlgbutton':3,'button':3,'flatbutton':3,'label':3,'icon':3,
	'tabpane':4,'tab':4,
	'listview':5,
	'tree':6,'treenode':6,'foldertree':6,
	'toolbar':7,'tbbutton':7,'outlookbar':7,'tool':7,
	'field':8,'form':8,'spinbutton':8,
	'hr':9, 'iframe':9, 'groupbox':9, 'slider':9,
	'datagrid':10,
	'file':11,'multifile':11,
	'datepicker':12,
	'timer':13,
	'combo':14,'selectlist':14,
	'box':15
};

QuiX.getWidgetsById = function(w, sid) {
	var ws = [];
	if (w._id_widgets[sid])
		ws = ws.concat(w._id_widgets[sid]);
	for (var i=0; i<w.widgets.length; i++) {
		if (w.widgets[i].widgets.length > 0) {
			ws = ws.concat(QuiX.getWidgetsById(w.widgets[i], sid));
		}
	}
	return ws;
}

QuiX.cleanupOverlays = function() {
	var ovr = document.desktop.overlays;
	while (ovr.length>0) ovr[0].close();
}

QuiX.Exception = function(name, msg) {
	this.name = name;
	this.message = msg;
}

QuiX.getTarget = function(evt) {
	if (evt.target) {
		var node = evt.target;
		while(node.nodeType != node.ELEMENT_NODE)
			node = node.parentNode;
		return node;
	}
	else
		return evt.srcElement;
}

QuiX.removeNode = function(node) {
	var oNode;
	if (node.removeNode)
		oNode = node.removeNode(true);
	else
		oNode = node.parentNode.removeChild(node);
	return oNode;
}

QuiX.createOutline = function(w) {
	var oW = new Widget({
		left:w.getLeft(),
		top:w.getTop(),
		width:w.getWidth(true),
		height:w.getHeight(true),
		border:2,
		overflow:'hidden'
	});
	
	var t = QuiX.getImage('__quix/images/transp.gif');
	t.style.width = '100%';
	t.style.height = '100%';
	oW.div.appendChild(t);
	
	w.parent.appendChild(oW);
	oW.redraw(true);
	//calculate size because minw/minh procedure can depends on it's children size
	oW.minw = (typeof w.minw == "function")?w.minw(w):w.minw;
	oW.minh = (typeof w.minh == "function")?w.minh(w):w.minh;
	oW.div.className = 'outline';
	return(oW);
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

QuiX.addEvent = function(el, type, proc) {
	if (el.addEventListener) {
		el.addEventListener(type.slice(2,type.length), proc, false);
		return true;
	} else if (el.attachEvent) {
		return el.attachEvent(type, proc);
	}
}

QuiX.removeEvent = function(el, type, proc) {
	if (el.removeEventListener) {
		el.removeEventListener(type.slice(2,type.length), proc, false);
		return true;
	} else if (el.detachEvent) {
		return el.detachEvent(type, proc);
	}
}

QuiX.sendEvent = function(el, module, type /*, args*/) {
	if (el.dispatchEvent) {
		if (!document.implementation.hasFeature(module,""))
			return false;
		var e = document.createEvent(module);
		e.initEvent(type.slice(2,type.length), true, false/*, args */);
		el.dispatchEvent(e);
		return true;
	} else if (el.fireEvent) {
		return el.fireEvent(type);
	}
}

QuiX.stopPropag = function(evt) {
	if (evt && evt.stopPropagation) evt.stopPropagation();
	else if (window.event) window.event.cancelBubble = true;
}

QuiX.cancelDefault = function(evt) {
	if (evt && evt.preventDefault) evt.preventDefault();
	else if (window.event) window.event.returnValue = false;
}

QuiX.XMLHttpRequest = function() {
	if (window.XMLHttpRequest)
		return new XMLHttpRequest;
	else if (window.ActiveXObject)
		return new ActiveXObject('microsoft.xmlhttp');
	else
		return null;
}

QuiX.domFromString = function(s)
{
	var dom = null;
	if (window.DOMParser)
		dom = (new DOMParser).parseFromString(s,'text/xml');
	else if (window.ActiveXObject)
	{
		dom = new ActiveXObject("msxml2.domdocument");
		dom.loadXML(s);
	}

	return dom;
}

QuiX.removeWidget = function(w) {
	var parentElement;
	
	if (w.__tooltip || w.__tooltipID)
		Widget__tooltipout(null, w);
	
	while (w.widgets.length>0)
		QuiX.removeWidget(w.widgets[0]);
	if (w.parent) {
		w.parent.widgets.removeItem(w);
		if (w._id)
			w._removeIdRef();
	}

	w._detachEvents();
	
	parentElement = w.div.parentNode || w.div.parentElement;
	if (parentElement)
		QuiX.removeNode(w.div);

	w._registry = null;
	w._customRegistry = null;
	w.div = null;
	w = null;
}

function QModule(sName, sFile, d) {
	this.isLoaded = false;
	this.name = sName;
	this.file = sFile;
	this.dependencies = d;
	this.type = 'script';
}

QModule.prototype.load = function(parser) {
	this.parser = parser;
	var oElement;
	if (this.type == 'script') {
		oElement = ce('SCRIPT');
		oElement.type = 'text/javascript';
		oElement.defer = true;
		oElement.src = this.file;
	}
	else {
		oElement = ce('LINK');
		oElement.type = 'text/css';
		oElement.href = this.file;
		oElement.rel = 'stylesheet';
	}
	oElement.resource = this;
	oElement.id = this.file;
	document.getElementsByTagName('head')[0].appendChild(oElement);
	if (this.type=='stylesheet') {
		this.isLoaded = true;
		parser.loadModules();
	}
	else {
		if (typeof(window.event) != 'undefined')
			oElement.onreadystatechange = Resource_onstatechange;
		else
			oElement.onload = Resource_onstatechange;
	}
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
	img.height = 0;
	img.width = 0;
	document.body.appendChild(img);
}

Resource_onstatechange = function() {
	if (this.readyState) {
		if (this.readyState=='loaded' || this.readyState=='complete') {
			this.resource.isLoaded = true;
			this.resource.parser.loadModules();
		}
	}
	else {
		if (this.tagName=='IMG') document.body.removeChild(this);
		this.resource.isLoaded = true;
		this.resource.parser.loadModules();
	}
}

