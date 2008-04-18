/************************
Splitter
************************/
function Splitter(params) {
	params = params || {};
	var spacing = parseInt(params.spacing) || 6;
	params.overflow = 'hidden';
	params.spacing = 0;
	this.base = Box;
	this.base(params);
	
	this._spacing = spacing;
	this.div.className = 'splitter';
	this.panes = [];
	this._handles = [];
}

QuiX.constructors['splitter'] = Splitter;
Splitter.prototype = new Box;

Splitter.prototype.appendChild = function(w) {
	if (this.panes.length > 0) {
		this._addHandle();
	}
	Box.prototype.appendChild(w, this);
	w.destroy = SplitterPane__destroy;
	this.panes.push(w);
}

Splitter.prototype._addHandle = function() {
	var handle;
	if (this.orientation == "h") {
		handle = new Widget({
			width : this._spacing,
			border : 1,
			overflow :'hidden'
		});
		handle.div.style.cursor = 'e-resize';
		handle.div.className = 'handleV';
	}
	else {
		handle = new Widget({
			height : this._spacing,
			border : 1,
			overflow :'hidden'
		});
		handle.div.style.cursor = 'n-resize';
		handle.div.className = 'handleH';
	}
	Box.prototype.appendChild(handle, this);
	handle.redraw();
	this._handles.push(handle);
	handle.attachEvent('onmousedown', SplitterHandle__mousedown);
	handle.attachEvent('ondblclick', SplitterHandle__dblclick);
}

Splitter.prototype._handleMoving = function(evt, iHandle) {
	var length_var = (this.orientation == 'h')?'width':'height';
	var length_func = (this.orientation == 'h')?'getWidth':'getHeight';
	var offset_var = (this.orientation == 'h')?'X':'Y';
	var min_length_var = (this.orientation == 'h')?'_calcMinWidth':'_calcMinHeight';

	var offset = evt['client' + offset_var] - QuiX['start' + offset_var];
	var pane1, pane2;
	if (this.panes[iHandle + 1].attributes._collapse) {
		pane1 = this.panes[iHandle + 1];
		pane2 = this.panes[iHandle];
		offset = -offset;
	}
	else {
		pane1 = this.panes[iHandle];
		pane2 = this.panes[iHandle + 1];
	}
	var length1 = pane1[length_func](true);
	var length2 = pane2[length_func](true);
	var limit1 = pane1[length_func]();
	var limit2 = pane2[length_func]();
	var min1 = pane1[min_length_var]();
	var min2 = pane2[min_length_var]();

	if (-offset < limit1 && offset < limit2) {
		pane1[length_var] = Math.max(length1 + offset, min1);
		if (pane2[length_var] != 'this.parent._calcWidgetLength()')
			pane2[length_var] = Math.max(length2 - offset, min2);
		this.redraw();
		if (length1 + offset >= min1 && length2 - offset >= min2)
			QuiX['start' + offset_var] = evt['client' + offset_var];
		else
			QuiX['start' + offset_var] = pane1.getScreenLeft() + length1;
	}
}

Splitter.prototype._endMoveHandle = function(evt, iHandle) {
	this.detachEvent('onmouseup');
	this.detachEvent('onmousemove');
	this.div.style.cursor = '';
	QuiX.attachFrames(this);
	QuiX.dragging = false;
}

function SplitterPane__destroy() {
	var oSplitter = this.parent;
	var length_var = (oSplitter.orientation == 'h')?'width':'height';
	for (var idx=0; idx < oSplitter.panes.length; idx++) {
		 if (oSplitter.panes[idx] == this)
		 	break;
	}
	if (this[length_var] == 'this.parent._calcWidgetLength()' &&
			oSplitter.panes.length > 1) {
		if (idx == 0)
			oSplitter.panes[1][length_var] = '-1';
		else
			oSplitter.panes[idx-1][length_var] = '-1';
	}
	if (oSplitter.panes.length > 1) {
		if (idx == 0) {
			oSplitter._handles[0].destroy();
			oSplitter._handles.splice(0, 1);			
		}
		else {
			oSplitter._handles[idx-1].destroy();
			oSplitter._handles.splice(idx-1, 1);
		}
	}
	Widget.prototype.destroy(this);
	oSplitter.panes.splice(idx, 1);
	oSplitter.redraw(true);
}

function SplitterHandle__mousedown(evt, w) {
	if (!w._isCollapsed) {
		var splitter = w.parent;
		QuiX.startX = evt.clientX;
		QuiX.startY = evt.clientY;
		QuiX.cancelDefault(evt);
		QuiX.dragging = true;
		QuiX.detachFrames(splitter);
		for (var idx=0; idx < splitter._handles.length; idx++) {
			 if (splitter._handles[idx] == w)
			 	break;
		}
		splitter.attachEvent('onmouseup',
			function(evt, w){w._endMoveHandle(evt, idx)});
		splitter.attachEvent('onmousemove',
			function(evt, w){w._handleMoving(evt, idx)});
		splitter.div.style.cursor = (w.parent.orientation == "h")?'e-resize':'n-resize';
	}
}

function SplitterHandle__dblclick(evt, w) {
	var splitter = w.parent;
	for (var idx=0; idx < splitter._handles.length; idx++) {
		 if (splitter._handles[idx] == w)
		 	break;
	}
	if (splitter.panes[idx+1].attributes._collapse) {
		idx = idx + 1;		
	}
	var pane = splitter.panes[idx];
	if (pane.isHidden()) {
		w._isCollapsed = false;
		w.div.style.cursor = (splitter.orientation == "h")?'e-resize':'n-resize';
		pane.show();
	}
	else {
		w._isCollapsed = true;
		w.div.style.cursor = 'default';
		pane.hide();
	}
	splitter.redraw();
}
