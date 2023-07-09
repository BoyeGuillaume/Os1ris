let load_html = `
<div class="ab-c-m loader">
    <div class="snippet" data-title="dot-pulse">
        <div class="stage">
            <div class="dot-pulse"></div>
        </div>
    </div>
    <span>Loading</span>
</div>
`;

class Page {
    constructor(name, currentTab, state, setupPerTabs) {
        this.name = name
        this.state = state
        this.setupPerTabs = setupPerTabs
        this.currentTab = currentTab
    }

    load(pushHistory = true) {
        $("#mainFrame").html(load_html);
        let state_str = JSON.stringify(this.state)
        $("#topHeaderTabs").html(Object.keys(this.setupPerTabs).map((obj, index) => {
            let js = `registry.goto('${this.name}', ${state_str}, true, '${obj}')`.replaceAll('"', '\'');
            return `<li class="nav-item${(obj == this.currentTab) ? " active" : ""}"><a class="nav-link" href="javascript:${js};">${obj}</a></li>`
        }))
        let params = $.param(this.state)
        if (params.length > 0) {
            params = "?" + params;
        }

        let url = `/index/${this.name}#${this.currentTab}${params}`
        if (pushHistory) {
            history.pushState({ url: window.location.toString() }, this.name, url);
        }
        else {
            history.replaceState({ url: window.location.toString() }, this.name, url);
        }

        // this function is suppose to setup the page
        this.setupPerTabs[this.currentTab](this.state);
    }
}

class PageRegistry {
    constructor() {
        this.pages = {}
    }

    push(name, onSetupPerTabs, id = undefined) {
        this.pages[name] = [onSetupPerTabs, id]
    }

    reload() {
        loadUrl(window.location)
    }

    goto(name, configuration, pushHistory = true, currentTab = undefined) {
        let element = this.pages[name]
        $('.activeSidebar').removeClass('activeSidebar')
        if (element) {
            let [onSetupPerTabs, id] = element
            if (!currentTab) {
                currentTab = Object.keys(onSetupPerTabs)[0]
            }
            new Page(name, currentTab, configuration, onSetupPerTabs).load(pushHistory)
            if (id) {
                let target = $(`#${id(configuration)}`)
                target.addClass('activeSidebar')
                target.parents().filter('li').addClass('activeSidebar')
            }
        }
        else {
            registry.goto('error', { error: `No page "${name}" was found within the registry` });
        }
    }

    error(error, pushHistory = true) {
        registry.goto('error', { error: error }, pushHistory)
    }

    write(html) {
        $("#mainFrame").html(`<div class="page">${html}</div>`); // markdown-body
    }
}

let registry = new PageRegistry()

function loadUrl(url) {
    let page_name = url.pathname
    page_name = page_name.slice(7);
    
    let params = {};
    url.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(str,key,value) {
        params[key] = decodeURIComponent(value);
    });

    let hash = url.hash;
    if (hash.length > 0) {
        let pos = hash.indexOf("?")
        if (pos > 0) {
            hash = hash.substring(1, pos);
        }
        else {
            hash = hash.substring(1);
        }
    }
    
    if (page_name.length > 0) {
        registry.goto(page_name, params, false, (hash.length > 0) ? decodeURIComponent(hash) : undefined)
    }
    else {
        // registry.goto("new-account", {})
    }
}

$(document).ready(function() {
    loadUrl(window.location)
})

window.onpopstate = function(e) {
    let url = e.srcElement.location.toString()
    if (url) {
        loadUrl(new URL(url));
    }
};
