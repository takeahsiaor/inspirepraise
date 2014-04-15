$(document).ready(function () {
    $('.common-songs-details').click(function(){
        ccli = $(this).attr('name');
        $.get('/song-usage-details-profile/', {'ccli':ccli}, function(response){
            $('#modal-content').empty();
            $(response).appendTo('#modal-content');
        });
    });


});