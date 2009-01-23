//==============================================================================
//  Copyright 2005-2008, Tassos Koutsovassilis
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

QuiX.utils = {};

function ce(t) {
	return(document.createElement(t));
}

//==============================================================================
//  String extensions
//==============================================================================
String.prototype.xmlDecode = function() {
	var s = this.replace(/&amp;/g, '&').replace(/&gt;/g , '>').
            replace(/&lt;/g, '<').replace(/&quot;/g, '"');
	return s;
}

String.prototype.xmlEncode = function() {
	var s = this.replace(/&/g, '&amp;').replace(/</g, '&lt;').
            replace(/>/g, '&gt;').replace(/"/g, '&quot;');
	return s;
}

String.prototype.trim = function() {
	var s = this.replace(/^\s+/, '').replace(/\s+$/, '');
	return s;
}

String.prototype.reverse = function() {
	var theString = "";
	for (var i=this.length-1; i>=0; i--)
		theString += this.charAt(i);
	return theString;
}

//==============================================================================
//  Array extensions
//==============================================================================
Array.prototype.hasItem = function(item) {
	for (var i=0; i<this.length; i++) {
		if (this[i]==item) return(true);
	}
	return(false);
}

if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = function(elt /*, from*/) {
		var len = this.length;
		var from = Number(arguments[1]) || 0;
		from = (from < 0) ? Math.ceil(from) : Math.floor(from);
		if (from < 0)
		  from += len;

		for (; from < len; from++)
			if (from in this && this[from] === elt)
				return from;
		return -1;
	}
}

Array.prototype.removeItem = function(item) {
	for (var i=0; i<this.length; i++) {
		if (this[i]==item) {
			this.splice(i,1);
			return(true);
		}
	}
	return(false);
}

Array.prototype.sortByAttribute = function(prop) {
	var sortfunc = function(a,b) {
		var prop1 = a[prop];
		var prop2 = b[prop];
		if (prop1<prop2 || !prop1) return -1
		else if (prop1>prop2 || !prop2) return 1
		else return 0
	}
	this.sort(sortfunc);
}
