/************************
List View
************************/

function ListView(params) {
	params = params || {};
	params.bgcolor = params.bgcolor || 'white';
	params.overflow = 'auto';
	
	var dragable = (params.dragable == 'true' || params.dragable == true);
	delete params.dragable;
	
	this.base = Widget;
	this.base(params);
	this.div.className = 'listview';
	this.cellPadding = params.cellpadding || 4;
	this.cellBorder = params.cellborder || 0;
	this.multiple = (params.multiple==true || params.multiple=="true")?true:false;
	this.nullText = params.nulltext || '&nbsp;';
	this.dateFormat = params.dateformat || 'ddd dd/mmm/yyyy time';
	this.trueImg = params.trueimg || '__quix/images/check16.gif';
	this.sortfunc = QuiX.getEventListener(params.sortfunc);

	this.hasSelector = false;
	this.selection = [];
	this.dataSet = [];
	
	this.orderby = null;
	this.sortorder = null;
	this._sortimg = null;
	
	this._dragable = dragable;
}

QuiX.constructors['listview'] = ListView;
ListView.prototype = new Widget;

ListView.prototype.customEvents = Widget.prototype.customEvents.concat(['onselect']);

ListView.prototype._registerHandler = function(eventType, handler, isCustom) {
	var wrapper;
	if (handler)
		switch (eventType) {
			case "onclick":
			case "ondblclick":
				//if it not wrapped wrap it...
				if(handler && handler.toString().lastIndexOf('return handler(evt || event, w)')==-1)
					wrapper = function(evt, w){ return ListView__onclick(evt, w, handler) };
				break;
		}
	wrapper = wrapper || handler;
	Widget.prototype._registerHandler(eventType, wrapper, isCustom, this);
}

ListView.prototype.addHeader = function(params, w) {
	var oListview = w || this;
	params.width = '100%';
	params.height = (!params.height || params.height<22)?22:parseInt(params.height);
	
	oListview.header = new Widget(params);
	oListview.appendChild(oListview.header);
	oListview.header.div.className = 'listheader';
	oListview.header.div.innerHTML = '<table cellspacing="0" width="100%" height="100%"><tr><td class="column filler">&nbsp;</td></tr></table>';
	oListview.header.div.style.backgroundPosition = '0px ' + (params.height-22) + 'px';
	oListview.header.redraw = ListViewHeader__redraw;
	
	var oRow = oListview.header.div.firstChild.rows[0];
	oListview.columns = oRow.cells;
	oRow.ondblclick = QuiX.stopPropag;
	
	if (oListview.hasSelector) {
		var selector = oListview._getSelector();
		oRow.insertBefore(selector, oRow.lastChild);
		oListview._deadCells = 1;
	} else
		oListview._deadCells = 0;

	var list = new Widget({
		top : function() {
			return oListview.header.isHidden()?0:oListview.header._calcHeight(true);
		},
		width : 'this.parent.getWidth()-1',
		height : 'this.parent.getHeight()-' + (parseInt(params.height) + 1),
		dragable : oListview._dragable
	});
	list._startDrag = List__startDrag;
	oListview.appendChild(list);
	
	list.div.className = 'list';
	var oTable = ce('TABLE');
	oTable.cellSpacing = 0;
	oTable.cellPadding = oListview.cellPadding;
	oTable.width = '100%';
	oTable.onmousedown = function(evt) {
		var evt = evt || event;
		if (oListview._isDisabled) return;
		var target = QuiX.getTarget(evt);
		while (target.tagName!='DIV') {
			if (target.tagName == 'TR') {
				oListview._selectline(evt, target);
				break;
			}
			target = target.parentElement || target.parentNode;
		}
	}
	var tbody = ce('TBODY');
	oTable.appendChild(tbody);
	list.div.appendChild(oTable);

	oListview.attachEvent('onscroll', ListView__onscroll);
	oListview.list = list.div.firstChild;

	this._deadCells = (this.hasSelector)?1:0;

	oListview.header.bringToFront();
	return(oListview.header);
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
	r.className = 'selected';
	r.isSelected = true;
}

ListView.prototype._unselrow = function(r) {
	r.className = '';
	r.isSelected = false;
	for (var i=0; i<this.columns.length-1; i++)
		if (this.columns[i].columnBgColor)
			r.cells[i].bgColor = this.columns[i].columnBgColor;
}

ListView.prototype._selectline = function (evt, row) {
	if (row.isSelected && QuiX.getMouseButton(evt)==2) {
		return;
	}
	var fire = this.multiple || !row.isSelected;
	
	if (!row.isSelected) {
		if (!this.multiple || !evt.shiftKey) this.clearSelection();
		this._selrow(row);
		this.selection.push(row.rowIndex);
	} else if (this.multiple && evt.shiftKey) {
		this._unselrow(row);
		this.selection.removeItem(row.rowIndex);
	} else {
		this.clearSelection();
		this._selrow(row);
		this.selection.push(row.rowIndex);
	}
	
	if (fire && this._customRegistry.onselect) {
		QuiX.getEventListener(this._customRegistry.onselect)(evt, this, this.dataSet[row.rowIndex]);
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
	for (var i=0; i<this.selection.length; i++) sel.push(this.dataSet[this.selection[i]]);
	if (sel.length==0)
		return null;
	else if (sel.length==1)
		return sel[0];
	else
		return sel;
}

ListView.prototype.sort = function(column) {
	if (this.orderby == column.name)
		this.sortorder = (this.sortorder=='ASC')?'DESC':'ASC';
	else
		this.sortorder = 'ASC';
	this.orderby = column.name;

	if (this._sortimg) QuiX.removeNode(this._sortimg);
	this._sortimg = new Image;
	this._sortimg.src = (this.sortorder=='ASC')?'__quix/images/asc8.gif':'__quix/images/desc8.gif';
	this._sortimg.align = 'absmiddle';
	column.appendChild(this._sortimg);
	
	if (this.sortfunc) {
		this.sortfunc(this);
	} else {
		// default sort behaviour
		this.dataSet.sortByAttribute(column.name);
		if (this.sortorder=='DESC') this.dataSet.reverse();
		this.refresh();
	}
}

ListView.prototype.addColumn = function(params, w) {
	var oListView = w || this;
	var oCol = ce('TD');
	var header_width, perc;
	
	oCol.className = 'column';
	oCol._isContainer = false;
	oCol.columnBgColor = params.bgcolor || '';
	oCol.style.padding = '0px ' + oListView.cellPadding + 'px 0px ' + oListView.cellPadding + 'px';

	if (params.width) {
		if (params.width.slice(params.width.length-1) == '%') {
			header_width = oListView.header.getWidth();
			perc = parseInt(params.width) / 100;
			var wi = parseInt(header_width * perc) - 2*this.cellPadding - 2;
			oCol.style.width = (wi>0?wi:0) + 'px';
			oCol.proportion = perc;
		}
		else
			oCol.style.width = (params.width - 2*oListView.cellPadding - 2*oListView.cellBorder) + 'px';
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
	
	oCol.sortable = (params.sortable=='false' || params.sortable==false)?false:true;
	if (oCol.sortable) {
		oCol.style.cursor = 'pointer';
		oCol.onclick = function(evt){
			oListView.sort(oCol);
			QuiX.stopPropag(evt);
		}
	}
	
	var oHeaderRow = oListView.header.div.firstChild.rows[0];
	oHeaderRow.insertBefore(oCol, oHeaderRow.lastChild);
	
	if (oCol.columnType == 'bool')
		oCol.trueImg = params.trueimg || oListView.trueImg;
	else if (oCol.columnType == 'date')
		oCol.format = params.format || oListView.dateFormat;
		
	oCol.columnAlign = params.align || 'left';
	
	var resizer = new Widget({
		width : 4,
		height : oListView.header._calcHeight(true),
		left : 'this.parent.parent._calcResizerOffset(this)',
		overflow : 'hidden'
	});
	oListView.header.appendChild(resizer);
	
	oCol.isResizable = (params.resizable=='false' || params.resizable==false)?false:true;
	if (oCol.isResizable) {
		var iColumn = oListView.columns.length - 1;
		resizer.div.className = 'resizer';
		resizer.attachEvent('onmousedown', function(evt) {
			oListView._moveResizer(evt, iColumn-1-oListView._deadCells);
		});
	}
	return oCol;
}

ListView.prototype._calcResizerOffset = function(w) {
	var oHeader = this.header;
	var left = (this.hasSelector)?10:0;
	var offset = 2 * parseInt(this.cellPadding);
	var column_width;
	for (var i=this._deadCells; i<this.columns.length; i++) {
		column_width = parseInt(this.columns[i].style.width);
		left += column_width + offset;

		if (this.list.rows.length > 0)
			this.list.rows[0].cells[i].style.width =
				column_width - this.cellBorder + 'px';

		if (oHeader.widgets[i - this._deadCells]==w) break;
	}
	left += (2*i);
	return left;
}

ListView.prototype._moveResizer = function(evt, iResizer) {
	var oWidget = this;
	QuiX.startX = evt.clientX;
	QuiX.startY = evt.clientY;
	QuiX.tmpWidget = QuiX.createOutline(this.header.widgets[iResizer]);
	this.attachEvent('onmouseup', function(evt){oWidget._endMoveResizer(evt, iResizer)});
	this.attachEvent('onmousemove', function(evt){oWidget._resizerMoving(evt, iResizer)});
}

ListView.prototype._resizerMoving = function(evt, iResizer) {
	var offsetX = evt.clientX - QuiX.startX;
	if ( offsetX > -(this.columns[iResizer + this._deadCells].offsetWidth - 2*this.cellPadding - this.cellBorder) )
		QuiX.tmpWidget.moveTo(this.header.widgets[iResizer]._calcLeft() + offsetX,
			this.header.widgets[iResizer]._calcTop());
}

ListView.prototype._endMoveResizer = function(evt, iResizer) {
	var iColumn = iResizer + this._deadCells;
	var offsetX = evt.clientX - QuiX.startX;
	var nw = parseInt(this.columns[iColumn].style.width) + offsetX;
	nw = (nw < 2*this.cellPadding)?2*this.cellPadding:nw;
	
	this.columns[iColumn].style.width = nw + 'px';
	if (this.columns[iColumn].proportion)
		this.columns[iColumn].proportion = 0;
	this.header.redraw(true);
	
	ListView__onscroll(null, this);
	QuiX.tmpWidget.destroy();
	this.detachEvent('onmouseup');
	this.detachEvent('onmousemove');
}

ListView.prototype.refresh = function(w) {
	w = w || this;
	var oRow, oCell, selector, sPad, oFiller, oListTable;
	var oValue, column_width, offset;
	var tbody = document.createElement("tbody");
	var docFragment = document.createDocumentFragment();
	// create rows
	for (i=0; i<w.dataSet.length; i++) {
		oRow = document.createElement("tr");
		oRow.isSelected = false;
		if (w.hasSelector) {
			selector = w._getSelector();
			selector.style.width = (8 - 2*w.cellPadding + 2) + 'px';
			oRow.appendChild(selector);
		}
		for (var j=0 + w._deadCells; j<w.columns.length-1; j++) {
			oCell = ce('TD');
			oCell.className = 'cell';
			column_width = w.columns[j].style.width;
			if (i==0 && column_width) {
				oCell.style.width = parseInt(column_width) - w.cellBorder + 'px';
			}

			oCell.style.borderWidth = w.cellBorder + 'px';
			sPad = (w.cellPadding + 1) + 'px';
			oCell.style.padding = '4px ' + sPad + ' 4px ' + sPad;
			if (w.columns[j].columnBgColor) oCell.bgColor = w.columns[j].columnBgColor;
			oRow.appendChild(oCell);
			oValue = w.dataSet[i][w.columns[j].name];
			w._renderCell(oCell, j, oValue, w.dataSet[i])
		}
		oFiller = ce('TD');
		oFiller.innerHTML = '&nbsp;';
		oRow.appendChild(oFiller);
		docFragment.appendChild(oRow);
	}
	tbody.appendChild(docFragment);
	oListTable = w.widgets[1].div.firstChild;
	oListTable.replaceChild(tbody, oListTable.tBodies[0]);
	
	w.div.scrollTop = '0px';
	w.selection = [];
	ListView__onscroll(null, w);
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
						cell.innerHTML = '<span style="white-space:nowrap">' + 
							column.options[i].caption + '</span>';
				}
				return;
			case 'img':
				elem = QuiX.getImage(value);
				elem.align = 'absmiddle';
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
				cell.innerHTML = '<span style="white-space:nowrap">' + 
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
		cell.innerHTML = '<span style="white-space:nowrap">' + 
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
		cell.innerHTML = '<span style="white-space:nowrap">' + 
			((value == '' && value != 0)?'&nbsp;':value) + '</span>';
	}
}

function ListView__onclick (evt, w, f) {
	if (!evt) return;
	var target = QuiX.getTarget(evt);
	while (target.tagName!='DIV') {
		if (target.tagName == 'TR') {
			f(evt, w, w.dataSet[target.rowIndex]);
			break;
		}
		target = target.parentElement || target.parentNode;
	}
}

function ListView__onscroll(evt, w) {
	w.header.div.style.top = w.div.scrollTop + 'px';
}

function ListColumn__setCaption(s) {
	this.innerHTML = '<span style="white-space:nowrap">' + s + '</span>'
}

function ListColumn__getCaption(s) {
	return this.firstChild.innerHTML;
}

function ListViewHeader__redraw(bForceAll) {
	var columns = this.parent.columns;
	var header_width = this._calcWidth();
	for (var i = this.parent._deadCells; i<columns.length; i++) {
		if (columns[i].proportion) {
			columns[i].style.width = parseInt(header_width * columns[i].proportion) -
									 2*this.parent.cellPadding - 2 + 'px';
		}
	}
	Widget.prototype.redraw(bForceAll, this);
}

function List__startDrag(x, y) {
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
				row.cells[j].style.width = srcTable.rows[0].cells[j].style.width;
			}			
		}
		table.firstChild.appendChild(row);
	}
	document.desktop.appendChild(dragable);
	dragable.redraw(true);

	QuiX.tmpWidget = dragable;
	QuiX.dragable = this.parent;

	document.desktop.attachEvent('onmouseover', Widget__detecttarget);
	document.desktop.attachEvent('onmousemove', Widget__drag);
}