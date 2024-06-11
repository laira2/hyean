import haystack
from haystack import indexes
from .models import Product

class ProductIndex(Indexes.SearchIndex, indexes.indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Product

