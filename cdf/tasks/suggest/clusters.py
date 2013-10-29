import os
import re

from autotagging.association_rules.algorithm import discover_query_strings_patterns
from autotagging.association_rules.algorithm import discover_metadata_patterns
from autotagging.association_rules.algorithm import discover_path_patterns
from autotagging.association_rules.algorithm import discover_mixed_patterns
from autotagging.association_rules.algorithm import build_children_relationship
from autotagging.visualization.textual import save_apriori_algorithm_results
from autotagging.visualization.textual import save_child_relationship

from cdf.streams.mapping import CONTENT_TYPE_INDEX, CONTENT_TYPE_NAME_TO_ID
from cdf.collections.urls.constants import CLUSTER_TYPE_TO_ID
from cdf.log import logger
from cdf.utils.s3 import fetch_files, push_file

def compute_mixed_clusters(crawl_id,
                           s3_uri,
                           first_part_id_size,
                           part_id_size,
                           tmp_dir_prefix='/tmp',
                           force_fetch=False):

    minimal_frequency = 0.03
    nb_urls = 100000

    # Fetch locally the files from S3
    tmp_dir = os.path.join(tmp_dir_prefix, 'crawl_%d' % crawl_id)
    if not os.path.exists(tmp_dir):
        try:
            os.makedirs(tmp_dir)
        except:
            pass

    output_dir = tmp_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # For now, compute clusters only with first part (to be improved)
    fetch_files(s3_uri,
                tmp_dir,
                regexp=['url(ids|infos|xcontents).txt.0.gz'],
                force_fetch=force_fetch)

    logger.info("Compute patterns cluster")

    patterns = []

    #find patterns on pathes
    path_patterns = discover_path_patterns(tmp_dir,
                                           nb_urls,
                                           minimal_frequency)
    cluster_type = CLUSTER_TYPE_TO_ID["pattern"]["path"]
    patterns.append([(cluster_type, pattern, support) for pattern, support in path_patterns])

    query_string_patterns = discover_query_strings_patterns(tmp_dir,
                                                            nb_urls,
                                                            minimal_frequency)
    cluster_type = CLUSTER_TYPE_TO_ID["pattern"]["qskey"]
    patterns.append([(cluster_type, pattern, support) for pattern, support in query_string_patterns])

    for metadata_type in ["title", "h1", "h2"]:
        logger.info("Discovering patterns on %s.", metadata_type)
        metadata_patterns = discover_metadata_patterns(tmp_dir,
                                                       nb_urls,
                                                       minimal_frequency,
                                                       metadata_type)

        cluster_type = CLUSTER_TYPE_TO_ID["metadata"][CONTENT_TYPE_NAME_TO_ID[metadata_type]]
        patterns.append([(cluster_type, pattern, support) for pattern, support in metadata_patterns])

    mixed_patterns = discover_mixed_patterns(patterns, minimal_frequency)
    if output_dir:
        save_apriori_algorithm_results(mixed_patterns,
                                       output_dir,
                                       "mixed",
                                       first_part_id_size,
                                       part_id_size)
    push_file(
        os.path.join(s3_uri, 'clusters_mixed.tsv'),
        os.path.join(output_dir, 'clusters_mixed.tsv')
    )


    file_name_regex = re.compile('url_suggested_clusters.txt.\d+.gz')
    for file_name in os.listdir(tmp_dir):
        if not file_name_regex.match(file_name):
            continue
        push_file(
            os.path.join(s3_uri, file_name),
            os.path.join(tmp_dir, file_name),
            )

    children_dictionary = build_children_relationship(mixed_patterns)
    if output_dir:
        save_child_relationship(children_dictionary, output_dir)

    push_file(
        os.path.join(s3_uri, 'cluster_mixed_children.tsv'),
        os.path.join(output_dir, 'cluster_mixed_children.tsv')
    )
