
function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [parseInt(result[1], 16),parseInt(result[2], 16),parseInt(result[3], 16)] : null;
}

function rgbToHex(r, g, b) {
    return (1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1);
}

function hueToRgb(p, q, t) {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
}

function hslToRgb(h, s, l) {
    let r, g, b;

    if (s === 0) {
        r = g = b = l; // achromatic
    } else {
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;
        r = hueToRgb(p, q, h + 1 / 3);
        g = hueToRgb(p, q, h);
        b = hueToRgb(p, q, h - 1 / 3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function rgbToHsl(r, g, b) {
    (r /= 255), (g /= 255), (b /= 255);
    const vmax = Math.max(r, g, b), vmin = Math.min(r, g, b);
    let h, s, l = (vmax + vmin) / 2;

    if (vmax === vmin) {
        return [0, 0, l]; // achromatic
    }

    const d = vmax - vmin;
    s = l > 0.5 ? d / (2 - vmax - vmin) : d / (vmax + vmin);
    if (vmax === r) h = (g - b) / d + (g < b ? 6 : 0);
    if (vmax === g) h = (b - r) / d + 2;
    if (vmax === b) h = (r - g) / d + 4;
    h /= 6;

    return [h, s, l];
}

function hslToHex(h, s, l) {
    let [r, g, b] = hslToRgb(h, s, l);
    return rgbToHex(r, g, b);
}

function getColorPallette(hexcolor) {
    let [r, g, b] = hexToRgb(hexcolor)
    let [h, s, l] = rgbToHsl(r, g, b);

    return [hslToHex(h, .60, 0.80), hslToHex(h, 1.0, 0.35)]
}

function formatCurrency(currency, number) {
    const formatter = new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: currency
    })
    return formatter.format(number)
}

$.fn.customTagEditor = function() {
    let tags = []

    $.get('/api/get-tags').done(data => {
        tags = data.map(o => o.name)
        this.tagEditor({
            placeholder: "Enter tags...",
            forceLowercase: true,
            maxTags: 10,
            maxLength: 25,
            delimiter:",",
            autocomplete: {
                delay: 0,
                position: { collision: 'flip' }, // automatic menu position up/down
                source: tags
            }
        })
    }).fail(function(err){
        registry.error(`Call to /api/get-tags endpoint failed: ${err}`, true)
    })
};

$.fn.Chart = function(configuration) {
    return new Chart(this[0], configuration)
}

function cumsum(array) {
    return _.reduce(array, (r, a) => _.concat(r, [((r.length && r[r.length - 1]) || 0) + a]), []);
}

function toLastDay(string) {
    let l = string.split('-').length
    let obj = new Date(string)
    if (l == 1) {
        obj = new Date(obj.setDate(1))
        obj = new Date(obj.setMonth(0))
        obj = new Date(obj.setFullYear(obj.getFullYear() + 1))
        obj = new Date(obj.setDate(0))
    }
    else if (l == 2) {
        obj = new Date(obj.setDate(1))
        obj = new Date(obj.setMonth(obj.getMonth() + 1))
        obj = new Date(obj.setDate(0))
    }
    return obj
}

var _callbackPopup;

function viewerCallback(obj, parse, format, styleFormatter, callback, spk = '') {
    let target = $(obj).parent().children('div')
    if ($(obj).parent().hasClass('editable')) {
        if (target.html().endsWith('<br>')) {
            target.html(target.html().slice(0, -4))
        }
        $(obj).parent().removeClass('editable')
        $(obj).parent().children('i').addClass('fa-pen')
        let result = parse(target.html())
        if (result !== undefined && (typeof result !== "number" || !isNaN(result))) {
            callback(result)
            $(obj).parent().attr('style', styleFormatter(result))
            result = format(result)
        }
        else {
            result = $(obj).parent().attr('old')
        }
        target.html(result)
        target.attr('contenteditable', 'false')
    }
    else {
        $(obj).parent().addClass('editable')
        $(obj).parent().attr('old', target.html())
        if (spk === 'currency') {
            target.html(target.html().replace(/[^0-9\-\/\.]/g,''))
        }
        $(obj).parent().children('i').removeClass('fa-pen')
        target.attr('contenteditable', 'true')
        target.focus()
    }
}

$.viewer = function(value, parse, format = (value) => value, styleFormatter = (value) => '', cw = ( text ) => {}, spk = '') {
    let callback = `viewerCallback(this, ${parse}, ${format}, ${styleFormatter}, ${cw}, '${spk}')`
    let formatter = eval(format)
    let parser = eval(parse)
    let styleFormatter2 = eval(styleFormatter)

    return `
        <div class="viewer-editable" style="${styleFormatter2(value)}"><div style="width: 100%;text-align: left;" onfocusout="javascript:${callback}" onkeypress="if(event.keyCode == 13) { $(this).blur(); return false; }">${formatter(value)}</div><gap></gap><i class="fa-solid fa-pen" onclick="javascript:${callback}"></i></div>
    `
}

$.amountViewer = function(currency, value, cw = ( amount ) => {}) {
    return $.viewer(value,
        `(value) => parseFloat(value)`,
        `(value) => formatCurrency('${currency}', value)`,
        `(value) => (value > 0.0) ? 'color: #56b84b' : 'color: #bf3b44'`,
        cw,
        'currency'
    )
}

$.dateViewer = function(date, require, cw = ( date ) => {}) {
    return $.viewer(date,
        (require) ? 
            `(value) => { let m = moment(value, 'DD/MM/YYYY'); if (!m.isValid()) return undefined; return m.format('YYYY-MM-DD'); }` :
            `(value) => { let m = moment(value, 'DD/MM/YYYY'); if (!m.isValid()) return null; return m.format('YYYY-MM-DD'); }`,
        `(value) => (value == null) ? '\u2014' : moment(value, 'YYYY-MM-DD').format('DD/MM/YYYY')`,
        `(value) => ''`,
        cw
    )
}

$.codeViewer = function(code, cw = (code) => {}) {
    // WARNING : XSS here, make sure that the value is correctly sanitize on the server !!
    return $.viewer(code,
        `(value) => _.unescape(value)`,
        `(value) => _.escape(value)`,
        `(value) => 'font-family: DejaVuSansMono;font-size: 13px;'`,
        cw,
        'code'
    )
}

$.popup = function(title, body, callback, button = ['OK', 'Cancel'], icon = undefined) {
    _callbackPopup = callback;
    let str = ""
    if (icon) {
        str = `
            <div class="icon"><i class="fa-solid fa-circle-${icon}"></i></div>
        `
    }
    $('#popupBinder').show()
    $('#popupBinder > .content').html(`
        <div class="title">${_.escape(title)}<span class="stretch"></span><i class="fa-solid fa-xmark" onclick="javascript:popupEnd(undefined)"></i></div>
        ${str}
        <div class="body">${body}</div>
        <div class="footer">
            ${ 
                button.map(function (name) {
                    var class_add = '';
                    switch (name) {
                        case 'Delete':
                            class_add = 'red-button'
                            break;
                    
                        case 'Create':
                        case 'Edit':
                            class_add = 'green-button';

                        default:
                            break;
                    }
                    return '<button class="button-58 sml-btn min-w-no h-auto '+ class_add +'" id="btn-'+name+'" style="padding: 5px 22px;" onclick="javascript:popupEnd(\''+name+'\')">' + _.escape(name) + '</button>'
                }).join(' ') 
            }
        </div>
        <script>
            function popupEnd(param) {
                $('#popupBinder').hide()
                _callbackPopup(param)
            }
        </script>
    `)
}

var counter = 0
var activeNotif = false
var nextNotif = []

$.dropNotif = function(id) {
    $(`#${id}`).hide('drop', { direction: 'rigth' }, 600, () => {
        $(`#${id}`).remove()
    })
}

$.pushNotif = function(type, content) {
    if (activeNotif) {
        nextNotif.push([type, content])
        return
    }
    activeNotif = true
    
    var uid = ++counter
    let elem = ''

    if (type == 'Error') {
        elem = `
        <div class="notification-entry notification-error" style="display:none;" id="notifId${uid}">
            <span>Error</span>
            ${_.escape(content)}
        </div>`
    }
    else if (type == 'Success') {
        elem = `
        <div class="notification-entry notification-success" style="display:none;" id="notifId${uid}">
            <span>Success</span>
            ${_.escape(content)}
        </div>`
    }

    $('#notificationStatic').html($('#notificationStatic').html() + elem)
    $(`#notifId${uid}`).show('drop', { direction: 'up' }, 600, () => {
        activeNotif = false
        if (nextNotif.length > 0) {
            let [type, content] = nextNotif.pop()
            $.pushNotif(type, content)
        }
    })

    setTimeout(() => {
        $.dropNotif('notifId' + uid)
    }, 4000);
}

function matchName(e) {
    if (e.key == ' ') {
        e.preventDefault()
        $(e.target).val($(e.target).val() + '_')
    } 
    return /[a-zA-Z0-9\u00C0-\u017F\_]/.test(e.key);
}

function getDescendantProp(obj, desc) {
    var arr = desc.split(".");
    while(arr.length && (obj = obj[arr.shift()]));
    return obj;
}
