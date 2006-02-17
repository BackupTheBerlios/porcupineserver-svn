/************************
Tree control
************************/

function TreeNode(params, p) {
	params = params || {};
	params.display = 'none';
	params.padding = '0,0,1,1';
	this.base = Widget;
	this.base(params);

	this.caption = params.caption;
	this.isExpanded = false;
	this.hasChildren = (params.haschildren=='true' || params.haschildren==true)? true:false;
	this.img = params.img;
	this.childNodes = this.widgets;

	this.div.className = 'treenode';
	this.div.style.whiteSpace = 'nowrap';
	this.setPosition();

	if (p instanceof TreeNode) {
		//sub node
		this.tree = p.tree;
		if (!p.hasChildren) p._addExpandImg();
		this.div.style.marginTop = '2px';
		this.div.style.marginLeft = this.tree.levelpadding + 'px';
	}
	else {
		// root node
		this.tree = p;
		this.setDisplay();
	}
	
	var oTree = this.tree;
	var oTreeNode = this;
	
	if (this.hasChildren) {
		this._addExpandImg();
	}
	else {
		var padding = this.getPadding();
		padding[0] = 13;
		this.setPadding(padding);
	}
	
	if (this.img) {
		var nm = QuiX.getImage(params.img);
		nm.border = 0;
		nm.style.verticalAlign = 'middle';
		nm.style.marginRight = '4px';
		this.div.appendChild(nm);
	}
	var oA = ce('A');
	oA.href = 'javascript:void(0)';
	oA.innerHTML = this.caption;
	
	this.div.appendChild(oA);
	this.anchor = oA;
	
	p.appendChild(this);
	if (this._isDisabled) this.disable();
	else this.enable();
}

TreeNode.prototype = new Widget;

TreeNode.prototype._addExpandImg = function() {
	var oTreeNode = this;
	var padding;
	var img = QuiX.getImage('images/expand.gif');
	img.onclick = function(){oTreeNode.toggle()};
	img.style.marginRight = '4px';
	img.style.verticalAlign = 'middle';
	
	if (!this.div.hasChildNodes)
		this.div.appendChild(img);
	else
		this.div.insertBefore(img, this.div.firstChild);
	
	this.attachEvent('ondblclick', function(evt){
		oTreeNode.toggle();
		QuiX.stopPropag(evt);
	});
	this.hasChildren = true;
	padding = this.getPadding();
	padding[0] = 0;
	this.setPadding(padding);
}

TreeNode.prototype.toggle = function() {
	if (!this.isExpanded) {
		if (this.tree.onexpand) this.tree.onexpand(this);
		for (var i=0; i < this.childNodes.length; i++) {
			this.childNodes[i].setDisplay();
		}
		this.div.childNodes[0].src = 'images/collapse.gif';
	}
	else {
		for (var i=0; i < this.childNodes.length; i++) {
			this.childNodes[i].setDisplay('none');
		}
		this.div.childNodes[0].src = 'images/expand.gif';
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


function Tree(params) {
	this.base = Widget;
	this.base(params);
	
	this.div.className = 'tree';
	if (params) {
		this.levelpadding = params.levelpadding || 14;
		this.onexpand = getEventListener(params.onexpand);
		this.onselect = getEventListener(params.onselect);
	}
	this.selectedWidget = null;
	this.roots = this.widgets;
}

Tree.prototype = new Widget;

Tree.prototype.selectNode = function(w) {
	if (this.selectedWidget) this.selectedWidget.anchor.className = '';
	w.anchor.className = 'selected';
	this.selectedWidget = w;
	if (this.onselect) this.onselect(w);
}

Tree.prototype.getSelection = function() {
	var retVal = (this.selectedWidget)? this.selectedWidget:this.roots[0];
	return(retVal);
}

function FolderTree(params) {
	this.base = Tree;
	this.base(params);

	this.method = params.method;
	this._onexpand = this.onexpand;
	this.onexpand = this.loadSubfolders;
}

FolderTree.prototype = new Tree;

FolderTree.prototype.loadSubfolders = function(treeNode) {
	var sID = treeNode.getId() || '';
	var xmlrpc = new XMLRPCRequest(QuiX.root + sID);
	xmlrpc.oncomplete = this.load_oncomplete;
	xmlrpc.callback_info = treeNode;
	xmlrpc.callmethod(this.method);
}

FolderTree.prototype.load_oncomplete = function(req) {
	var newNode;
	var treeNode = req.callback_info;
	var oFolders = req.response;
	while ( treeNode.childNodes.length > 0 ) {
		treeNode.childNodes[0].destroy();
	}
	for (var i=0; i<oFolders.length; i++) {
		newNode = new TreeNode(oFolders[i], treeNode);
		newNode.setDisplay();
	}
	if (this._onexpand) this._onexpand(treeNode);
}