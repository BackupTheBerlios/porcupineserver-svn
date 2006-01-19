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
	this.interactive = (params.interactive=="true")?true:false;
	var iSpacing = params.spacing || 4;
	this.spacing = parseInt(iSpacing);
	this.panes = [];
	this.handles = [];
}

Splitter.prototype = new Widget;

Splitter.prototype.addPane = function(params) {
	var ow2, handle;
	var oSplitter = this;
	if (params.length=="-1")
		params.length = function(){return(oSplitter._calcPaneLength())};
	params.overflow = params.overflow || 'hidden';
	var on_off = (params.onoff=='true')?true:false;
	var iPane = this.panes.length;

	if (iPane>0 && this.interactive) {
		if (this.orientation=="v") {
			handle = new Widget(
				{
					left:function(){return(oSplitter._getPaneOffset(iPane)-oSplitter.spacing)},
					width:this.spacing,height:"100%",border:1,overflow:'hidden'
				});
			handle.div.style.cursor = 'e-resize';
			handle.div.className = 'handleV';
		}
		else {
			handle = new Widget(
				{
					top:function(){return(oSplitter._getPaneOffset(iPane)-oSplitter.spacing)},
					width:"100%",height:this.spacing,border:1,overflow:'hidden'
				});
			handle.div.style.cursor = 'n-resize';
			handle.div.className = 'handleH';
		}
		this.appendChild(handle);
		this.handles.push(handle);
		handle.attachEvent('onmousedown', function(evt){oSplitter._moveHandle(evt, iPane-1)});
	}
	
	function onoff(evt ,w) {
		var dir, padding;
		var p = w.parent;
		var prop = (oSplitter.orientation=='v')?'width':'height';
		var prop2 = (oSplitter.orientation=='v')?'left':'top';
		var padding_offset = (oSplitter.orientation=='v')?0:2;
		if (p[prop]!=8) {
			padding = p.getPadding();
			w.attributes.length = p[prop];
			w.attributes.padding = padding[padding_offset + 1];
			dir = (oSplitter.orientation=='v')?'right':'down';
			w.setImageURL('images/on_off_' + dir + '.gif');
			p[prop] = 8;
			padding[padding_offset + 1] = 0;
			padding[padding_offset] += 8;
			p.setPadding(padding);
			w[prop2] = -padding[padding_offset];
			oSplitter.redraw();
		} else {
			p[prop] = w.attributes.length;
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

	if (this.orientation=="v") {
		ow2 = new Widget(
			{
				left:function(){return(oSplitter._getPaneOffset(iPane))},
				width:params.length,height:"100%",overflow:params.overflow,
				bgcolor:params.bgcolor,
				border:params.border,style:params.style,
				padding:params.padding,id:params.id
			});
		this.appendChild(ow2);
		if (on_off && !this.interactive) {
			padding = ow2.getPadding();
			padding[1] += 8;
			ow2.setPadding(padding);
			onoff_w = new FlatButton (
				{
					width:8, height:'this.parent.getHeight(true)', padding:'2,2,2,2',
					top:-ow2.getPadding()[2], left:'this.parent.getWidth(true)-8',
					img:'images/on_off_left.gif', onclick: onoff
				});
			ow2.appendChild(onoff_w);
		}
	} else {
		ow2 = new Widget(
			{
				top:function(){return(oSplitter._getPaneOffset(iPane))},
				width:"100%",height:params.length,overflow:params.overflow,
				bgcolor:params.bgcolor,
				border:params.border,style:params.style,
				padding:params.padding,id:params.id
			});
		this.appendChild(ow2);
		if (on_off && !this.interactive) {
			padding = ow2.getPadding();
			padding[3] += 8;
			ow2.setPadding(padding);
			onoff_w = new FlatButton (
				{
					width:'this.parent.getWidth(true)', height:8, padding:'2,2,2,2',
					top:'this.parent.getHeight(true)-8', left:-ow2.getPadding()[0],
					img:'images/on_off_up.gif', imgalign:'top', onclick: onoff
				});
			ow2.appendChild(onoff_w);
		}
	}
	
	ow2.div.className = 'pane';
	this.panes.push(ow2);
	this.redraw();
	return(ow2);
}

Splitter.prototype._getPaneOffset=function(iPane) {
	var offset = 0;
	if (this.orientation=="v") {
		for (var i=0; i<iPane; i++) offset += this.panes[i].getWidth(true) + this.spacing;
	}
	else {
		for (var i=0; i<iPane; i++) offset += this.panes[i].getHeight(true) + this.spacing;
	}
	return(offset);
}

Splitter.prototype._calcPaneLength = function() {
	var tl = 0;
	for (var i=0; i<this.panes.length; i++) {
		if (this.orientation=="v") {
			if (typeof(this.panes[i].width)!='function') tl+=this.panes[i].getWidth(true);
		}
		else {
			if (typeof(this.panes[i].height)!='function') tl+=this.panes[i].getHeight(true);
		}
	}
	var l = (this.orientation=="v")?this.getWidth():this.getHeight();
	var nl = l-tl-((this.panes.length-1)*this.spacing);
	return(nl>0?nl:0);
}

Splitter.prototype._moveHandle = function(evt, iHandle) {
	var oWidget = this;
	QuiX.startX = evt.clientX;
	QuiX.startY = evt.clientY;

	QuiX.tmpWidget = QuiX.createOutline(this.handles[iHandle]);

	this.attachEvent('onmouseup', function(evt){oWidget._endMoveHandle(evt, iHandle)});
	this.attachEvent('onmousemove',function(evt){oWidget._handleMoving(evt, iHandle)})
	this.div.style.cursor = (this.orientation=="v")?'e-resize':'n-resize';
}

Splitter.prototype._handleMoving = function(evt, iHandle) {
	if (this.orientation=="v") {
		offsetX = evt.clientX - QuiX.startX;
		if (offsetX>-this.panes[iHandle].getWidth(true) && offsetX<this.panes[iHandle+1].getWidth(true))
			QuiX.tmpWidget.moveTo(this.handles[iHandle]._calcLeft() + offsetX,
						this.handles[iHandle]._calcTop());
	}
	else {
		offsetY = evt.clientY - QuiX.startY;
		if (offsetY>-this.panes[iHandle].getHeight(true) && offsetY<this.panes[iHandle+1].getHeight(true))
			QuiX.tmpWidget.moveTo(this.handles[iHandle]._calcLeft(),
						this.handles[iHandle]._calcTop() + offsetY);
	}
}

Splitter.prototype._endMoveHandle = function(evt, iHandle) {
	var nl;
	var offsetX = evt.clientX - QuiX.startX;
	var offsetY = evt.clientY - QuiX.startY;
	if (this.orientation=="v") {
		offsetX = (offsetX>this.panes[iHandle+1].getWidth(true))?this.panes[iHandle+1].getWidth(true):offsetX;
		offsetX = (offsetX<-this.panes[iHandle].getWidth(true))?-this.panes[iHandle].getWidth(true):offsetX;
		if (typeof(this.panes[iHandle].width)!='function') {
			nl = this.panes[iHandle].getWidth(true)+offsetX;
			this.panes[iHandle].width = Math.round((nl/this.getWidth())*100) + '%';
		}
		if (typeof(this.panes[iHandle+1].width)!='function') {
			 nl = this.panes[iHandle+1].getWidth(true)-offsetX;
			 this.panes[iHandle+1].width = Math.round((nl/this.getWidth())*100) + '%';
		}
	}
	else {
		offsetY = (offsetY>this.panes[iHandle+1].getHeight(true))?this.panes[iHandle+1].getHeight(true):offsetY;
		offsetY = (offsetY<-this.panes[iHandle].getHeight(true))?-this.panes[iHandle].getHeight(true):offsetY;
		if (typeof(this.panes[iHandle].height)!='function') {
			nl = this.panes[iHandle].getHeight(true)+offsetY;
			this.panes[iHandle].height = Math.round((nl/this.getHeight())*100) + '%';
		}
		if (typeof(this.panes[iHandle+1].height)!='function') {
			nl = this.panes[iHandle+1].getHeight(true)-offsetY;
			this.panes[iHandle+1].height = Math.round((nl/this.getHeight())*100) + '%';
		}
	}
	QuiX.tmpWidget.destroy();
	this.redraw();
	this.detachEvent('onmouseup');
	this.detachEvent('onmousemove');
	this.div.style.cursor = '';
}