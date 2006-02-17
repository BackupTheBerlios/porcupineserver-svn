/************************
Toolbars
************************/

function Toolbar(params) {
	params = params || {};
	this.base = Widget;
	params.padding = '2,4,0,0';
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
	this.toolheight = params.toolheight || 20;
	this.tools = [];
	this.panes = [];
	this.activePane = 0;
}

OutlookBar.prototype = new Widget;

OutlookBar.prototype.addPane = function(params) {
	var w = new Widget(
		{
			width:"100%",height:this.toolheight,
			border:1,padding:'2,2,2,2',overflow:'hidden'
		});
	this.appendChild(w);
	w.setPosition('relative');
	w.div.className = 'tool';
	w.div.innerHTML = params.caption;
	var oBar = this;
	var iPane = this.tools.length;
	w.attachEvent('onclick', function(){oBar.activatePane(iPane)});
	this.tools.push(w);
	
	var w1 = new Widget(
		{
			width:"100%",id:params.id,
			height:"this.parent.getHeight(true)-this.parent.tools.length*this.parent.toolheight",
			overflow:'auto'
		});
	this.appendChild(w1);
	if (this.panes.length!=0) w1.setDisplay('none');
	w1.setPosition('relative');
	this.panes.push(w1);
	return(w1);
}

OutlookBar.prototype.activatePane = function(iPane) {
	this.panes[this.activePane].setDisplay('none');
	this.panes[iPane].setDisplay();
	this.activePane = iPane;
}