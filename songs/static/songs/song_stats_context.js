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
    
    options = { 'content': 'InspirePraise can keep track of song usage information for users and ministries. \
                            By choosing your personal profile or a ministry you are a part of in the select box,\
                            you can easily view\
                            when you or your ministry last used a song, what key the song was used in, and more!',
                'placement': 'right',
                
                };
    $('#song-stats-context-help').popover(options);
    
});