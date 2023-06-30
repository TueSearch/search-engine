"""
This module contains the Document model. It represents a crawled document.
"""
import peewee

from crawler.sql_models.base import BaseModel


class Server(BaseModel):
    """
    Represents a server.
    """
    id = peewee.BigAutoField(primary_key=True)
    name = peewee.TextField()
    is_black_list = peewee.BooleanField(default=False)
    page_rank = peewee.FloatField(default=0.0)
    total_jobs = peewee.BigIntegerField(default=0)
    success_jobs = peewee.BigIntegerField(default=0)
    relevant_jobs = peewee.BigIntegerField(default=0)

    class Meta:
        """
        Meta class for the Server model.
        """
        table_name = 'servers'

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()
