/************************
Splitter
************************/
function Splitter(params) {
	params = params || {};
	params.overflow = 'hidden';
	this.base = Widget;
	this.base(params);
	this.div.className = 'splitter';
	
	this.orientation = params.orientation || "v";
	var iSpacing = params.spacing || 4;
	this.spacing = parseInt(iSpacing);
	this.panes = [];
	this._handles = [];
}

QuiX.constructors['splitter'] = Splitter;
Splitter.prototype = new Widget;

Splitter.prototype.addPane = function(params) {
	var ow2;

	params.overflow = params.overflow || 'hidden';
	var on_off = (params.onoff=='true' || params.onoff==true)?true:false;

	ow2 = new Widget(params);
	
	ow2.onoff = on_off;
	ow2.length = params.length || '-1';
	ow2.destroy = SplitterPane__destroy;

	if (this.orientation=="v") {
		ow2.height = '100%';
		if (ow2.length!='-1')
			ow2.width = ow2.length;
	}
	else {
		ow2.width = '100%';
		if (ow2.length!='-1')
			ow2.height = ow2.length;
	}
	
	this.appendChild(ow2);
	
	ow2.div.className = 'pane';
	this.panes.push(ow2);
	
	return(ow2);
}

Splitter.prototype.redraw = function(bForceAll) {
	var oPane, onoff_w;
	
	var offset_var = (this.orientation=='v')?'left':'top';
	var length_var = (this.orientation=='v')?'width':'height';
	
	for (var i=0; i<this.panes.length; i++) {
		oPane = this.panes[i];
		oPane[offset_var] = 'this.parent._getPaneOffset(' + i + ')';

		if (oPane.length == '-1') {
			oPane[length_var] = 'this.parent._calcPaneLength()';
		}
		else
			oPane[length_var] = oPane.length;
	}

	if (bForceAll) {
		for (var i=0; i<this.panes.length; i++) {
			oPane = this.panes[i];
			if (oPane.onoff == true) {
				if (!this.getWidgetById('__onoff' + i)) {
					if (this.orientation == 'v') {
						oPane.addPaddingOffset('Right', 8);
						onoff_w = new FlatButton({
							id : '__onoff' + i,
							width : 8,
							height : 'this.parent.getHeight(true)',
							padding : '2,2,2,2',
							top : -this.getPadding()[2],
							left : 'this.parent._getPaneOffset(' + (i + 1) + ')-8',
							img : '__quix/images/on_off_left.gif',
							onclick : SplitterOnOff_click
						});
					}
					else {
						oPane.addPaddingOffset('Bottom', 8);
						onoff_w = new FlatButton({
							id : '__onoff' + i,
							width : 'this.parent.getWidth(true)',
							height : 8,
							padding : '2,2,2,2',
							top : 'this.parent._getPaneOffset(' + (i + 1) + ')-8',
							left : -this.getPadding()[0],
							img : '__quix/images/on_off_up.gif',
							imgalign : 'top',
							onclick : SplitterOnOff_click, 
							style : 'font-size:0px'
						});
					}
					onoff_w.attributes._paneIndex = i;
					this.appendChild(onoff_w);
				}
			}
			else {
				onoff_w = this.getWidgetById('__onoff' + i);
				if (onoff_w) {
					onoff_w.destroy();
					if (this.orientation == 'v')
						oPane.addPaddingOffset('Right', -8);
					else
						oPane.addPaddingOffset('Bottom', -8);
				}
			}
		}
		
		if (this._handles.length == 0 && this.spacing > 0) {
			//we need to create all the resizing handles
			for (i=1; i<this.panes.length; i++)
				this._addHandle();
		}
		for (i=0; i<this._handles.length; i++) {
			this._handles[i][length_var] = this.spacing;
			this._handles[i][offset_var] = 'this.parent._getPaneOffset(' + (i + 1) + ')-this.parent.spacing';
		}
	}
	Widget.prototype.redraw(bForceAll, this);
}

Splitter.prototype._addHandle = function() {
	if (this.orientation=="v") {
		handle = new Widget({
			width:this.spacing,
			height:"100%",
			border:1,
			overflow:'hidden'
		});
		handle.div.style.cursor = 'e-resize';
		handle.div.className = 'handleV';
	}
	else {
		handle = new Widget({
			width:"100%",
			height:this.spacing,
			border:1,
			overflow:'hidden'
		});
		handle.div.style.cursor = 'n-resize';
		handle.div.className = 'handleH';
	}
	this.appendChild(handle);
	this._handles.push(handle);
	handle.attachEvent('onmousedown', SplitterHandle__mousedown);
}

Splitter.prototype._getPaneOffset = function(iPane) {
	var offset = 0;
	if (this.orientation=="v") {
		for (var i=0; i<iPane; i++)
			offset += this.panes[i].getWidth(true) + this.spacing;
	}
	else {
		for (var i=0; i<iPane; i++)
			offset += this.panes[i].getHeight(true) + this.spacing;
	}
	return(offset);
}

Splitter.prototype._calcPaneLength = function() {
	var tl = 0;
	var free_panes = 0;
	for (var i=0; i<this.panes.length; i++) {
		if (this.orientation == "v") {
			if (this.panes[i].length != '-1')
				tl += this.panes[i].getWidth(true);
			else
				free_panes += 1;
		}
		else {
			if (this.panes[i].length != '-1')
				tl += this.panes[i].getHeight(true);
			else
				free_panes += 1;
		}
	}
	var l = (this.orientation=="v")?this.getWidth():this.getHeight();
	
	var nl = (l - tl - ((this.panes.length-1)*this.spacing)) / free_panes;
	return(nl>0?nl:0);
}

Splitter.prototype._handleMoving = function(evt, iHandle) {
	if (this.orientation=="v") {
		offsetX = evt.clientX - QuiX.startX;
		if (offsetX>-this.panes[iHandle].getWidth(true) && offsetX<this.panes[iHandle+1].getWidth(true))
			QuiX.tmpWidget.moveTo(this._handles[iHandle]._calcLeft() + offsetX,
						this._handles[iHandle]._calcTop());
	}
	else {
		offsetY = evt.clientY - QuiX.startY;
		if (offsetY>-this.panes[iHandle].getHeight(true) && offsetY<this.panes[iHandle+1].getHeight(true))
			QuiX.tmpWidget.moveTo(this._handles[iHandle]._calcLeft(),
						this._handles[iHandle]._calcTop() + offsetY);
	}
}

Splitter.prototype._endMoveHandle = function(evt, iHandle) {
	var nl;
	var total_size;
	var force_resize = false;
	var offsetX = evt.clientX - QuiX.startX;
	var offsetY = evt.clientY - QuiX.startY;
	if (this.orientation=="v") {
		offsetX = (offsetX>this.panes[iHandle+1].getWidth(true))?this.panes[iHandle+1].getWidth(true):offsetX;
		offsetX = (offsetX<-this.panes[iHandle].getWidth(true))?-this.panes[iHandle].getWidth(true):offsetX;

		nl = this.panes[iHandle].getWidth(true) + offsetX;
		this.panes[iHandle].length = nl;

		if (this.panes[iHandle+1].length != '-1') {
			nl = this.panes[iHandle+1].getWidth(true) - offsetX;
			this.panes[iHandle + 1].length = nl;
		}
	}
	else {
		offsetY = (offsetY>this.panes[iHandle+1].getHeight(true))?this.panes[iHandle+1].getHeight(true):offsetY;
		offsetY = (offsetY<-this.panes[iHandle].getHeight(true))?-this.panes[iHandle].getHeight(true):offsetY;

		nl = this.panes[iHandle].getHeight(true) + offsetY;
		this.panes[iHandle].length = nl;

		if (this.panes[iHandle+1].length != '-1') {
			nl = this.panes[iHandle+1].getHeight(true) - offsetY;
			this.panes[iHandle+1].length = nl;
		}
	}
	
	QuiX.tmpWidget.destroy();
	this.redraw();
	this.detachEvent('onmouseup');
	this.detachEvent('onmousemove');
	this.div.style.cursor = '';
}

function SplitterPane__destroy() {
	var oSplitter = this.parent;
	for (var idx=0; idx < oSplitter.panes.length; idx++) {
		 if (oSplitter.panes[idx] == this)
		 	break;
	}
	if (this.length == '-1' && oSplitter.panes.length > 1) {
		if (idx == 0)
			oSplitter.panes[1].length = '-1';
		else
			oSplitter.panes[idx-1].length = '-1';
	}
	//if (oSplitter.interactive && oSplitter.panes.length > 1) {
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
	QuiX.startX = evt.clientX;
	QuiX.startY = evt.clientY;
	
	for (var idx=0; idx < w.parent._handles.length; idx++) {
		 if (w.parent._handles[idx] == w)
		 	break;
	}

	QuiX.tmpWidget = QuiX.createOutline(w);

	w.parent.attachEvent('onmouseup', function(evt, w){w._endMoveHandle(evt, idx)});
	w.parent.attachEvent('onmousemove', function(evt, w){w._handleMoving(evt, idx)});
	w.parent.div.style.cursor = (w.parent.orientation=="v")?'e-resize':'n-resize';
}

function SplitterOnOff_click(evt, w) {
	var dir, padding;
	var oSplitter = w.parent;
	var pane_index = w.attributes._paneIndex;
	var p = oSplitter.panes[pane_index];
	var prop2 = (oSplitter.orientation=='v')?'left':'top';
	var padding_offset = (oSplitter.orientation=='v')?'Left':'Top';
	if ( p.length!=0 ) {
		//collapse
		padding = p.getPadding();
		w.attributes._length = p.length;
		w.attributes._padding = padding;
		dir = (oSplitter.orientation=='v')?'right':'down';
		w.setImageURL('__quix/images/on_off_' + dir + '.gif');
		p.length = 0;
		p.setPadding([0,0,0,0]);
		p.addPaddingOffset(padding_offset, 8);
		oSplitter.redraw();
	} else {
		//expand
		p.length = w.attributes._length;
		dir = (oSplitter.orientation=='v')?'left':'up';
		w.setImageURL('__quix/images/on_off_' + dir + '.gif');
		p.setPadding(w.attributes._padding);
		oSplitter.redraw();
	}
}