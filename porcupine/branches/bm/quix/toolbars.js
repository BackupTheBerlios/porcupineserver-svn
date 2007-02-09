/************************
Toolbars
************************/

function Toolbar(params) {
	params = params || {};
	this.base = Widget;
	params.padding = params.padding || '2,4,0,0';
	params.border = params.border || 1;
	params.overflow = 'hidden';
	this.base(params);
	this.div.className = 'toolbar';
	this.handle = new Widget({width:4,height:"100%",border:0,overflow:'hidden'});
	this.appendChild(this.handle);
	this.handle.div.className = 'handle';

	var iSpacing = params.spacing || 4;
	this.spacing = parseInt(iSpacing);
	this.buttons = [];
}

Toolbar.prototype = new Widget;

Toolbar.prototype._getOffset = function(oButton) {
	var offset = 0;
	for (var i=0; i<this.buttons.length; i++) {
		if (this.buttons[i]==oButton)
			break;
		offset += this.buttons[i]._calcWidth(true) + this.spacing;
	}
	return(offset + this.handle._calcWidth(true) + 4);
}

Toolbar.prototype.addButton = function(params) {
	params.left = "this.parent._getOffset(this)";
	params.height = "100%";
	var oButton = new FlatButton(params);
	oButton.destroy = ToolbarButton__destroy;
	this.appendChild(oButton);
	this.buttons.push(oButton);
	return(oButton);
}

Toolbar.prototype.addSeparator = function() {
	var l = "this.parent._getOffset(this)";
	var oSep = new Widget({left:l,width:2,height:"100%",border:1,overflow:'hidden'});
	oSep.destroy = ToolbarButton__destroy;
	this.appendChild(oSep);
	oSep.div.className = 'separator';
	this.buttons.push(oSep);
	return(oSep);
}

ToolbarButton__destroy = function() {
	var parent = this.parent;
	parent.buttons.removeItem(this);
	if (this.base)
		this.base.prototype.destroy(this);
	else
		Widget.prototype.destroy(this);
	parent.redraw();
}

function OutlookBar(params) {
	params = params || {};
	this.base = Widget;
	params.overflow = 'hidden';
	this.base(params);
	this.div.className = 'outlookbar';
	
	this.headerHeight = params.headerheight || 20;
	this.panes = [];
	this.activePane = 0;
}

OutlookBar.prototype = new Widget;

OutlookBar.prototype.addPane = function(params) {
	var header = new Label({
		width : "100%",
		height : this.headerHeight,
		border : 1,
		padding : '2,2,2,2',
		overflow : 'hidden',
		caption : params.caption,
		align : params.align || 'center'
	});
	this.appendChild(header);
	header.setPosition('relative');
	header.div.className = 'tool';
	header.attachEvent('onclick', OutlookBarHeader__onclick);

	params.width = '100%';
	params.height = 'this.parent.getHeight(true)-this.parent.panes.length*this.parent.headerHeight';

	var w1 = new Widget(params);
	
	this.appendChild(w1);

	if (this.panes.length!=0)
		w1.setDisplay('none');
	w1.setPosition('relative');

	this.panes.push(w1);

	w1.header = header;
	w1.setCaption = OutlookBarPane__setCaption;
	w1.getCaption = OutlookBarPane__getCaption;
	w1.destroy = OutlookBarPane__destroy;
	return(w1);
}

OutlookBar.prototype.activatePane = function(iPane) {
	if (this.activePane > -1)
		this.panes[this.activePane].setDisplay('none');
	this.panes[iPane].setDisplay();
	this.activePane = iPane;
}

function OutlookBarHeader__onclick(evt, w) {
	var oBar = w.parent;
	for (var i=0; i<oBar.panes.length; i++) {
		if (oBar.panes[i].header == w) {
			oBar.activatePane(i);
			return;
		}
	}
}
function OutlookBarPane__setCaption(sCaption) {
	this.header.setCaption(sCaption);
}

function OutlookBarPane__getCaption() {
	return this.header.getCaption();
}

function OutlookBarPane__destroy() {
	var oBar = this.parent;
	oBar.panes.removeItem(this);
	if (oBar.panes.length < oBar.activePane + 1)
		oBar.activePane = oBar.panes.length - 1;
	this.header.destroy();
	Widget.prototype.destroy(this);
	oBar.redraw();
}