$(document).ready( function () {
    var $cur_modal;
    $('table.mymodal-click').on("click", "tr",
        function (event) {
            // Activate the modal
            pk = $(event.currentTarget).attr('data-id');
            $cur_modal = $('div[data-target='+pk+']');
            $cur_modal.css('display', 'block');

            // Check to see we've already retrieved the schedule
            sched_div = $('div.modal-schedule[data-id='+pk+']')[0];
            if ($(sched_div).attr('data-state') == 'empty' ) {
                $.get(
                    "/ta_application/review/"+pk,
                    function (data) {
                        $(sched_div).html(data);
                        $(sched_div).attr('data-state', 'retrieved');
                    },
                    "html"
                );
            }
        }); //$('table .mymodal-click)

    //Hide the modal if we click outside of it
    $(window).click( function( event ) {
        if (event.target == $cur_modal[0]) {
            $cur_modal.css('display', 'none');
        }
    });
}); // end $(document).ready
