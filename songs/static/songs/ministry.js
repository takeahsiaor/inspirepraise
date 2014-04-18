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
        $('.give-admin-checkbox').attr('checked', false);
    });
    
    $('#give-admin-rights-confirm').click(function(){
        ministry_id = $(this).attr('name');
        membership_ids = '';
        $('.give-admin-checkbox:checked').each(function(){
           membership_ids = membership_ids + $(this).attr('name') +','; 
        });
        $.get('/admin-rights/', {'ministry_id':ministry_id, 'membership_ids':membership_ids, 'give':true}, function(response){
            window.location.replace("/ministry/"+ministry_id);
        });
    });
    
    $('.revoke-admin-button').click(function(){
        $('.revoke-admin-checkbox').attr('checked', false);
    });
    
    $('#revoke-admin-rights-confirm').click(function(){
        ministry_id = $(this).attr('name');
        membership_ids = '';
        $('.revoke-admin-checkbox:checked').each(function(){
           membership_ids = membership_ids + $(this).attr('name') +','; 
        });
        $.get('/admin-rights/', {'ministry_id':ministry_id, 'membership_ids':membership_ids, 'revoke':true}, function(response){
            window.location.replace("/ministry/"+ministry_id);
        });
    });    
});