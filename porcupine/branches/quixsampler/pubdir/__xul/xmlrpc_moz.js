//===============================================================================
//    Copyright 2000, 2001, 2002 Virtual Cowboys (info@virtualcowboys.nl)
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

//xmlrpc client
function __displayError__(e) {
	document.desktop.parseFromString('<a:dialog xmlns:a="http://www.innoscript.org/quix"'+
		' title="Error: ' + e.name + '" resizable="true" close="true"' +
		' width="520" height="180" left="center" top="center">' +
		'<a:wbody><a:splitter orientation="v" spacing="0" width="100%" height="100%">' +
		'<a:pane length="60"><a:icon left="center" top="10" width="32" height="32" img="images/error32.gif"></a:icon></a:pane>' +
		'<a:pane length="-1" padding="4,4,4,4" overflow="auto"><a:xhtml>' +
		'<pre style="color:red;font-size:12px;font-family:monospace;padding-left:4px">' + e.message.xmlEncode() + '</pre></a:xhtml></a:pane>' +
		'</a:splitter></a:wbody><a:dlgbutton onclick="__closeDialog__" width="70" height="22" caption="Close"></a:dlgbutton></a:dialog>');
}

Object.prototype.toXMLRPC = function() {
	var wo = this.valueOf();
	if(wo.toXMLRPC == this.toXMLRPC) {
		retstr = "<struct>";
		for(prop in this) {
			if(typeof wo[prop] != "function") {
				retstr += "<member><name>" + prop + "</name><value>" + _getXml(wo[prop]) + "</value></member>";
			}
		}
		retstr += "</struct>";
		return retstr;
	}
	else {
		return wo.toXMLRPC();
	}
}

String.prototype.toXMLRPC = function() {
	return "<string>" + this.xmlEncode() + "</string>";
}

Number.prototype.toXMLRPC = function() {
	if(this == parseInt(this)){
		return "<int>" + this + "</int>";
	}
	else if(this == parseFloat(this)) {
		return "<double>" + this + "</double>";
	}
	else {
		return false.toXMLRPC();
	}
}

Boolean.prototype.toXMLRPC = function() {
	if (this==true) return "<boolean>1</boolean>";
	else return "<boolean>0</boolean>";
}

Date.prototype.toXMLRPC = function() {
	var d = "<dateTime.iso8601>" + this.toIso8601() + "</dateTime.iso8601>";
	return(d);
}

Date.prototype.toIso8601 = function() {
	var s = doYear(this.getFullYear()) + "-" +
			doZero(this.getMonth() + 1) + "-" +
			doZero(this.getDate()) + "T" +
			doZero(this.getHours()) + ":" +
			doZero(this.getMinutes()) + ":" +
			doZero(this.getSeconds());
	return(s);

	function doZero(nr) {
		nr = String("0" + nr);
		return nr.substr(nr.length-2, 2);
	}
	
	function doYear(year) {
		if(year > 9999 || year < 0) 
			throw new QuiX.Exception("Malformed XMLRPC request", "Unsupported year: " + year);
			
		year = String("0000" + year)
		return year.substr(year.length-4, 4);
	}
}

Date.prototype.parseIso8601 = function(s) {
	var sn = "/";
	if(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})/.test(s)) {
  			return new Date(RegExp.$2 + sn + RegExp.$3 + sn + 
			RegExp.$1 + " " + RegExp.$4 + ":" + 
			RegExp.$5 + ":" + RegExp.$6);
  	}
	else
		return new Date();
}

Array.prototype.toXMLRPC = function() {
	var retstr = "<array><data>";
	for(var i=0;i<this.length;i++) {
		retstr += "<value>" + _getXml(this[i]) + "</value>";
	}
	return retstr + "</data></array>";
}

function _getXml(obj) {
	if( obj == null || obj == undefined || ( typeof obj == "number" && !isFinite(obj) ) )
		return false.toXMLRPC();
	else
		return obj.toXMLRPC();
}

function XMLRPCRequest(sUrl) {
	this.url = sUrl;
	this.xmlhttp = new XMLHttpRequest();

	this.onreadystatechange = null;
	this.oncomplete = null;
	
	this.callback_info = null;
	this.response = null;

	this.onerror = null;

	var req = this;

	this.xmlhttp.onreadystatechange = function() {
		if (req.xmlhttp != null) {
			if (req.xmlhttp.readyState==4) {
				// parse response...
				retVal = req.processResult();
				if (retVal!=null && req.oncomplete) {
					req.response = retVal;
					req.oncomplete(req);
				}
				req.xmlhttp = null;
			}
			else {
				if (req.onreadystatechange) req.onreadystatechange(req);
			}
		}

	}
}

XMLRPCRequest.prototype.handleError = function (e) {
	__displayError__(e);
	if (this.onerror) this.onerror(this, e);
}

XMLRPCRequest.prototype.processResult = function() {
	try {
		if (this.xmlhttp.status == 200) {
			//getIncoming message
			dom = this.xmlhttp.responseXML;
			//alert(dom.xml);
			if (dom) {
				var rpcErr, main;
	
				//Check for XMLRPC Errors
				rpcErr = dom.getElementsByTagName("fault");
				if(rpcErr.length > 0) {
					rpcErr = this.toObject(this.getNode(rpcErr[0], [0]));
					throw new QuiX.Exception(rpcErr.faultCode, rpcErr.faultString);
		   		}
	
				//handle method result
				main = dom.getElementsByTagName("param");
				if (main.length == 0) {
					throw new QuiX.Exception('Malformed XMLRPC response', this.xmlhttp.responseText)
				}
				data = this.toObject(this.getNode(main[0], [0]));
				return data;
			}
			else {
				throw new QuiX.Exception('Malformed XMLRPC response', this.xmlhttp.responseText);
			}
		}
		else {
			throw new QuiX.Exception('HTTP Exception (' + this.xmlhttp.status + ')', this.xmlhttp.statusText);
		}
	}
	catch (e) {
		this.handleError(e);
	}
}

XMLRPCRequest.prototype.getNode = function(data, tree) {
	var nc = 0; //nodeCount
	if(data != null) {
		for(i=0;i<data.childNodes.length;i++) {
			if(data.childNodes[i].nodeType == 1) {
				if(nc == tree[0]) {
					data = data.childNodes[i];
					if(tree.length > 1) {
						tree.shift();
						data = this.getNode(data, tree);
					}
					return data;
				}
				nc++
			}
		}
	}	
	return false;
}

XMLRPCRequest.prototype.toObject = function(data) {
	var ret, i;
	//alert(data.tagName);
	switch(data.tagName) {
		case "string":
			return (data.firstChild) ? new String(data.firstChild.nodeValue) : "";
			break;
		case "int":
		case "i4":
		case "double":
			return (data.firstChild) ? new Number(data.firstChild.nodeValue) : 0;
			break;
		case "dateTime.iso8601":
			return( new Date().parseIso8601(data.firstChild.nodeValue) );
			break;
		case "array":
			data = this.getNode(data, [0]);
			if(data && data.tagName == "data") {
				ret = new Array();
				var i = 0;
				while(child = this.getNode(data, [i++])) {
					ret.push(this.toObject(child));
				}
				return ret;
			}
			else {
				throw new QuiX.Exception('Malformed XMLRPC response', 'Bad array.');
			}
			break;
		case "struct":
			ret = {};
			var i = 0;
			while(child = this.getNode(data, [i++])) {
				if(child.tagName == "member") {
					ret[this.getNode(child, [0]).firstChild.nodeValue] = this.toObject(this.getNode(child, [1]));
				}
				else {
					throw new QuiX.Exception('Malformed XMLRPC response', "'member' element expected, found '" + child.tagName + "' instead");
				}
			}
			return ret;
			break;
		case "boolean":
			return Boolean(isNaN(parseInt(data.firstChild.nodeValue)) ? (data.firstChild.nodeValue == "true") : parseInt(data.firstChild.nodeValue))
			break;
/*
		case "base64":
			return this.decodeBase64(data.firstChild.nodeValue);
			break;
*/
		case "value":
			child = this.getNode(data, [0]);
			return (!child) ? ((data.firstChild) ? new String(data.firstChild.nodeValue) : "") : this.toObject(child);
			break;
		default:
			throw new QuiX.Exception('Malformed XMLRPC response', 'Invalid tag name: ' + data.tagName);
	}
}


XMLRPCRequest.prototype.callmethod = function(method_name) {
	try {
		if (!this._validateMethodName(method_name)) {
			var message = '<?xml version="1.0"?><methodCall><methodName>' + method_name + '</methodName><params>';
		
		   	for(var i=1;i<arguments.length;i++)
		   		message += '<param><value>' + _getXml(arguments[i]) + '</value></param>';
		
			message += '</params></methodCall>';
			
			this.xmlhttp.open('POST', this.url, true);
			this.xmlhttp.setRequestHeader("User-Agent", "vcXMLRPC running on " + navigator.userAgent);
			this.xmlhttp.setRequestHeader("Content-type", "text/xml");
			this.xmlhttp.send(message);
		}
		else
			throw new QuiX.Exception('Malformed XMLRPC request', 'Invalid XMLRPC method name "' + method_name + '"');
	}
	catch (e) {
		this.handleError(e);
	}
}

XMLRPCRequest.prototype._validateMethodName = function(mname) {
	if( /^[A-Za-z0-9\._\/:]+$/.test(name) )
		return true
	else
		return false
}
