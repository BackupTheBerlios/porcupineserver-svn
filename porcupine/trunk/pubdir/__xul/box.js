/************************
Box layout
************************/
function Box(params) {
	params = params || {};
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'box';
	this.orientation = params.orientation || 'h';
	var iSpacing = params.spacing || 2;
	this.spacing = parseInt(iSpacing);
}

Box.prototype = new Widget;

Box.prototype.appendChild = function(w) {
	w.destroy = BoxWidget__destroy;
	if (this.orientation == 'h') {
		w.height = w.height || '100%';
		w.length = w.width || '-1';
	}
	else {
		w.width = w.width || '100%';
		w.length = w.height || '-1';
	}
	Widget.prototype.appendChild(w, this);
	this.redraw(true);
}

Box.prototype.redraw = function(bForceAll) {
	var oWidget;
	if (bForceAll) {
		var offset_var = (this.orientation=='h')?'left':'top';
		var length_var = (this.orientation=='h')?'width':'height';
		
		for (var i=0; i<this.widgets.length; i++) {
			oWidget = this.widgets[i];
			oWidget[offset_var] = 'this.parent._getWidgetOffset(' + i + ')';
	
			if (oWidget.length == '-1') {
				oWidget[length_var] = 'this.parent._calcWidgetLength()';
			}
			else
				oWidget[length_var] = oWidget.length;
		}
	}
	Widget.prototype.redraw(bForceAll, this);
}

Box.prototype._getWidgetOffset=function(iPane) {
	var offset = 0;
	if (this.orientation=='h') {
		for (var i=0; i<iPane; i++)
			offset += this.widgets[i].getWidth(true) + this.spacing;
	}
	else {
		for (var i=0; i<iPane; i++)
			offset += this.widgets[i].getHeight(true) + this.spacing;
	}
	return(offset);
}

Box.prototype._calcWidgetLength = function() {
	var tl = 0;
	var free_widgets = 0;
	for (var i=0; i<this.widgets.length; i++) {
		if (this.orientation == 'h') {
			if (this.widgets[i].length != '-1')
				tl += this.widgets[i].getWidth(true);
			else
				free_widgets += 1;
		}
		else {
			if (this.widgets[i].length != '-1')
				tl += this.widgets[i].getHeight(true);
			else
				free_widgets += 1;
		}
	}
	var l = (this.orientation=='h')?this.getWidth():this.getHeight();
	
	var nl = (l - tl - ((this.widgets.length-1)*this.spacing)) / free_widgets;
	return(nl>0?nl:0);
}

function BoxWidget__destroy() {
	var oBox = this.parent;
	for (var idx=0; idx < oBox.widgets.length; idx++) {
		 if (oBox.widget[idx] == this)
		 	break;
	}
	if (this.length == '-1' && oBox.widgets.length > 1) {
		if (idx == 0)
			oBox.widgets[1].length = '-1';
		else
			oBox.widgets[idx-1].length = '-1';
	}
	Widget.prototype.destroy(this);
	oBox.redraw(true);
}