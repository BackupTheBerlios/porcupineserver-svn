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
	this.interactive = (params.interactive=="true"||params.interactive==true)?true:false;
	var iSpacing = params.spacing || 4;
	this.spacing = parseInt(iSpacing);
	this.panes = [];
	this._handles = [];
}

Splitter.prototype = new Widget;

Splitter.prototype.addPane = function(params) {
	var ow2;
	var oSplitter = this;

	params.overflow = params.overflow || 'hidden';
	var on_off = (params.onoff=='true' || params.onoff==true)?true:false;

	if (this.panes.length>0 && this.interactive) {
		this._addHandle();
	}
	
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
	this.redraw(true);
	
	return(ow2);
}

Splitter.prototype.redraw = function(bForceAll) {
	var oPane, onoff_w;
	var free_panes = 0;
	
	var offset_var = (this.orientation=='v')?'left':'top';
	var length_var = (this.orientation=='v')?'width':'height';
	
	for (var i=0; i<this.panes.length; i++) {
		oPane = this.panes[i];
		oPane[offset_var] = 'this.parent._getPaneOffset(' + i + ')';

		if (oPane.length == '-1') {
			oPane[length_var] = 'this.parent._calcPaneLength()';
			free_panes +=1
		}
		else
			oPane[length_var] = oPane.length;
	}

	if (bForceAll) {
		for (var i=0; i<this.panes.length; i++) {
			oPane = this.panes[i];
			if (oPane.onoff == true) {
				if (!oPane.getWidgetById('__onoff')) {
					if (this.orientation == 'v') {
						oPane.addPaddingOffset('Right', 8);
						onoff_w = new FlatButton({
							id : '__onoff',
							width : 8,
							height : 'this.parent.getHeight(true)',
							padding : '2,2,2,2',
							top : -oPane.getPadding()[2],
							left : 'this.parent.getWidth(true)-8',
							img : 'images/on_off_left.gif',
							onclick : SplitterOnOff_click
						});
					}
					else {
						oPane.addPaddingOffset('Bottom', 8);
						onoff_w = new FlatButton({
							id : '__onoff',
							width : 'this.parent.getWidth(true)',
							height : 8,
							padding : '2,2,2,2',
							top : 'this.parent.getHeight(true)-8',
							left : -oPane.getPadding()[0],
							img : 'images/on_off_up.gif',
							imgalign : 'top',
							onclick : SplitterOnOff_click, 
							style : 'font-size:0px'
						});
					}
					oPane.appendChild(onoff_w);
				}
			}
			else {
				onoff_w = oPane.getWidgetById('__onoff');
				if (onoff_w) {
					onoff_w.destroy();
					if (this.orientation == 'v')
						oPane.addPaddingOffset('Right', -8);
					else
						oPane.addPaddingOffset('Bottom', -8);
				}
			}
		}
		
		if (this.interactive) {
			if (this._handles.length == 0) {
				//we need to create all the resizing handles
				for (i=1; i<this.panes.length; i++)
					this._addHandle();
			}
			for (i=0; i<this._handles.length; i++) {
				this._handles[i][length_var] = this.spacing;
				this._handles[i][offset_var] = 'this.parent._getPaneOffset(' + (i + 1) + ')-this.parent.spacing';
			}
		}
		else {
			//remove all handles
			while (this._handles.length > 0) {
				this._handles[0].destroy();
				this._handles.splice(0, 1)
			}
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
	if (oSplitter.interactive && oSplitter.panes.length > 1) {
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
	var p = w.parent;
	var oSplitter = p.parent;
	var prop2 = (oSplitter.orientation=='v')?'left':'top';
	var padding_offset = (oSplitter.orientation=='v')?0:2;
	if ( p.length!=8 ) {
		//collapse
		padding = p.getPadding();
		w.attributes.length = p.length;
		w.attributes.padding = padding[padding_offset + 1];
		dir = (oSplitter.orientation=='v')?'right':'down';
		w.setImageURL('images/on_off_' + dir + '.gif');
		p.length = 8;
		padding[padding_offset + 1] = 0;
		padding[padding_offset] += 8;
		p.setPadding(padding);
		w[prop2] = -padding[padding_offset];
		oSplitter.redraw();
	} else {
		//expand
		p.length = w.attributes.length;
		w[prop2] = (oSplitter.orientation=='v')?'this.parent.getWidth(true)-8':'this.parent.getHeight(true)-8';
		dir = (oSplitter.orientation=='v')?'left':'up';
		w.setImageURL('images/on_off_' + dir + '.gif');
		padding = p.getPadding();
		padding[padding_offset + 1] = w.attributes.padding;
		padding[padding_offset] -= 8;
		p.setPadding(padding);
		oSplitter.redraw();
	}
}