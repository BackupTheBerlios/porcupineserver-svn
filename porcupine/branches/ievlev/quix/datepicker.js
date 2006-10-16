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
	this.setValue(params.value || '');
	
	var oDatepicker = this;
	var oDropdown = this.dropdown;
	oDropdown.parseFromString(
		'<a:box orientation="v" bgcolor="menu" xmlns:a="http://www.innoscript.org/quix" width="100%" height="100%" spacing="4" childrenalign="center">' +
			'<a:rect width="195" height="22">' + 
				'<a:flatbutton width="22" height="100%" caption="&lt;&lt;"></a:flatbutton>' +
				'<a:combo id="month" left="24" width="100" height="100%" editable="false"></a:combo>' +
				'<a:spinbutton id="year" maxlength="4" left="123" width="50" height="100%" editable="true"></a:spinbutton>' +
				'<a:flatbutton left="173" width="22" height="100%" caption="&gt;&gt;"></a:flatbutton>' +
			'</a:rect>' +
			'<a:rect length="-1"/>' +
		'</a:box>',
		function(w) {
			var spl = w;
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
			
			spl.widgets[0].attachEvent('onclick', QuiX.stopPropag);
		
			oDatepicker.year = spl.getWidgetById('year');
			oDatepicker.year.onchange = function() { oDatepicker.onYear(); }
			oDatepicker.year.attachEvent('onkeyup', function() { oDatepicker.onYear(); });
		
			oDatepicker.month = spl.getWidgetById('month');
			for (var i=0; i<oDatepicker.dt.Months.length; i++)
				oDatepicker.month.addOption({caption:oDatepicker.dt.Months[i], value:i});
			oDatepicker.month.onchange = DatepickerMonth__change;
			
			oDatepicker.month.div.firstChild.onclick = DatepickerMonth__click;
			oDatepicker.month.button.attachEvent('onclick', DatepickerMonth__click);
			
			spl.getWidgetsByType(FlatButton)[0].attachEvent('onclick', DatepickerPrev__click);
			spl.getWidgetsByType(FlatButton)[1].attachEvent('onclick', DatepickerNext__click);
			
			oDatepicker.render(spl.widgets[1].div);
			oDatepicker.fill();
		}
	);
}

Datepicker.prototype = new Combo;

Datepicker.prototype.getValue = function() {
	return this.dt;
}

Datepicker.prototype.setValue = function(val) {
	this.isNow = false;
	if (!(val instanceof Date)) {
		if (val == '') {
			this.dt = new Date();
			this.dt.setHours(0);
			this.dt.setMinutes(0);
			this.dt.setSeconds(0);
			this.isNow = true;
		}
		else {
			this.dt = new Date().parseIso8601(val);
		}
	}
	else {
		this.dt=new Date(val);
	}
	this.div.firstChild.value = this.dt.format('ddd dd/mmm/yyyy');
}

Datepicker.prototype.render = function(container) {
	var oT1, oTR1, oTD1, oTH1;
	var oT2, oTR2, oTD2;
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
	    oTH1.innerHTML = this.dt.Days[i].slice(0,1);
	    oTH1.className = 'DatePicker';
	}
	this.aCells = new Array;
	for ( var j = 0; j < 6; j++ ) {
	    this.aCells.push(new Array);
	    oTR1 = oT1.insertRow(oT1.rows.length);
	    for ( i = 0; i < 7; i++ ) {
			this.aCells[j][i] = oTR1.insertCell(oTR1.cells.length);
			this.aCells[j][i].onclick = DatepickerCell__click;
	    }
	}
	container.appendChild(frg.firstChild);
}

Datepicker.prototype.fill = function() {
	this.clear();
	var nRow = 0;
	var d = new Date( this.dt.getTime() );
	var now = new Date();
	var m = d.getMonth();
	for ( d.setDate(1); d.getMonth() == m; d.setTime(d.getTime() + 86400000) ) {
		var nCol = d.getDay();
		this.aCells[nRow][nCol].innerHTML = d.getDate();
		if ( d.getDate() == now.getDate() && d.getMonth() == now.getMonth() && d.getYear() == now.getYear() ) {
		   this.aCells[nRow][nCol].className = 'DatePickerBtnSelect';
		}
		if ( nCol == 6 ) nRow++;
	}
	this.month.setValue(m);
	this.year.setValue(this.dt.getFullYear());
}

Datepicker.prototype.clear = function() {
	for ( var j = 0; j < 6; j++ )
		for ( var i = 0; i < 7; i++ ) {
			this.aCells[j][i].innerHTML = "&nbsp;"
			this.aCells[j][i].className = 'DatePickerBtn';
		}
}

Datepicker.prototype.onYear = function() {
	var y = this.year.getValue();
	if ( y && !isNaN(y) ) {
		this.dt.setFullYear(parseInt(y));
		this.fill();
	}
}

Datepicker.prototype.onMonth = function() {
	this.dt.setMonth(this.month.getValue());
	this.fill();
}

Datepicker.prototype.onDay = function(oCell) {
	var d = parseInt(oCell.innerHTML);
	if ( d > 0 ) {
		this.dt.setDate(d);
		this.setValue(this.dt);
	}
}

Datepicker.prototype.onPrev = function() {
	if ( this.dt.getMonth() == 0 ) {
		this.dt.setFullYear(this.dt.getFullYear() - 1);
		this.dt.setMonth(11);
	}
	else
		this.dt.setMonth(this.dt.getMonth() - 1);
	this.fill();
}

Datepicker.prototype.onNext = function() {
	if ( this.dt.getMonth() == 11 ) {
		this.dt.setFullYear(this.dt.getFullYear() + 1);
		this.dt.setMonth(0);
	}
	else {
		this.dt.setMonth(this.dt.getMonth() + 1);
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