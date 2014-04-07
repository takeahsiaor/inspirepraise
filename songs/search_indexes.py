from haystack import indexes
from songs.models import Song

class SongIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    key_line = indexes.CharField(model_attr='key_line')
    authors = indexes.MultiValueField()
    content_auto = indexes.EdgeNgramField(model_attr='title')
    # will not do 'fuzzy search' for key line
    # content_auto = indexes.EdgeNgramField(model_attr='key_line')
    # content_auto = indexes.EdgeNgramField(model_attr='authors')
    
    def get_model(self):
        return Song
        
    def prepare_authors(self, object):
        return ['%s' % (author.full_name) for author in object.authors.all()]
        
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
        
# class BookIndex(indexes.SearchIndex, indexes.Indexable):
    # text = indexes.CharField(document=True, use_template=True)
    # content_auto = indexes.EdgeNgramField(model_attr='name')
    
    # def get_model(self):
        # return Book
    
    # def index_queryset(self, using=None):
        # return self.get_model().objects.all()
    