import os
import gzip

from cdf.log import logger
from cdf.utils.s3 import push_file
from cdf.features.links.links import OutlinksTransducer, InlinksTransducer
from cdf.features.links.bad_links import get_bad_links, get_bad_link_counters
from cdf.features.main.streams import InfosStreamDef
from cdf.features.links.streams import (
    OutlinksRawStreamDef, OutlinksStreamDef,
    InlinksRawStreamDef, BadLinksStreamDef,
    BadLinksCountersStreamDef)
from cdf.tasks.decorators import TemporaryDirTask as with_temporary_dir
from cdf.tasks.constants import DEFAULT_FORCE_FETCH


@with_temporary_dir
def make_links_counter_file(crawl_id, s3_uri,
                            part_id, link_direction,
                            tmp_dir=None, force_fetch=DEFAULT_FORCE_FETCH):
    if link_direction == "out":
        transducer = OutlinksTransducer
        stream_name = OutlinksRawStreamDef
    else:
        transducer = InlinksTransducer
        stream_name = InlinksRawStreamDef

    stream_links = stream_name().load(s3_uri, tmp_dir, part_id, force_fetch)
    generator = transducer(stream_links).get()

    filenames = {
        'links': 'url_{}_links_counters.txt.{}.gz'.format(link_direction, part_id),
        'canonical': 'url_{}_canonical_counters.txt.{}.gz'.format(link_direction, part_id),
        'redirect': 'url_{}_redirect_counters.txt.{}.gz'.format(link_direction, part_id),
    }

    # lazily open files
    file_created = {}
    for i, entry in enumerate(generator):
        # TODO remove hard coded index
        link_type = entry[1]
        if link_type not in file_created:
            file_created[link_type] = gzip.open(os.path.join(tmp_dir, filenames[link_type]), 'w')
        file_created[link_type].write(str(entry[0]) + '\t' + '\t'.join(str(k) for k in entry[2:]) + '\n')

    for _f in file_created.itervalues():
        _f.close()

    # push all created files to s3
    logger.info('Pushing links counter files to S3')
    for counter_file in file_created.values():
        counter_filename = os.path.basename(counter_file.name)
        logger.info('Pushing {}'.format(counter_filename))
        push_file(
            os.path.join(s3_uri, counter_filename),
            os.path.join(tmp_dir, counter_filename),
        )


@with_temporary_dir
def make_bad_link_file(crawl_id, s3_uri,
                       first_part_id_size=500000,
                       part_id_size=500000,
                       tmp_dir=None, force_fetch=DEFAULT_FORCE_FETCH):
    """
    Generate a tsv file that list all urls outlink to an error url:
      url_src_id  url_dest_id error_http_code

    Ordered on url_src_id
    """
    stream_kwargs = {
        'uri': s3_uri,
        'tmp_dir': tmp_dir,
        'force_fetch': force_fetch,
    }

    generator = get_bad_links(
        InfosStreamDef.load(**stream_kwargs),
        OutlinksStreamDef.load(**stream_kwargs)
    )

    BadLinksStreamDef.persist(
        generator, s3_uri,
        first_part_size=first_part_id_size,
        part_size=part_id_size
    )


@with_temporary_dir
def make_bad_link_counter_file(crawl_id, s3_uri,
                               part_id,
                               tmp_dir=None,
                               force_fetch=DEFAULT_FORCE_FETCH):
    """
    Generate a counter file that list bad link counts by source url and http code
      url_src_id  http_code  count

    This method depend on the file generated by `make_bad_link_file`
    Ordered on url_src_id and http_code
    """
    stream = BadLinksStreamDef.load(
        s3_uri,
        tmp_dir=tmp_dir,
        part_id=part_id,
        force_fetch=force_fetch
    )
    generator = get_bad_link_counters(stream)
    BadLinksCountersStreamDef.persist(
        generator,
        s3_uri,
        part_id=part_id
    )