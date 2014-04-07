
$(document).ready(function () {
    //need to figure out a better way to validate before submit? or is validating after submit fine?
   $("form").submit(function(e){
        e.preventDefault();
        $verse_query = $("input[name='query']").val();
        if ($verse_query == ''){
            $('#alerts').empty();
            $('<div class="search_verse_bad_alert">Oops! Please enter verses to search.</div>')
              .appendTo($('#alerts'))
              .fadeIn('slow')
              .delay(3000)
              .fadeOut('slow');
            return
        }
        
        $('.small_spin').attr('class', 'small_spinner');
        //checks if verse grouping is parsable
        $.get('/worship/is-parsable/', {'query':$verse_query}, function(response){
            //yes it is parsable!!
            if (response.indexOf('True') >= 0 ){
                $('#verse_search_results').empty();

                $.get('/worship/search/by-verses/', {'query':$verse_query}, function(response){
                    $(response).appendTo('#verse_search_results');
                    $('.small_spinner').attr('class', 'small_spin');
                });
            }
            //no it's not!
            else{
                $('.small_spinner').attr('class', 'small_spin');
                $('#alerts').empty();
                $("<div class='search_verse_bad_alert'>Oops! We don't understand what you typed or the verses don't exist.</div>")
                  .appendTo($('#alerts'))
                  .fadeIn('slow')
                  .delay(3000)
                  .fadeOut('slow');
            }
        });
   });
   
   //this is for having the search behavior look up multiple verse groupings
   // $("input[name='search']").click(function(){
        
        // var $versestring ='';
        // $('.verse').each(function(){
            // $versestring = $versestring + ' | ' + $(this).text();
        // });
        
        // if($versestring== ''){
            // $('#alerts').empty();
            // $('<div class="search_bad_alert">Oops! Please enter verses to search.</div>')
              // .appendTo($('#alerts'))
              // .fadeIn('slow')
              // .delay(3000)
              // .fadeOut('slow');
        // }
        // else{
            // $('.small_spin').attr('class', 'small_spinner');
            // $('#verse_search_results').empty();
            // $.get('/worship/search/by-verses/results-handler', {verses: $versestring}, function(response){
                
                // $(response).appendTo('#verse_search_results');
                
            // });
        // }
   // });

    
    
});



