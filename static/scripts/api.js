function RefreshAccountList()
{
    return $.ajax({
        url: '/api/list-accounts',
        method: 'GET',
        dataType: 'json'
    }).done(function(data) {
        $('#sideBarAccountListing').html(
            data.map(obj => `<li class="icon" id="viewAccountBtn${_.escape(obj.aid)}" onclick="registry.goto('view-account', { aid: ${_.escape(obj.aid)} })"><i class="fa-solid fa-file-invoice-dollar"></i>${_.escape(obj.name)}</li>`).join('')
        )
    }).fail(function(err){
        registry.error(`Call to /api/list-accounts endpoint failed: ${err}`)
    })
}

function RefreshBudgetList()
{
    $.get('/api/list-budgets')
    .done(function(data) {
        $('#sideBarBudgetListing').html(
            data.map(obj => `<li class="icon" id="viewBudgetBtn${_.escape(obj.bid)}" onclick="registry.goto('view-budget', { bid: ${_.escape(obj.bid)} })"><i class="fa-solid fa-receipt"></i>${_.escape(obj.name)} <span class="interval">(${_.escape(obj.interval)})</span></li>`).join('')
        )
    })
    .fail(function(err) {
        registry.error(`Call to /api/list-budgets endpoint failed: ${err}`)
    })
}

$(document).ready(() => {
    RefreshAccountList()
    RefreshBudgetList()
});

function CreateAccount(name, creation_date, currency, description)
{
    return $.ajax({
        url: '/api/create-account',
        method: 'POST',
        dataType: 'json',
        data: { name: name, creation_date: creation_date, currency: currency, description: description }
    }).done(function(data) {
        history.back()
        RefreshAccountList()
        registry.goto('view-account', { aid: data.aid })
    }).fail(function(err){
        registry.error(`Call to /api/create-account endpoint failed: ${err}`, true)
    })
}

function CreateTransaction(aid, amount, date, available_date, description, tags, navigate=true)
{
    return $.post('/api/create-transaction', { aid: aid, amount: amount, date: date, available_date: available_date, description: description, tags: tags.join(",") })
    .done(function(data) {
        if (navigate) {
            history.back()
            registry.goto('view-account', { 'aid': aid }, false, 'Transactions')
        }
    }).fail(function(err){
        registry.error(`Call to /api/create-transaction endpoint failed: ${err}`, true)
    })
}

function UpdateTag(id, name, color)
{
    return $.post('/api/update-tag', { id: id, name: name, color: color })
    .done(function(data) {
        registry.reload()
    }).fail(function(err){
        registry.error(`Call to /api/update-tag endpoint failed: ${err}`, true)
    })
}

function RemoveTransaction(aid, id)
{
    $.popup('Delete', 'Do you really want to delete these transaction ? This process cannot be undone', (answer) => {
        if (answer === 'Delete') {
            $.post('/api/delete-transaction', { aid: aid, id: id })
            .done(function(data) {
                registry.reload()
            })
            .fail(function(err) {
                registry.error(`Call to /api/delete-transaction endpoint failed`, false)
            })
        }
    }, ['Delete', 'Cancel'], 'exclamation')
}

function UpdateTransactionField(aid, id, field, value)
{
    $.post('/api/update-transaction', { aid: aid, id: id, field: field, value: value })
    .done(function(data) {
        registry.reload()
    })
    .fail(function(err) {
        registry.error(`Call to /api/update-transaction endpoint failed`, false)
    })
}

function CreateBudget(name, interval)
{
    $.post('/api/create-budget', { name: name, interval: interval })
    .done(function(data) {
        history.back()
        RefreshBudgetList()
        registry.goto('view-budget', { bid: data.bid })
    })
    .fail(function(err) {
        registry.error(`Call to /api/create-budget endpoint failed`, false)
    })
}

function DeleteAccount(aid, name)
{
    $.popup('Delete', `
        <div style='color:#000;'>
            You are about to delete the account "${name}". This action cannot be undone. If you still want to 
            procceed, please write <b style='color:#555;'>I agree to delete the account ${_.escape(name)}</b> in the box bellow 
        </div>
        <div class='nice-form-group'>
            <input type="text" class="m-t-20 m-b-20" id="nameConfirm" pattern="I agree to delete the account ${_.escape(name)}" placeholder="Confirm" required />
        </div>
        <script>
            $('#btn-Delete').attr('disabled', true)
            $('#nameConfirm').on('input', function(i) {
                $('#btn-Delete').attr('disabled', $(i.target).val() != 'I agree to delete the account ${_.escape(name)}')
            })
        </script>
    `, (answer) => {
        if (answer === 'Delete') {
            $.post('/api/delete-account', { aid: aid })
            .done(function(data) {
                history.back()
                RefreshAccountList()
            })
            .fail(function(err) {
                registry.error(`Call to /api/delete-account endpoint failed`, false)
            })
        }
    }, ['Delete', 'Cancel'], 'exclamation')
}

function CreateNewIncome(name, bid)
{
    $.popup('Create new Income', `
        <div style='color:#000;'>
            You are about to create a new income source into budget "${name}"
        </div>
        
        <div class="nice-form-group">
            <label for="name">
                Name
                <i class="fa-solid fa-circle-question">
                    <span>The name of the Income to be created</span>
                </i>
            </label>
            <input type="text" id="nameInput" name="name" placeholder="Income name" maxlength="25" minlength="4" onkeypress="javascript: return matchName(event)" required />
        </div>
        <script>
            $('#btn-Create').attr('disabled', true)
            $('#nameInput').on('input', function(i) {
                $('#btn-Create').attr('disabled', $(i.target).val().length <= 3)
            })
        </script>
    `, (answer) => {
        if (answer === 'Create') {
            let name = $('#nameInput').val()
            $.post('/api/create-income', { 'bid': bid, 'name': name })
            .done(function(data) {
                registry.reload()
            })
            .fail(function(err) {
                registry.error(`Call to /api/create-income endpoint failed`, false)
            })
        }
    }, ['Create', 'Cancel'])
}

function CreateNewExpense(name, bid)
{
    $.popup('Create new Expense', `
        <div style='color:#000;'>
            You are about to create a new expense source into budget "${name}"
        </div>
        
        <div class="nice-form-group">
            <label for="name">
                Name
                <i class="fa-solid fa-circle-question">
                    <span>The name of the Expense to be created</span>
                </i>
            </label>
            <input type="text" id="nameInput" name="name" placeholder="Expense name" maxlength="25" minlength="4" onkeypress="javascript: return matchName(event)" required />
        </div>
        <script>
            $('#btn-Create').attr('disabled', true)
            $('#nameInput').on('input', function(i) {
                $('#btn-Create').attr('disabled', $(i.target).val().length <= 3)
            })
        </script>
    `, (answer) => {
        if (answer === 'Create') {
            let name = $('#nameInput').val()
            $.post('/api/create-expense', { 'bid': bid, 'name': name })
            .done(function(data) {
                registry.reload()
            })
            .fail(function(err) {
                registry.error(`Call to /api/create-expense endpoint failed`, false)
            })
        }
    }, ['Create', 'Cancel'])
}

function UpdateIncome(bid, biid, field, value)
{
    $.post('/api/update-income', { bid: bid, biid: biid, field: field, value: value })
    .fail(function(err) {
        registry.error(`Call to /api/update-income endpoint failed`, false)
    })
    .done(function(data) {
        if (data['Error'] !== undefined) {
            $.pushNotif('Error', `Fail to sanitize input: ${data['Error']}`)
        }
        else {
            $.pushNotif('Success', data['Message'])
        }
        registry.reload()
    })
}

function UpdateExpense(bid, bsid, field, value)
{
    $.post('/api/update-expense', { bid: bid, bsid: bsid, field: field, value: value })
    .fail(function(err) {
        registry.error(`Call to /api/update-expense endpoint failed`, false)
    })
    .done(function(data) {
        if (data['Error'] !== undefined) {
            $.pushNotif('Error', `Fail to sanitize input, ${data['Error']}`)
        }
        else {
            $.pushNotif('Success', data['Message'])
        }
        registry.reload()
    })
}

function DeleteIncome(bid, biid) {
    $.popup('Delete Income', `
        <div style='color:#000;'>
            You are about to delete income source "${biid}"
        </div>
    `, (answer) => {
        if (answer === 'Delete') {
            $.post('/api/delete-income', { bid: bid, biid: biid })
            .fail(function(err) {
                $.pushNotif('Error', `Fail to delete income ${biid} for budget ${bid}`)
            })
            .done(function(data) {
                $.pushNotif('Success', `Income ${biid} successfully deleted`)
                registry.reload()
            })
        }
    }, ['Delete', 'Cancel'])
}

function DeleteExpense(bid, bsid) {
    $.popup('Delete Expense', `
        <div style='color:#000;'>
            You are about to delete expense category "${bsid}"
        </div>
    `, (answer) => {
        if (answer === 'Delete') {
            $.post('/api/delete-expense', { bid: bid, bsid: bsid })
            .fail(function(err) {
                $.pushNotif('Error', `Fail to delete expense ${bsid} for budget ${bid}`)
            })
            .done(function(data) {
                $.pushNotif('Success', `Expense ${bsid} successfully deleted`)
                registry.reload()
            })
        }
    }, ['Delete', 'Cancel'])
}

function SubmitContact(first_name, last_name, email, country, content)
{
    $.post('/api/submit-contact', { first_name: first_name, last_name: last_name, email: email, country: country, content: content })
    .fail(function(err) {
        registry.error(`Failed to submit contact form, the call to /api/submit-contact failed`, true)
    })
    .done(function(data) {
        $.pushNotif('Success', `Ticket successfully posted`)
        registry.reload()
    })
}

function EditBudgetInterval(bid, interval)
{
    $.post('/api/update-budget-interval', { bid: bid, interval: interval })
    .fail(function(err) {
        registry.error(`Failed to update interval, the call to /api/update-budget-interval failed`, true)
    })
    .done(function() {
        $.pushNotif('Success', 'Interval successfully updated')
        registry.reload()
        RefreshBudgetList()
    })
}
