$("li.collapsable").click((e) => {
    let target = $(e.target).parent().children('ul');
    if (target[0]) {
        target.toggleClass('collapsed');
        if (target.hasClass('collapsed')) {
            target.animate({ height: 0 }, 400);
        }
        else {
            target.animate({ height: target[0].scrollHeight }, 400);
        }
    }
});

$("#profile").click(() => {
    let pos = $("#profile").position()
    $("#profileDropdown").css({ 'display': 'block' });
    $("#profileDropdown").css({ top: pos.bot, right: 50 });
    $("#profileDropdown").animate({ 'max-height': $("#profileDropdown").children(".container").height() + 20 }, 400, "linear");
});

// Fa-beat animation for adding an account
$(".add-btn").hover(function() {
    $( this ).addClass('fa-beat');
}, function() {
    $( this ).removeClass('fa-beat');
})

$(document).mousedown(function(e) {
    var container = $("#profileDropdown");
    var container2 = $("#profile");
    if (!container.is(e.target) && container.has(e.target).length === 0 &&
        !container2.is(e.target) && container2.has(e.target).length === 0) {
        $("#profileDropdown").animate({ 'max-height': 0 }, 400, "linear", function() { $(this).css({ 'display': 'none' }); });
    }
});
