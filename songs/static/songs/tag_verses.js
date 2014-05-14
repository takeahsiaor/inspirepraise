
$(document).ready(function () {
    var stack_topright = {"dir1": "down", "dir2": "left", "firstpos1":45, "firstpos2":15};
        // MUST MUST MUST CLEAN DATA!!
        //must i? does this really matter in this case? everything is get parameters
        //no interaction with database beyond querying for it
    var tagged_songs = [];
    //function to add delay to key up
    var delay = (function(){
        var timer = 0;
        return function(callback, ms){
            clearTimeout (timer);
            timer = setTimeout(callback, ms);
        };
    })();
    
    //function to get songs from view
    function get_songs(){
        $song_query = $("input[name='song_query']").val();
        if ($song_query != ''){
            $('.small_spin').attr('class', 'small_spinner');
        }
        $('#search_results').empty();
        $.get('/st/', {query:$song_query}, function(response){
            $('#search_results').empty();
            $(response).appendTo('#search_results');
            $('.small_spinner').attr('class', 'small_spin');
            //check to make sure song isn't already tagged
            $('.song').each(function(){
                var $ccli = $(this).attr('id');
                var $in = jQuery.inArray($ccli, tagged_songs);
                //if it is tagged, change class to song tagged and disable the button
                if ( $in >= 0){
                    $(this).attr('class', 'song success');
                    $(this).find('.tag-button').attr('disabled', true);
                }
            });
            //activate modal functionality
            $('.clickable').click(function(){
                var $ccli = $(this).parent().attr('id');
                $.get('/song-info-pop/'+$ccli, function(response){
                    $('#song-details-content').empty();
                    $(response).appendTo('#song-details-content');
                    $('#song-details-modal').modal('toggle');
                });
            });
            //activate button functionality
            $('.tag-button').click(function(){
                var $versestring ='';
                $('.verse').each(function(){
                    $versestring = $versestring + ' | ' + $(this).text();
                });
                var $ccli = $(this).attr('name');
                //check that there are verses to be tagged
                //if not
                if($versestring== ''){
                    // $('#alerts').empty();
                    // $('<div class="alert alert-danger">Oops! Please enter verses to tag.</div>')
                      // .appendTo($('#alerts'))
                      // .fadeIn('slow')
                      // .delay(3000)
                      // .fadeOut('slow');
                        $.pnotify({
                            title: 'Oops!',
                            text: 'Please enter verses to tag!',
                            delay: 3000,
                            styling: "bootstrap",
                            addclass: "alert-danger",
                            stack: stack_topright,
                            
                        });
                   
                }
                //if there are verses
                else{
                    //send info to django view for tagging logic
                    //$.post( "test.php", { name: "John", time: "2pm" } );
                    $.get('/tag-handler/', {verses: $versestring, ccli:$ccli});
                        $.pnotify({
                            title: 'Tag Complete!',
                            text: 'Thanks for your submission!',
                            type: 'success',
                            delay: 3000,
                            styling: "bootstrap",
                            stack: stack_topright,
                            
                        });
                    //this changes the class of the tr in which the button resides
                    $(this).parent().parent().attr('class', 'song success');
                    //how best to handle already tagged songs? what if verses change? reallow them to be tagged?
                    //currently: tag will load ccli into array. if a verse group is removed/added, array is deleted
                    tagged_songs.push($ccli);
                    $(this).attr('disabled', true);
                }
            });
            
            //if you click on the "did you mean" will reload based on that
            $('#suggestion').click(function(){
                var $suggestion = $('#suggestion').text();
                $("input[name='song_query']").val($suggestion);
                get_songs();
            });
    
        });
    }

    
    // original verse section: deals with handling click of add verse button
    $("input[name='add_verses']").click(function(){
        $verse_query = $("input[name='verse_query']").val();
        if ($verse_query == ''){

            $.pnotify({
                title: 'Oops!',
                text: 'Please enter verses to tag!',
                delay: 3000,
                styling: "bootstrap",
                addclass: "alert-danger",
                stack: stack_topright,
                
            });
        }
        else {
            //checks if verse grouping is parsable
            $.get('/is-parsable/', {'query':$verse_query}, function(response){
                //yes it is parsable!!
                if (response.indexOf('True') >= 0 ){
                    $("<tr class='verses remove'><td class='closer'><a href='#' title='Click to remove' class='verse_close' id='"+$verse_query+"'>&#215;</a></td><td class='verse'>"+$verse_query+"</td></tr>").appendTo('#verse_results');
                    $("input[name='verse_query']").val("");
                    //when adding another verse group, untag songs and undo all css
                    tagged_songs = [];
                    $('.success').children().children().attr('disabled', false);
                    $('.success').attr('class', 'song');
                    //doesn't refresh list but rather just changes the classes and reenables buttons
                    $('.verse_close').click(function(){
                        $(this).parent().parent().remove();
                        tagged_songs = [];
                        $('.success').children().children().attr('disabled', false);
                        $('.success').attr('class', 'song');
                    });
                }
                //no it's not!
                else{
                    $.pnotify({
                        title: 'Oops!',
                        text: "What you typed is gibberish to us or the verses don't exist!",
                        delay: 3000,
                        styling: "bootstrap",
                        addclass: "alert-danger",
                        stack: stack_topright,
                        
                    });
                }
                
            });
        }
    });
    
    //consider using jquery.ajax later
    //song section
    $("input[name='search_songs']").on('click', function(){
        get_songs();
    });
    
    $("input[name='song_query']").keyup(function(){
        delay(function(){
            get_songs();
        }, 650);

    });
});



