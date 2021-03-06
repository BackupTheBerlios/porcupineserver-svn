/************************
Windows & Dialogs
************************/

// generic event handlers

function __closeDialog__(evt, w) {
    w.getParentByType(QuiX.ui.Window).close();
}

// window

QuiX.ui.Window = function(/*params*/) {
    var params = arguments[0] || {};
    var overflow = params.overflow;
    var padding = params.padding;
    var bgcolor = params.bgcolor;
    var hasStatus = (params.status == "true" || params.status == true);
    params.border = QuiX.theme.window.border;
    params.padding = QuiX.theme.window.padding;
    delete params.bgcolor;
    params.opacity = (QuiX.effectsEnabled)? 0:1;
    params.onmousedown = QuiX.wrappers.eventWrapper(
        QuiX.ui.Window._onmousedown,
        params.onmousedown);
    params.oncontextmenu = QuiX.wrappers.eventWrapper(
        QuiX.ui.Window._oncontextmenu,
        params.oncontextmenu);
    params.overflow = (QuiX.utils.BrowserInfo.family == 'moz'
        && QuiX.utils.BrowserInfo.OS == 'MacOS')? 'auto':'hidden';

    // adjust width and height based on theme
    var arrPad = params.padding.split(',');
    params.height = parseInt(params.height) +
                    QuiX.theme.window.title.height +
                    ((hasStatus)? QuiX.theme.window.status.height:0) +
                    2 * params.border +
                    parseInt(arrPad[2]) + parseInt(arrPad[3]) +
                    2 * QuiX.theme.window.body.border;
    params.width = parseInt(params.width) +
                   2 * params.border +
                   parseInt(arrPad[0]) + parseInt(arrPad[1]) +
                   2 * QuiX.theme.window.body.border;

    this.base = QuiX.ui.Widget;
    this.base(params);
    this.minw = params.minw || 120;
    this.minh = params.minh || 26;
    this.isMinimized = false;
    this.isMaximized = false;
    this.childWindows = [];
    this.opener = null;
    this._statex = 0;
    this._statey = 0;
    this._statew = 0;
    this._stateh = 0;
    this._childwindows = [];
    this.div.className = 'window';
    var box = new QuiX.ui.Box({
        width : '100%',
        height : '100%',
        orientation : 'v',
        spacing : 0
    });
    this.appendChild(box);
    this.title = QuiX.theme.window.title.get(params.title, params.img);
    this.title.div.className = 'header';
    box.appendChild(this.title);

    // attach events
    var self = this;

    this.title.getWidgetById('_t').attachEvent(
        'onmousedown',
        QuiX.ui.Window._titleonmousedown);
    this.title.getWidgetById('_t').attachEvent('ondblclick',
        function() {
            if (!self.isMinimized)
                self.maximize();
        });

    this.title.getWidgetById('c0').attachEvent('onclick',
        function() {
            if (self.buttonIndex)
                self.buttonIndex = -1;
            self.close();
        });
    this.title.getWidgetById('c1').attachEvent('onclick',
        function() {
            self.maximize();
        });
    this.title.getWidgetById('c2').attachEvent('onclick',
        function() {
            self.minimize();
        });
    var canClose = (params.close == 'true' || params.close == true);
    var canMini = (params.minimize == 'true' || params.minimize == true);
    var canMaxi = (params.maximize == 'true' || params.maximize == true);
    if (!canMini)
        this.title.getWidgetById('c2').hide();
    if (!canMaxi) {
        this.title.getWidgetById('c1').hide();
        this.title.getWidgetById('_t').detachEvent('ondblclick');
    }
    if (!canClose)
        this.title.getWidgetById('c0').hide();

    // client area
    this.body = new QuiX.ui.Widget({
        border : QuiX.theme.window.body.border,
        overflow : overflow,
        padding : padding,
        bgcolor: bgcolor
    });
    this.body.div.className = 'body';
    box.appendChild(this.body);

    // status
    if (hasStatus)
        this.addStatusBar();

    // resize handle
    var resizable = (params.resizable == "true" || params.resizable == true);
    this.setResizable(resizable);

    // effects
    if (QuiX.effectsEnabled) {
        var effect = new QuiX.ui.Effect({
            id : '_eff_fade',
            type : 'fade-in',
            auto : true,
            steps : 4
        });
        this.appendChild(effect);
        var mini_effect = new QuiX.ui.Effect({
            id : '_eff_mini',
            type : 'wipe-out',
            interval : 10,
            end : 0.1,
            steps : 8,
            oncomplete : QuiX.ui.Window._onminimize
        });
        this.appendChild(mini_effect);
        var maxi_effect = new QuiX.ui.Effect({
            id : '_eff_maxi',
            type : 'wipe-in',
            interval : 10,
            steps : 8,
            oncomplete : QuiX.ui.Window._onmmaximize
        });
        this.appendChild(maxi_effect);
    }
}

QuiX.constructors['window'] = QuiX.ui.Window;
QuiX.ui.Window.prototype = new QuiX.ui.Widget;
QuiX.ui.Window.prototype.customEvents =
    QuiX.ui.Widget.prototype.customEvents.concat(['onclose']);

QuiX.ui.Window.prototype.setIcon = function(sUrl) {
    var icon = this.title.getWidgetById('_t');
    icon.setImageURL(sUrl);
    icon.redraw(true);
}

QuiX.ui.Window.prototype.getIcon = function() {
    var icon = this.title.getWidgetById('_t');
    return icon.getImageURL();
}

QuiX.ui.Window.prototype.setResizable = function(bResizable) {
    var oWindow = this;
    if (bResizable && !this._resizer) {
        this._resizer = QuiX.theme.window.resizer.get();
        this.appendChild(this._resizer);
        this._resizer.div.className = 'resize';
        this._resizer.div.style.zIndex = QuiX.maxz; //stay on top
        this._resizer.attachEvent('onmousedown',
            function(evt){
                oWindow._startResize(evt);
                QuiX.cancelDefault(evt);
                QuiX.stopPropag(evt);
            });
    }
    else if (!bResizable && this._resizer) {
        this._resizer.destroy();
        this._resizer = null;
    }
}

QuiX.ui.Window.prototype.addControlButton = function(iWhich) {
    var oButton = this.title.getWidgetById('c' + iWhich.toString());
    oButton.show();
    this.title.redraw();
}

QuiX.ui.Window.prototype.removeControlButton = function(iWhich) {
    var oButton = this.title.getWidgetById('c' + iWhich.toString());
    oButton.hide();
    this.title.redraw();
}

QuiX.ui.Window.prototype.close = function() {
    QuiX.cleanupOverlays();
    if (this._customRegistry.onclose)
        QuiX.getEventListener(this._customRegistry.onclose)(this);
    while (this.childWindows.length != 0)
        this.childWindows[0].close();
    if (this.opener && this.opener.childWindows)
        this.opener.childWindows.removeItem(this);
    if (QuiX.effectsEnabled) {
        var self = this;
        var eff = this.getWidgetById('_eff_fade', true);
        eff.attachEvent('oncomplete', function() {
            self.destroy();
        });
        eff.play(true);
    }
    else	
        this.destroy();
}

QuiX.ui.Window.prototype.setTitle = function(s) {
    var icon = this.title.getWidgetById('_t');
    icon.setCaption(s);
}

QuiX.ui.Window.prototype.getTitle = function() {
    var icon = this.title.getWidgetById('_t');
    return icon.getCaption();
}

QuiX.ui.Window.prototype.addStatusBar = function() {
    if (!this.statusBar) {
        this.statusBar = QuiX.theme.window.status.get();
        this.statusBar.div.className = 'status';
        this.widgets[0].appendChild(this.statusBar);
    }
}

QuiX.ui.Window.prototype.removeStatusBar = function() {
    if (this.statusBar) {
        this.statusBar.destroy();
        this.statusBar = null;
        this.redraw();
    }
}

QuiX.ui.Window.prototype.setStatus = function(s) {
    if (this.statusBar)
        this.statusBar.setCaption(s);
}

QuiX.ui.Window.prototype.getStatus = function() {
    if (this.statusBar)
        return this.statusBar.getCaption();
    else
        return null;
}

QuiX.ui.Window.prototype.minimize = function() {
    var w = this,
        maxControl = w.title.getWidgetById('c1'),
        minControl = w.title.getWidgetById('c2'),
        childWindow,
        effect;
    if (minControl) {
        w.isMinimized = !w.isMinimized;
        if (w.isMinimized) {
            var i;
            var padding = w.getPadding();
            if (w._resizer)
                w._resizer.hide();
            w._stateh = w.getHeight(true);
            w.height = w.title.getHeight(true) + 2*w.getBorderWidth() +
                padding[2] + padding[3];
            if (maxControl)
                maxControl.disable();
            for (i=0; i<w.childWindows.length; i++) {
                childWindow = w.childWindows[i];
                if (!childWindow.isHidden()) {
                    childWindow.hide();
                    w._childwindows.push(childWindow);
                }
            }
            if (QuiX.effectsEnabled) {
                effect = w.getWidgetById('_eff_mini', true);
                effect.play();
            }
            else {
                w.redraw();
            }
        }
        else {
            w.bringToFront();
            w.height = w._stateh;
            if (QuiX.effectsEnabled) {
                effect = w.getWidgetById('_eff_maxi', true);
                effect.play();
            }
            else {
                QuiX.ui.Window._onmmaximize(w);
            }
            w.redraw();
            
            if (maxControl)
                maxControl.enable();
        }
    }
}

QuiX.ui.Window.prototype.maximize = function() {
    var w = this;
    var maxControl = w.title.getWidgetById('c1');
    var minControl = w.title.getWidgetById('c2');
    if (maxControl) {
        if (!w.isMaximized) {
            w._statex = w._calcLeft();
            w._statey = w._calcTop();
            w._statew = w._calcWidth(true);
            w._stateh = w._calcHeight(true);
            w.top = 0; w.left = 0;
            w.height = '100%';
            w.width = '100%';
            if (minControl)
                minControl.disable();
            if (w._resizer)
                w._resizer.disable();
            w.title.getWidgetById('_t').detachEvent('onmousedown');
            w.isMaximized = true;
        }
        else {
            w.top = w._statey;
            w.left = w._statex;
            w.width = w._statew;
            w.height = w._stateh;
            if (minControl)
                minControl.enable();
            if (w._resizer)
                w._resizer.enable();
            w.title.getWidgetById('_t').attachEvent('onmousedown');
            w.isMaximized = false;
        }
        w.redraw();
    }
}

QuiX.ui.Window.prototype.bringToFront = function() {
    QuiX.cleanupOverlays();
    if (this.div.style.zIndex < this.parent.maxz) {
        var sw, dt, i;
        var macff = (QuiX.utils.BrowserInfo.family == 'moz' &&
                     QuiX.utils.BrowserInfo.OS == 'MacOS');
        QuiX.ui.Widget.prototype.bringToFront.apply(this, arguments);
        if (macff) {
            dt = document.desktop;
            //hide scrollbars
            sw = dt.query('/(auto|scroll)/.exec(w.getOverflow()) != param',
                          null);
            for (i=0; i<sw.length; i++) {
                if (sw[i] != this.parent)
                    sw[i].div.style.overflow = 'hidden';
            }
            //restore scrollbars
            for (i=0; i<sw.length; i++)
                sw[i].setOverflow(sw[i]._overflow);
        }
    }
}

QuiX.ui.Window.prototype.showWindow = function(sUrl, oncomplete) {
    var oWin = this;
    this.parent.parseFromUrl(sUrl,
        function(w) {
            oWin.childWindows.push(w);
            w.opener = oWin;
            if (oncomplete) oncomplete(w);
        }
    );
}

QuiX.ui.Window.prototype.showWindowFromString = function(s, oncomplete) {
    var oWin = this;
    this.parent.parseFromString(s, 
        function(w) {
            oWin.childWindows.push(w);
            w.opener = oWin;
            if (oncomplete) oncomplete(w);
        }
    );
}

QuiX.ui.Window._titleonmousedown = function(evt, w) {
    QuiX.cleanupOverlays();
    QuiX.stopPropag(evt);
    QuiX.cancelDefault(evt);
    w.parent.parent.parent.bringToFront();
    w.parent.parent.parent._startMove(evt);
}

QuiX.ui.Window._onmousedown = function(evt, w) {
    if (QuiX.getMouseButton(evt) == 0) {
        w.bringToFront();
        QuiX.stopPropag(evt);
    }
    QuiX.cancelDefault(evt);
    QuiX.cleanupOverlays();
}

QuiX.ui.Window._oncontextmenu = function(evt, w) {
    QuiX.stopPropag(evt);
    return false;
}

QuiX.ui.Window._onminimize = function(eff) {
    eff.parent.div.style.clip = 'rect(auto,auto,auto,auto)';
    eff.parent.redraw();
}

QuiX.ui.Window._onmmaximize = function(w) {
    if (!(w instanceof QuiX.ui.Window))
        w = w.parent;
    if (w._resizer)
        w._resizer.show();
    while (w._childwindows.length > 0) {
        childWindow = w._childwindows.pop();
        childWindow.show();
    }
}

// dialog

QuiX.ui.Dialog = function(/*params*/) {
    var params = arguments[0] || {};
    var stat = params.status || false;
    var resizable = params.resizable || false;

    params.status = false;
    params.resizable = false;
    params.onkeypress = QuiX.ui.Dialog._onkeypress;

    this.base = QuiX.ui.Window;
    this.base(params);

    this.footer = new QuiX.ui.Widget({
        height : 32,
        padding : '0,0,0,0',
        overflow : 'hidden',
        onclick : QuiX.stopPropag
    });
    this.widgets[0].appendChild(this.footer);

    this.buttonHolder = new QuiX.ui.Widget({
        top : 0,
        height : '100%',
        width : 0,
        border : 0,
        overflow:'hidden'
    });
    this.buttonHolder.redraw = QuiX.ui.Dialog._buttonHolderRedraw;

    this.setButtonsAlign(params.align);
    this.footer.appendChild(this.buttonHolder);
    this.buttons = this.buttonHolder.widgets;

    //status
    if (stat.toString() == 'true')
        this.addStatusBar();

    // resize handle
    if (resizable.toString() == 'true')
        this.setResizable(true);

    this.buttonIndex = -1;
    this.defaultButton = null;
}

QuiX.constructors['dialog'] = QuiX.ui.Dialog;
QuiX.ui.Dialog.prototype = new QuiX.ui.Window;

QuiX.ui.Dialog._calcButtonHolderLeft = function(memo) {
    return this.parent.getWidth(false, memo) - this.getWidth(true, memo);
}

QuiX.ui.Dialog.prototype.setButtonsAlign = function(sAlign) {
    var left;
    switch (sAlign) {
        case 'left':
            left = 0;
            break;
        case 'center':
            left = 'center';
            break;
        default:
            left = QuiX.ui.Dialog._calcButtonHolderLeft;
    }
    this.buttonHolder.left = left;
    this.buttonHolder.redraw();
}

QuiX.ui.Dialog.prototype.addButton = function(params) {
    params.top = 'center';
    var oWidget = new QuiX.ui.DialogButton(params, this);
    this.buttonHolder.appendChild(oWidget);
    this.buttonHolder.redraw();
    if (params['default'] == 'true') {
        this.defaultButton = oWidget;
        this.defaultButton.widgets[0].div.className += ' default';
    }
    return oWidget;
}

QuiX.ui.Dialog._onkeypress = function(evt, w) {
    if (evt.keyCode == 13 && w.defaultButton)
        w.defaultButton.click();
    else if (evt.keyCode == 27 && w.title.getWidgetById('c0'))
        w.close();
}

QuiX.ui.Dialog._buttonHolderRedraw = function(bForceAll /*, memo*/) {
    var memo = arguments[1] || {};
    var iOffset = 0;
    for (var i=0; i<this.widgets.length; i++) {
        this.widgets[i].left = iOffset;
        iOffset += this.widgets[i]._calcWidth(true, memo) + 8;
    }
    this.width = iOffset;
    QuiX.ui.Widget.prototype.redraw.apply(this, [bForceAll, memo]);
}

// dialog button

QuiX.ui.DialogButton = function(params, dialog) {
    this.base = QuiX.ui.Button;
    this.base(params);
    this.dialog = dialog;
}

QuiX.ui.DialogButton.prototype = new QuiX.ui.Button;

QuiX.ui.DialogButton.prototype._registerHandler =
function(eventType, handler, isCustom) {
    var wrapper;
    if (handler && handler.toString().lastIndexOf(
            'return handler(evt || event, self)') == -1)
        wrapper = function(evt, w) {
            w.dialog.buttonIndex = w.dialog.buttons.indexOf(w);
            handler(evt, w);
        }
    wrapper = wrapper || handler;
    QuiX.ui.Widget.prototype._registerHandler.apply(this,
        [eventType, wrapper, isCustom]);
}
