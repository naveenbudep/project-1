import unittest
import mock
from cdf.core.features import Feature

from cdf.core.streams.base import StreamDefBase
from cdf.query.datamodel import (
    get_fields,
    get_groups,
    _get_field_rights,
    _data_model_sort_key,
    _get_group_sort_key
)
from cdf.core.metadata.constants import RENDERING, FIELD_RIGHTS
from cdf.metadata.url.url_metadata import ES_LIST, ES_NO_INDEX, LIST


class CustomStreamDef(StreamDefBase):
    FILE = 'test'
    HEADERS = (
        ('id', int),
        ('url', str)
    )
    URL_DOCUMENT_DEFAULT_GROUP = "main"
    URL_DOCUMENT_MAPPING = {
        "url": {
            "verbose_name": "Url",
            "type": "string",
            "settings": {
                RENDERING.URL
            }
        },
        "title": {
            "verbose_name": "Title",
            "type": "string",
            "group": "semantic_metadata",
            "settings": {
                FIELD_RIGHTS.SELECT
            }
        },
        "content": {
            "verbose_name": "Contents",
            "type": "string",
            "settings": {
                ES_LIST,
                FIELD_RIGHTS.FILTERS
            }
        },
        "content_same_urls": {
            "verbose_name": "Contents with the same url",
            "type": "string",
            "settings": {
                ES_LIST,
                ES_NO_INDEX,
                FIELD_RIGHTS.FILTERS_EXIST,
                FIELD_RIGHTS.SELECT
            }
        },
        "private": {
            "type": "string",
            "settings": {
                FIELD_RIGHTS.PRIVATE
            }
        },
        "admin": {
            "type": "string",
            "settings": {
                FIELD_RIGHTS.ADMIN
            }
        },
        "serialized_list": {
            "type": "string",  # Store a json encoded into an ES string (not a list of strings)
            "settings": {
                LIST   # .. but when unserialized, will return a list !
            }
        }
    }

class TestDataModelSortKey(unittest.TestCase):
    def setUp(self):
        self.groups = {
            "foo": "Foo",
            "bar": "Bar",
            "": ""
        }

    def test_nominal_case(self):
        self.assertLess(
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "bar"}), self.groups),
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "foo"}), self.groups),
        )

    def test_different_groups(self):
        #fields are sorted alphabetically
        self.assertLess(
            _data_model_sort_key((11, {"group": "bar", "verbose_name": "foo"}), self.groups),
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "bar"}), self.groups),
        )

    def test_missing_group(self):
        self.assertLess(
            _data_model_sort_key((11, {"verbose_name": "bar"}), self.groups),
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "foo"}), self.groups),
        )

    def test_missing_verbose_name(self):
        self.assertLess(
            _data_model_sort_key((11, {"group": "foo"}), self.groups),
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "foo"}), self.groups),
        )

    def test_missing_group_name(self):
        #when there is no group name, we set the group name to ""
        self.assertLess(
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "foo"}), {}),
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "foo"}), self.groups)
        )

    def test_group_name_ordering(self):
        groups = {"foo": "a", "bar": "z"}
        self.assertLess(
            #foo comes first because its group name is "a"
            _data_model_sort_key((11, {"group": "foo", "verbose_name": "foo"}), groups),
            _data_model_sort_key((11, {"group": "bar", "verbose_name": "bar"}), groups)
        )

class TestGetGroupSortKey(unittest.TestCase):
    def test_nominal_case(self):
        #standard fields should be ordered alphabetically
        self.assertLess(
            _get_group_sort_key("bar", "Bar"),
            _get_group_sort_key("foo", "Foo")
        )

    def test_scheme_case(self):
        #scheme should come before anything else
        self.assertLess(
            _get_group_sort_key("scheme", "Scheme"),
            _get_group_sort_key("foo", "Foo")
        )
        #even groups without name
        self.assertLess(
            _get_group_sort_key("scheme", "Scheme"),
            _get_group_sort_key("", "")
        )

    def test_main_case(self):
        #main should come before anything else (except scheme)
        self.assertLess(
            _get_group_sort_key("main", "Main"),
            _get_group_sort_key("foo", "Foo")
        )
        #even groups without name
        self.assertLess(
            _get_group_sort_key("main", "Main"),
            _get_group_sort_key("", "")
        )
        #but not before scheme
        self.assertLess(
            _get_group_sort_key("scheme", "Scheme"),
            _get_group_sort_key("main", "Main")
        )

    def test_previous_fields(self):
        #previous fields come after standard field
        self.assertLess(
            _get_group_sort_key("qux", "Qux"),
            _get_group_sort_key("previous.bar", "Previous Bar")
        )
        #standard previous fields are order alphabetically
        self.assertLess(
            _get_group_sort_key("previous.bar", "Previous Bar"),
            _get_group_sort_key("previous.foo", "Previous Foo")
        )
        #previous.schem comes before other previous fields
        self.assertLess(
            _get_group_sort_key("previous.scheme", "Previous Scheme"),
            _get_group_sort_key("previous.foo", "Previous Foo")
        )
        #previous.main comes before other previous fields
        self.assertLess(
            _get_group_sort_key("previous.main", "Previous Main"),
            _get_group_sort_key("previous.foo", "Previous Foo")
        )
        #previous fields come before diff fields
        self.assertLess(
            _get_group_sort_key("previous.foo", "Previous Foo"),
            _get_group_sort_key("diff.foo", "Diff Foo")
        )

    def test_diff_fields(self):
        #diff fields come after standard field
        self.assertLess(
            _get_group_sort_key("qux", "Qux"),
            _get_group_sort_key("diff.bar", "Diff Bar")
        )
        #diff fields come after previous field
        self.assertLess(
            _get_group_sort_key("previous.qux", "Previous Qux"),
            _get_group_sort_key("diff.bar", "Diff Bar")
        )
        #standard diff fields are order alphabetically
        self.assertLess(
            _get_group_sort_key("diff.bar", "Diff Bar"),
            _get_group_sort_key("diff.foo", "Diff Foo")
        )
        #diff.scheme comes before other diff fields
        self.assertLess(
            _get_group_sort_key("diff.scheme", "Diff Scheme"),
            _get_group_sort_key("diff.foo", "Diff Foo")
        )
        #diff.main comes before other diff fields
        self.assertLess(
            _get_group_sort_key("diff.main", "Diff Main"),
            _get_group_sort_key("diff.foo", "Diff Foo")
        )
        #diff.main comes after any main field
        self.assertLess(
            _get_group_sort_key("previous.qux", "Previous Qux"),
            _get_group_sort_key("diff.main", "Diff Main")
        )


class FieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.feature1 = Feature('feature1', 'feature1', None, None)
        # mock stream_def in feature
        self.feature1.get_streams_def = mock.Mock(return_value=[CustomStreamDef])
        self.features = [self.feature1]

    def test_harness(self):
        data_model = get_fields({'feature1': None},
                                available_features=self.features)
        data_model = {k['value']: k for k in data_model}
        self.assertEquals(
            data_model['url'],
            {
                "value": "url",
                "name": "Url",
                "data_type": "string",
                "field_type": "url",
                "is_sortable": True,
                "group": "main",
                "multiple": False,
                "rights": ["filters", "select"]
            }
        )

        self.assertEquals(
            data_model['title'],

            {
                "value": "title",
                "name": "Title",
                "data_type": "string",
                "field_type": "string",
                "is_sortable": True,
                "group": "semantic_metadata",
                "multiple": False,
                "rights": ["select"]
            }
        )

        # `content` field is `multiple`
        self.assertTrue(data_model['content']["multiple"])
        # `content` field can be filtered but no returned in the results
        self.assertEquals(data_model["content"]["rights"], ["filters"])
        # `serialized_list` is multiple (LIST flag checking)
        self.assertTrue(data_model['serialized_list']["multiple"])

        # `content_same_urls` field can be filtered
        # but only with `exists` check and  returned in the results
        self.assertEquals(
            data_model['content_same_urls']["rights"],
            ["filters_exist", "select"]
        )

    def test_enabled(self):
        fields = get_fields({"main": {"lang": True}})
        self.assertTrue('Lang' in [k["name"] for k in fields])

        fields = get_fields({"main": {"lang": False}})
        self.assertFalse('lang' in [k["name"] for k in fields])

        fields = get_fields({"main": None})
        self.assertFalse('lang' in [k["name"] for k in fields])

    def test_groups(self):
        groups = get_groups({"main": {"lang": True}})
        self.assertEquals(
            [g['id'] for g in groups],
            ['scheme', 'main']
        )

    def test_ordering(self):
        data_model = get_fields({'feature1': None},
                                available_features=self.features)
        data_model = [k['value'] for k in data_model]
        # datamodel should be sorted within each field
        expected = [
            'serialized_list',
            'content',
            'content_same_urls',
            'url',
            'title'  # title is in an other group
        ]
        self.assertEqual(expected, data_model)

    def test_private(self):
        data_model = get_fields(
            {'feature1': None},
            available_features=self.features
        )
        data_model = [k['value'] for k in data_model]
        # by default `private` is excluded
        self.assertFalse("private" in data_model)

        data_model = get_fields(
            {'feature1': None},
            remove_private=False,
            available_features=self.features
        )
        data_model = [k['value'] for k in data_model]
        self.assertTrue("private" in data_model)

    def test_admin(self):
        data_model = get_fields(
            {'feature1': None},
            available_features=self.features
        )
        data_model = [k['value'] for k in data_model]
        # by default `admin` is excluded
        self.assertFalse("admin" in data_model)

        data_model = get_fields(
            {'feature1': None},
            remove_admin=False,
            available_features=self.features
        )
        data_model = [k['value'] for k in data_model]
        self.assertTrue("admin" in data_model)


class TestGetFieldRights(unittest.TestCase):
    def test_nominal_case(self):
        settings = {ES_LIST, FIELD_RIGHTS.SELECT}
        actual_result = _get_field_rights(settings)
        expected_result = ["select"]
        self.assertItemsEqual(expected_result, actual_result)

    def test_default_value(self):
        settings = {ES_LIST}
        actual_result = _get_field_rights(settings)
        expected_result = ["select", "filters"]
        self.assertItemsEqual(expected_result, actual_result)

    def test_admin_field(self):
        settings = {ES_LIST, FIELD_RIGHTS.ADMIN, FIELD_RIGHTS.SELECT}
        actual_result = _get_field_rights(settings)
        expected_result = ["admin", "select"]
        self.assertItemsEqual(expected_result, actual_result)

    def test_default_value_admin_field(self):
        settings = {ES_LIST, FIELD_RIGHTS.ADMIN}
        actual_result = _get_field_rights(settings)
        expected_result = ["admin", "select", "filters"]
        self.assertItemsEqual(expected_result, actual_result)


class ComparisonTestCase(unittest.TestCase):
    def setUp(self):
        self.feature_options = {
            "main": None,
            "links": None,
            # TODO it's better to name it `feature_options` for consistency
            "comparison": {"options": {"main": None, "links": None}}
        }

    def test_fields(self):
        # current crawl : feature main, links and comparison are enabled
        # previous crawl : only main is enabled
        fields = get_fields(self.feature_options)
        fields_configs = [f['value'] for f in fields]
        self.assertIn('url', fields_configs)
        self.assertIn('previous.url', fields_configs)
        # `main_image` not enabled on the previous crawl
        self.assertNotIn('previous.main_image', fields_configs)

        fields_verbose = [f['name'] for f in fields]
        self.assertIn('Previous Http Code', fields_verbose)

    def test_groups(self):
        # current crawl : feature main, links and comparison are enabled
        # previous crawl : only main is enabled
        groups = get_groups(self.feature_options)
        names = [g['id'] for g in groups]

        self.assertIn('inlinks', names)
        self.assertIn('previous.inlinks', names)
        self.assertIn('diff.inlinks', names)

    def test_groups_non_comparison(self):
        # current crawl : feature main, links and comparison are enabled
        # previous crawl : only main is enabled
        groups = get_groups({'links': None})
        names = [g['id'] for g in groups]

        self.assertIn('inlinks', names)
        self.assertNotIn('previous.inlinks', names)
        self.assertNotIn('diff.inlinks', names)
