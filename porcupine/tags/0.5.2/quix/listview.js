/************************
List View
************************/

function ListView(params) {
	params = params || {};
	params.bgcolor = params.bgcolor || 'white';
	params.overflow = 'hidden';
	
	var dragable = (params.dragable=='true' || params.dragable==true);
	delete params.dragable;
	
	this.base = Widget;
	this.base(params);
	this.div.className = 'listview';
	this.cellPadding = parseInt(params.cellpadding) || 4;
	this.cellBorder = parseInt(params.cellborder) || 0;
	this.multiple = (params.multiple==true || params.multiple=="true");
	this.nullText = params.nulltext || '&nbsp;';
	this.dateFormat = params.dateformat || 'ddd dd/mmm/yyyy time';
	this.trueImg = params.trueimg || '__quix/images/check16.gif';
	this.sortfunc = QuiX.getEventListener(params.sortfunc);
	this.altColors = (params.altcolors || ',').split(',');
	this.highlightColors =
		(params.highlightcolors || 'white,#6699FF').split(',');
	this.rowHeight = parseInt(params.rowheight);

	this.hasSelector = false;
	this.selection = [];
	this.dataSet = [];
	
	this._orderBy = null;
	this._sortOrder = null;
	this._sortimg = null;
	
	this._dragable = dragable;
}

QuiX.constructors['listview'] = ListView;
ListView.prototype = new Widget;

ListView.prototype.customEvents =
	Widget.prototype.customEvents.concat(['onselect', 'onrowprerender',
										'onrendercomplete']);

ListView.prototype.cellThreshold = 2000;

ListView.prototype._registerHandler = function(eventType, handler, isCustom) {
	var wrapper;
	if (handler)
		switch (eventType) {
			case "onclick":
			case "ondblclick":
				//if it not wrapped wrap it...
				if(handler && handler.toString().lastIndexOf(
						'return handler(evt || event, w)')==-1)
					wrapper = function(evt, w) {
						return ListView__onclick(evt, w, handler)
					};
				break;
		}
	wrapper = wrapper || handler;
	Widget.prototype._registerHandler(eventType, wrapper, isCustom, this);
}

ListView.prototype.addHeader = function(params, w) {
	var oListview = w || this;
	params.width = '100%';
	params.height = (!params.height || params.height<22)?
					22:parseInt(params.height);
	params.overflow = 'hidden';
	
	oListview.header = new Widget(params);
	oListview.appendChild(oListview.header);
	oListview.header.div.className = 'listheader';
	oListview.header.div.innerHTML =
		'<table cellspacing="0" width="100%" height="100%"><tr>' +
		'<td class="column filler">&nbsp;</td><td width="32">&nbsp;</td></tr></table>';
		
	var oRow = oListview.header.div.firstChild.rows[0];
	oListview.columns = oRow.cells;
	oRow.ondblclick = QuiX.stopPropag;
	
	if (oListview.hasSelector) {
		var selector = oListview._getSelector();
		oRow.insertBefore(selector, oRow.lastChild.previousSibling);
		oListview._deadCells = 1;
	} else
		oListview._deadCells = 0;
	
	var ltop, lho;
	if (oListview.header.isHidden()) {
		ltop = 0;
		lho = 0;
	}
	else {
		ltop = oListview.header._calcHeight(true);
		lho = parseInt(params.height) + 1;
	}

	var list = new Widget({
		top : ltop,
		width : 'this.parent.getWidth()-1',
		height : 'this.parent.getHeight()-' + lho,
		dragable : oListview._dragable,
		overflow : 'auto'
	});
	list._startDrag = List__startDrag;
	oListview.appendChild(list);
	
	list.div.className = 'list';
	var oTable = ce('TABLE');
	oTable.cellSpacing = 0;
	oTable.cellPadding = oListview.cellPadding;
	if (QuiX.browser != 'ie') oTable.width = '100%';
	oTable.onmousedown = ListView__onmousedown;
	var tbody = ce('TBODY');
	oTable.appendChild(tbody);
	list.div.appendChild(oTable);

	list.attachEvent('onscroll', ListView__onscroll);
	oListview.list = list.div.firstChild;
	return(oListview.header);
}

ListView.prototype.redraw = function(bForceAll) {
	var columns = this.columns;
	var header_width = this._calcWidth();
	var wdth;
	// resize proportional cells
	for (var i = this._deadCells; i<columns.length; i++) {
		if (columns[i].proportion) {
			wdth = (parseInt(header_width * columns[i].proportion) -
					2*this.cellPadding - 2) + 'px';
			columns[i].style.width = wdth;
			if (this.list.firstChild.rows.length > 0)
				this.list.rows[0].cells[i].style.width = wdth;
		}
	}
	Widget.prototype.redraw(bForceAll, this);
}

ListView.prototype._getSelector = function() {
	var s = ce('TD');
	s.className = 'column';
	s.style.width = '8px';
	s.innerHTML = '&nbsp;';
	return s;
}

ListView.prototype._selrow = function(r) {
	for (var i=0; i<this.columns.length-1; i++)
		if (this.columns[i].columnBgColor)
			r.cells[i].bgColor = '';
	r.style.color = this.highlightColors[0];
	r.style.backgroundColor = this.highlightColors[1];
	r.isSelected = true;
}

ListView.prototype._unselrow = function(r) {
	r.style.color = '';
	r.style.backgroundColor = this.altColors[r.rowIndex % 2];
	r.isSelected = false;
	for (var i=0; i<this.columns.length-1; i++)
		if (this.columns[i].columnBgColor)
			r.cells[i].bgColor = this.columns[i].columnBgColor;
}

ListView.prototype._selectline = function(evt, row) {
	if (row.isSelected && QuiX.getMouseButton(evt)==2) {
		return false;
	}
	var fire = this.multiple || !row.isSelected;
	if (!row.isSelected) {
		if (!this.multiple || !evt.shiftKey) this.clearSelection();
		this._selrow(row);
		this.selection.push(row.rowIndex);
	}
	else if (this.multiple && evt.shiftKey) {
		this._unselrow(row);
		this.selection.removeItem(row.rowIndex);
	}
	else {
		this.clearSelection();
		this._selrow(row);
		this.selection.push(row.rowIndex);
	}
	if (fire && this._customRegistry.onselect) {
		QuiX.getEventListener(this._customRegistry.onselect)(
			evt, this, this.dataSet[row.rowIndex]);
	}
}

ListView.prototype.select = function(i) {
	var tr = this.list.rows[i];
	if (!tr.isSelected) {
		this._selrow(this.list.rows[i]);
		if (!this.multiple)
			this.selection = [i];
		else
			this.selection.push(i);
	}
}

ListView.prototype.clearSelection = function() {
	var selRow;
	for (var i=0; i<this.selection.length; i++) {
		selRow = this.list.rows[this.selection[i]];
		this._unselrow(selRow);
	}
	this.selection = [];
}

ListView.prototype.removeSelected = function() {
	var selRow;
	this.selection.sort(function(a,b){
		return(a>b?-1:1)
	});
	for (var i=0; i<this.selection.length; i++) {
		this.dataSet.splice(this.selection[i], 1);
		this.list.deleteRow(this.selection[i]);
	}
	this.selection = [];
	this.refresh();
}

ListView.prototype.getSelection = function() {
	sel = [];
	for (var i=0; i<this.selection.length; i++)
		sel.push(this.dataSet[this.selection[i]]);
	if (sel.length==0)
		return null;
	else if (sel.length==1)
		return sel[0];
	else
		return sel;
}

ListView.prototype.addColumn = function(params, w) {
	var oListView = w || this;
	var oCol = ce('TD');
	var header_width, perc;
	
	oCol.className = 'column';
	oCol._isContainer = false;
	oCol.columnBgColor = params.bgcolor || '';
	oCol.style.padding = '0px ' + oListView.cellPadding + 'px';

	if (params.width) {
		if (params.width.slice(params.width.length-1) == '%')
			oCol.proportion = parseInt(params.width) / 100;
		else {
			var offset = (QuiX.browser == 'saf')?0:2*oListView.cellPadding + 2*oListView.cellBorder;
			oCol.style.width = (params.width - offset) + 'px';
		}
	}

	oCol.setCaption = ListColumn__setCaption;
	oCol.getCaption = ListColumn__getCaption;

	oCol.name = params.name;
	var sCaption = params.caption || '&nbsp;';
	oCol.setCaption(sCaption);
		
	oCol.columnType = params.type || 'str';
	if (params.xform) {
		oCol.xform = params.xform;
		oCol._xform = QuiX.getEventListener(oCol.xform);
	}
	
	oCol.sortable = (params.sortable=='false' || params.sortable==false)?
					false:true;
	if (oCol.sortable) {
		oCol.style.cursor = 'pointer';
		oCol.onclick = ListColumn__onclick;
	}
	
	var oHeaderRow = oListView.header.div.firstChild.rows[0];
	oHeaderRow.insertBefore(oCol, oHeaderRow.lastChild.previousSibling);
	
	if (oCol.columnType == 'bool')
		oCol.trueImg = params.trueimg || oListView.trueImg;
	else if (oCol.columnType == 'date')
		oCol.format = params.format || oListView.dateFormat;
		
	oCol.columnAlign = params.align || 'left';
	
	var resizer = new Widget({
		width : 6,
		height : oListView.header._calcHeight(),
		left : 'this.parent.parent._calcResizerOffset(this)',
		overflow : 'hidden'
	});
	oListView.header.appendChild(resizer);
	
	oCol.isResizable =
		(params.resizable=='false' || params.resizable==false)?false:true;
	if (oCol.isResizable) {
		var iColumn = oHeaderRow.cells.length - 2;
		resizer.div.className = 'resizer';
		resizer.attachEvent('onmousedown', function(evt) {
			oListView._moveResizer(evt, iColumn-1-oListView._deadCells);
			QuiX.cancelDefault(evt);
		});
	}
	return oCol;
}

ListView.prototype._calcResizerOffset = function(w) {
	var oHeader = this.header;
	var left = (this.hasSelector)?10:0;
	var offset = (QuiX.browser=='saf')?-2:2*this.cellPadding;
	var offset2 = (QuiX.browser=='saf')?0:this.cellBorder;
	var column_width;
	for (var i=this._deadCells; i<this.columns.length; i++) {
		column_width = parseInt(this.columns[i].style.width);
		left += column_width + offset;

		if (this.list.rows.length > 0)
			this.list.rows[0].cells[i].style.width =
				column_width - offset2 + 'px';

		if (oHeader.widgets[i - this._deadCells]==w) break;
	}
	left += (2*i);
	return left - 1;
}

ListView.prototype._moveResizer = function(evt, iResizer) {
	var oWidget = this;
	QuiX.cancelDefault(evt);
	QuiX.startX = evt.clientX;
	this.attachEvent('onmouseup', function(evt){
		oWidget._endMoveResizer(evt, iResizer)});
	this.attachEvent('onmousemove', function(evt){
		oWidget._resizerMoving(evt, iResizer)});
}

ListView.prototype._resizerMoving = function(evt, iResizer) {
	var nw, sx;
	var iColumn = iResizer + this._deadCells;
	var offsetX = evt.clientX - QuiX.startX;
	nw = parseInt(this.columns[iColumn].style.width) + offsetX;
	nw = (nw < 2*this.cellPadding)?2*this.cellPadding:nw;
	if (nw > 2*this.cellPadding) {
		this.columns[iColumn].style.width = nw + 'px';
		this.header.redraw();
		this.header.div.scrollLeft = this.widgets[1].div.scrollLeft;
		QuiX.startX = evt.clientX;
	}
}

ListView.prototype._endMoveResizer = function(evt, iResizer) {
	var iColumn = iResizer + this._deadCells;
	if (this.columns[iColumn].proportion)
		this.columns[iColumn].proportion = null;
	this.detachEvent('onmouseup');
	this.detachEvent('onmousemove');
}

ListView.prototype.getColumnByName = function(colName) {
	for (var i=0; i<this.columns.length; i++)
		if (this.columns[i].name == colName)
			return this.columns[i];
	return null;
}

ListView.prototype.sort = function(colName, order) {
	var column = this.getColumnByName(colName);
	if (this._sortimg) {
		QuiX.removeNode(this._sortimg);
		this._sortimg = null;
	}
	if (this.sortfunc)
		this.sortfunc(this, colName, order);
	else {
		// default sort behaviour
		this.dataSet.sortByAttribute(colName);
		if (order.toUpperCase()=='DESC')
			this.dataSet.reverse();
		this.refresh();
	}
	if (column) {
		this._sortimg = new Image;
		this._sortimg.src = (order.toUpperCase()=='ASC')?
							'__quix/images/asc8.gif':'__quix/images/desc8.gif';
		this._sortimg.align = 'absmiddle';
		column.appendChild(this._sortimg);
	}
	this._orderBy = colName;
	this._sortOrder = order.toUpperCase();
}

ListView.prototype._isSorted = function() {
	var field = this._orderBy;
	var order = this._sortOrder;
	for (var i=0; i<this.dataSet.length - 1; i++) {
		if (order == 'ASC') {
			if (this.dataSet[i][field] > this.dataSet[i+1][field])
				return false;
		}
		else {
			if (this.dataSet[i][field] < this.dataSet[i+1][field])
				return false;
		}
	}
	return true;
}

ListView.prototype.refresh = function(w) {
	var w = w || this;
	var tbody = w.list.tBodies[0];
	while(tbody.firstChild)
		tbody.removeChild(tbody.firstChild);
	w.selection = [];
	if (w._sortimg && !w._isSorted()) {
		QuiX.removeNode(w._sortimg);
		w._sortimg = null;
		w._orderBy = null;
		w._sortOrder = null;
	}
	if (w.dataSet.length * w.columns.length > w.cellThreshold) {
		if (w._timeout)
			window.clearTimeout(w._timeout);
		w._timeout = window.setTimeout(function(){w._refresh(0, 30)}, 0);
	}
	else
		w._refresh(0, w.dataSet.length);
}

ListView.prototype._refresh = function(start, step) {
	var oRow, oCell, selector, oFiller;
	var value, columnWidth, offset;
	var rowHeight, offset;
	var w = this;
	var tbody = w.list.tBodies[0];
	var rowBgColor;
	var listBgColor = w.getBgColor();
	if (w.rowHeight) {
		if (QuiX.browser == 'ie')
			offset = 2 * w.cellPadding;
		else
			offset = 0;
		rowHeight = (w.rowHeight - offset) + 'px';
	}
	var cellPadding = '4px ' + (w.cellPadding + 1) + 'px';
	var cellBorder = w.cellBorder + 'px';	
	// create rows
	for (var i=start; i < start + step && i < w.dataSet.length; i++) {
		oRow = document.createElement("tr");
		oRow.isSelected = false;
		rowBgColor = w.altColors[i%2];
		oRow.style.backgroundColor = rowBgColor;
		if (rowHeight)
			oRow.style.height = rowHeight;
		if (w.hasSelector) {
			selector = w._getSelector();
			offset = (QuiX.browser=='saf')?0:2*w.cellPadding - 2;
			selector.style.width = (8 - offset) + 'px';
			oRow.appendChild(selector);
		}
		for (var j=0 + w._deadCells; j<w.columns.length-2; j++) {
			cell = document.createElement('td');
			cell.className = 'cell';
			columnWidth = w.columns[j].style.width;
			if (i==0 && columnWidth) {
				offset = (QuiX.browser=='saf')?0:w.cellBorder;
				if (w.columns[j].proportion) {
					cell.style.width =
						(parseInt(w._calcWidth() * w.columns[j].proportion) -
						 2*w.cellPadding - 2) + 'px';
				}
				else
					cell.style.width = (parseInt(columnWidth) -
										 offset) + 'px';
			}
			cell.style.borderWidth = cellBorder;
			cell.style.padding = cellPadding;
			if (w.columns[j].columnBgColor)
				cell.bgColor = w.columns[j].columnBgColor;
			oRow.appendChild(cell);
			value = w.dataSet[i][w.columns[j].name];
			w._renderCell(cell, j, value, w.dataSet[i])
		}
		oFiller = ce('TD');
		oFiller.innerHTML = '&nbsp;';
		oFiller.className = 'cell';
		oFiller.style.borderWidth = cellBorder;
		oFiller.style.borderRight = 'none';
		
		oRow.appendChild(oFiller);
		if (w._customRegistry.onrowprerender)
			w._customRegistry.onrowprerender(w, oRow, w.dataSet[i]);
		tbody.appendChild(oRow);
	}
	if (i<w.dataSet.length)
		w._timeout = window.setTimeout(function(){
			if (w.div) w._refresh(i, step)}, 300);
	else
		if (w._customRegistry.onrendercomplete)
			w._customRegistry.onrendercomplete(w);
}

ListView.prototype._renderCell = function(cell, cellIndex, value, obj) {
	var elem, column, column_type;

	if (value==undefined) {
		cell.innerHTML = this.nullText;
		return;
	}
	
	if (cellIndex != null) {
		column = this.columns[cellIndex];
		cell.align = column.columnAlign;
		column_type = column.columnType;
	
		switch (column_type) {
			case 'optionlist':
				for (var i=0; i<column.options.length; i++) {
					if (value==column.options[i].value)
						cell.innerHTML = '<span>' + 
							column.options[i].caption + '</span>';
				}
				return;
			case 'img':
				elem = QuiX.getImage(value);
				elem.align = 'absmiddle';
				elem.ondragstart = QuiX.cancelDefault;
				cell.appendChild(elem);
				return;
			case 'bool':
				if (value) {
					while (cell.childNodes.length > 0) {
						QuiX.removeNode(cell.childNodes[0]);					
					}
					elem = QuiX.getImage(column.trueImg)
					elem.align = 'absmiddle';
					cell.appendChild(elem);
				}
				else
					cell.innerHTML = '&nbsp;'
				return;
			case 'date':
				cell.innerHTML = '<span>' + 
					value.format(column.format) + '</span>';
				return;
			default:
				if (typeof column_type == 'function') {
					cell.appendChild(column_type(column,obj,value))
					return;
				}
		}
		if (column._xform)
			value = column._xform(obj, value);
	}
	
	// auto-detect value type
	if (value instanceof Date) {
		cell.innerHTML = '<span>' + 
			value.format(this.dateFormat) + '</span>';
	} else if (typeof(value) == 'boolean') {
		if (value) {
			elem = QuiX.getImage(this.trueImg)
			elem.align = 'absmiddle';
			cell.appendChild(elem);
		} else {
			cell.innerHTML = '&nbsp;';
		}
	} else {
		cell.innerHTML = '<span>' + 
			((value == '' && value != 0)?'&nbsp;':value) + '</span>';
	}
}

ListView.prototype._getRow = function(evt) {
	var target = (QuiX.getTarget(evt));
	while (target && target.tagName != 'TR')
		target = QuiX.getParentNode(target);
	return target;	
}

function ListView__onclick (evt, w, f) {
	if (!evt) return;
	var row = w._getRow(evt);
	if (row)
		f(evt, w, w.dataSet[row.rowIndex]);
	else
		QuiX.cancelDefault(evt);
}

function ListView__onmousedown(evt) {
	var evt = evt || event;
	QuiX.cancelDefault(evt);
	var lv = QuiX.getTargetWidget(evt).parent;
	if (lv._isDisabled) return;
	var row = lv._getRow(evt);
	if (row)
		lv._selectline(evt, row);
}

function ListView__onscroll(evt, w) {
	w.parent.header.div.scrollLeft = w.div.scrollLeft;
}

function ListColumn__setCaption(s) {
	this.innerHTML = '<span style="white-space:nowrap">' + s + '</span>';
}

function ListColumn__getCaption(s) {
	return this.firstChild.innerHTML;
}

function ListColumn__onclick(evt) {
	var sortOrder, orderBy;
	var evt = evt || event;
	var lv = QuiX.getTargetWidget(evt).parent;
	if (lv._orderBy == this.name)
		sortOrder = (lv._sortOrder=='ASC')?'DESC':'ASC';
	else
		sortOrder = 'ASC';
	orderBy = this.name;
	lv.sort(orderBy, sortOrder);
	QuiX.stopPropag(evt);
}

function List__startDrag(x, y, el) {
	if (el.tagName == 'DIV')
		return;
	var dragable = new Widget({
		width : this.getWidth(true),
		height : 1,
		border : 1,
		style : 'border:1px solid transparent'
	});
	with (dragable) {
		div.className = this.div.className;
		setPosition('absolute');
		left = x + 2;
		top = y + 2;
		setOpacity(.5);
	}
	// fill with selected rows
	var src_row, row;
	var srcTable = this.div.firstChild;
	var table = srcTable.cloneNode(false);
	table.appendChild(ce('TBODY'));
	dragable.div.appendChild(table);
	
	for (var i=0; i<this.parent.selection.length; i++) {
		src_row = srcTable.rows[this.parent.selection[i]];
		dragable.height += src_row.offsetHeight;
		row = src_row.cloneNode(true);
		if (i==0) {
			for (var j=0; j<row.cells.length; j++) {
				row.cells[j].style.width =
					srcTable.rows[0].cells[j].style.width;
			}	
		}
		table.firstChild.appendChild(row);
	}
	document.desktop.appendChild(dragable);
	dragable.div.style.zIndex = QuiX.maxz;
	dragable.redraw(true);

	QuiX.tmpWidget = dragable;
	QuiX.dragable = this.parent;

	document.desktop.attachEvent('onmouseover', Widget__detecttarget);
	document.desktop.attachEvent('onmousemove', Widget__drag);
}
