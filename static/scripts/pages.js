// https://codepen.io/NielsVoogt/pen/eYBQpPR
let currency_list = Object.entries(currency).map(([key, value]) => `<option value="${key}">${key} (${value})</option>`).sort().join('')

function staticPageAjax(endpoint, conf) {
    $.ajax({
        url: endpoint
    }).done(function(data) {
        registry.write(data)
    }).fail(function() {
        registry.error(`The AJAX request to ${endpoint} failed`)
    })
}

function staticPage(endpoint, callback) {
    $.ajax({
        url: endpoint
    }).done(callback)
    .fail(function() {
        registry.error(`The AJAX request to ${endpoint} failed`)
    })
}

function fetchData(endpoint, adata, callback) {
    $.get(endpoint, adata, callback, 'json').fail(function(){
        registry.error(`The AJAX request to ${endpoint} failed`)
    })
}

registry.push("new-account", {
    "Create": (state) => {
        registry.write(`
            <div class="nice-form-group std-w">
                <h1>Create new account:</h1>
                <br>
    
                <p>
                    An account is a record used to track financial transactions for an entity. It categorizes and summarizes financial information, enabling accurate reporting and analysis. Accounts are essential for effective financial management and decision-making.
                </p>
    
                <br>
    
                <form action="javascript:submit();">
                <div class="nice-form-group">
                    <label for="name">
                        Name
                        <i class="fa-solid fa-circle-question">
                            <span>The name of the Account to be created</span>
                        </i>
                    </label>
                    <input type="text" id="name" name="name" placeholder="Account Name" maxlength="25" onkeypress="javascript: return matchName(event)" required />
                </div>
                
                <br>
                
                <div class="nice-form-group">
                    <label for="creation_date">
                        Creation Date
                        <i class="fa-solid fa-circle-question">
                            <span>The date when this account was first created</span>
                        </i>
                    </label>
                    <input type="date" id="creation_date" name="creation_date" required />
                </div>
                
                <br>
                
                <div class="nice-form-group">
                    <label for="currency">
                        Currency
                        <i class="fa-solid fa-circle-question">
                            <span>The currency associated with this account</span>
                        </i>
                    </label>
                    
                    <select name="currency" required><option disabled selected value> -- select an option -- </option>${currency_list}</select>
                </div>
                
                <br>
                
                <div class="nice-form-group">
                    <label for="description">
                        Description
                        <i class="fa-solid fa-circle-question">
                            <span>Additional description or notes about this account</span>
                        </i>
                    </label>
                    <textarea id="description" name="description" placeholder="Account Description"></textarea>
                </div>
                
    
                <br>
    
                <div class="nice-form-group">
                    <button class="button-58" type="submit" id="CreateAccount">Create Account</button>
                </div>
                </form>
    
                <script>
                    function submit(){
                        let name = $("input[name='name']").val();
                        let creation_date = $("input[name='creation_date']").val();
                        let currency = $("select[name='currency']").val();
                        let description = $("#description").val();
                        CreateAccount(name, creation_date, currency, description);
                        $("#CreateAccount").prop( "disabled", true );
                    }
                </script>
            </div>
        `);
    }
})

registry.push("view-account", {
    'Overview': (state) => fetchData('/api/get-account', {aid: state.aid}, (data) => {
        registry.write(`
        <div>
            <h1>${_.escape(data.name)} - Overview</h1>

            <br>

            <table class="invisible-table" style="max-width: 70%">
                <tr>
                    <td>Name</td>
                    <td>${_.escape(data.name)}</td>
                </tr>
                <tr>
                    <td>Account Creation</td>
                    <td>${new Date(data.creation_date).toLocaleDateString({ year: "numeric",month: "2-digit",day: "numeric" })}</td>
                </tr>
                <tr>
                    <td>Registration in Osiris</td>
                    <td>${new Date(data.registration_date).toLocaleString({ year: "numeric",month: "2-digit",day: "numeric" })}</td>
                </tr>
                <tr>
                    <td>Last transaction</td>
                    <td>${data.last_transaction_date ? _.escape(new Date(data.last_transaction_date).toLocaleString({ year: "numeric",month: "2-digit",day: "numeric" })) : "Never"}</td>
                </tr>
                <tr>
                    <td>Number of transaction</td>
                    <td>${_.escape(data.number_of_transaction)}</td>
                </tr>
                <tr>
                    <td>Currency</td>
                    <td>${currency[data.currency]} (${_.escape(data.currency)})</td>
                </tr>
                <tr>
                    <td>Description</td>
                    <td>${_.escape(data.description)}</td>
                </tr>
                <tr>
                    <td>Balance</td>
                    <td>${formatCurrency(_.escape(data.currency), parseFloat(data.balance.balance))}</td>
                </tr>
                <tr>
                    <td>Available Balance</td>
                    <td>${formatCurrency(_.escape(data.currency), parseFloat(data.balance.available_balance))}</td>
                </tr>
            </table>
            <h1 class="m-t-65 m-b-25">Evolution</h1>
            <div class="nice-form-group center config-bar">
                <span style="flex-grow: 4;"></span>
                <vertical-bar></vertical-bar>
                <label for="selection">Interval: </label>
                <select name="selection" onchange="javascript:updateChart()">
                    <option fmt="MMM yyyy" title2="Monthly balance" title="Monthly growth" interval="month">Month</option>
                    <option fmt="MMM yyyy" title2="Balance every semester" title="Growth every semester" interval="semester">Semester</option>
                    <option fmt="MMM yyyy" title2="Balance every trimester" title="Growth every trimester" interval="trimester">Trimester</option>
                    <option fmt="MMM yyyy" title2="Yearly balance" title="Yearly growth" interval="year">Year</option>
                    <option fmt="dd MMM yyyy" title2="Daily balance" title="Daily growth" interval="day">Day</option>
                </select>
            </div>
            <div style="width: 80%;" class="center"><canvas id="mainGraph"></canvas></div>
            <div style="width: 80%;" class="center"><canvas id="secondGraph"></canvas></div>
            
            <h1 class="m-t-65 m-b-25">Danger Zone</h1>
            <p style="color: #555">
                All actions within this zone cannot be undone. Please make sure you are willing to perform them before validating them.
            </p>
            <div class="danger-zone">
                <button onclick="javascript:DeleteAccount(${_.escape(data.aid)}, '${_.escape(data.name)}')">Delete Account</button>
            </div>
            <script>
                var delayed;
                var delayed2;
                var chart = $('#mainGraph').Chart({
                    type: 'bar',
                    options: {
                        grouped: true,
                        plugins: {
                            title: { display: true, text: ' Loading... ' },
                            tooltip: {
                                callbacks: {
                                    label: (context) => {
                                        return formatCurrency("${_.escape(data.currency)}", context.parsed.y);
                                    },
                                }
                            }
                        },
                        animation: {
                            onComplete: () => {
                                delayed = true;
                            },
                            delay: (context) => {
                                let delay = 0;
                                if (context.type === 'data' && context.mode === 'default' && !delayed) {
                                  delay = 0.2 * (context.dataIndex * 300 + context.datasetIndex * 100);
                                }
                                return delay;
                            },
                        },
                        scales: {
                            x: {
                                title: { display: true, text: 'Date' },
                                type: 'time',
                            },
                            y: {
                                title: { display: true, text: 'Net growth' },
                                ticks: {
                                    callback: (value, index, ticks) => formatCurrency("${_.escape(data.currency)}", value)
                                }
                            },
                        }
                    }
                });

                var chart2 = $('#secondGraph').Chart({
                    type: 'line',
                    options: {
                        plugins: {
                            title: { display: true, text: ' Loading... ' },
                            tooltip: {
                                callbacks: {
                                    label: (context) => {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        label += formatCurrency("${_.escape(data.currency)}", context.parsed.y);
                                        return label;
                                    },
                                }
                            },
                        },
                        animation: {
                            onComplete: () => {
                                delayed2 = true;
                            },
                            delay: (context) => {
                                let delay = 0;
                                if (context.type === 'data' && context.mode === 'default' && !delayed2) {
                                  delay = 0.2 * (context.dataIndex * 300 + context.datasetIndex * 100);
                                }
                                return delay;
                            },
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index',
                        },
                        scales: {
                            x: {
                                title: { display: true, text: 'Date' },
                                type: 'time'
                            },
                            y: {
                                title: { display: true, text: 'Net growth' },
                                ticks: {
                                    callback: (value, index, ticks) => formatCurrency("${_.escape(data.currency)}", value)
                                }
                            },
                        }
                    },
                })
                
                var updateChart = () => {
                    let target = $('select[name="selection"]').children('option:selected')
                    let interval = target.attr('interval')
                    let title = target.attr('title')
                    let title2 = target.attr('title2')
                    let fmt = target.attr('fmt')

                    $.get('/api/get-balance-history', { aid: ${state.aid}, 'interval': interval }, function(data) {

                        let labels = _.union(data.date.map(e => e.date), data.available_date.map(e => e.available_date)).filter(e => !_.isNull(e)).sort(function(a,b){
                            return new Date(a) - new Date(b);
                        })

                        let futureIndex = ((labels.findIndex(o => toLastDay(o) >= new Date()) + 1) || labels.length + 1) - 1

                        let total_growth = labels.map(lbl => {
                            return data.date.filter(e => e.date === lbl).map(e => e.balance)[0] ?? 0
                        })

                        let available_growth = labels.map(lbl => {
                            return data.available_date.filter(e => e.available_date === lbl).map(e => e.balance)[0] ?? 0
                        })

                        delayed = false;
                        delayed2 = false;

                        chart.data.labels = labels;
                        chart.data.datasets = [
                            {
                                label: 'Total growth',
                                borderWidth: 1,
                                data: total_growth
                            },
                            {
                                label: 'Available growth',
                                borderWidth: 1,
                                data: available_growth
                            },
                        ]
                        chart.options.plugins.title.text = title
                        chart.options.scales.x.time.tooltipFormat = fmt
                        chart.update()
                        const skipped = (ctx, value) => ctx.p0.skip || ctx.p1.skip ? value : undefined;

                        chart2.data.labels = labels;
                        chart2.data.datasets = [
                            {
                                label: 'Total balance',
                                data: cumsum(total_growth),
                                segment: {
                                    borderDash: ctx => { return ctx.p1DataIndex >= futureIndex ? [2] : undefined }
                                },
                                spanGaps: true
                            },
                            {
                                label: 'Available balance',
                                data: cumsum(available_growth),
                                segment: {
                                    borderDash: ctx => { return ctx.p1DataIndex >= futureIndex ? [2] : undefined }
                                },
                                fill: {
                                    target: '-1',
                                    above: '#ff000010',
                                    below: '#0000ff10'
                                }
                            }
                        ]
                        chart2.options.plugins.title.text = title2
                        chart2.options.scales.x.time.tooltipFormat = fmt
                        chart2.update()
                    })
                }
                updateChart()
            </script>
        </div>
        `);
    }),

    'Transactions': (state) => fetchData('/api/get-account', {aid: state.aid}, (account_data) => {
        // https://gridjs.io/docs/integrations/jquery
        registry.write(`
        <div>
            <div class="flex-row" style="gap: 10px;"    >
                <button class="button-58 small-btn" onclick="javascript:registry.goto('view-account', { aid: ${state.aid} }, true, 'New Transaction')">
                    <i class="fa-regular fa-square-plus fa-lg m-r-5"></i> New
                </button>
                <button class="button-58 small-btn" onclick="javascript:import_()">
                    <i class="fa-solid fa-file-import fa-lg m-r-5"></i> Import
                </button>
                <button class="button-58 small-btn" onclick="javascript:export_()">
                    <i class="fa-solid fa-file-export fa-lg m-r-5"></i> Export
                </button>
                <input type="file" id="openFileForUpload" style="display: none;" />
            </div>
            <div id="transactionMainTable"></div>
            <script>
                function import_() {
                    $("#openFileForUpload").click()
                }

                function export_() {
                    $.get('/api/get-transaction', {'aid': ${state.aid}, 'offset': 0, 'limit': 65536}, (data) => {
                        let string = JSON.stringify(data.results.map(object => {
                            let dict = _.pick(object, 'amount', 'date', 'available_date', 'description')
                            dict.tags = object.tags.split(',').map(id => data.tags.find(e => e.id == id).name).filter(e => !_.isNull(e)).filter(e => e != "")
                            return dict
                        }))
                        let elem = document.createElement('a');
                        elem.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(string));
                        elem.setAttribute('download', 'transactions.json');
                        elem.style.display = 'none';
                        document.body.appendChild(elem);
                        elem.click();
                        document.body.removeChild(elem);
                    }, 'json')
                }

                $("#openFileForUpload").change((e) => {
                    let file = e.target.files[0];
                    
                    // setting up the reader
                    var reader = new FileReader();
                    reader.readAsText(file,'UTF-8');
                 
                    // here we tell the reader what to do when it's done reading...
                    reader.onload = readerEvent => {
                        try {
                            let content = JSON.parse(readerEvent.target.result); // this is the content!
                            content.forEach(elem => CreateTransaction(${state.aid}, elem['amount'], elem['date'], elem['available_date'], elem['description'], elem['tags'], false))
                        }
                        catch (error) {
                            console.log(error)
                            registry.error('Fail to open JSON file')
                        }
                    }
                });

                $(document).ready(() => {
                    const grid = $("div#transactionMainTable").Grid({
                        columns: ['Index', 
                        {name: 'Date',formatter: (cell, row) => gridjs.html($.dateViewer(cell, true, "(value) => UpdateTransactionField(${state.aid}, "+ _.escape(row.cells[0].data) +", 'date', value)"))},
                        {name: 'Available Date',formatter: (cell, row) => gridjs.html($.dateViewer(cell, false, "(value) => UpdateTransactionField(${state.aid}, "+ _.escape(row.cells[0].data) +", 'available_date', value)"))},
                        'Registration Date', 
                        {name: 'Amount',formatter: (cell, row) => gridjs.html($.amountViewer("${account_data.currency}", parseFloat(cell), "(value) => UpdateTransactionField(${state.aid}, "+_.escape(row.cells[0].data)+", 'amount', value)"))},
                        { name: 'Description', sort: false, width: '250px' },
                        { name: 'Tags', sort: false, width: '150px', formatter: (cell) => gridjs.html('<ul class="tag-editor" style="border:none;font-size:12px;padding:0;">' + cell + '</ul>') },
                        {
                            sort: false,
                            id: 'actions',
                            formatter: (cell) => gridjs.html(
                                '<span class="btn-container" style="display: flex; align-content: center; min-height: 26px; ">' +
                                '<button class="red-hover" onclick="javascript:RemoveTransaction(${state.aid}, '+ cell +')"><i class="fa-solid fa-trash fa-sm"></i></button>' +
                                '</span>'
                            ),
                            width: '40px',
                        }],
                        search: {
                            server: {
                                url: (prev,keyword) => prev + "&search=" + keyword
                            }
                        },
                        sort: {
                            multiColumn: false,
                            server: {
                                url: (prev, columns) => {
                                    if (!columns.length) return prev;
                                    
                                    const col = columns[0];
                                    const dir = col.direction === 1 ? 'asc' : 'desc';
                                    let colName = ['id', 'date', 'available_date', 'registration_date', 'amount'][col.index];
                                    
                                    return prev + "&order=" + colName + "&dir=" + dir;
                                }
                            }
                        },
                        resizable: true,
                        pagination: {
                            limit: 15,
                            server: {
                                url: (prev, page, limit) => prev + '&limit='+ limit +'&offset=' + (page*limit)
                            }
                        },
                        style: {
                            td: {
                                'padding': '2px 8px 2px 15px'
                            }
                        },
                        server: {
                            url: '/api/get-transaction?aid=${state.aid}',
                            then: data => {
                                return data.results.map(object => {
                                    return [object.id,
                                        object.date,
                                        object.available_date,
                                        new Date(object.registration_date).toLocaleString({ year: "numeric",month: "2-digit",day: "numeric" }),
                                        object.amount,
                                        object.description,
                                        object.tags.split(',').filter(i => i).map(id => {
                                            let tag = _.find(data.tags, e => e.id == id);
                                            let [secondaryColor, color] = getColorPallette(tag.color ?? '52bfff');
                                            
                                            return '<li style="display: block;"><div class="tag-editor-spacer">, </div><div class="tag-editor-tag" style="color: #'+color+'; background-color: #'+ secondaryColor +'; border-radius: 3px;">'+ _.escape(tag.name) +'</div></li>';
                                        }).join(''),
                                        object.id]
                                })
                            },
                            total: data => data.count
                        },
                        className: {
                            search: 'nice-form-group search-grid-table'
                        }
                    });

                })

            </script>
        </div>
        `);
    }),

    'New Transaction': (state) => fetchData('/api/get-account', {aid: state.aid}, (data) => {
            registry.write(`
            <div class="nice-form-group std-w">
                <h1>New Transaction:</h1>

                <br>
                <p>
                    You are about to create a new transaction in account ${_.escape(data.name)}
                </p>
                <br>
                
                <form action="javascript:submit();">

                <div class="nice-form-group">
                    <label for="amount">
                        Amount
                        <i class="fa-solid fa-circle-question">
                            <span>The date when this account was first created</span>
                        </i>
                    </label>
                    <input type="number" step="0.01" pattern="^\d*(\.\d{0,1})?$" id="amount" class="icon-left money-input" name="amount" required />
                </div>
                
                <br>

                <div class="nice-form-group">
                    <label for="date">
                        Date 
                        <i class="fa-solid fa-circle-question">
                            <span>Date when the transaction was performed</span>
                        </i>
                    </label>
                    <input type="date" id="date" name="date" required/>
                </div>
                
                <br>

                <div class="nice-form-group">
                    <label for="available_date">
                        Available Date <span style='color: #888;'>(optional)</span>
                        <i class="fa-solid fa-circle-question">
                            <span>Date at which the transaction take effect in the bank</span>
                        </i>
                    </label>
                    <input type="date" id="available_date" name="available_date" />
                </div>

                <br>

                <div class="nice-form-group">
                    <label for="amount">
                        Tags
                        <i class="fa-solid fa-circle-question">
                            <span>Tags describing the transaction</span>
                        </i>
                    </label>
                    <input type="text" id="tagEditor" name="tags" />
                </div>
                
                <br>
                
                <div class="nice-form-group">
                    <label for="description">
                        Description <span style='color: #888;'>(optional)</span>
                        <i class="fa-solid fa-circle-question">
                            <span>Additional description or notes about this transaction</span>
                        </i>
                    </label>
                    <textarea id="description" name="description" placeholder="Transaction Description"></textarea>
                </div>
                
                <br>

                <div class="nice-form-group">
                    <button class="button-58" type="submit" id="CreateTransaction">Create Transaction</button>
                </div>
                </form>

                <script>
                    function submit(){
                        let amount = $("input[name='amount']").val();
                        let date = $("input[name='date']").val();
                        let available_date = $("input[name='available_date']").val();
                        let description = $("#description").val();
                        let tags = $("#tagEditor").tagEditor('getTags')[0].tags;
                        CreateTransaction(${state.aid}, amount, date, available_date, description, tags);
                        $("#CreateTransaction").prop( "disabled", true );
                    }
                    $("#tagEditor").customTagEditor()
                </script>
            </div>
        `);
    })
}, (state) => `viewAccountBtn${state.aid}`)

registry.push("error", {
    "main": (state) => {
        let message = "";
        if (state['error']) {
            message = "<p>" + state['error'] + "</p>";
        }

        registry.write(`
            <div class="ab-c-m error">
                <span><i class="fa-solid fa-triangle-exclamation"></i></span>
                An unexpected error has occurred.
                ${message}
            </div>
        `);
    }
})

registry.push("support", {
    "Support": (state) => staticPageAjax('/static/support.html')
}, () => 'supportButton')

registry.push("about", {
    "About": (state) => staticPageAjax('/static/about.html'),
    "Third-Party": (state) => staticPageAjax('/static/third-party.html')
}, () => 'aboutButton')

registry.push("new-budget", {
    'Create': (state) => {
        registry.write(`
            <div class="nice-form-group std-w">
                <h1>Create new budget:</h1>
                <br>

                <p>
                    An account is a record used to track financial transactions for an entity. It categorizes and summarizes financial information, enabling accurate reporting and analysis. Accounts are essential for effective financial management and decision-making.
                </p>

                <br>

                <form action="javascript:submit();">
                <div class="nice-form-group">
                    <label for="name">
                        Name
                        <i class="fa-solid fa-circle-question">
                            <span>The name of the budget to be created</span>
                        </i>
                    </label>
                    <input type="text" id="name" name="name" placeholder="Budget Name" maxlength="25" required />
                </div>
                
                <br>
                
                <div class="nice-form-group">
                    <label for="interval">
                        Interval
                        <i class="fa-solid fa-circle-question">
                            <span>The interval associated with this budget</span>
                        </i>
                    </label>
                    
                    <select name="interval" id="intervalOption" required>
                        <option disabled selected value> -- select an option -- </option>
                        <option value="day">Daily</option>
                        <option value="month">Monthly</option>
                        <option value="year">Yearly</option>
                        <option value="semester">Every semester</option>
                        <option value="trimester">Every trimester</option>
                    </select>
                </div>
                <br>
    
                <div class="nice-form-group">
                    <button class="button-58" type="submit" id="CreateBudget">Create Budget</button>
                </div>
                </form>
    
                <script>
                    function submit(){
                        let name = $("#name").val()
                        let interval = $("#intervalOption").find(":selected").attr('value')
                        CreateBudget(name, interval);
                        $("#CreateBudget").prop( "disabled", true );
                    }
                </script>

                <br>
            </div>
        `)
    }
})

registry.push("tags", {
    "Settings": (state) => {
        registry.write(`
            <div>
                <h1>Tags</h1>
                <p class="text-dis m-t-25 m-b-25" style="max-width: 60%;">
                    A tag is a customizable label or keyword assigned to specific transactions in the accounting application.
                    It allows you to categorize and organize transactions based on shared characteristics or attributes, facilitating
                    easy grouping and identification for future reference and analysis. Tags provide a flexible way to personalize and
                    enhance the organization of your financial data.
                </p>
                <button class="button-58 small-btn" onclick="javascript:saveTag()">
                    <i class="fa-solid fa-floppy-disk m-r-8"></i> Save
                </button>
                <br>
                <table class="tag-table" id="tagTable">
                    <tr skip="e">
                        <th>Tag</th>
                        <th>Edit</th>
                        <th>Color</th>
                    </tr>
                    <tr>
                        <td>
                            <ul class="tag-editor" style="border:none;font-size:12px;padding:0;">
                                <li style="display: block;"><div class="tag-editor-spacer">, </div><div class="tag-editor-tag">Tag#1</div></li>
                            </ul>
                        </td>
                        <td><input type="text" /></td>
                        <td>
                            <button data-jscolor="{ format:'hex',uppercase:true }">
                                Select color
                            </button>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <ul class="tag-editor" style="border:none;font-size:12px;padding:0;">
                                <li style="display: block;"><div class="tag-editor-spacer">, </div><div class="tag-editor-tag">Tag#2</div></li>
                            </ul>
                        </td>
                        <td><input type="text" /></td>
                        <td>
                            <button data-jscolor="{ format:'hex',uppercase:true }">
                                Select color
                            </button>
                        </td>
                    </tr>
                </table>
                <script>
                    var oldTags;

                    $.get('/api/get-tags', {}).done(function(data) {
                        oldTags = data;
                        $('#tagTable').html(
                            "<tr jQuerySkip><th>Tag</th><th>Edit</th><th>Color</th></tr>" + 
                            data.map(obj => {
                                let value = obj.color ?? '52bfff';
                                let [secondaryColor, color] = getColorPallette(value);
                                return "<tr>" +
                                    '<td><ul class="tag-editor" style="border:none;font-size:12px;padding:0;">' +
                                    '<li style="display: block;"><div class="tag-editor-spacer">, </div><div class="tag-editor-tag" style="color: #'+color+'; background-color: #'+ secondaryColor +'; border-radius: 3px;">' + _.escape(obj.name) + '</div></li>' +
                                    '</ul></td>' +
                                    '<td><input type="text" value="' + obj.name + '"/></td>' +
                                    '<td>' + 
                                    '<button data-jscolor="{ format:\\\'hex\\\',uppercase:true, value:\\\''+value+'\\\' }">Select color</button>' +
                                    '</td>' +
                                    '</tr>'
                            }).join(' ')
                        )
                        jscolor.install();
                    }).fail(function(err){
                        registry.error('Call to /api/get-tags endpoint failed: ' + err, true)
                    })

                    function saveTag() {
                        if (oldTags) {
                            $("#tagTable").children('tr:not([jQuerySkip])').each((idx,obj) => {
                                let name = $(obj).children().eq(1).children('input').val();
                                let color = $(obj).children().eq(2).children('button').attr('data-current-color').slice(1);
                                if (name != oldTags[idx].name || (color.toLowerCase() != (oldTags[idx].color ?? '52bfff'))) {
                                    UpdateTag(oldTags[idx].id, name, color.toLowerCase())
                                }
                            })
                        }
                    }
                </script>
            </div>
        `);
    }
}, () => 'tagButton')

registry.push("view-budget", {
    "Overview": (state) => fetchData('/api/get-budget', {bid: state.bid}, (data) => {
        staticPage('/static/budget-overview.html', (text) => {
            let context = {
                state: state,
                data: data
            }
            registry.write(text
                .replaceAll(/@@((.|\n|\r)*?)@@/g, function(match, script) {
                    return eval(script)
                })    
                .replaceAll(/%%([a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*)%%/g, function(match, name) {
                    return getDescendantProp(context, name);
                }))
        })
    }),
    "Settings": (state) => fetchData('/api/get-budget', { bid: state.bid }, (data) => {
        staticPage('/static/page_budget.html', (tuto) => {
            registry.write(`
                <div class="markdown-body">
                    <h1>${_.escape(data.name)} - Settings <span class="interval" style="color: #888;">(${_.escape(data.interval)})</span></h1>
                    <br>

                    <h2>Incomes/Expenses</h2>

                    <div class="flex-row m-b-15" style="gap: 10px;">
                        <button class="button-58 small-btn" onclick="javascript:CreateNewIncome('${data.name}', ${data.bid})">
                            <i class="fa-regular fa-square-plus fa-lg m-r-5"></i> New income
                        </button>
                        <button class="button-58 small-btn" onclick="javascript:CreateNewExpense('${data.name}', ${data.bid})">
                            <i class="fa-regular fa-square-plus fa-lg m-r-5"></i> New expense
                        </button>
                        <button class="button-58 small-btn" onclick="javascript:OnChangeInterval()">
                        <i class="fa-solid fa-calendar-days fa-lg m-r-5"></i> Change interval
                        </button>
                    </div>
                    
                    <table class="table-budget-categories m-b-45">
                        <tr>
                            <th colspan="5">Incomes</th>
                        </tr>
                        <tr>
                            <th style="width: 220px;">Name</th>
                            <th style="width: 50px;">Priority</th>
                            <th>Matcher</th>
                            <th style="width: 100px;">Safety Level</th>
                            <th style="width:0px">Actions</th>
                        </tr>
                        ${
                            data.income.map(object => {
                                let additionalStyle = (object.matcher.length) ? '' : 'background-color: #ff000030'
                                return `
                                    <tr style='${additionalStyle}'>
                                        <td>${$.viewer(object.name, '(x) => _.unescape(x)', '(x) => _.escape(x)', '(x) => x', `(x) => UpdateIncome(${data.bid}, ${object.biid}, 'name', x)`)}</td>
                                        <td>${$.viewer(object.priority, '(x) => parseInt(x)', '(x) => x', '(x) => x', `(x) => UpdateIncome(${data.bid}, ${object.biid}, 'priority', x)`)}</td>
                                        <td>${$.codeViewer(object.matcher, `(x) => UpdateIncome(${data.bid}, ${object.biid}, 'matcher', x)`)}</td>
                                        <td>${$.viewer(object.safety_level, '(x) => parseFloat(x) / 100', '(x) => (100*x).toFixed(0)+\'%\'', '(x) => x', `(x) => UpdateIncome(${data.bid}, ${object.biid}, 'safety_level', x)`)}</td>
                                        <td><span class="btn-container" style="display: flex; align-content: center; min-height: 26px; "><button class="red-hover" onclick="javascript:DeleteIncome(${data.bid}, ${object.biid})"><i class="fa-solid fa-trash fa-sm"></i></button></span></td>
                                    </tr>
                                `
                            }).join(' ')
                        }
                    </table>

                    <table class="table-budget-categories">
                        <tr>
                            <th colspan="5">Expenses</th>
                        </tr>
                        <tr>
                            <th style="width: 220px;">Name</th>
                            <th style="width: 50px;">Priority</th>
                            <th>Matcher</th>
                            <th>Allocated</th>
                            <th style="width:0px">Actions</th>
                        </tr>
                        
                        ${
                            data.expense.map(object => {
                                let additionalStyle = (object.matcher.length && object.formula.length) ? '' : 'background-color: #ff000030'
                                return `
                                    <tr style='${additionalStyle}'>
                                        <td>${$.viewer(object.name, '(x) => _.unescape(x)', '(x) => _.escape(x)', '(x) => x', `(x) => UpdateExpense(${data.bid}, ${object.bsid}, 'name', x)`)}</td>
                                        <td>${$.viewer(object.priority, '(x) => parseInt(x)', '(x) => x', '(x) => x', `(x) => UpdateExpense(${data.bid}, ${object.bsid}, 'priority', x)`)}</td>
                                        <td>${$.codeViewer(object.matcher, `(x) => UpdateExpense(${data.bid}, ${object.bsid}, 'matcher', x)`)}</td>
                                        <td>${$.codeViewer(object.formula, `(x) => UpdateExpense(${data.bid}, ${object.bsid}, 'formula', x)`)}</td>
                                        <td><span class="btn-container" style="display: flex; align-content: center; min-height: 26px; "><button class="red-hover" onclick="javascript:DeleteExpense(${data.bid}, ${object.bsid})"><i class="fa-solid fa-trash fa-sm"></i></button></span></td>
                                    </tr>
                                `
                            }).join(' ')
                        }
                    </table>

                    ${tuto}
                </div>

                <script>
                    function OnChangeInterval() {
                        let string = '<p>You are about to change the interval corresponding with the current budget.</p>'
                        string += '<div class="nice-form-group">'
                        string += '<select id="budgetEditIntervalSelection">'
                        string += '<option value="day" ${(data.interval == 'day') ? 'selected' : ''}>Daily</option>'
                        string += '<option value="month" ${(data.interval == 'month') ? 'selected' : ''}>Monthly</option>'
                        string += '<option value="year" ${(data.interval == 'year') ? 'selected' : ''}>Yearly</option>'
                        string += '<option value="semester" ${(data.interval == 'semester') ? 'selected' : ''}>Every semester</option>'
                        string += '<option value="trimester" ${(data.interval == 'trimester') ? 'selected' : ''}>Every trimester</option>'
                        string += '</select>'
                        string += '</div>'

                        $.popup('Change Interval', string, (answer) => {
                            if (answer === 'Edit') {
                                let result = $('#budgetEditIntervalSelection').find(":selected").attr('value')
                                EditBudgetInterval(${data.bid}, result)
                            }
                        }, ['Edit', 'Cancel'])
                    }
                </script>
            `)
        })
    })
}, (state) => `viewBudgetBtn${state.bid}`)
