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
	this.pages = [];
	this.activeTab = null;
}

TabPane.prototype = new Widget;

TabPane.prototype.addTab = function(params) {
	var oTabPane = this;
	var iTabIndex = this.tabs.length;
	var oTab = new Widget({
		border:1,
		padding:'6,6,4,6',
		overflow:'hidden',
		height:26,
		onclick:function(evt){oTabPane.activateTab(iTabIndex)},
		onmouseover:Tab__mouseover,
		onmouseout:Tab__mouseout
	});
	this.appendChild(oTab);
	oTab.onactivate = getEventListener(params.onactivate);
	oTab.setDisplay('inline');
	oTab.setPos('relative');
	oTab.div.className = 'tab';
	oTab.div.innerHTML = params.caption;
	this.tabs.push(oTab);
	var w = new Widget(
		{
			top: 24,
			height:"this.parent.getHeight()-24",
			width:"100%",border:1,padding:params.padding || '8,8,8,8',overflow:'auto'
		});
	this.appendChild(w);
	w.div.className = 'tabpage';
	this.pages.push(w);
	this.activateTab(0);
	return(w);
}

TabPane.prototype.activateTab = function(iTab) {
	this.pages[iTab].bringToFront();
	this.tabs[iTab].bringToFront();
	this.tabs[iTab].div.style.top='-2px';
	this.tabs[iTab].div.className='tab';
	this.tabs[iTab].div.style.cursor='default';
	this.tabs[iTab].detachEvent('onmouseout');
	this.tabs[iTab].detachEvent('onmouseover');
	this.tabs[iTab].detachEvent('onclick');
	if (this.activeTab!=null && this.activeTab!=iTab) {
		this.tabs[this.activeTab].div.style.top=0;
		this.tabs[this.activeTab].attachEvent('onmouseout');
		this.tabs[this.activeTab].attachEvent('onmouseover');
		this.tabs[this.activeTab].attachEvent('onclick');
		this.tabs[this.activeTab].div.style.cursor='';
	}
	var iActive = this.activeTab;
	this.activeTab = iTab;
	if (iActive!=iTab && this.tabs[iTab].onactivate)
		this.tabs[iTab].onactivate(this, iTab);
}

function Tab__mouseover(evt, w) {
	w.div.className = 'tab over';
}

function Tab__mouseout(evt, w) {
	w.div.className = 'tab';
}