/************************
Date picker control
************************/

function Datepicker(params) {
	params = params || {};
	params.editable = false;
	params.menuheight = 160;
	params.img = params.img || '__quix/images/date16.gif';
	this.base = Combo;
	this.base(params);
	
	this.format = params.dateformat || 'ddd dd/mmm/yyyy';
	this.setValue(params.value || '');
	
	this.dropdown.parseFromString(
		'<box orientation="v" xmlns="http://www.innoscript.org/quix" width="100%" height="100%" spacing="4" childrenalign="center">' +
			'<rect height="26" width="195" padding="2,2,2,2">' + 
				'<flatbutton width="22" height="100%" caption="&lt;&lt;"/>' +
				'<combo id="month" left="22" width="100" height="100%" editable="false"/>' +
				'<spinbutton id="year" maxlength="4" left="121" width="50" height="100%" editable="true"/>' +
				'<flatbutton left="171" width="22" height="100%" caption="&gt;&gt;"/>' +
			'</rect>' +
			'<rect/>' +
		'</box>', Datepicker__fill);

	if (this._isDisabled) {
		this.div.firstChild.disabled = true;
		this.div.firstChild.style.backgroundColor = 'menu';
		if (!this.readonly) this.div.firstChild.onclick = null;
	}
}

QuiX.constructors['datepicker'] = Datepicker;
Datepicker.prototype = new Combo;

Datepicker.prototype.getValue = function() {
	return this.dt;
}

Datepicker.prototype.setValue = function(val) {
	if (!(val instanceof Date)) {
		if (val == '')
			this.dt = new Date();
		else
			this.dt = new Date().parseIso8601(val);
	}
	else {
		var old_dt = this.dt;
		this.dt = new Date(val);
		if (old_dt != this.dt && this._customRegistry.onchange)
			QuiX.getEventListener(this._customRegistry.onchange)(this);
	}
	this._navdt = new Date(this.dt);
	this.div.firstChild.value = this.dt.format(this.format);
}

Datepicker.prototype.render = function(container) {
	var oT1, oTR1, oTH1, cell;
	var frg = document.createDocumentFragment();
	frg.appendChild(oT1 = document.createElement('table'));
	oT1.width='100%';
	oT1.height='100%';
	oT1.cellSpacing = 0;
	oT1.border = 0;
	oT1.datepicker = this;
	
	oTR1 = oT1.insertRow(oT1.rows.length);
	for ( i = 0; i < 7; i++ ) {
		oTH1 = document.createElement("th");
	    oTR1.appendChild(oTH1);
	    oTH1.innerHTML = this._navdt.Days[i].slice(0,1);
	    oTH1.className = 'DatePicker';
	}
	
	for ( var j = 0; j < 6; j++ ) {
	    oTR1 = oT1.insertRow(oT1.rows.length);
	    oTR1.align = 'center';
	    for ( i = 0; i < 7; i++ ) {
			cell = oTR1.insertCell(oTR1.cells.length);
			cell.onclick = DatepickerCell__click;
	    }
	}
	container.appendChild(frg.firstChild);
	this._dayTable = container.firstChild;
}

Datepicker.prototype.fill = function() {
	var nRow = 0;
	var cell, nCol, iDate;
	var d = new Date( this._navdt.getTime() );
	var now = new Date();
	var m = d.getMonth();
	
	this.clear();
	this._selectedCell = null;
	this._nowCell = null;
	
	for ( d.setDate(1); d.getMonth() == m; d.setTime(d.getTime() + 86400000) ) {
		nCol = d.getDay();
		iDate = d.getDate();
		cell = this._dayTable.rows[nRow + 1].cells[nCol];
		cell.innerHTML = d.getDate();
		cell.className = 'DatePickerBtn';
		if (iDate == this.dt.getDate() &&
			 m == this.dt.getMonth() &&
			 d.getYear() == this.dt.getYear()){
			cell.className = 'DatePickerBtnSelect';
			this._selectedCell = cell;
		}
		if ( iDate == now.getDate() &&
			 m == now.getMonth() &&
			 d.getYear() == now.getYear() ) {
		   cell.className = 'DatePickerBtnNow';
		   this._nowCell = cell;
		}

		if ( nCol == 6 ) nRow++;
	}
	this.month.setValue(m);
	this.year.setValue(this._navdt.getFullYear());
}

Datepicker.prototype.clear = function() {
	var cell;
	for ( var j = 0; j < 6; j+=4)
		for ( var i = 0; i < 7; i++ ) {
			cell = this._dayTable.rows[j + 1].cells[i];
			cell.innerHTML = "&nbsp;";
			cell.className = 'DatePickerBtn';
		}
}

Datepicker.prototype.onYear = function() {
	var y = this.year.getValue();
	if ( y && !isNaN(y) ) {
		this._navdt.setFullYear(parseInt(y));
		this.fill();
	}
}

Datepicker.prototype.onMonth = function() {
	this._navdt.setMonth(this.month.getValue());
	this.fill();
}

Datepicker.prototype.onDay = function(oCell) {
	var d = parseInt(oCell.innerHTML);
	if ( d > 0 ) {
		this._navdt.setDate(d);
		
		if (this._selectedCell) {
			if (this._selectedCell == this._nowCell)
				this._selectedCell.className = 'DatePickerBtnNow';
			else
				this._selectedCell.className = 'DatePickerBtn';
		}
		
		oCell.className = 'DatePickerBtnSelect';
		this._selectedCell = oCell;
		
		this.setValue(this._navdt);
	}
}

Datepicker.prototype.onPrev = function() {
	if ( this._navdt.getMonth() == 0 ) {
		this._navdt.setFullYear(this._navdt.getFullYear() - 1);
		this._navdt.setMonth(11);
	}
	else
		this._navdt.setMonth(this._navdt.getMonth() - 1);
	this.fill();
}

Datepicker.prototype.onNext = function() {
	if ( this._navdt.getMonth() == 11 ) {
		this._navdt.setFullYear(this._navdt.getFullYear() + 1);
		this._navdt.setMonth(0);
	}
	else {
		this._navdt.setMonth(this._navdt.getMonth() + 1);
	}
	this.fill();
}

DatepickerMonth__click = function(evt, w) {
	var oCombo;
	if (w)
		oCombo = w.parent
	else
		oCombo = (this.parentNode || this.parentElement).widget;
	if (!oCombo.dropdown.isExpanded)
		oCombo.showDropdown();
	else
		oCombo.dropdown.close();
	QuiX.stopPropag(evt);
}

function DatepickerMonth__change(w) {
	var oDatepicker = w.parent.parent.parent.combo;
	oDatepicker.onMonth();
}

function DatepickerYear__change(x, w) {
	var oDatepicker = (w || x).parent.parent.parent.combo;
	oDatepicker.onYear();
}

function DatepickerNext__click(evt, w) {
	var oDatepicker = w.parent.parent.parent.combo;
	oDatepicker.onNext();
}

function DatepickerPrev__click(evt, w) {
	var oDatepicker = w.parent.parent.parent.combo;
	oDatepicker.onPrev();
}

function DatepickerCell__click() {
	var oDatepicker;
	if (QuiX.browser=='moz')
		oDatepicker = this.parentNode.parentNode.parentNode.datepicker;
	else
		oDatepicker = this.parentElement.parentElement.parentElement.datepicker;
	oDatepicker.onDay(this);
}

function Datepicker__fill(box) {
	var oDropdown = box.parent;
	var oDatepicker = oDropdown.combo;
	
	oDropdown.minw = oDropdown.width = 200;
	oDropdown.minh = oDropdown.height = 160;
	oDropdown.widgets[1].bringToFront();
	
	oDropdown.close = function() {
		document.desktop.overlays.removeItem(this);
		if (oDatepicker.month.isExpanded)
			oDatepicker.month.dropdown.close();
		oDatepicker.isExpanded = false;
		this.detach();
	}
	
	box.widgets[0].attachEvent('onclick', QuiX.stopPropag);

	oDatepicker.year = box.getWidgetById('year');
	oDatepicker.year.attachEvent('onchange', DatepickerYear__change);
	oDatepicker.year.attachEvent('onkeyup', DatepickerYear__change);

	oDatepicker.month = box.getWidgetById('month');
	for (var i=0; i<oDatepicker.dt.Months.length; i++)
		oDatepicker.month.addOption({caption:oDatepicker.dt.Months[i], value:i});
	oDatepicker.month.attachEvent('onchange', DatepickerMonth__change);
	
	oDatepicker.month.div.firstChild.onclick = DatepickerMonth__click;
	oDatepicker.month.button.attachEvent('onclick', DatepickerMonth__click);
	
	box.getWidgetsByType(FlatButton)[0].attachEvent('onclick', DatepickerPrev__click);
	box.getWidgetsByType(FlatButton)[1].attachEvent('onclick', DatepickerNext__click);
	
	oDatepicker.render(box.widgets[1].div);
	oDatepicker.fill();
}
