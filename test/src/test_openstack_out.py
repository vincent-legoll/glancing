#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import uuid
import unittest

from tutils import get_local_path

# Setup PYTHONPATH for openstack_out
sys.path.append(get_local_path('..', '..', 'src'))

import utils
import openstack_out

glance_image_show = '''\
+------------------+--------------------------------------+
| Property         | Value                                |
+------------------+--------------------------------------+
| checksum         | ee1eca47dc88f4879d8a229cc70a07c6     |
| container_format | bare                                 |
| created_at       | 2015-05-12T08:14:10                  |
| deleted          | False                                |
| disk_format      | qcow2                                |
| id               | 185beafd-c5fc-4877-bbcc-e49a8d3f03ed |
| is_public        | True                                 |
| min_disk         | 0                                    |
| min_ram          | 0                                    |
| name             | cirros-0.3.4-x86_64                  |
| owner            | 0d932173c3504d0a93716329ceef753a     |
| protected        | False                                |
| size             | 13287936                             |
| status           | active                               |
| updated_at       | 2015-05-12T08:14:11                  |
+------------------+--------------------------------------+
'''

neutron_agent_list = '''\
+--------------------------------------+--------------------+---------+-------+----------------+
| id                                   | agent_type         | host    | alive | admin_state_up |
+--------------------------------------+--------------------+---------+-------+----------------+
| 0662cf3c-7926-4e7e-a385-4a2c7b520c1f | Metadata agent     | c7-netw | xxx   | True           |
| 19ba2d90-bbd8-44da-8116-b1155e91f1fb | Open vSwitch agent | c7-netw | xxx   | True           |
| 69fd6ef2-04ef-43e4-a3de-fcc997f35edb | DHCP agent         | c7-netw | xxx   | True           |
| 75b1db74-fea4-46ed-8133-2eefe1155074 | L3 agent           | c7-netw | xxx   | True           |
| 76efb32a-03d6-4974-810a-e76fc95e7d80 | Open vSwitch agent | c7-cpu  | xxx   | True           |
+--------------------------------------+--------------------+---------+-------+----------------+
'''

pb = '''\

# Comment
# Probleme |

+----+------+
| 1  | 2    |
+----+------+
|
||
| |
|||
||||
| | |
| | | |
| ZERO
| UN |
| UN | DEUX |
| UN | DEUX | TROIS |
+----+------+

# Comment
# Probleme |||

'''

class OpenstackOutGetFieldTest(unittest.TestCase):

    def test_openstack_out_get_field_ok(self):
        f = openstack_out.get_field(['false'])
        self.assertEqual('', f)

        f = openstack_out.get_field(['true'])
        self.assertEqual('', f)

        f = openstack_out.get_field(['-c', '666', '--', 'neutron', 'agent-list'])
        self.assertEqual('', f)

        f = openstack_out.get_field(['-c', '1', '--', 'neutron', 'agent-list'])
        self.assertEqual(['Metadata agent', 'Open vSwitch agent', 'DHCP agent', 'L3 agent', 'Open vSwitch agent'], f)

        f = openstack_out.get_field(['-c', '1', '-P', 'vSwitch', '--', 'neutron', 'agent-list'])
        self.assertEqual(['Metadata agent', 'DHCP agent', 'L3 agent'], f)

        f = openstack_out.get_field(['-t', '1', '-c', '1', '-P', 'vSwitch', '--', 'neutron', 'agent-list'])
        self.assertEqual(['Metadata agent'], f)

        f = openstack_out.get_field(['-p', 'Metadata', '-c', '1', '--', 'neutron', 'agent-list'])
        self.assertEqual(['Metadata agent'], f)

        f = openstack_out.get_field(['-p', 'default', '-c', '1', '--', 'nova', 'secgroup-list'])
        self.assertEqual(['default'], f)

        f = openstack_out.get_field(['-p', 'default', '-c', '2', '--', 'nova', 'secgroup-list'])
        self.assertEqual(['default'], f)

        f = openstack_out.get_field(['-p', 'default', '-c', '0', '--', 'nova', 'secgroup-list'])
        u = uuid.UUID(f[0])
        self.assertEqual(uuid.UUID, type(u))

        f = openstack_out.get_field(['-p', 'default', '--', 'nova', 'secgroup-list'])
        u = uuid.UUID(f[0])
        self.assertEqual(uuid.UUID, type(u))

        f = openstack_out.get_field(['--', 'nova secgroup-list'])
        u = uuid.UUID(f[0])
        self.assertEqual(uuid.UUID, type(u))

    def test_openstack_out_get_field(self):
        with utils.devnull('stderr'):
            with self.assertRaises(SystemExit):
                openstack_out.get_field()
            with self.assertRaises(SystemExit):
                openstack_out.get_field(None)
            with self.assertRaises(SystemExit):
                openstack_out.get_field([])
            with self.assertRaises(SystemExit):
                openstack_out.get_field('')

class OpenstackOutMBTest(unittest.TestCase):

    def test_openstack_out_map_block_pb(self):
        b = openstack_out.map_block(pb)
        self.assertEqual(b, {'': '', 'UN': 'DEUX'})
        # should be 3, but there are collisions in the map
        self.assertEqual(len(b), 2)

    def test_openstack_out_map_block_gl(self):
        b = openstack_out.map_block(glance_image_show)
        self.assertEqual(b['checksum'], 'ee1eca47dc88f4879d8a229cc70a07c6')
        self.assertEqual(b['id'], '185beafd-c5fc-4877-bbcc-e49a8d3f03ed')
        # should be 3, but there are collisions in the map
        self.assertEqual(len(b), 15)

    def test_openstack_out_map_block_ne(self):
        b = openstack_out.map_block(neutron_agent_list)
        self.assertEqual(b['75b1db74-fea4-46ed-8133-2eefe1155074'], ['L3 agent', 'c7-netw', 'xxx', 'True'])
        # 5 elems per line...
        self.assertEqual(len(b), 5)

class OpenstackOutMainTest(unittest.TestCase):

    def test_openstack_out_main(self):
        with utils.stringio() as output:
            with utils.redirect('stdout', output):
                openstack_out.main(['-p', 'L3', '-c', '1', '--', 'neutron', 'agent-list'])
                self.assertEqual(output.getvalue(), 'L3 agent\n')

class OpenstackOutPBTest(unittest.TestCase):

    def test_openstack_out_parse_block_header_pb(self):
        h, b = openstack_out.parse_block(pb)
        self.assertEqual(len(h), 2)
        self.assertEqual(h[0], '1')
        self.assertEqual(h[1], '2')

    def test_openstack_out_parse_block_header_gl(self):
        h, b = openstack_out.parse_block(glance_image_show)
        self.assertEqual(len(h), 2)
        self.assertEqual(h[0], 'Property')
        self.assertEqual(h[1], 'Value')

    def test_openstack_out_parse_block_header_ne(self):
        h, b = openstack_out.parse_block(neutron_agent_list)
        self.assertEqual(len(h), 5)
        self.assertEqual(h[0], 'id')
        self.assertEqual(h[1], 'agent_type')
        self.assertEqual(h[2], 'host')
        self.assertEqual(h[3], 'alive')
        self.assertEqual(h[4], 'admin_state_up')

    def test_openstack_out_parse_block_body_pb(self):
        h, b = openstack_out.parse_block(pb)
        self.assertEqual(len(b), 3)
        self.assertEqual(b[0], ['', ''])
        self.assertEqual(b[1], ['', ''])
        self.assertEqual(b[2], ['UN', 'DEUX'])

    def test_openstack_out_parse_block_body_gl(self):
        h, b = openstack_out.parse_block(glance_image_show)
        self.assertEqual(len(b), 15)
        self.assertEqual(b[0], ['checksum', 'ee1eca47dc88f4879d8a229cc70a07c6'])
        self.assertEqual(b[1], ['container_format', 'bare'])

    def test_openstack_out_parse_block_body_ne(self):
        h, b = openstack_out.parse_block(neutron_agent_list)
        self.assertEqual(len(b), 5)
        self.assertEqual(b[3], ['75b1db74-fea4-46ed-8133-2eefe1155074', 'L3 agent', 'c7-netw', 'xxx', 'True'])
