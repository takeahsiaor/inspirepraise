$(document).ready(function () {
    // $('.common-songs-details').click(function(){
        // ccli = $(this).attr('id');
        // ministry_id = $(this).attr('name');
        // $.get('/song-usage-details-ministry/', {'ccli':ccli, 'ministry_id':ministry_id }, function(response){
            // $('#modal-content').empty();
            // $(response).appendTo('#modal-content');
        // });
    // });
    // $('.make-admin-button').click(function(){
        // $('.give-admin-checkbox').attr('checked', false);
    // });
    $('.song-stats-context').change(function(){
        id = $(this).val();
        $('#context-loading-spinner').removeClass('hidden');
        $.get('/change-song-stats-context/', {'id':id}, function(response){
            // do i need this page reload?
            window.location.reload() 
        });
    });

});