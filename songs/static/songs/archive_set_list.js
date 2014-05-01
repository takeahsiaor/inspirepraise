
$(document).ready(function () {
//handles the functionality for the modals in the archive setlist page
//including details, delete archived setlist, and reuse setlist. 

    $('.modal-setlist-details').click(function(){
        var $setlist_id = $(this).attr('name')
        $.get('/modalarchivesetlist/', {'setlist_id':$setlist_id}, function(response){
            $('#setlist-details-modal-body').empty();
            $('.modal-footer').empty()
            $('#myModalLabel').html('Archived Setlist Details');
            $(response).appendTo('#setlist-details-modal-body');
            var footer = '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
            $(footer).appendTo('.modal-footer');
        });
    });
    
    $('.delete-setlist').click(function(){
        var $setlist_id = $(this).attr('name')
        $.get('/modalarchivesetlist/', {'setlist_id':$setlist_id}, function(response){
            $('.modal-footer').empty()
            $('#setlist-details-modal-body').empty();
            $('#myModalLabel').html('Confirm Delete!');
            var warning = '<div class="alert alert-danger"><p><strong>Are you sure you want to delete this setlist?</strong>\
                <br>This cannot be undone</p></div>';
            $(warning).appendTo('#setlist-details-modal-body');
            $(response).appendTo('#setlist-details-modal-body');
            var footer = '<button type="button" class="btn btn-danger confirm-delete-setlist" \
            data-dismiss="modal" name="'+$setlist_id+'">Delete!</button>\
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>';
            $(footer).appendTo('.modal-footer');
            
            $('.confirm-delete-setlist').click(function(){
                $.get('/update-setlist/', {'delete':$setlist_id}, function(response){
                    $('li[name='+$setlist_id+']').slideUp(function(){
                        $(this).remove();
                    }) //could do different effects
                })
            });
        });

    });
    
    $('.reuse-setlist').click(function(){
        var $setlist_id = $(this).attr('name')    
        $.get('/modalarchivesetlist/', {'setlist_id':$setlist_id}, function(response){
            $('.modal-footer').empty()
            $('#setlist-details-modal-body').empty();
            $('#myModalLabel').html('Confirm Reuse!');
            var warning = '<div class="alert alert-success"><p><strong>Are you sure you want to reuse this setlist?</strong>\
                <br>This will replace then archive your current setlist</p></div>';
            $(warning).appendTo('#setlist-details-modal-body');
            $(response).appendTo('#setlist-details-modal-body');
            var footer = '<button type="button" class="btn btn-success confirm-reuse-setlist" \
            data-dismiss="modal" name="'+$setlist_id+'">Reuse!</button>\
                <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>';
            $(footer).appendTo('.modal-footer');
            $('.confirm-reuse-setlist').click(function(){
                // alert($setlist_id);
                $.get('/update-setlist/', {'reuse-setlist':$setlist_id}, function(response){
                    $('li[name='+$setlist_id+']').slideUp(function(){
                        $(this).remove();
                    }) //could do different effects
                    window.location.replace("/setlist/");
                })
            });
            
            
            
        });
    });
    


});




