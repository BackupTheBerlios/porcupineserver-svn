/************************
Box layout
************************/

function Box(params) {
	params = params || {};
	params.overflow = params.overflow || 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'box';
	this.orientation = params.orientation || 'h';
	var spacing = (typeof params.spacing == 'undefined')? 2:params.spacing;
	this.spacing = parseInt(spacing);
	this.childrenAlign = params.childrenalign;
}

QuiX.constructors['box'] = Box;
Box.prototype = new Widget;

Box.prototype.appendChild = function(w) {
	w.destroy = BoxWidget__destroy;
	if (this.orientation == 'h')
		w.height = w.height || '100%';
	else
		w.width = w.width || '100%';
	Widget.prototype.appendChild(w, this);
}

Box.prototype.redraw = function(bForceAll) {
	if (bForceAll) {
		var oWidget;
		var offset_var = (this.orientation=='h')?'left':'top';
		var center_var = (this.orientation=='h')?'top':'left';
		var length_var = (this.orientation=='h')?'width':'height';
		var width_var = (this.orientation=='h')?'height':'width';
		
		for (var i=0; i<this.widgets.length; i++) {
			oWidget = this.widgets[i];
			oWidget[offset_var] = 'this.parent._getWidgetOffset(' + i + ')';
			oWidget[center_var] = 'this.parent._getWidgetPos(' + i + ')';

			if (oWidget[length_var] == null || oWidget[length_var] == '-1')
				oWidget[length_var] = 'this.parent._calcWidgetLength()';
			if (oWidget[width_var] == '-1')
				oWidget[width_var] = 'this.parent._calcWidgetWidth()';
		}
	}
	Widget.prototype.redraw(bForceAll, this);
}

Box.prototype._getWidgetPos = function(iPane) {
	var oWidget = this.widgets[iPane];
	var boxalign =  oWidget.boxAlign || this.childrenAlign;
	var w1 = (this.orientation=='h')?this.getHeight():this.getWidth();
	var w2 = (this.orientation=='h')?oWidget.getHeight(true):oWidget.getWidth(true);
	switch (boxalign) {
		case 'center':
			return (w1 - w2)/2;
		case 'right':
		case 'bottom':
			return (w1 - w2);
		default: 	
			return 0;
	}
}

Box.prototype._getWidgetOffset=function(iPane) {
	var offset = 0;
	if (iPane > 0)
	{
		var i = iPane - 1;
		var ow = this.widgets[i];
		while (ow.isHidden() && i >= 0) {
			ow = this.widgets[i];
			i -= 1;
		}
		if (this.orientation=='h')
			offset = ow.getLeft() + ow.getWidth(true) + this.spacing;
		else
			offset = ow.getTop() + ow.getHeight(true) + this.spacing;
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

Box.prototype._calcWidgetWidth = function() {
	var w;
	var tl = 0;
	var min_var = (this.orientation=='h')?'_calcMinHeight':'_calcMinWidth';
	
	for (var i=0; i<this.widgets.length; i++) {
		w = this.widgets[i];
		if (w.isHidden()) continue;
		var min = w[min_var]();
		tl = Math.max(tl,min);
	}
	return tl;
}

function BoxWidget__destroy() {
	var oBox = this.parent;
	var length_var = (oBox.orientation=='h')?'width':'height';
	
	for (var idx=0; idx < oBox.widgets.length; idx++) {
		 if (oBox.widgets[idx] == this)
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

function FlowBox(params) {
	params = params || {};
	params.overflow = params.overflow || 'auto';
	this.base = Widget;
	this.base(params);
	this.div.className = 'box';
	var iSpacing = params.spacing || 8;
	this.spacing = parseInt(iSpacing);
	this.valign = params.valign || 'center';
}

QuiX.constructors['flowbox'] = FlowBox;
FlowBox.prototype = new Widget;

FlowBox.prototype.appendChild = function(w) {
	w.destroy = FlowBoxWidget__destroy;
	Widget.prototype.appendChild(w, this);
	this._rearrange(this.widgets.length - 1);	
}

FlowBox.prototype.redraw = function(bForceAll) {
	Widget.prototype.redraw(bForceAll, this);
	this._rearrange(0);
}

FlowBox.prototype._rearrange = function(iStart) {
	var x = 0;
	var y = 0;
	var rowHeight = 0;
	var iWidth = this.getWidth();
	
	if (iStart > 0) {
		x = this.widgets[iStart - 1].left +
			this.widgets[iStart-1].width +
			this.spacing;
		y = this.widgets[iStart - 1].top;
		rowHeight = this._calcRowHeight(iStart);
	}
	
	for (var i=iStart; i<this.widgets.length; i++) {
		with (this.widgets[i]) {
			if (x + width + this.spacing > iWidth && x != 0) {
				x = 0;
				y += rowHeight + this.spacing;
				rowHeight = 0;
			}
			moveTo(x, y);
			x += width + this.spacing;
			rowHeight = Math.max(rowHeight, height);
		}
	}
}

FlowBox.prototype._calcRowHeight = function(iStart) {
	var rowHeight = 0;
	var iCount = 1
	var prev = this.widgets[iStart - iCount];
	if (prev.left !=0) {
		do {
			rowHeight = Math.max(rowHeight, prev.height);
			iCount += 1;
			prev = this.widgets[iStart - iCount];
		} while (prev.left != 0)
	}
	return rowHeight;
}

function FlowBoxWidget__destroy() {
	var oFlowBox = this.parent;
	for (var i=0; i<oFlowBox.widgets.length; i++) {
		if (oFlowBox.widgets[i] == this)
			break;
	}
	Widget.prototype.destroy(this);
	if (i < oFlowBox.widgets.length)
		oFlowBox._rearrange(i);
}
