from backend.streamers import DocumentBodyTokensStringStreamer
from backend.vector_spaces.base_vector_space import BaseVectorSpaceModel


class BodyTfidf(BaseVectorSpaceModel):
    class Meta:
        table_name = 'body_tfidf'

    def generator(self):
        return DocumentBodyTokensStringStreamer()
