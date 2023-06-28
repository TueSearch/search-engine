"""
This module contains the Document model. It represents a crawled document.
"""
import peewee

from crawler.models.base import BaseModel


class Server(BaseModel):
    """
    Represents a server.
    """
    id = peewee.BigAutoField(primary_key=True)
    name = peewee.TextField()
    is_black_list = peewee.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()
