
$(document).ready(function () {
    //this stuff is for the alerts

    var stack_topright = {"dir1": "down", "dir2": "left", "firstpos1":45, "firstpos2":15};
    $('#download-all').click(function(){
        $.pnotify({
            title: 'Downloading!',
            text: 'That thing that you were trying to do worked! Single file dude!',
            type: 'success',
            delay: 3000,
            styling: "bootstrap",
            closer_hover: true,
            addclass: "stack-topright",
            stack: stack_topright,
        });
        var transpose_values_str = '';
        //get all the transpose values in order
        $('.transpose-value').each(function(){
            transpose_values_str = transpose_values_str + $(this).val() + ',';
        });
        //can't use ajax
        window.location.replace("/pdf/?transpose_values="+transpose_values_str+"&single_song=no");
        //?remove=true&ccli=129378
    });
    
    $('.download-lyrics').click(function(){
        $.pnotify({
            title: 'Downloading!',
            text: 'Yes! Lyrics for Mediashout, Propresenter, Easyworship or other worship presenter!',
            type: 'success',
            delay: 3000,
            styling: "bootstrap",
            closer_hover: true,
            addclass: "stack-topright",
            stack: stack_topright,
        });
        var ccli = $(this).attr('name');
        window.location.replace("/lyrics/?single_song=yes&ccli="+ccli);
    });
    
    $('.download-lyrics-setlist').click(function(){
        $.pnotify({
            title: 'Downloading!',
            text: 'Yes! Lyrics for Mediashout, Propresenter, Easyworship or other worship presenter!',
            type: 'success',
            delay: 3000,
            styling: "bootstrap",
            closer_hover: true,
            addclass: "stack-topright",
            stack: stack_topright,
        });
        var ccli = $(this).attr('name');
        window.location.replace("/lyrics/?single_song=no");
    });    
    
    
    
    $('.download-single').click(function(){
        $.pnotify({
            title: 'Downloading!',
            text: 'That thing that you were trying to do worked!',
            type: 'success',
            delay: 3000,
            styling: "bootstrap",
            closer_hover: true,
            addclass: "stack-topright",
            stack: stack_topright,
        });
        //get ccli
        var ccli = $(this).attr('name');
        var transpose_values_str = $("#"+ccli+"-transpose").val()+','; 
        //added unncessary comma to keep algorithm the same
        //as when downloading multiple songs into one
        window.location.replace("/pdf/?single_song=yes&ccli="+ccli+"&transpose_values="+encodeURIComponent(transpose_values_str));
        
    });
    
    $('.remove-song').click(function(){
        $ccli = $(this).attr('name');
        $.get('/update-setlist/', {'remove':true, 'ccli':$ccli}, function(response){
            setlist_length = setlist_length - 1;
            $('.nav_setlistnum').text(setlist_length.toString());
        });    
        $(this).closest('li').slideUp(function(){
            $(this).remove();
            $('#refresh-chords').trigger('click');
        }) //could do different effects
    });
    
    $('.reset-key').click(function(){
        $reset_ccli = $(this).attr('name');
        var ccli_str = '';
        $('.sortable>li').each(function(){
            var ccli = $(this).attr('name');
            var key = $('#'+ccli+'-transpose').val();
            ccli_str = ccli_str + ccli + '-'+key+','
        });
        $.get('/update-setlist/', {'reset':$reset_ccli, 'ccli':ccli_str}, function(response){
            $('#'+$reset_ccli+'-transpose').html(response);
            $('#refresh-chords').trigger('click');
        });
    });
    
    //everytime you open up the publish modal, reset the options
    $('.publish-button').click(function(){
        $('#save-usage-stats').prop('checked', false);
        $('#send-to-none').prop('checked', true);
    });
    
    //this is when you click the ok button in the publish modal
    $('.share-setlist').click(function(){
        ministry_id = $('input[name=ministryOption]:checked').val();
        save_stats = $('#save-usage-stats').prop('checked');
        $.pnotify({
            title: 'Setlist Published!',
            text: "Cool! You've just published this setlist!",
            type: 'success',
            delay: 3000,
            styling: "bootstrap",
            closer_hover: true,
            addclass: "stack-topright",
            stack: stack_topright,
        });
        $.get('/push-setlist/', {'ministry_id':ministry_id, 'save_stats':save_stats}, function(response){
        
        });
    });
    
    $('.transpose-value').change(function() {
        var ccli_str = '';
        $(".sortable>li").each(function(){
            var ccli = $(this).attr('name');
            var key = $('#'+ccli+'-transpose').val();
            ccli_str = ccli_str + ccli + '-'+key+','
        });
        var ccli = $(this).attr('name');
        var key = $('#'+ccli+'-transpose').val();
        var ccli_keychange = ccli +'-'+key;
        $.get('/update-setlist/', {'ccli':ccli_str, 'ccli-keychange':ccli_keychange,}, function(response){
            $('#refresh-chords').trigger('click');
        });
    });

    
    $('.testing').click(function(){
        alert(archived);
    })
    
    
    $('.archive-setlist').click(function(){
        $.pnotify({
            title: 'Archived!',
            text: 'The setlist has been saved permanently!',
            type: 'success',
            delay: 3000,
            styling: "bootstrap",
            closer_hover: true,
            addclass: "stack-topright",
            stack: stack_topright,
        });
        $.get('/update-setlist/',{'archive':true}, function(response){
            setlist_length = 0;
            $('.nav_setlistnum').text(setlist_length.toString());
            $('#setlist_results').empty();
            $('#testarea').empty();
            $('#setlist_results').text('No songs in setlist');
        });
        //$(this).attr('disabled',true);

    });
    
    $('.modal-chord-preview').click(function(){
        var $ccli = $(this).attr('name')
        var transpose_value_str = $('#'+$ccli+'-transpose').val()
        $.get('/modalchord/', {'ccli':$ccli, 'transpose_value_str':transpose_value_str}, function(response){
            $('#modal-body').empty();
            $(response).appendTo('#modal-body');
        });
    });
    
    
    $('.refresh-chords').click(function(){
        var button_clicked = $(this);
        var index = button_clicked.attr('name');
        var $ccli = $(this).attr('id').slice(0, -4);
        var transpose_values_str = '';
        
        //get all the transpose values in order
        //$('.transpose-value').each(function(){
        //    transpose_values_str = transpose_values_str + $(this).val() + ',';
        //});
        
        //right now since any action to the setlist will force click refresh-chords
        //it is appropriate to have this be the location where the archived flag gets set to false
        //archived = false; //do i need this?? or can i just enable the button again?
        
        //wow this is really bad!!!!!!!!!!!!!!!!!!
        if (archived == false) {
            $('.archive-setlist').attr('disabled', false);
        }
        else {
            $('.archive-setlist').attr('disabled', true);
        }
        archived = false;
        //fix this!
        
        $.get('/testchord/',  function(response){
        
            $('#testarea').empty();
            $(response).appendTo('#testarea');
            
            var slider = $('.bxslider').bxSlider({
                minSlides: 2,
                maxSlides: 3,
                moveSlides:1, 
                slideWidth: 360,
                slideMargin: 10,
                controls:false,
                pager: false,
                adaptiveHeight: true,
            });
            
            //if the thing you clicked has a class of "jump" will go to slide
            //maybe instead of combining this, only show the jump button once chords are present
            if (button_clicked.hasClass("jump")){
                slider.goToSlide(parseInt(index));
            }

            //slide index is dependent on the moveSlides variable
            
            $('#slider-next-top').click(function(){
                slider.goToNextSlide();
                return false;
            });
            
            $('#slider-prev-top').click(function(){
                slider.goToPrevSlide();
                return false;
            });       
            
            $('#slider-next-bot').click(function(){
                slider.goToNextSlide();
                return false;
            });
            
            $('#slider-prev-bot').click(function(){
                slider.goToPrevSlide();
                return false;
            });       

        });
    });


    $('.song').each(function(){
        var $ccli = $(this).attr('id').slice(0, -4);
        
        var $in = -1; //= jQuery.inArray($ccli, setlist);
        $.each(setlist, function(index, value){
            if (jQuery.inArray($ccli, value) >=0){
                $in = index;
            }
        });
        
        //if it is tagged, change class to song tagged and disable the button
        if ( $in >= 0){
            $(this).attr('class', 'song success');
            $('#'+$ccli+'-add').attr('disabled', true);
            $('#'+$ccli+'-remove').attr('disabled', false);
        }
    });
    
    $('.add-button').click(function(){
        $ccli = $(this).attr('name');
        $key = $('#'+$ccli+'-transpose').val();
        $('#'+$ccli+'-add').attr('disabled', true);

        
        $.get('/update-setlist/', {'add':true, 'ccli':$ccli, 'key':$key}, function(response){
            $('#'+$ccli+'-row').attr('class', 'song success'); //turn it green
            $('#'+$ccli+'-remove').attr('disabled', false);
            setlist_length = setlist_length + 1;
            $('.nav_setlistnum').text(setlist_length.toString());
        });
    });
    
    $('#clear_setlist').click(function(){
        $.get('/update-setlist/', {'add':true, 'ccli':'clear'}, function(response){
            setlist_length = 0;
            $('.nav_setlistnum').text(setlist_length.toString());
            $('#setlist_results').empty();
            $('#testarea').empty();
            $('#setlist_results').text('No songs in setlist');
        });
    });
    
    $('.remove-button').click(function(){
        $ccli = $(this).attr('name');
        $.get('/update-setlist/', {'remove':true, 'ccli':$ccli}, function(response){
            $('#'+$ccli+'-row').attr('class', 'song'); //turn it green
            $('#'+$ccli+'-add').attr('disabled', false);
            $('#'+$ccli+'-remove').attr('disabled', true);
            setlist_length = setlist_length - 1;
            $('.nav_setlistnum').text(setlist_length.toString());
            // $('.song').each(function(){
                // var $ccli = $(this).attr('id');
                // var $in = jQuery.inArray($ccli, tagged_songs);
                // //if it is tagged, change class to song tagged and disable the button
                // if ( $in >= 0){
                    // $(this).attr('class', 'song tagged');
                    // $(this).find('.tag-button').attr('disabled', true);
                // }
            // });
        });
    });
    
    //this will automatically load the chords in the setlist 
    $('#refresh-chords').trigger('click');
    

});



