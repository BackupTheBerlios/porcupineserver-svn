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

//QuiX generic functions

function Clipboard() {
	this.contains = '';
	this.action = '';
	this.items = [];
}

var QuiX = {};

QuiX.version = '0.6 build 20061015';
QuiX.namespace = 'http://www.innoscript.org/quix';
QuiX.startX = 0;
QuiX.startY = 0;
QuiX.clipboard = new Clipboard();
QuiX.tmpWidget = null;
QuiX.images = [];

QuiX.progress = '<a:rect xmlns:a="http://www.innoscript.org/quix" ' +
		'width="240" height="48" overflow="hidden" top="center" left="center" ' +
		'border="2" bgcolor="white" style="border-color:#999999;border-style:solid" '+
		'padding="1,1,1,1"><a:xhtml><center>Please wait...<br/><br/>' +
		'<span></span></center></a:xhtml>' +
		'<a:progressbar id="pb" width="150" maxvalue="1" height="4" ' +
		'top="center" left="center"></a:progressbar></a:rect>';

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
	'field':8,'form':8,'spinbutton':8,
	'hr':9, 'iframe':9, 'groupbox':9,
	'datagrid':10,
	'file':11,'multifile':11,
	'datepicker':12,
	'timer':13,
	'combo':14,'selectlist':14,
	'box':15
};

QuiX.getWidgetsById = function(w, sid) {
	var ws = [];
	if (w._id_widgets[sid]) ws = ws.concat(w._id_widgets[sid]);
	for (var i=0; i<w.widgets.length; i++) {
		ws = ws.concat(QuiX.getWidgetsById(w.widgets[i], sid));
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
	return (evt.target || evt.srcElement);
}

QuiX.removeNode = function(node) {
	if (node.removeNode)
		node.removeNode(true);
	else
		node.parentNode.removeChild(node);
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
