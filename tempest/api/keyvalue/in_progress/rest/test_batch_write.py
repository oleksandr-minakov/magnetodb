# Copyright 2014 Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64

from tempest.api.keyvalue.rest_base.base import MagnetoDBTestCase
from tempest.common.utils.data_utils import rand_name
from tempest import exceptions
from tempest.test import attr


class MagnetoDBBatchWriteTest(MagnetoDBTestCase):

    def setUp(self):
        super(MagnetoDBBatchWriteTest, self).setUp()
        self.tname = rand_name().replace('-', '')

    @attr(type=['BWI-12'])
    def test_batch_write_put_empty_attr_name(self):
        self.client.create_table(self.build_x_attrs('S'),
                                 self.tname,
                                 self.smoke_schema)
        self.addResourceCleanUp(self.client.delete_table, self.tname)
        self.wait_for_table_active(self.tname)
        item = self.build_x_item('S', 'forum1', 'subject2',
                                 ('', 'N', '1000'))
        request_body = {'request_items': {self.tname: [{'put_request':
                                                        {'item': item}}]}}
        with self.assertRaises(exceptions.BadRequest):
            self.client.batch_write_item(request_body)

    @attr(type=['BWI-14'])
    def test_batch_write_put_b(self):
        self.client.create_table(self.build_x_attrs('S'),
                                 self.tname,
                                 self.smoke_schema)
        self.addResourceCleanUp(self.client.delete_table, self.tname)
        self.wait_for_table_active(self.tname)
        value = base64.b64encode('\xFF')
        item = self.build_x_item('S', 'forum1', 'subject2',
                                 ('message', 'B', value))
        request_body = {'request_items': {self.tname: [{'put_request':
                                                        {'item': item}}]}}
        headers, body = self.client.batch_write_item(request_body)
        self.assertIn('unprocessed_items', body)
        self.assertEqual(body['unprocessed_items'], {})
        key_conditions = {
            self.hashkey: {
                'attribute_value_list': [{'S': 'forum1'}],
                'comparison_operator': 'EQ'
            }
        }
        headers, body = self.client.query(self.tname,
                                          key_conditions=key_conditions,
                                          consistent_read=True)
        self.assertEqual(item, body['items'][0])

    @attr(type=['BWI-15'])
    def test_batch_write_put_bs(self):
        self.client.create_table(self.build_x_attrs('S'),
                                 self.tname,
                                 self.smoke_schema)
        self.addResourceCleanUp(self.client.delete_table, self.tname)
        self.wait_for_table_active(self.tname)
        value = base64.b64encode('\xFF')
        item = self.build_x_item('S', 'forum1', 'subject2',
                                 ('message', 'BS', [value, value]))
        request_body = {'request_items': {self.tname: [{'put_request':
                                                        {'item': item}}]}}
        headers, body = self.client.batch_write_item(request_body)
        self.assertIn('unprocessed_items', body)
        self.assertEqual(body['unprocessed_items'], {})
        key_conditions = {
            self.hashkey: {
                'attribute_value_list': [{'S': 'forum1'}],
                'comparison_operator': 'EQ'
            }
        }
        headers, body = self.client.query(self.tname,
                                          key_conditions=key_conditions,
                                          consistent_read=True)
        self.assertEqual(item, body['items'][0])

    @attr(type=['BWI-17'])
    def test_batch_write_put_n_empty_value(self):
        self.client.create_table(self.build_x_attrs('S'), self.tname,
                                 self.smoke_schema)
        self.addResourceCleanUp(self.client.delete_table, self.tname)
        self.wait_for_table_active(self.tname)
        item = self.build_x_item('S', 'forum1', 'subject2',
                                 ('message', 'N', ''))
        request_body = {'request_items': {self.tname: [{'put_request':
                                                        {'item': item}}]}}
        with self.assertRaises(exceptions.BadRequest):
            self.client.batch_write_item(request_body)

    @attr(type=['BWI-42'])
    def test_batch_write_put_delete_same_item(self):
        self.client.create_table(self.smoke_attrs, self.tname,
                                 self.smoke_schema)
        self.addResourceCleanUp(self.client.delete_table, self.tname)
        self.wait_for_table_active(self.tname)
        item = self.build_smoke_item('forum1', 'subject2',
                                     'message text', 'John', '10')
        key = {self.hashkey: {'S': 'forum1'}, self.rangekey: {'S': 'subject2'}}
        request_body = {'request_items': {self.tname: [{'put_request':
                                                        {'item': item}},
                                                       {'delete_request':
                                                        {'key': key}}]}}
        with self.assertRaises(exceptions.BadRequest):
            self.client.batch_write_item(request_body)

    @attr(type=['BWI-54_1'])
    def test_batch_write_too_short_tname(self):
        tname = 'qq'
        item = self.build_x_item('S', 'forum1', 'subject2',
                                 ('message', 'S', 'message text'))
        request_body = {'request_items': {tname: [{'put_request':
                                                   {'item': item}}]}}

        with self.assertRaises(exceptions.BadRequest):
            self.client.batch_write_item(request_body)

    @attr(type=['BWI-54_2'])
    def test_batch_write_too_long_tname(self):
        tname = 'q' * 256
        item = self.build_x_item('S', 'forum1', 'subject2',
                                 ('message', 'S', 'message text'))
        request_body = {'request_items': {tname: [{'put_request':
                                                   {'item': item}}]}}

        with self.assertRaises(exceptions.BadRequest):
            self.client.batch_write_item(request_body)

    @attr(type=['BWI-54_3'])
    def test_batch_write_non_existent_table(self):
        tname = 'non_existent_table'
        item = self.build_x_item('S', 'forum1', 'subject2',
                                 ('message', 'S', 'message text'))
        request_body = {'request_items': {tname: [{'put_request':
                                                   {'item': item}}]}}

        with self.assertRaises(exceptions.NotFound):
            self.client.batch_write_item(request_body)
