/************************
Tree control
************************/

function TreeNode(params) {
	params = params || {};
	params.display = 'none';
	params.padding = '13,0,1,1';
	this.base = Widget;
	this.base(params);

	this.isExpanded = false;
	this.hasChildren = (params.haschildren=='true' || params.haschildren==true)? true:false;
	this.img = params.img || null;
	this._expandImg = null;
	this._imgElement = null;
	this.childNodes = this.widgets;

	this.div.className = 'treenode';
	this.div.style.whiteSpace = 'nowrap';
	this.setPosition();

	var oA = ce('A');
	oA.href = 'javascript:void(0)';
	this.div.appendChild(oA);
	this.anchor = oA;
	this.setCaption(params.caption || '');
}

TreeNode.prototype = new Widget;

TreeNode.prototype.redraw = function(bForceAll) {
	this.tree = this.parent.tree || this.parent;
	if (this.parent instanceof TreeNode) {
		//sub node
		if (!this.parent.hasChildren)
			this.parent._addExpandImg();
		this.div.style.marginLeft = this.tree.levelpadding + 'px';
		this.div.style.marginTop = '2px';
		if (this.parent.isExpanded)
			this.setDisplay();
	}
	else {
		// root node
		this.setDisplay();
	}

	if (this.hasChildren && this.childNodes.length == 0)
		this._addExpandImg();

	if (this.img) {
		if (this._imgElement!==null)
			this._imgElement.src = this.img;
		else {
			var nm = QuiX.getImage(this.img);
			nm.border = 0;
			nm.style.verticalAlign = 'middle';
			nm.style.marginRight = '4px';
			this.div.insertBefore(nm, this.anchor);
			this._imgElement = nm;
		}
	}
	else {
		if (this._imgElement) {
			QuiX.removeNode(this._imgElement);
			this._imgElement = null;
		}
	}
	if (this._isDisabled)
		this.disable();
	else
		this.enable();

	Widget.prototype.redraw(bForceAll, this);
}

TreeNode.prototype.destroy = function() {
	var p = this.parent;
	Widget.prototype.destroy(this);
	if (p instanceof TreeNode && p.childNodes.length == 0 && !p.hasChildren) {
		p._removeExpandImg();
	}
}

TreeNode.prototype._addExpandImg = function() {
	if (this._expandImg == null) {
		var oTreeNode = this;
		this.setPadding([0,0,1,1]);

		var img = QuiX.getImage('images/expand.gif');
		img.onclick = function(){oTreeNode.toggle()};
		img.style.marginRight = '4px';
		img.style.verticalAlign = 'middle';
		
		this.div.insertBefore(img, this.div.firstChild);
		
		this._expandImg = img;
		this.attachEvent('ondblclick', TreeNode_bdlclick);
	}
}

TreeNode.prototype._removeExpandImg = function() {
	if (this._expandImg) {
		QuiX.removeNode(this._expandImg);
		this._expandImg = null;
		this.setPadding([13,0,1,1]);
	}
}

TreeNode.prototype.getCaption = function() {
	return this.anchor.innerHTML;
}

TreeNode.prototype.setCaption = function(sCaption) {
	this.anchor.innerHTML = sCaption;
}

TreeNode.prototype.toggle = function() {
	if (!this.isExpanded) {
		if (this.tree._customRegistry.onexpand)
			this.tree._customRegistry.onexpand(this);
		for (var i=0; i < this.childNodes.length; i++) {
			this.childNodes[i].setDisplay();
		}
		this._expandImg.src = 'images/collapse.gif';
	}
	else {
		for (var i=0; i < this.childNodes.length; i++) {
			this.childNodes[i].setDisplay('none');
		}
		this._expandImg.src = 'images/expand.gif';
	}
	this.isExpanded = !this.isExpanded;
}

TreeNode.prototype.disable = function() {
	if (this.anchor) {
		this.anchor.className = 'disabled';
		this.anchor.onclick = null;
	}
	Widget.prototype.disable(this);
}

TreeNode.prototype.enable = function() {
	var oTreeNode = this;
	this.anchor.className = '';
	this.anchor.onclick = function(){oTreeNode.tree.selectNode(oTreeNode)};
	Widget.prototype.enable(this);
}

function TreeNode_bdlclick(evt, w) {
	w.toggle();
	QuiX.stopPropag(evt);
}

function Tree(params) {
	this.base = Widget;
	this.base(params);
	
	this.div.className = 'tree';
	if (params)
		this.levelpadding = params.levelpadding || 14;
	
	this.selectedWidget = null;
	this.roots = this.widgets;
}

Tree.prototype = new Widget;

Tree.prototype.customEvents = Widget.prototype.customEvents.concat(['onexpand', 'onselect']);

Tree.prototype.selectNode = function(w) {
	if (this.selectedWidget)
		this.selectedWidget.anchor.className = '';
	w.anchor.className = 'selected';
	this.selectedWidget = w;
	if (this._customRegistry.onselect)
		this._customRegistry.onselect(w);
}

Tree.prototype.getSelection = function() {
	var retVal = (this.selectedWidget)? this.selectedWidget:this.roots[0];
	return(retVal);
}

function FolderTree(params) {
	this.base = Tree;
	this.base(params);

	this.method = params.method;
	this._onexpand = this._customRegistry.onexpand;
	this.attachEvent('onexpand', this.loadSubfolders);
}

FolderTree.prototype = new Tree;

FolderTree.prototype.loadSubfolders = function(treeNode) {
	var sID = treeNode.getId() || '';
	var xmlrpc = new XMLRPCRequest(QuiX.root + sID);
	xmlrpc.oncomplete = treeNode.tree.load_oncomplete;
	xmlrpc.callback_info = treeNode;
	xmlrpc.callmethod(treeNode.tree.method);
}

FolderTree.prototype.load_oncomplete = function(req) {
	var newNode;
	var treeNode = req.callback_info;
	var oFolders = req.response;
	while ( treeNode.childNodes.length > 0 ) {
		treeNode.childNodes[0].destroy();
	}
	for (var i=0; i<oFolders.length; i++) {
		newNode = new TreeNode(oFolders[i]);
		treeNode.appendChild(newNode);
	}
	if (this._onexpand)
		this._onexpand(treeNode);
}