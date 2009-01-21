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

QuiX.rpc = {};

QuiX.rpc.handleError = function(req, e) {
	QuiX.removeLoader();
	document.desktop.parseFromString(
		'<dialog xmlns="http://www.innoscript.org/quix" '+
		'title="Error: ' + e.name + '" resizable="true" close="true" ' +
		'width="560" height="240" left="center" top="center">' +
		'<wbody><box spacing="8" width="100%" height="100%">' +
		'<icon width="56" height="56" padding="12,12,12,12" ' +
			'img="$THEME_URL$images/error32.gif"/>' +
		'<rect padding="4,4,4,4" overflow="auto"><xhtml><![CDATA[' +
		'<pre style="color:red;font-size:12px;font-family:monospace;' +
			'padding-left:4px">' + e.message + '</pre>]]></xhtml>' +
		'</rect></box></wbody><dlgbutton onclick="__closeDialog__" ' +
			'width="70" height="22" caption="Close"></dlgbutton></dialog>');
	if (req.onerror) req.onerror(req, e);
}
