"""
This module contains the page rank algorithm.
"""
import os
import traceback

import networkx as nx
from dotenv import load_dotenv
from tqdm import tqdm

from backend.streamers import DocumentStreamer
from crawler import utils
from crawler.sql_models.job import Job
from crawler.sql_models.server import Server
from crawler.worker.url_relevance import URL

load_dotenv()

LOG = utils.get_logger(__file__)
DIRECTED_LINK_GRAPH_FILE = os.getenv("DIRECTED_LINK_GRAPH_FILE")
PAGERANK_FILE = os.getenv("PAGERANK_FILE")


def construct_directed_link_graph_from_crawled_documents():
    """
    Construct a directed link graph from the crawled documents.

    The constructed graph will be saved as a pickle file.
    """
    LOG.info("Start constructing directed link graph")
    graph = nx.DiGraph()
    for from_document in tqdm(DocumentStreamer()):
        from_server = Server.select().where(Server.id == from_document.job["server_id"]).get().name
        for to_job in Job.select().where((Job.parent_id == from_document.id)):
            to_server = URL(to_job.url).server_name
            if not graph.has_edge(from_server, to_server) and from_server != to_server:
                graph.add_edge(from_server, to_server, weight=1)
            elif from_server != to_server:
                graph[from_server][to_server]['weight'] += 1
    LOG.info("Finished constructing directed link graph")
    utils.io.write_pickle_file(graph, DIRECTED_LINK_GRAPH_FILE)
    LOG.info("Wrote directed link graph")


def read_directed_graph() -> nx.DiGraph:
    """
    Read the directed link graph from the pickle file.
    """
    return utils.io.read_pickle_file(DIRECTED_LINK_GRAPH_FILE)


def read_page_rank() -> dict:
    """
    Read the page rank from the json file.
    """
    return utils.io.read_json_file(PAGERANK_FILE)


def construct_page_rank_of_servers_from_directed_graph():
    """
    Construct the page rank of the servers.
    """
    try:
        LOG.info("Start constructing page rank")
        network_graph = read_directed_graph()

        # Find isolated nodes
        isolated_nodes = [node for node, degree in network_graph.degree() if degree == 0]

        ranking = nx.pagerank(network_graph,
                              max_iter=int(os.getenv("PAGERANK_MAX_ITER")),
                              personalization=utils.io.read_json_file("scripts/pagerank_personalization.json"))
        LOG.info("Finished constructing page rank")
        utils.io.write_json_file(ranking, PAGERANK_FILE)
        LOG.info("Wrote page rank")
    except Exception as error:
        LOG.error(f"Error while constructing page rank. Properly too little data. Try again, later: {error}")
        traceback.print_exc()


def update_page_rank_of_servers_in_database():
    """
    Update the page rank of the servers.
    """
    page_rank = read_page_rank()
    LOG.info("Updating page rank")
    for server in tqdm(Server.select().execute()):
        try:
            server.page_rank = page_rank.get(server.name, 0)
            server.save()
            LOG.info(f"Updated page rank of {server.name} to {server.page_rank}")
        except Exception as e:
            LOG.error(f"Error while updating page rank of {server.name}: {e}")
