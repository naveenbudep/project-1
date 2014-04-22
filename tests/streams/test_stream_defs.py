import os
import tempfile
import unittest
import StringIO
import shutil

from cdf.core.streams.base import StreamDefBase


class CustomStreamDef(StreamDefBase):
    FILE = 'test'
    HEADERS = (
        ('id', int),
        ('url', str)
    )


class TestStreamsDef(unittest.TestCase):
    def test_field_idx(self):
        self.assertEquals(CustomStreamDef.field_idx('id'), 0)
        self.assertEquals(CustomStreamDef.field_idx('url'), 1)

    def test_file(self):
        f = StringIO.StringIO()
        f.write('1\thttp://www.site.com/\n')
        f.write('2\thttp://www.site.com/2\n')
        f.seek(0)

        stream = CustomStreamDef.get_stream_from_file(f)
        self.assertTrue(isinstance(stream.stream_def, CustomStreamDef))
        self.assertEquals(stream.next(), [1, 'http://www.site.com/'])
        self.assertEquals(stream.next(), [2, 'http://www.site.com/2'])

    def test_iterator(self):
        iterator = iter([
            [1, 'http://www.site.com/'],
            [2, 'http://www.site.com/2']
        ])
        stream = CustomStreamDef.get_stream_from_iterator(iterator)
        self.assertTrue(isinstance(stream.stream_def, CustomStreamDef))
        self.assertEquals(stream.next(), [1, 'http://www.site.com/'])
        self.assertEquals(stream.next(), [2, 'http://www.site.com/2'])

    def test_to_dict(self):
        entry = [1, 'http://www.site.com/']
        self.assertEquals(
            CustomStreamDef().to_dict(entry),
            {'id': 1, 'url': 'http://www.site.com/'}
        )

    def test_persist(self):
        iterator = iter([
            [0, 'http://www.site.com/'],
            [1, 'http://www.site.com/1'],
            [2, 'http://www.site.com/2'],
            [3, 'http://www.site.com/3'],
            [4, 'http://www.site.com/4'],
            [5, 'http://www.site.com/5'],
            [6, 'http://www.site.com/6']
        ])
        tmp_dir = tempfile.mkdtemp()
        CustomStreamDef().persist(
            iterator,
            tmp_dir,
            first_part_id_size=2,
            part_id_size=3
        )
        self.assertEquals(
            os.listdir(tmp_dir),
            ['test.txt.0.gz', 'test.txt.1.gz', 'test.txt.2.gz']
        )
        self.assertEquals(
            list(CustomStreamDef.get_stream_from_directory(tmp_dir, part_id=0)),
            [
                [0, 'http://www.site.com/'],
                [1, 'http://www.site.com/1'],
            ]
        )
        self.assertEquals(
            list(CustomStreamDef.get_stream_from_directory(tmp_dir, part_id=1)),
            [
                [2, 'http://www.site.com/2'],
                [3, 'http://www.site.com/3'],
                [4, 'http://www.site.com/4'],
            ]
        )
        self.assertEquals(
            list(CustomStreamDef.get_stream_from_directory(tmp_dir, part_id=2)),
            [
                [5, 'http://www.site.com/5'],
                [6, 'http://www.site.com/6']
            ]
        )

        # Test without part_id
        self.assertEquals(
            list(CustomStreamDef.get_stream_from_directory(tmp_dir)),
            [
                [0, 'http://www.site.com/'],
                [1, 'http://www.site.com/1'],
                [2, 'http://www.site.com/2'],
                [3, 'http://www.site.com/3'],
                [4, 'http://www.site.com/4'],
                [5, 'http://www.site.com/5'],
                [6, 'http://www.site.com/6']
            ]
        )
        shutil.rmtree(tmp_dir)

    def test_persist_with_part_id(self):
        iterator = iter([
            [0, 'http://www.site.com/'],
            [1, 'http://www.site.com/1'],
            [2, 'http://www.site.com/2'],
            [3, 'http://www.site.com/3'],
            [4, 'http://www.site.com/4'],
            [5, 'http://www.site.com/5'],
            [6, 'http://www.site.com/6']
        ])
        tmp_dir = tempfile.mkdtemp()
        CustomStreamDef().persist(
            iterator,
            tmp_dir,
            part_id=1
        )
        self.assertEquals(
            list(CustomStreamDef.get_stream_from_directory(tmp_dir, part_id=1)),
            [
                [0, 'http://www.site.com/'],
                [1, 'http://www.site.com/1'],
                [2, 'http://www.site.com/2'],
                [3, 'http://www.site.com/3'],
                [4, 'http://www.site.com/4'],
                [5, 'http://www.site.com/5'],
                [6, 'http://www.site.com/6']
            ]
        )
        shutil.rmtree(tmp_dir)

    def test_temporary_dataset(self):
        dataset = CustomStreamDef.create_temporary_dataset()
        # Write in reversed to ensure that the dataset will be sorted
        for i in xrange(6, -1, -1):
            dataset.append(i, 'http://www.site.com/{}'.format(i))
        tmp_dir = tempfile.mkdtemp()
        dataset.persist(tmp_dir, first_part_id_size=2, part_id_size=3)

        self.assertEquals(
            list(CustomStreamDef.get_stream_from_directory(tmp_dir)),
            [
                [0, 'http://www.site.com/0'],
                [1, 'http://www.site.com/1'],
                [2, 'http://www.site.com/2'],
                [3, 'http://www.site.com/3'],
                [4, 'http://www.site.com/4'],
                [5, 'http://www.site.com/5'],
                [6, 'http://www.site.com/6']
            ]
        )
        shutil.rmtree(tmp_dir)
