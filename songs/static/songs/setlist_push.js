$(document).ready(function () {
 
 $('.accept-setlist').click(function(){
        setlist_id = $(this).attr('name');
        $(this).closest('li').slideUp(function(){
            $(this).remove();
        })
        $.get('/push-setlist-decision/', {'accept':setlist_id}, function(response){
            if (response.indexOf('False') >= 0){ //response is true if there are still pushed setlists
                $('#setlist-push-alert-close').trigger('click');
            }
            index = response.indexOf('|');
            setlist_length = response.substring(0,index);
            $('.nav_setlistnum').text(setlist_length.toString());
        });
    });
    
    $('.reject-setlist').click(function(){
        setlist_id = $(this).attr('name');
        $(this).closest('li').slideUp(function(){
            $(this).remove();
        });
        $.get('/push-setlist-decision/', {'reject':setlist_id}, function(response){
            if (response.indexOf('False') >= 0){ //response is true if there are still pushed setlists
                $('#setlist-push-alert-close').trigger('click');
            }
        });
    });
});