//==============================================================================
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

QuiX.parsers = {}

//==============================================================================
// XML-RPC Parser
//==============================================================================
QuiX.parsers.XMLRPC = {}

QuiX.parsers.XMLRPC.stringify = function(obj) {
	if (obj == null || obj == undefined || (typeof obj == "number" &&
                                            !isFinite(obj)))
		return false.toXMLRPC();
	else {
		var wo = obj.valueOf();
		if(!wo.toXMLRPC) {
			var retstr = "<struct>";
			for(var prop in obj) {
				if(typeof wo[prop] != "function") {
					retstr += "<member><name>" + prop + "</name><value>" +
							  QuiX.parsers.XMLRPC.stringify(wo[prop]) +
                              "</value></member>";
				}
			}
			retstr += "</struct>";
			return retstr;
		}
		else
			return wo.toXMLRPC();
	}
}

QuiX.parsers.XMLRPC.parse = function(xml) {
    function getNode(data, len) {
        var nc = 0; //nodeCount
        if(data != null) {
            for(var i=0; i<data.childNodes.length; i++) {
                if(data.childNodes[i].nodeType == 1) {
                    if(nc == len)
                        return data.childNodes[i];
                    else
                        nc++
                }
            }
        }
        return false;
    }
    function toObject(data) {
        var ret, i, elem;
        switch(data.tagName) {
            case "string":
                return (data.firstChild)?
                       data.firstChild.nodeValue.toString():"";
                break;
            case "int":
            case "i4":
            case "double":
                return (data.firstChild)?
                       new Number(data.firstChild.nodeValue):0;
                break;
            case "dateTime.iso8601":
                return new Date().parseIso8601(data.firstChild.nodeValue);
                break;
            case "array":
                data = getNode(data, 0);
                if(data && data.tagName == "data") {
                    ret = [];
                    for (i=0; i<data.childNodes.length; ++i) {
                        elem = data.childNodes[i];
                        if (elem.nodeType == 1) ret.push(toObject(elem));
                    }
                    return ret;
                }
                else
                    throw new QuiX.Exception('Malformed XMLRPC response',
                                             'Bad array.');
                break;
            case "struct":
                ret = {};
                for (i=0; i<data.childNodes.length; ++i) {
                    elem = data.childNodes[i];
                    if (elem.nodeType == 1) {
                        if(elem.tagName == "member")
                            ret[getNode(elem,0).firstChild.nodeValue] =
                                toObject(getNode(elem, 1));
                        else
                            throw new QuiX.Exception(
                                    'Malformed XMLRPC response',
                                    "'member' element expected, found '" +
                                    elem.tagName + "' instead");
                    }
                }
                return ret;
                break;
            case "boolean":
                return Boolean(isNaN(parseInt(data.firstChild.nodeValue))?
                    (data.firstChild.nodeValue == "true"):
                    parseInt(data.firstChild.nodeValue));
                break;
            case "value":
                var child = getNode(data, 0);
                return (!child)? ((data.firstChild)?
                    data.firstChild.nodeValue.toString():""):toObject(child);
                break;
            default:
                throw new QuiX.Exception('Malformed XMLRPC response',
                                         'Invalid tag name: ' + data.tagName);
        }
    }

    if (typeof xml === 'string')
        xml = QuiX.domFromString(xml);

    //Check for XMLRPC Errors
    var rpcErr = xml.getElementsByTagName("fault");
    if (rpcErr.length > 0) {
        rpcErr = toObject(getNode(rpcErr[0], 0));
        throw new QuiX.Exception(rpcErr.faultCode, rpcErr.faultString);
    }
    //handle result
    var main = xml.getElementsByTagName("param");
    if (main.length == 0) {
        throw new QuiX.Exception('Malformed XMLRPC message',
                                 '"param" element is missing');
    }
    var data = toObject(getNode(main[0], 0));
    return data;
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

Array.prototype.toXMLRPC = function() {
	var retstr = "<array><data>";
	for (var i=0; i<this.length; i++) {
		retstr += "<value>" + QuiX.parsers.XMLRPC.stringify(this[i]) +
                  "</value>";
	}
	return retstr + "</data></array>";
}
