/************************
Tree node
************************/

function TreeNode(params) {
	params = params || {};
	params.display = 'none';
	params.padding = '13,0,1,1';
	params.onmousedown = QuiX.cancelDefault;
	
	this.base = Widget;
	this.base(params);

	this.isExpanded = false;
	this._hasChildren = (params.haschildren=='true' || params.haschildren==true)?true:false;
	this.img = params.img || null;
	
	if (params.imgheight)
		this.imgHeight = parseInt(params.imgheight);
	if (params.imgwidth)
		this.imgWidth = parseInt(params.imgwidth);
	
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
	this._putImage();
}

QuiX.constructors['treenode'] = TreeNode;
TreeNode.prototype = new Widget;

TreeNode.prototype.appendChild = function (w) {
	w.tree = this.tree;
	w.div.style.margin = '2px 0px 0px ' + this.tree.levelpadding + 'px';
	Widget.prototype.appendChild(w, this);
	if (!w._isDisabled)
		w.enable();
}

TreeNode.prototype._putImage = function() {
	if (this.img) {
		if (this._imgElement != null) {
			if (this._imgElement.src != this.img)
				this._imgElement.src = this.img;
		}
		else {
			var nm = QuiX.getImage(this.img);
			nm.border = 0;
			nm.style.verticalAlign = 'middle';
			nm.style.marginRight = '4px';
			
			if (this.imgHeight)
				nm.style.height = this.imgHeight + 'px';
			if (this.imgWidth)
				nm.style.width = this.imgWidth + 'px';
			
			this.anchor.insertBefore(nm, this.anchor.firstChild);
			this._imgElement = nm;
		}
	}
	else {
		if (this._imgElement) {
			QuiX.removeNode(this._imgElement);
			this._imgElement = null;
		}
	}
}

TreeNode.prototype.redraw = function(bForceAll) {
	this._putImage();
	if (this.hasChildren())
		this._addExpandImg();
	if (this.parent instanceof TreeNode) {
		//sub node
		if (!this.parent._hasChildren) {
			this.parent._addExpandImg();
			this.parent._hasChildren = true;
		}
		if (this.parent.isExpanded)
			this.show();
		else
			this.hide();
	}
	else {
		// root node
		this.show();
	}
	Widget.prototype.redraw.apply(this, arguments);
}

TreeNode.prototype._updateParent = function() {
	var p = this.parent;
	if (p instanceof TreeNode && p.childNodes.length == 1) {
		p._removeExpandImg();
		p._hasChildren = false;
	}
}

TreeNode.prototype.destroy = function() {
	this._updateParent();
	var tree = this.tree; 
	Widget.prototype.destroy.apply(this, arguments);
	if (tree.selectedWidget && tree.selectedWidget.div == null)
		tree.selectedWidget = null;
}

TreeNode.prototype.detach = function() {
	this._updateParent();
	Widget.prototype.detach.apply(this, arguments);
}

TreeNode.prototype._addExpandImg = function() {
	if (this._expandImg == null) {
		var oTreeNode = this;
		this.setPadding([0,0,1,1]);

		var img;
		if (this.isExpanded)
			img = QuiX.getImage('__quix/images/collapse.gif');
		else
			img = QuiX.getImage('__quix/images/expand.gif');
		img.onclick = function(evt){
			oTreeNode.toggle()
			QuiX.stopPropag(evt || event);
		};
		img.style.marginRight = '4px';
		img.style.verticalAlign = 'middle';
		this.div.insertBefore(img, this.div.firstChild);
		this._expandImg = img;
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
	return this.anchor.lastChild.data;
}

TreeNode.prototype.setCaption = function(sCaption) {
	if (this.anchor.lastChild)
		QuiX.removeNode(this.anchor.lastChild);
	this.anchor.appendChild(document.createTextNode(sCaption));
}

TreeNode.prototype.toggle = function() {
	this.isExpanded = !this.isExpanded;
	if (this.isExpanded) {
		this._expandImg.src = '__quix/images/collapse.gif';
		for (var i=0; i < this.childNodes.length; i++) {
			this.childNodes[i].show();
		}
		if (this.tree._customRegistry.onexpand)
			this.tree._customRegistry.onexpand(this);
	}
	else {
		this._expandImg.src = '__quix/images/expand.gif';
		for (var i=0; i < this.childNodes.length; i++) {
			this.childNodes[i].hide();
		}
	}
}

TreeNode.prototype.hasChildren = function() {
	return this._hasChildren || this.childNodes.length > 0;
}

TreeNode.prototype.disable = function() {
	if (this.anchor) {
		this.anchor.className = 'disabled';
		this.anchor.onclick = null;
	}
	Widget.prototype.disable.apply(this, arguments);
}

TreeNode.prototype.enable = function() {
	var oTreeNode = this;
	this.anchor.className = '';
	this.anchor.onclick = function(){oTreeNode.tree.selectNode(oTreeNode)};
	Widget.prototype.enable.apply(this, arguments);
}

/************************
Tree
************************/

function Tree(params) {
	this.base = Widget;
	this.base(params);
	
	this.div.className = 'tree';
	if (params)
		this.levelpadding = params.levelpadding || 14;
	
	this.selectedWidget = null;
	this.roots = this.widgets;
}

QuiX.constructors['tree'] = Tree;
Tree.prototype = new Widget;

Tree.prototype.customEvents =
	Widget.prototype.customEvents.concat(['onexpand', 'onselect']);

Tree.prototype.appendChild = function (w) {
	w.tree = this;
	Widget.prototype.appendChild(w, this);
	if (!w._isDisabled)
		w.enable();
}

Tree.prototype.selectNode = function(w) {
	if (this.selectedWidget)
		this.selectedWidget.anchor.className = '';
	w.anchor.className = 'selected';
	this.selectedWidget = w;
	if (this._customRegistry.onselect)
		this._customRegistry.onselect(w);
}

Tree.prototype.getSelection = function() {
	return this.selectedWidget;
}

/************************
Folder tree
************************/

function FolderTree(params) {
	this.base = Tree;
	this.base(params);

	this.method = params.method;
	this._onexpand = this._customRegistry.onexpand;
	this.attachEvent('onexpand', this.loadSubfolders);
}

QuiX.constructors['foldertree'] = FolderTree;
FolderTree.prototype = new Tree;

FolderTree.prototype.loadSubfolders = function(treeNode) {
	var sID = treeNode.getId() || '';
	var xmlrpc = new XMLRPCRequest(QuiX.root + sID);
	xmlrpc.oncomplete = treeNode.tree.load_oncomplete;
	xmlrpc.callback_info = treeNode;
	xmlrpc.callmethod(treeNode.tree.method);
	for (var i=0; i< treeNode.childNodes.length; i++ ) {
		treeNode.childNodes[i].hide();
	}
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
		//custom attributes
		if (oFolders[i].attributes) {
			for (var attr in oFolders[i].attributes){
				newNode.attributes[attr] = oFolders[i].attributes[attr];
			}
		}
		treeNode.appendChild(newNode);
		newNode.redraw();
	}
	if (treeNode.tree._onexpand)
		treeNode.tree._onexpand(treeNode);
}
