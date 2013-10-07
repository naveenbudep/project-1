import copy
import pyhash
hasher = pyhash.fnv1_32()

from collections import defaultdict, Counter
from pandas import DataFrame

from cdf.streams.mapping import CONTENT_TYPE_INDEX, MANDATORY_CONTENT_TYPES
from cdf.streams.utils import group_left, idx_from_stream
from cdf.collections.tagging_stats.constants import COUNTERS_FIELDS, CROSS_PROPERTIES_COLUMNS
from cdf.utils.dict import deep_update, flatten_dict
from cdf.utils.hashing import string_to_int64


def delay_to_range(delay):
    if delay >= 2000:
        return "delay_gte_2s"
    elif delay >= 1000:
        return "delay_from_1s_to_2s"
    elif delay >= 500:
        return "delay_from_500ms_to_1s"
    return "delay_lt_500ms"


class MetricsAggregator(object):

    def __init__(self, stream_patterns, stream_infos, stream_properties, stream_outlinks, stream_inlinks):
        self.stream_patterns = stream_patterns
        self.stream_infos = stream_infos
        self.stream_properties = stream_properties
        self.stream_inlinks = stream_inlinks
        self.stream_outlinks = stream_outlinks

    def get(self):
        """
        Return a tuple of dictionaries
        Values are a sub-dictonnary with fields :
            * `cross_properties`, a tuple with following format :
            (host, resource_type, content_type, depth, http_code, index, follow)
            str,  str,           str,          int,   http_code, bool,  bool
            * `counters` : a dictionary of counters

        Ex :
        {
            "cross_properties": ["www.site.com", "/article", "text/html", 1, 200, True, True],
            "counters": {
                "pages_nb": 10,
                "redirections_nb": 0,
                "inlinks_internal_nb": {
                    "total": 10,
                    "follow": 8,
                    "follow_unique": 6,
                    "nofollow": 2,
                    "nofollow_combinations": {
                        "link_meta": 1,
                        "link": 1
                    }
                },
                "outlinks_internal_nb": {
                    "total": 10,
                    "follow": 8,
                    "follow_unique": 6,
                    "nofollow": 2,
                    "nofollow_combinations": {
                        "link_meta": 1,
                        "link": 1
                    }
                },
                "outlinks_external_nb": {
                    "total": 10,
                    "follow": 8,
                    "follow_unique": 6,
                    "nofollow": 2,
                    "nofollow_combinations": {
                        "link_meta": 1,
                        "link": 1
                    }
                },
                "total_delay_ms": 3400,
                "avg_delay": 800,
                "delay_gte_500ms": 3,
                "delay_gte_1s": 3,
                "delay_gte_2s": 1,
                "canonical_nb": {
                    "filled": 3,
                    "equal": 1,
                    "not_filled": 0
                }
            }
        }
        """

        left = (self.stream_patterns, 0)
        streams_ref = {'properties': (self.stream_properties, 0),
                       'infos': (self.stream_infos, 0),
                       'inlinks': (self.stream_inlinks, idx_from_stream('inlinks', 'id')),
                       'outlinks': (self.stream_outlinks, idx_from_stream('outlinks', 'id')),
                       }

        host_idx = idx_from_stream('patterns', 'host')
        depth_idx = idx_from_stream('infos', 'depth')
        content_type_idx = idx_from_stream('infos', 'content_type')
        infos_mask_idx = idx_from_stream('infos', 'infos_mask')
        resource_type_idx = idx_from_stream('properties', 'resource_type')

        http_code_idx = idx_from_stream('infos', 'http_code')
        delay2_idx = idx_from_stream('infos', 'delay2')

        inlinks_type_idx = idx_from_stream('inlinks', 'link_type')
        inlinks_src_idx = idx_from_stream('inlinks', 'src_url_id')

        outlinks_type_idx = idx_from_stream('outlinks', 'link_type')
        outlinks_src_idx = idx_from_stream('outlinks', 'id')
        outlinks_dst_idx = idx_from_stream('outlinks', 'dst_url_id')

        counter_dict = {}
        for field in COUNTERS_FIELDS:
            deep_update(counter_dict, reduce(lambda x, y: {y: x}, reversed(field.split('.') + [0])))

        results = dict()
        for k, result in enumerate(group_left(left, **streams_ref)):
            infos = result[2]['infos'][0]
            outlinks = result[2]['outlinks']
            inlinks = result[2]['inlinks']

            # Reminder : 1 gzipped, 2 notused, 4 meta_noindex 8 meta_nofollow 16 has_canonical 32 bad canonical
            index = not (4 & infos[infos_mask_idx] == 4)
            follow = not (8 & infos[infos_mask_idx] == 8)

            http_code = infos[http_code_idx]
            in_queue = http_code in (0, 1, 2)
            # If the page has not been crawled, we skip it
            if in_queue:
                continue

            # If not crawled, the file has not properties
            properties = result[2]['properties'][0]

            key = (result[1][host_idx],
                   properties[resource_type_idx],
                   infos[content_type_idx],
                   infos[depth_idx],
                   http_code,
                   index,
                   follow)

            if key not in results:
                results[key] = copy.deepcopy(counter_dict)

            results[key]['pages_nb'] += 1

            results[key][delay_to_range(infos[delay2_idx])] += 1
            results[key]['total_delay_ms'] += infos[delay2_idx]

            results[key]['redirections_nb'] += len(filter(lambda i: i[outlinks_type_idx].startswith("r"), outlinks))

            # Get the first canonical tag found (a page may be have 2 canonicals tags by mistake
            canonicals = filter(lambda i: i[outlinks_type_idx] == "canonical", outlinks)
            if canonicals:
                canonical = canonicals[0]
                results[key]['canonical_nb']['filled'] += 1
                if canonical[outlinks_src_idx] == canonical[outlinks_dst_idx]:
                    results[key]['canonical_nb']['equal'] += 1
                else:
                    results[key]['canonical_nb']['not_equal'] += 1

            results[key]['canonical_nb']['incoming'] += len(filter(lambda i: i[inlinks_type_idx] == "canonical", inlinks))

            # Store inlinks and outlinks counters
            """
            "outlinks_external_nb": {
                    "total": 10,
                    "follow": 8,
                    "follow_unique": 6,
                    "nofollow": 2,
                    "nofollow_combinations": {
                        "link_meta": 1,
                        "link": 1
                    }
                },
            """
            for link_direction in ('inlinks', 'outlinks'):
                follow_idx = idx_from_stream(link_direction, 'follow')
                type_idx = inlinks_type_idx if link_direction == "inlinks" else outlinks_type_idx
                if link_direction == "outlinks":
                    dst_idx = idx_from_stream(link_direction, 'dst_url_id')
                    external_idx = idx_from_stream(link_direction, 'external_url')

                # Count follow_unique links
                follow_urls = set()

                if link_direction == "outlinks":
                    unique_idx = outlinks_dst_idx
                    is_inlink = False
                else:
                    unique_idx = inlinks_src_idx
                    is_inlink = True

                for link in result[2][link_direction]:
                    if link[type_idx] == "a":
                        # If is_inlink, it's necessarily as we don't crawl the web :)
                        is_internal = is_inlink or link[dst_idx] > 0
                        url_id = link[unique_idx]

                        """
                        If the link is external and the follow_key is robots,
                        That means that the url is finally internal (not linked once in follow)
                        """
                        if not is_internal and link_direction == "outlinks" and "robots" in link[follow_idx]:
                            is_internal = True
                            url_id = string_to_int64(link[external_idx])

                        # Many statuses possible for an url, we concatenate them after a sort an split them with a double underscore
                        follow_key = '_'.join(sorted(link[follow_idx]))
                        counter_key = '{}_{}_nb'.format(link_direction, "internal" if is_internal else "external")
                        results[key][counter_key]['total'] += 1
                        results[key][counter_key]['follow' if follow_key == 'follow' else 'nofollow'] += 1

                        if is_internal and follow_key == "follow":
                            follow_urls.add(url_id)

                        if follow_key != 'follow':
                            if follow_key not in results[key][counter_key]['nofollow_combinations']:
                                results[key][counter_key]['nofollow_combinations'][follow_key] = 1
                            else:
                                results[key][counter_key]['nofollow_combinations'][follow_key] += 1

                if len(follow_urls) > 0:
                    results[key]['{}_internal_nb'.format(link_direction)]['follow_unique'] += len(follow_urls)

        # Transform defaultdict to dict
        final_results = []
        for key, counters in results.iteritems():
            final_results.append({"cross_properties": list(key), "counters": counters})
        return final_results


class MetricsConsolidator(object):

    def __init__(self, part_stats):
        """
        Consolidate all dictionnaries coming from all PropertiesStats parts and aggregate counters by cross-property into one.
        """
        self.part_stats = part_stats

    def consolidate(self, return_flatten=True):
        """
        Return a dictionnary of aggregated values by cross-property

        {
            ("www.site.com", "/article", "text/html", 1, 200, True, True): {
                "pages_nb": 6766,
                ...
            }
        }
        """
        results = defaultdict(Counter)
        for part_stat in self.part_stats:
            for s_ in part_stat:
                results[tuple(s_['cross_properties'])].update(Counter(flatten_dict(s_['counters'])))

        # Replace Counters objects by dicts
        if return_flatten:
            return {key: dict(values) for key, values in results.iteritems()}

        document = {}
        for cross_properties, counters in results.iteritems():
            document[cross_properties] = {}
            for k, v in counters.iteritems():
                deep_update(document[cross_properties], reduce(lambda x, y: {y: x}, reversed(k.split('.') + [v])))
        return document

    def get_dataframe(self):
        results = self.consolidate()

        def transform_dict(cross_property, d_):
            t_dict = dict(d_)
            t_dict.update({CROSS_PROPERTIES_COLUMNS[i]: value for i, value in enumerate(cross_property)})
            t_dict.update({k: t_dict.get(k, 0) for k in COUNTERS_FIELDS})
            return t_dict

        prepare_df_rows = []
        for key, counters in results.iteritems():
            prepare_df_rows.append(transform_dict(key, counters))

        df = DataFrame(prepare_df_rows)
        return df


class MetadataAggregator(object):

    """
    Streams injected in This class should be the entire dataset of a crawl to ensure that the unicity of metadatas are valid
    """
    def __init__(self, stream_patterns, stream_properties, stream_contents, stream_infos):
        self.stream_patterns = stream_patterns
        self.stream_properties = stream_properties
        self.stream_contents = stream_contents
        self.stream_infos = stream_infos

    def get(self):
        """
        Return a tuple of dictionnaries :

        For each dict, an index "keys" with the following tuple :
        (host, resource_type, content_type, depth, http_code, index, follow)
         str,  str,           str,          int,   http_code, bool,  bool

        Ex :
        [
            {
                "keys": ["www.site.com", "/article", "text/html", 1, 200, True, True],
                "counters": {
                   "title_global_unik_nb": 4,
                   "title_local_unik_nb": 5,
                   "desc_filled_nb": 6,
                   "desc_global_unik_nb": 4,
                   "desc_local_unik_nb": 5,
                   "h1_filled_nb": 6,
                   "h1_global_unik_nb": 4,
                   "h1_local_unik_nb": 5
                    "h1_filled_nb": 3,
                    "h1_unique_nb": 5,
                    ...
            },
            {
                ...
            }
        ]
        """
        left = (self.stream_patterns, 0)
        streams_ref = {'properties': (self.stream_properties, 0),
                       'contents': (self.stream_contents, idx_from_stream('contents', 'id')),
                       'infos': (self.stream_infos, idx_from_stream('infos', 'id')),
                       }

        hashes_global = {ct_id: defaultdict(set) for ct_id in CONTENT_TYPE_INDEX.iterkeys()}

        host_idx = idx_from_stream('patterns', 'host')
        resource_type_idx = idx_from_stream('properties', 'resource_type')
        content_meta_type_idx = idx_from_stream('contents', 'content_type')
        content_hash_idx = idx_from_stream('contents', 'hash')
        depth_idx = idx_from_stream('infos', 'depth')
        http_code_idx = idx_from_stream('infos', 'http_code')
        infos_mask_idx = idx_from_stream('infos', 'infos_mask')
        content_type_idx = idx_from_stream('infos', 'content_type')

        results = defaultdict(Counter)

        for result in group_left(left, **streams_ref):
            # Reminder : 1 gzipped, 2 notused, 4 meta_noindex 8 meta_nofollow 16 has_canonical 32 bad canonical
            infos = result[2]['infos'][0]
            index = not (4 & infos[infos_mask_idx] == 4)
            follow = not (8 & infos[infos_mask_idx] == 8)

            http_code = infos[http_code_idx]
            if http_code != 200:
                continue

            key = (result[1][host_idx],
                   result[2]['properties'][0][resource_type_idx],
                   infos[content_type_idx],
                   infos[depth_idx],
                   infos[http_code_idx],
                   index,
                   follow
                   )
            hash_key = hasher(','.join(str(k) for k in key))
            contents = result[2]['contents']

            # For each url, we check if it has correctly title, description and h1 filled
            # If not, we'll consider that the url has not enough metadata

            metadata_score = 0
            # Meta filled
            for ct_id, ct_txt in CONTENT_TYPE_INDEX.iteritems():
                if len(filter(lambda i: i[content_meta_type_idx] == ct_id, contents)):
                    results[key]['metadata_nb.%s.filled' % ct_txt] += 1
                    if ct_txt in MANDATORY_CONTENT_TYPES:
                        metadata_score += 1
                else:
                    results[key]['metadata_nb.%s.not_filled' % ct_txt] += 1

            if metadata_score < 3:
                results[key]['metadata_nb.not_enough'] += 1

            # Fetch --first-- hash from each content type and watch add it to hashes set
            ct_found = set()
            for content in contents:
                ct_id = content[content_meta_type_idx]
                # If ct_i is already in ct_found, so it's the not the first content
                if ct_id not in ct_found:
                    ct_found.add(ct_id)
                    hashes_global[ct_id][content[content_hash_idx]].add(hash_key)

        # Concatenate results
        results = dict(results)
        final_results = []
        for key in results.iterkeys():
            # Transform Counter to dict
            counters = copy.copy(dict(results[key]))
            hash_key = hasher(','.join(str(k) for k in key))
            for ct_id, ct_txt in CONTENT_TYPE_INDEX.iteritems():
                # If [ct_txt]_filled_nb not exists, we create the fields
                if not 'metadata_nb.%s.filled' % ct_txt in counters:
                    counters['metadata_nb.%s.filled' % ct_txt] = 0
                    counters['metadata_nb.%s.unique' % ct_txt] = 0
                else:
                    # We fetch all set where there is only the hash_key (that means uniq)
                    counters['metadata_nb.%s.unique' % ct_txt] = len(filter(lambda i: i == set((hash_key,)), hashes_global[ct_id].itervalues()))
                if not 'metadata_nb.%s.not_filled' % ct_txt in counters:
                    counters['metadata_nb.%s.not_filled' % ct_txt] = 0

            if not 'metadata_nb.not_enough' in counters:
                counters['metadata_nb.not_enough'] = 0
            final_results.append(
                {
                    "cross_properties": key,
                    "counters": counters
                }
            )
        return final_results