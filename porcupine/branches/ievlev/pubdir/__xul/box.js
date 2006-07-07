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
	if (this.orientation == 'h')
		w.height = w.height || '100%';
	else
		w.width = w.width || '100%';
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
	
			if (oWidget[length_var] == null || oWidget[length_var] == '-1')
				oWidget[length_var] = 'this.parent._calcWidgetLength()';
		}
	}
	Widget.prototype.redraw(bForceAll, this);
}

Box.prototype._getWidgetOffset=function(iPane) {
	var offset = 0;
	if (this.orientation=='h') {
		for (var i=0; i<iPane; i++)
		{
			if (this.widgets[i].isHidden()) continue;
			offset += this.widgets[i].getWidth(true) + this.spacing;
		}
	}
	else {
		for (var i=0; i<iPane; i++)
		{
			if (this.widgets[i].isHidden()) continue;
			offset += this.widgets[i].getHeight(true) + this.spacing;
		}
	}
	return(offset);
}

Box.prototype._calcWidgetLength = function() {
	var tl = 0;
	var free_widgets = 0;
	var length_var = (this.orientation=='h')?'width':'height';
	
	for (var i=0; i<this.widgets.length; i++) {
		if (this.widgets[i].isHidden()) continue;
		if (this.widgets[i][length_var] != 'this.parent._calcWidgetLength()') {
			if (this.orientation=='h')
				tl += this.widgets[i]._calcWidth(true);
			else
				tl += this.widgets[i]._calcHeight(true);
		}
		else
			free_widgets += 1;
	}
	var l = (this.orientation=='h')?this.getWidth():this.getHeight();
	
	var nl = (l - tl - ((this.widgets.length-1)*this.spacing)) / free_widgets;
	return(nl>0?nl:0);
}

function BoxWidget__destroy() {
	var oBox = this.parent;
	var length_var = (oBox.orientation=='h')?'width':'height';
	
	for (var idx=0; idx < oBox.widgets.length; idx++) {
		 if (oBox.widget[idx] == this)
		 	break;
	}
	if (this[length_var] == '-1' && oBox.widgets.length > 1) {
		if (idx == 0)
			oBox.widgets[1][length_var] = '-1';
		else
			oBox.widgets[idx-1][length_var] = '-1';
	}
	Widget.prototype.destroy(this);
	oBox.redraw(true);
}