
$(document).ready(function () {

   $("form").submit(function(e){
        e.preventDefault();
        $query = $("input[name='query']").val();
        if ($query == ''){
            $('#alerts').empty();
            $('<div class="alert alert-danger">Oops! Please enter terms to search.</div>')
              .appendTo($('#alerts'))
              .fadeIn('slow')
              .delay(3000)
              .fadeOut('slow');
            return
        }
        if ($query.length > 50){
            $('#alerts').empty();
            $('<div class="alert alert-danger">Oops! Keep your submission under 50 characters.</div>')
              .appendTo($('#alerts'))
              .fadeIn('slow')
              .delay(3000)
              .fadeOut('slow');
            e.preventDefault();
            return
        }
        $('.small_spin').attr('class', 'small_spinner');
        $.get('/worship/search/by-info/', {'query': $query}, function(response){
            $('#song_search_results').empty();
            $(response).appendTo('#song_search_results');
            $('.small_spinner').attr('class', 'small_spin');
        });


   });
    
   // $("input[name='search']").click(function(){
        // $query = $("input[name='query']").val();
        // if ($query == ''){
            // $('#alerts').empty();
            // $('<div class="search_song_bad_alert">Oops! Please enter terms to search.</div>')
              // .appendTo($('#alerts'))
              // .fadeIn('slow')
              // .delay(3000)
              // .fadeOut('slow');
            // return
        // }
        // if ($query.length > 50){
            // $('#alerts').empty();
            // $('<div class="search_song_bad_alert">Oops! Keep your submission under 50 characters.</div>')
              // .appendTo($('#alerts'))
              // .fadeIn('slow')
              // .delay(3000)
              // .fadeOut('slow');
            // return
        // }
        // $('.small_spin').attr('class', 'small_spinner');
        // $.get('/worship/search/by-info/results-handler/', {query:$query}, function(response){
            // $('#song_search_results').empty();
            // $(response).appendTo('#song_search_results');
            // $('.small_spinner').attr('class', 'small_spin');
        // });

   // });
   
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



