from cdf.core.metadata.dataformat import check_enabled
from cdf.metadata.url.url_metadata import (
    STRING_TYPE, ES_NOT_ANALYZED,
    ES_DOC_VALUE, AGG_CATEGORICAL,
    INT_TYPE, URL_ID, BOOLEAN_TYPE,
    AGG_NUMERICAL, ES_LIST, ES_NO_INDEX,
    STRUCT_TYPE, FAKE_FIELD,
    STRING_NB_MAP_MAPPING
)
from cdf.core.metadata.constants import RENDERING, FIELD_RIGHTS


DATA_FORMAT_FIXTURE = {
    # url property data
    "url": {
        "verbose_name": "Url",
        "type": STRING_TYPE,
        "settings": {
            ES_NOT_ANALYZED,
            RENDERING.URL
        }
    },
    "id": {
        "verbose_name": "Id",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            FIELD_RIGHTS.PRIVATE,
            FIELD_RIGHTS.SELECT,
            FIELD_RIGHTS.FILTERS,
            URL_ID
        }
    },
    "crawl_id": {
        "type": INT_TYPE,
        "settings": {
            FIELD_RIGHTS.PRIVATE,
            FIELD_RIGHTS.SELECT,
            FIELD_RIGHTS.FILTERS
        }
    },
    "path": {
        "verbose_name": "Path",
        "type": STRING_TYPE,
        "settings": {ES_NOT_ANALYZED}
    },
    "http_code": {
        "verbose_name": "Http Code",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            # `http_code` have 2 roles
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    "depth": {
        "verbose_name": "Depth",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            # assume possible depth is finite
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    # title tag
    "metadata.title.contents": {
        "verbose_name": "Title",
        "type": STRING_TYPE,
        "settings": {ES_NOT_ANALYZED, ES_LIST}
    },
    # h1 tag
    "metadata.h1.contents": {
        "verbose_name": "H1",
        "type": STRING_TYPE,
        "settings": {ES_NOT_ANALYZED, ES_LIST}
    },
    # description tag
    "metadata.description.contents": {
        "verbose_name": "Page description",
        "type": STRING_TYPE,
        "settings": {ES_NOT_ANALYZED, ES_LIST}
    },
    # h2 tag
    "metadata.h2.contents": {
        "verbose_name": "H2",
        "type": STRING_TYPE,
        "settings": {ES_NOT_ANALYZED, ES_LIST}
    },

    # h3 tag
    "metadata.h3.contents": {
        "verbose_name": "H3",
        "type": STRING_TYPE,
        "settings": {ES_NOT_ANALYZED, ES_LIST}
    },
    # title tag
    "metadata.title.nb": {
        "verbose_name": "Number of Page Titles",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL,
            AGG_CATEGORICAL
        }
    },
    # h1 tag
    "metadata.h1.nb": {
        "verbose_name": "Number of H1",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    # description tag
    "metadata.description.nb": {
        "verbose_name": "Number of Page Description",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    # h2 tag
    "metadata.h2.nb": {
        "verbose_name": "Number of H2",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    # h3 tag
    "metadata.h3.nb": {
        "verbose_name": "Number of H3",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    "metadata.title.duplicates.nb": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    "metadata.h1.duplicates.nb": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    "metadata.description.duplicates.nb": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    "metadata.title.duplicates.urls_exists": {
        "type": "boolean",
        "default_value": None
    },
    "metadata.h1.duplicates.urls_exists": {
        "type": "boolean",
        "default_value": None
    },
    "metadata.description.duplicates.urls_exists": {
        "type": "boolean",
        "default_value": None
    },
    "metadata.title.duplicates.urls": {
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_STATUS,
            URL_ID,
            FIELD_RIGHTS.SELECT
        }
    },
    "metadata.h1.duplicates.urls": {
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_STATUS,
            URL_ID,
            FIELD_RIGHTS.SELECT
        }
    },
    "metadata.description.duplicates.urls": {
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_STATUS,
            URL_ID,
            FIELD_RIGHTS.SELECT
        }
    },
    "metadata.title.duplicates.is_first": {
        "type": BOOLEAN_TYPE
    },
    "metadata.h1.duplicates.is_first": {
        "type": BOOLEAN_TYPE
    },
    "metadata.description.duplicates.is_first": {
        "type": BOOLEAN_TYPE
    },

    "canonical.to.url": {
        "verbose_name": "Canonical To",
        "type": STRUCT_TYPE,
        "values": {
            "url_str": {"type": "string"},
            "url_id": {"type": "integer"},
        },
        "settings": {
            ES_NO_INDEX,
            RENDERING.URL_STATUS,
            FIELD_RIGHTS.FILTERS_EXIST,
            FIELD_RIGHTS.SELECT,
            URL_ID
        }
    },
    "canonical.to.equal": {
        "verbose_name": "Canonical is the Same Url",
        "type": BOOLEAN_TYPE,
        "settings": {AGG_CATEGORICAL}
    },
    "canonical.to.url_exists": {
        "type": "boolean",
        "default_value": None
    },

    # incoming canonical link
    "canonical.from.nb": {
        "verbose_name": "Number of Incoming Canonical",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    "canonical.from.urls": {
        "verbose_name": "Canonical From",
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_STATUS,
            FIELD_RIGHTS.FILTERS_EXIST,
            FIELD_RIGHTS.SELECT,
            URL_ID
        }
    },
    "canonical.from.urls_exists": {
        "type": "boolean",
        "default_value": None
    },

    # outgoing redirection
    "redirect.to.url": {
        "verbose_name": "Redirects to",
        "type": STRUCT_TYPE,
        "values": {
            "url_str": {"type": "string"},
            "url_id": {"type": "integer"},
            "http_code": {"type": "integer"}
        },
        "settings": {
            ES_NO_INDEX,
            RENDERING.URL_STATUS,
            FIELD_RIGHTS.FILTERS_EXIST,
            FIELD_RIGHTS.SELECT,
            URL_ID
        }
    },
    "redirect.to.url_exists": {
        "type": BOOLEAN_TYPE,
        "default_value": None,
    },

    # incoming redirection
    "redirect.from.nb": {
        "verbose_name": "Number of Incoming Redirects",
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_CATEGORICAL,
            AGG_NUMERICAL
        }
    },
    "redirect.from.urls": {
        "verbose_name": "Redirected From",
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_HTTP_CODE,
            FIELD_RIGHTS.FILTERS_EXIST,
            FIELD_RIGHTS.SELECT,
            URL_ID
        }
    },
    "redirect.from.urls_exists": {
        "type": "boolean",
        "default_value": None
    },

    # erroneous outgoing internal links
    "outlinks_errors.3xx.nb": {
        "type": INT_TYPE,
        "verbose_name": "Number of error links in 3xx",
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_errors.3xx.urls": {
        "type": INT_TYPE,
        "verbose_name": "Sample of error links in 3xx",
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            FIELD_RIGHTS.SELECT,
            RENDERING.URL,
            URL_ID
        }
    },
    "outlinks_errors.3xx.urls_exists": {
        "type": "boolean",
        "default_value": None
    },

    "outlinks_errors.4xx.nb": {
        "type": INT_TYPE,
        "verbose_name": "Number of error links in 4xx",
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_errors.4xx.urls": {
        "type": INT_TYPE,
        "verbose_name": "Sample of error links in 4xx",
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            FIELD_RIGHTS.SELECT,
            RENDERING.URL,
            URL_ID
        }
    },
    "outlinks_errors.4xx.urls_exists": {
        "type": "boolean",
        "default_value": None
    },

    "outlinks_errors.5xx.nb": {
        "type": INT_TYPE,
        "verbose_name": "Number of error links in 5xx",
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_errors.5xx.urls": {
        "type": INT_TYPE,
        "verbose_name": "Sample of error links in 5xx",
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            FIELD_RIGHTS.SELECT,
            RENDERING.URL,
            URL_ID
        }
    },
    "outlinks_errors.5xx.urls_exists": {
        "type": "boolean",
        "default_value": None
    },
    # total error_links number
    "outlinks_errors.total": {
        "type": "integer",
        "verbose_name": "Number of error links in 3xx/4xx/5xx",
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },

    # incoming links, must be internal
    "inlinks_internal.nb.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.nb.unique": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.nb.follow.unique": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.nb.follow.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.nb.nofollow.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.nb.nofollow.combinations.link": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.nb.nofollow.combinations.meta": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.nb.nofollow.combinations.link_meta": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "inlinks_internal.urls": {
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_LINK_STATUS,
            FIELD_RIGHTS.SELECT,
            URL_ID
        }
    },
    "inlinks_internal.urls_exists": {
        "type": "boolean",
        "default_value": None
    },
    "inlinks_internal.anchors.nb": {
        "type": INT_TYPE,
        "verbose_name": "Number of incoming text anchors",
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        },
        "enabled": check_enabled("top_anchors")
    },
    "inlinks_internal.anchors.top": {
        "type": STRUCT_TYPE,
        "values": STRING_NB_MAP_MAPPING,
        "settings": {
            RENDERING.STRING_NB_MAP,
            FIELD_RIGHTS.SELECT
        },
        "enabled": check_enabled("top_anchors")
    },
    # The following field is already created with the above one (as a STRUCT_TYPE)
    # But we need to return it to request it
    "inlinks_internal.anchors.top.text": {
        "type": STRING_TYPE,
        "settings": {
            FAKE_FIELD,
            FIELD_RIGHTS.FILTERS
        },
        "enabled": check_enabled("top_anchors")
    },
    # internal outgoing links (destination is a internal url)
    "outlinks_internal.nb.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.unique": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.follow.unique": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.follow.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.combinations.link": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.combinations.meta": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.combinations.robots": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.combinations.link_meta": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.combinations.link_robots": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.combinations.meta_robots": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.nb.nofollow.combinations.link_meta_robots": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_internal.urls": {
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_LINK_STATUS,
            FIELD_RIGHTS.SELECT
        },
    },
    "outlinks_internal.urls_exists": {
        "type": BOOLEAN_TYPE,
        "default_value": None
    },

    # external outgoing links (destination is a external url)
    "outlinks_external.nb.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_external.nb.follow.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_external.nb.nofollow.total": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_external.nb.nofollow.combinations.link": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_external.nb.nofollow.combinations.meta": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },
    "outlinks_external.nb.nofollow.combinations.link_meta": {
        "type": INT_TYPE,
        "settings": {
            ES_DOC_VALUE,
            AGG_NUMERICAL
        }
    },

    # a `previous` field
    "previous.inlinks_internal.urls": {
        "type": INT_TYPE,
        "settings": {
            ES_NO_INDEX,
            ES_LIST,
            RENDERING.URL_LINK_STATUS,
            FIELD_RIGHTS.SELECT,
            URL_ID
        }
    }
}
