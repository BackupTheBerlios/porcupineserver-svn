/************************
List View
************************/

function ListView(params) {
	params = params || {};
	params.bgcolor = params.bgcolor || 'white';
	params.overflow = 'auto';
	
	if (params.onclick) {
		this.onclick = params.onclick;
		delete params.onclick
	}
	
	if (params.ondblclick) {
		this.ondblclick = params.ondblclick;
		delete params.ondblclick
	}

	this.base = Widget;
	this.base(params);
	this.div.className = 'listview';
	this.cellPadding = params.cellpadding || 4;
	this.cellBorder = params.cellborder || 0;
	this.multiple = (params.multiple==true || params.multiple=="true")?true:false;
	this.nullText = params.nulltext || '&nbsp;';
	this.dateFormat = params.dateformat || 'ddd dd/mmm/yyyy time';
	this.trueImg = params.trueimg || 'images/check16.gif';
	this.onselect = params.onselect;
	this.sortfunc = getEventListener(params.sortfunc);

	if (this.onclick) {
		this._onclick = getEventListener(this.onclick);
		this.attachEvent('onclick', ListView__onclick);
	}
	if (this.ondblclick) {
		this._ondblclick = getEventListener(this.ondblclick);
		this.attachEvent('ondblclick', ListView__ondblclick);
	}
	
	this.hasSelector = false;

	this.selection = [];
	this.dataSet = [];
	
	this.orderby = null;
	this.sortorder = null;
	this._sortimg = null;
}

ListView.prototype = new Widget;

ListView.prototype.addHeader = function(params, w) {
	var oListview = w || this;
	params.width = '100%';
	params.height = (!params.height || params.height<22)?22:parseInt(params.height);
	
	oListview.header = new Widget(params);
	oListview.appendChild(oListview.header);
	oListview.header.div.className = 'listheader';
	oListview.header.div.innerHTML = '<table cellspacing="0" width="100%" height="100%"><tr><td class="column filler">&nbsp;</td></tr></table>';
	oListview.header.div.style.backgroundPosition = '0px ' + (params.height-22) + 'px';
	
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
		top: function() { return oListview.header.isHidden()?0:oListview.header._calcHeight(true); },
		width:'this.parent.getWidth()-1',
		height:'this.parent.getHeight()-' + params.height + 1
	});
	oListview.appendChild(list);
	
	list.div.className = 'list';
	var oTable = ce('TABLE');
	oTable.cellSpacing = 0;
	oTable.cellPadding = oListview.cellPadding;
	oTable.width = '100%';
	oTable.onmousedown = function(evt) {
		evt = evt || event;
		var target = QuiX.getTarget(evt);
		while (target.tagName!='DIV') {
			if (target.tagName == 'TR') {
				oListview._selectline(evt || event, target);
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
	if (this.onselect)
		getEventListener(this.onselect)(evt, this, this.dataSet[row.rowIndex]);
	
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
	this._sortimg.src = (this.sortorder=='ASC')?'images/asc8.gif':'images/desc8.gif';
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
	oCol.className = 'column';
	oCol.columnBgColor = params.bgcolor || '';
	oCol.style.padding = '0px ' + oListView.cellPadding + 'px 0px ' + oListView.cellPadding + 'px';
	oCol.style.width = (params.width - 2*oListView.cellPadding - 2*oListView.cellBorder) + 'px';
	oCol.setCaption = ListColumn__setCaption;
	oCol.getCaption = ListColumn__getCaption;

	oCol.name = params.name;
	var sCaption = params.caption || '&nbsp;';
	oCol.setCaption(sCaption);
		
	oCol.columnType = params.type || 'str';
	if (params.xform) {
		oCol.xform = params.xform;
		oCol._xform = getEventListener(oCol.xform);
	}
	
	oCol.sortable = (params.sortable=='false')?false:true;
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
	
	var iOffset;
	if (oListView.header.widgets.length>0)
		iOffset = oListView.header.widgets[oListView.header.widgets.length - 1].left;
	else
		iOffset = (oListView.hasSelector)?10:-2;
	
	var resizer = new Widget({
		width : 4,
		height : oListView.header._calcHeight(true),
		left : iOffset + parseInt(params.width) + (oListView.cellPadding/2) - (2*oListView.cellBorder),
		overflow : 'hidden',
		border : 0
	});
	oListView.header.appendChild(resizer);
	
	oCol.isResizable = (params.resizable=='false')?false:true;
	if (oCol.isResizable) {
		var iColumn = oListView.columns.length - 1;
		resizer.div.className = 'resizer';
		resizer.attachEvent('onmousedown', function(evt) {
			oListView._moveResizer(evt, iColumn-1-oListView._deadCells);
		});
	}
	return oCol;
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
	if (offsetX>-parseInt(this.columns[iResizer + this._deadCells].style.width))
		QuiX.tmpWidget.moveTo(this.header.widgets[iResizer]._calcLeft() + offsetX,
			this.header.widgets[iResizer]._calcTop());
}

ListView.prototype._endMoveResizer = function(evt, iResizer) {
	var iColumn = iResizer + this._deadCells;
	var offsetX = evt.clientX - QuiX.startX;
	var nw = parseInt(this.columns[iColumn].style.width) + offsetX;
	nw = (nw<2*this.cellPadding)?2*this.cellPadding:nw;
	var iOldWidth = parseInt(this.columns[iColumn].style.width);
	this.columns[iColumn].style.width = nw + 'px';
	if (this.list.rows.length > 0)
		this.list.rows[0].cells[iColumn].style.width = nw- this.cellBorder + 'px';
	for (var i=iResizer; i<this.columns.length - this._deadCells; i++)
		this.header.widgets[i].left += nw - iOldWidth;
	this.header.redraw(true);
	ListView__onscroll(null, this);
	QuiX.tmpWidget.destroy();
	this.detachEvent('onmouseup');
	this.detachEvent('onmousemove');
}

ListView.prototype.refresh = function() {
	var oRow, oCell, selector, sPad, oFiller, oListTable;
	var oValue;
	var tbody = document.createElement("tbody");
	var docFragment = document.createDocumentFragment();
	// create rows
	for (i=0; i<this.dataSet.length; i++) {
		oRow = document.createElement("tr");
		oRow.isSelected = false;
		if (this.hasSelector) {
			selector = this._getSelector();
			selector.style.width = (8 - 2*this.cellPadding + 2) + 'px';
			oRow.appendChild(selector);
		}
		for (var j=0 + this._deadCells; j<this.columns.length-1; j++) {
			var oCell = ce('TD');
			oCell.className = 'cell';
			if (i==0)
				oCell.style.width = parseInt(this.columns[j].style.width) - this.cellBorder + 'px';

			oCell.style.borderWidth = this.cellBorder + 'px';
			sPad = (this.cellPadding + 1) + 'px';
			oCell.style.padding = '4px ' + sPad + ' 4px ' + sPad;
			if (this.columns[j].columnBgColor) oCell.bgColor = this.columns[j].columnBgColor;
			oRow.appendChild(oCell);
			oValue = this.dataSet[i][this.columns[j].name];
			this._renderCell(oCell, j, oValue, this.dataSet[i])
		}
		oFiller = ce('TD');
		oFiller.innerHTML = '&nbsp;';
		oRow.appendChild(oFiller);
		docFragment.appendChild(oRow);
	}
	tbody.appendChild(docFragment);
	oListTable = this.widgets[1].div.firstChild;
	oListTable.replaceChild(tbody, oListTable.tBodies[0]);
	
	this.div.scrollTop = '0px';
	this.selection = [];
	ListView__onscroll(null, this);
}

ListView.prototype._renderCell = function(cell, cellIndex, value, obj) {
	var elem, column, column_type;

	cell.innerHTML = '';
	if (value==undefined) {
		cell.innerHTML = this.nullText;
		cell.style.cursor = 'default';
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
		if (value=='') value=' ';
		cell.innerHTML = '<span style="white-space:nowrap"></span>';
		cell.style.cursor = 'default';
		cell.firstChild.appendChild(document.createTextNode(value));
	}
}

function ListView__onclick (evt, w) {
	var target = QuiX.getTarget(evt);
	while (target.tagName!='DIV') {
		if (target.tagName == 'TR') {
			w._onclick(evt, w, w.dataSet[target.rowIndex]);
			break;
		}
		target = target.parentElement || target.parentNode;
	}
}

function ListView__ondblclick(evt, w) {
	var target = QuiX.getTarget(evt);
	while (target.tagName!='DIV') {
		if (target.tagName == 'TR') {
			w._ondblclick(evt, w, w.dataSet[target.rowIndex]);
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

