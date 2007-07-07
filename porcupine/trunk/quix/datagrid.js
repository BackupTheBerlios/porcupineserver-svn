/************************
Data Grid
************************/

function DataGrid(params) {
	params = params || {};
	params.multiple = true;
	params.cellborder = params.cellborder || 1;
	params.cellpadding = params.cellpadding || 2;

	this.base = ListView;
	this.base(params);
	
	this.name = params.name;
	this.hasSelector = true;
}

DataGrid.prototype = new ListView;

DataGrid.prototype.addHeader = function(params) {
	var oHeader = ListView.prototype.addHeader(params, this);
	this.widgets[1].attachEvent('onclick', DataGrid__onclick);
	return(oHeader);
}

DataGrid.prototype.addColumn = function(params) {
	var oCol = ListView.prototype.addColumn(params, this);
	oCol.editable = (params.editable=='false' ||
					 params.editable == false)?false:true;
	return(oCol);
}

DataGrid.prototype.getValue = function(params) {
	return this.dataSet;
}

DataGrid.prototype.disable = function() {
	if (this.attributes.__editwidget) {
		this.attributes.__editwidget.destroy();
		this.attributes.__editwidget = null;
		this.detachEvent('onmousedown');
	}
	Widget.prototype.disable(this);
}

function DataGrid__onclick(evt, w) {
	var target=null, idx, ridx, editValue, w2, w2_type;
	target = QuiX.getTarget(evt);
	while (target.tagName!='TD' && target!=document.body)
		target = target.parentElement || target.parentNode;
	if (target!=document.body) {
		idx = target.cellIndex;
		ridx = (target.parentElement || target.parentNode).rowIndex;
		if (idx>0 && idx<w.parent.columns.length-1 && w.parent.columns[idx].editable) {
			editValue = w.parent.dataSet[ridx][w.parent.columns[idx].name];
			switch (w.parent.columns[idx].columnType) {
				case 'optionlist':
					w2 = new Combo({
						top: target.offsetTop,
						left: target.offsetLeft,
						width: target.offsetWidth,
						height: target.offsetHeight
					});
					w.appendChild(w2);
				
					var options = w.parent.columns[idx].options;
					for (var i=0; i<options.length; i++) {
						if (editValue==options[i].value)
							options[i].selected = true;
						else
							options[i].selected = false;
						w2.addOption(options[i]);
					}
					break;
				case 'bool':
					w2_type = 'checkbox';
				default:
					w2 = new Field({
						top: target.offsetTop,
						left: target.offsetLeft,
						width: target.offsetWidth,
						height: target.offsetHeight,
						value: editValue,
						type: w2_type
					});
					w.appendChild(w2);
			}
			w2.redraw();
			w.parent.attributes.__editwidget = w2;
			w.parent.attributes.__rowindex = ridx;
			w.parent.attributes.__cellindex = idx;
			w.parent.attachEvent('onmousedown', DataGrid__onmousedown);
		}
	}
}

function DataGrid__onmousedown (evt, w) {
	var rowindex = w.attributes.__rowindex;
	var cellindex = w.attributes.__cellindex;
	var oCell = w.list.rows[rowindex].cells[cellindex];
	var value = w.attributes.__editwidget.getValue();
	w.dataSet[rowindex][w.columns[cellindex].name] = value;
	w._renderCell(oCell, cellindex, value);

	w.attributes.__editwidget.destroy();
	w.attributes.__editwidget = null;

	w.detachEvent('onmousedown');
	
	delete w.attributes.__editwidget;
}