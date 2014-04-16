$(document).ready(function () {
    $('.common-songs-details').click(function(){
        ccli = $(this).attr('id');
        ministry_id = $(this).attr('name');
        $.get('/song-usage-details-ministry/', {'ccli':ccli, 'ministry_id':ministry_id }, function(response){
            $('#modal-content').empty();
            $(response).appendTo('#modal-content');
        });
    });
    $('.make-admin-button').click(function(){
        $('.admin-rights-checkbox').attr('checked', false);
    });
    
    $('#give-admin-rights-confirm').click(function(){
        ministry_id = $(this).attr('name');
        membership_ids = '';
        $('.admin-rights-checkbox:checked').each(function(){
           membership_ids = membership_ids + $(this).attr('name') +','; 
        });
        $.get('/give-admin-rights/', {'ministry_id':ministry_id, 'membership_ids':membership_ids}, function(response){
            window.location.replace("/ministry/"+ministry_id);
        });
    });
});