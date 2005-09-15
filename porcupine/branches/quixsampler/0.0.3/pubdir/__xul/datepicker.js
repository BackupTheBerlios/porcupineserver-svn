/************************
Date picker control
************************/

function Datepicker(params) {
	params = params || {};
	params.editable = false;
	params.menuheight = 160;
	params.img = params.img || 'images/date16.gif';
	this.base = Combo;
	this.base(params);
	if (params.value)
		this.value = new Date().parseIso8601(params.value);
	else {
		this.value = new Date();
		this.value.setHours(0);
		this.value.setMinutes(0);
		this.value.setSeconds(0);
	}
	this.dt = this.value;
	this.div.firstChild.value = this.dt.format('ddd dd/mmm/yyyy');
	var oDatepicker = this;
	this.getValue = function() { return(oDatepicker.value); }
	this.setValue = function(val) {
		oDatepicker.value=new Date(val);
		oDatepicker.dt = this.value;
		oDatepicker.div.firstChild.value = oDatepicker.dt.format('ddd dd/mmm/yyyy');
	}
}

Datepicker.prototype = new Combo;

Datepicker.prototype.showDropdown = function() {
	var oDatepicker = this;
	Combo.prototype.showDropdown(this);
	var oDropdown = oDatepicker.dropdown;

	oDropdown.parseFromString(
		'<a:splitter orientation="h" xmlns:a="http://www.innoscript.org/quix" width="100%" height="100%" spacing="0">' +
			'<a:pane length="28" bgcolor="menu">' +
				'<a:rect left="center" top="center" width="190" height="22">' + 
					'<a:flatbutton width="20" height="100%" caption="&lt;&lt;"></a:flatbutton>' +
					'<a:combo id="month" left="21" width="100" height="100%" editable="false"></a:combo>' +
					'<a:spinbutton id="year" maxlength="4" left="121" width="50" height="100%" editable="true"></a:spinbutton>' +
					'<a:flatbutton left="171" width="20" height="100%" caption="&gt;&gt;"></a:flatbutton>' +
				'</a:rect>' +
			'</a:pane>' +
			'<a:pane length="-1"></a:pane>' +
		'</a:splitter>',
		function(w) {
			var spl = w;
			oDropdown.minw = oDropdown.width = 200;
			oDropdown.minh = oDropdown.height = 160;
			oDropdown.widgets[1].bringToFront();
			oDropdown.redraw();
			
			oDropdown.close = function() {
				document.desktop.overlays.removeItem(this);
				if (oDatepicker.month.isExpanded) oDatepicker.month.dropdown.close();
				oDatepicker.isExpanded = false;
				this.destroy();
			}
			
			spl.panes[0].attachEvent('onclick', QuiX.stopPropag);
		
			oDatepicker.year = spl.getWidgetById('year');
			oDatepicker.year.onchange = function() { oDatepicker.onYear(); }
			oDatepicker.year.attachEvent('onkeyup', function() { oDatepicker.onYear(); });
		
			oDatepicker.month = spl.getWidgetById('month');
			for (var i=0; i<oDatepicker.dt.Months.length; i++)
				oDatepicker.month.addOption({caption:oDatepicker.dt.Months[i], value:i});
			oDatepicker.month.onchange = function() { oDatepicker.onMonth(); }
			
			_monthclick = function(evt, w) {
				if (!oDatepicker.month.isExpanded) {
					oDatepicker.month.showDropdown();
				}
				else
					oDatepicker.month.dropdown.close();
				QuiX.stopPropag(evt);
			}
			oDatepicker.month.div.firstChild.onclick = _monthclick;
			oDatepicker.month.button.attachEvent('onclick', _monthclick);
				
			spl.getWidgetsByType(FlatButton)[0].attachEvent('onclick', function() { oDatepicker.onPrev(); })
			spl.getWidgetsByType(FlatButton)[1].attachEvent('onclick', function() { oDatepicker.onNext(); })
		
			oDatepicker.render(spl.panes[1].div);
			oDatepicker.fill();
		}
	);
}

Datepicker.prototype.render = function(container) {
	var oT1, oTR1, oTD1, oTH1;
	var oT2, oTR2, oTD2;
	
	container.appendChild(oT1 = document.createElement("table"));
	oT1.width='100%';
	oT1.height='100%';
	oT1.cellSpacing = 0;
	oT1.border = 0;
	
	oTR1 = oT1.insertRow(oT1.rows.length);
	for ( i = 0; i < 7; i++ ) {
		oTH1 = document.createElement("th");
	    oTR1.appendChild(oTH1);
	    oTH1.innerHTML = this.dt.Days[i].slice(0,1);//this.texts.days[i];
	    oTH1.className = 'DatePicker';
	}
	this.aCells = new Array;
	for ( var j = 0; j < 6; j++ ) {
	    this.aCells.push(new Array);
	    oTR1 = oT1.insertRow(oT1.rows.length);
	    for ( i = 0; i < 7; i++ ) {
			this.aCells[j][i] = oTR1.insertCell(oTR1.cells.length);
			this.aCells[j][i].oDatePicker = this;
			this.aCells[j][i].onclick = function() {
				this.oDatePicker.onDay(this);
			}
	    }
	}
}

Datepicker.prototype.fill = function() {
	this.clear();
	var nRow = 0;
	var d = new Date(this.dt.getTime());
	var now = new Date();
	var m = d.getMonth();
	for ( d.setDate(1); d.getMonth() == m; d.setTime(d.getTime() + 86400000) ) {
		var nCol = d.getDay();
		this.aCells[nRow][nCol].innerHTML = d.getDate();
		if ( d.getDate() == this.dt.getDate() && d.getMonth() == now.getMonth() && d.getYear() == now.getYear() ) {
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
		this.div.firstChild.value = this.dt.format('ddd dd/mmm/yyyy');
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
