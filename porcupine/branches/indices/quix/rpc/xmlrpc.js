//==============================================================================
//  Copyright 2000, 2001, 2002 Virtual Cowboys (info@virtualcowboys.nl)
//  Copyright 2005 - 2008 Tassos Koutsovassilis and contributors
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

function XMLRPCRequest(sUrl, async) {
	this.async = ((typeof async) == "undefined")?true:async;
	this.url = sUrl;
	this.xmlhttp = QuiX.XHRPool.getInstance();
	
	this.onreadystatechange = null;
	this.oncomplete = null;
	
	this.callback_info = null;
	this.response = null;
	
	this.onerror = null;
}

XMLRPCRequest.prototype.processResult = function() {
	try {
		var dom = this.xmlhttp.responseXML;
		if (dom) {
            return QuiX.parsers.XMLRPC.parse(dom);
		}
		else {
			throw new QuiX.Exception('QuiX.rpc.XMLRPCRequest',
									 'Malformed XMLRPC response');
		}
	}
	catch (e) {
		QuiX.rpc.handleError(this, e);
	}
}

XMLRPCRequest.prototype.callmethod = function(method_name) {
	try {
		if (this._validateMethodName(method_name)) {
			var message = '<?xml version="1.0"?><methodCall><methodName>' +
						  method_name + '</methodName><params>';
		   	for (var i=1; i<arguments.length; i++)
		   		message += '<param><value>' +
                           QuiX.parsers.XMLRPC.stringify(arguments[i]) +
		   				   '</value></param>';
			message += '</params></methodCall>';
			
			QuiX.addLoader();
			
			this.xmlhttp.open('POST', this.url, this.async);
			this.xmlhttp.setRequestHeader("Content-type", "text/xml");
			
			var req = this;
			this.xmlhttp.onreadystatechange = function() {
				if (req.xmlhttp.readyState==4) {
					// parse response...
					QuiX.removeLoader();
					var retVal = req.processResult();
					if (retVal != null && req.oncomplete) {
						req.response = retVal;
						req.oncomplete(req);
					}
					QuiX.XHRPool.release(req.xmlhttp);
				}
				else {
					if (req.onreadystatechange)
						req.onreadystatechange(req);
				}
			}
			this.xmlhttp.send(message);
		}
		else
			throw new QuiX.Exception('QuiX.rpc.XMLRPCRequest.callMethod',
									 'Invalid XMLRPC method name "' +
									 method_name + '"');
	}
	catch (e) {
		QuiX.rpc.handleError(this, e);
	}
}

XMLRPCRequest.prototype._validateMethodName = function(mname) {
	if( /^[A-Za-z0-9\._\/:]+$/.test(mname) )
		return true
	else
		return false
}
