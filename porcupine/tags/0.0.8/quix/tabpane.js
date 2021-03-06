/************************
Tab Pane
************************/

function TabPane(params) {
	params = params || {};
	this.base = Widget;
	params.overflow = 'hidden';
	this.base(params);
	this.div.className = 'tabpane';
	
	this.tabs = [];
	this.activeTab = null;
}

TabPane.prototype = new Widget;

TabPane.prototype.addTab = function(params) {
	var oTab = new Label({
		border : 1,
		padding : '6,6,4,6',
		overflow : 'hidden',
		height : 26,
		caption : params.caption,
		onclick : Tab__click,
		onmouseover : Tab__mouseover,
		onmouseout : Tab__mouseout
	});
	this.appendChild(oTab);
	oTab.setDisplay('inline');
	oTab.setPosition('relative');
	oTab.div.className = 'tab';

	params.top = 24;
	params.height = 'this.parent.getHeight()-24';
	params.width = '100%';
	params.border = 1;
	params.padding = params.padding || '8,8,8,8';
	params.overflow = 'auto';

	var w = new Widget(params);
	this.appendChild(w);
	w.div.className = 'tabpage';
	w.tabButton = oTab;
	w.destroy = Tab__destroy;
	w.onactivate = params.onactivate;
	
	this.tabs.push(w);
	this.activateTab(0);
	return(w);
}

TabPane.prototype.activateTab = function(iTab) {
	var activeTabButton;
	var iActive = this.activeTab;
	var oTab = this.tabs[iTab];
	oTab.bringToFront();
	
	oTab.tabButton.bringToFront();
	oTab.tabButton.div.style.top='-2px';
	oTab.tabButton.div.className='tab';
	oTab.tabButton.div.style.cursor='default';
	oTab.tabButton.detachEvent('onmouseout');
	oTab.tabButton.detachEvent('onmouseover');
	oTab.tabButton.detachEvent('onclick');
	
	if (iActive != null && iActive != iTab) {
		activeTabButton = this.tabs[iActive].tabButton;
		activeTabButton.div.style.top=0;
		activeTabButton.attachEvent('onmouseout');
		activeTabButton.attachEvent('onmouseover');
		activeTabButton.attachEvent('onclick');
		activeTabButton.div.style.cursor='';
	}

	this.activeTab = iTab;
	if (iActive!=iTab && oTab.onactivate) {
		getEventListener(oTab.onactivate)(this, iTab);
	}
}

function Tab__destroy() {
	var oTab = this.parent;
	var activeTab = oTab.activeTab;
	for (var idx=0; idx < oTab.tabs.length; idx++) {
		 if (oTab.tabs[idx] == this)
		 	break;
	}
	if (idx > 0)
		oTab.activateTab(idx - 1);
	else {
		if (oTab.tabs.length > 1)
			oTab.activateTab(1);
		else
			oTab.activeTab = null;
	}
	oTab.tabs.splice(idx, 1);
	this.tabButton.destroy();
	Widget.prototype.destroy(this);
}

function Tab__mouseover(evt, w) {
	w.div.className = 'tab over';
}

function Tab__mouseout(evt, w) {
	w.div.className = 'tab';
}

function Tab__click(evt, w) {
	var oTabPane = w.parent;
	for (var iTab=0; iTab<oTabPane.tabs.length; iTab++) {
		if (oTabPane.tabs[iTab].tabButton == w)
			break;
	}
	oTabPane.activateTab(iTab);
}