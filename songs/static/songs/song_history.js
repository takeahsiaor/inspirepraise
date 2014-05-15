
$(document).ready(function () {
//handles the functionality for the modals in the archive setlist page
//including details, delete archived setlist, and reuse setlist. 

    $('.song-history-modal-button').click(function(){
        var $detail_id = $(this).attr('id');
        var $ccli = $(this).attr('name');
        $.get('/song-usage-details-profile/', {'ccli':$ccli, 'detail_id':$detail_id}, function(response){
            $('#song-history-modal-content').empty();
            $(response).appendTo('#song-history-modal-content');
            $('#song-history-details').modal('toggle')
        });
    });
});




