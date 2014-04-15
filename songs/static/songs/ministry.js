$(document).ready(function () {
    $('.common-songs-details').click(function(){
        ccli = $(this).attr('id');
        ministry_id = $(this).attr('name');
        $.get('/song-usage-details-ministry/', {'ccli':ccli, 'ministry_id':ministry_id }, function(response){
            $('#modal-content').empty();
            $(response).appendTo('#modal-content');
        });
    });
});