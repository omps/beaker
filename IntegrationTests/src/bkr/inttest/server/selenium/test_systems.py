
# vim: set fileencoding=utf-8:

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import logging
import requests
from urlparse import urljoin
from urllib import urlencode, urlopen
import uuid
import lxml.etree
from turbogears.database import session
import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from bkr.inttest.server.selenium import WebDriverTestCase
from bkr.inttest import data_setup, get_server_base, with_transaction, \
        DummyVirtManager, DatabaseTestCase
from bkr.inttest.assertions import assert_sorted
from bkr.server import dynamic_virt
from bkr.server.model import Cpu, Key, Key_Value_String, System, SystemStatus, SystemPermission
from bkr.inttest.server.webdriver_utils import check_system_search_results, login
from bkr.inttest.server.requests_utils import patch_json

def atom_xpath(expr):
    return lxml.etree.XPath(expr, namespaces={'atom': 'http://www.w3.org/2005/Atom'})

class TestSystemsGrid(WebDriverTestCase):

    @with_transaction
    def setUp(self):
        data_setup.create_system()
        self.browser = self.get_browser()

    def test_atom_feed_link_is_present(self):
        b = self.browser
        b.get(get_server_base())
        b.find_element_by_xpath('/html/head/link[@rel="feed" '
                'and @title="Atom feed" and contains(@href, "tg_format=atom")]')

    # https://bugzilla.redhat.com/show_bug.cgi?id=704082
    def test_show_all_columns_works(self):
        b = self.browser
        b.get(get_server_base())
        b.find_element_by_link_text('Show Search Options').click()
        Select(b.find_element_by_name('systemsearch-0.table'))\
            .select_by_visible_text('System/Name')
        b.find_element_by_link_text('Toggle Result Columns').click()
        b.find_element_by_link_text('Select All').click()
        b.find_element_by_id('searchform').submit()
        b.find_element_by_xpath('//title[text()="Systems"]')
        # check number of columns in the table
        ths = b.find_elements_by_xpath('//table[@id="widget"]//th')
        self.assertEquals(len(ths), 30)

class TestSystemsGridSorting(WebDriverTestCase):

    @classmethod
    def setUpClass(cls):
        with session.begin():
            # ensure we have lots of systems
            for cores in [1, 2, 3]:
                for vendor, model, status, type, user in zip(
                        [u'Acer', u'Dell', u'HP'],
                        [u'slow model', u'fast model', u'big model'],
                        [u'Automated', u'Manual', u'Removed'],
                        [u'Machine', u'Prototype'],
                        [data_setup.create_user() for _ in range(3)]):
                    system = data_setup.create_system(vendor=vendor,
                            model=model, status=status, type=type)
                    system.user = data_setup.create_user()
                    system.cpu = Cpu(cores=cores)

    def setUp(self):
        self.browser = self.get_browser()

    # https://bugzilla.redhat.com/show_bug.cgi?id=651418

    def check_column_sort(self, column_heading):
        b = self.browser
        column_headings = [th.text for th in
                b.find_elements_by_xpath('//table[@id="widget"]/thead//th')]
        self.assertIn(column_heading, column_headings)
        column_index = column_headings.index(column_heading) + 1 # xpath indices are 1-based
        b.find_element_by_xpath('//table[@id="widget"]/thead//th[%d]//a' % column_index).click()

        cell_values = []
        # Next page number
        # Assume our current page is 1
        next_page = 2
        while True:
            cell_values.extend(cell.text for cell in
                    b.find_elements_by_xpath('//table[@id="widget"]/tbody/tr/td[%d]' % column_index))
            # Keeping scrolling through pages until we have seen at least two distinct cell values
            # (so that we can see that it is really sorted)
            if len(set(cell_values)) > 1:
                break
            try:
                b.find_element_by_xpath('//div[contains(@class, "pagination")]'
                        '//ul/li/a[normalize-space(string())="%s"]' % next_page).click()
            except NoSuchElementException:
                raise AssertionError('Tried all pages, but every cell had the same value!')
            next_page += 1
        assert_sorted(cell_values, key=lambda x: x.lower())

    # We test both ordinary listing (i.e. with no search query) as well as 
    # searching, because they go through substantially different code paths

    def go_to_listing(self):
        self.browser.get(get_server_base())

    def go_to_search_results(self):
        b = self.browser
        b.get(get_server_base())
        b.find_element_by_link_text('Show Search Options').click()
        Select(b.find_element_by_name('systemsearch-0.table'))\
            .select_by_visible_text('CPU/Cores')
        Select(b.find_element_by_name('systemsearch-0.operation'))\
            .select_by_visible_text('greater than')
        b.find_element_by_name('systemsearch-0.value').send_keys('1')
        b.find_element_by_link_text('Add').click()
        Select(b.find_element_by_name('systemsearch-1.table'))\
            .select_by_visible_text('System/Name')
        Select(b.find_element_by_name('systemsearch-1.operation'))\
            .select_by_visible_text('is not')
        b.find_element_by_name('systemsearch-1.value').send_keys('bob')
        b.find_element_by_id('searchform').submit()
        b.find_element_by_xpath('//title[text()="Systems"]')

    def test_can_sort_listing_by_status(self):
        self.go_to_listing()
        self.check_column_sort('Status')

    def test_can_sort_listing_by_vendor(self):
        self.go_to_listing()
        self.check_column_sort('Vendor')

    def test_can_sort_listing_by_model(self):
        self.go_to_listing()
        self.check_column_sort('Model')

    def test_can_sort_listing_by_user(self):
        self.go_to_listing()
        self.check_column_sort('User')

    def test_can_sort_listing_by_type(self):
        self.go_to_listing()
        self.check_column_sort('Type')

    def test_can_sort_search_results_by_vendor(self):
        self.go_to_search_results()
        self.check_column_sort('Vendor')

    def test_can_sort_search_results_by_user(self):
        self.go_to_search_results()
        self.check_column_sort('User')

    def test_can_sort_search_results_by_type(self):
        self.go_to_search_results()
        self.check_column_sort('Type')

    def test_can_sort_search_results_by_status(self):
        self.go_to_search_results()
        self.check_column_sort('Status')

    def test_can_sort_search_results_by_model(self):
        self.go_to_search_results()
        self.check_column_sort('Model')

    # XXX also test with custom column selections

class TestSystemsAtomFeed(DatabaseTestCase):

    def feed_contains_system(self, feed, fqdn):
        xpath = atom_xpath('/atom:feed/atom:entry/atom:title[text()="%s"]' % fqdn)
        return len(xpath(feed))

    def system_count(self, feed):
        xpath = atom_xpath('count(/atom:feed/atom:entry)')
        return int(xpath(feed))

    def test_all_systems(self):
        with session.begin():
            systems = [data_setup.create_system() for _ in range(25)]
            removed_system = data_setup.create_system(status=SystemStatus.removed)

        feed_url = urljoin(get_server_base(), '?' + urlencode({
                'tg_format': 'atom', 'list_tgp_order': '-date_modified',
                'list_tgp_limit': '0'}))
        feed = lxml.etree.parse(urlopen(feed_url)).getroot()
        self.assert_(self.system_count(feed) >= 25, self.system_count(feed))
        for system in systems:
            self.assertTrue(self.feed_contains_system(feed, system.fqdn))
        self.assertFalse(self.feed_contains_system(feed, removed_system.fqdn))

    def test_removed_systems(self):
        with session.begin():
            system1 = data_setup.create_system(status=SystemStatus.removed)
            system2 = data_setup.create_system()

        feed_url = urljoin(get_server_base(), 'removed?' + urlencode({
            'tg_format': 'atom', 'list_tgp_order': '-date_modified',
            'list_tgp_limit': '0'}))
        feed = lxml.etree.parse(urlopen(feed_url)).getroot()
        self.assertEquals(self.system_count(feed), 
                          System.query.filter(System.status==SystemStatus.removed).count())
        self.assertTrue(self.feed_contains_system(feed, system1.fqdn))
        self.assertFalse(self.feed_contains_system(feed, system2.fqdn))

    def test_link_to_rdfxml(self):
        with session.begin():
            system = data_setup.create_system()
        feed_url = urljoin(get_server_base(), '?' + urlencode({
                'tg_format': 'atom', 'list_tgp_order': '-date_modified',
                'list_tgp_limit': '0'}))
        feed = lxml.etree.parse(urlopen(feed_url)).getroot()
        href_xpath = atom_xpath(
                '/atom:feed/atom:entry[atom:title/text()="%s"]'
                '/atom:link[@rel="alternate" and @type="application/rdf+xml"]/@href'
                % system.fqdn)
        href, = href_xpath(feed)
        self.assertEqual(href,
                '%sview/%s?tg_format=rdfxml' % (get_server_base(), system.fqdn))

    def test_link_to_turtle(self):
        with session.begin():
            system = data_setup.create_system()
        feed_url = urljoin(get_server_base(), '?' + urlencode({
                'tg_format': 'atom', 'list_tgp_order': '-date_modified',
                'list_tgp_limit': '0'}))
        feed = lxml.etree.parse(urlopen(feed_url)).getroot()
        href_xpath = atom_xpath(
                '/atom:feed/atom:entry[atom:title/text()="%s"]'
                '/atom:link[@rel="alternate" and @type="application/x-turtle"]/@href'
                % system.fqdn)
        href, = href_xpath(feed)
        self.assertEqual(href,
                '%sview/%s?tg_format=turtle' % (get_server_base(), system.fqdn))

    def test_filter_by_pool(self):
        with session.begin():
            data_setup.create_system(fqdn=u'nopool.system')
            pool = data_setup.create_system_pool()
            data_setup.create_system(fqdn=u'inpool.system').pools.append(pool)
        feed_url = urljoin(get_server_base(), '?' + urlencode({
                'tg_format': 'atom', 'list_tgp_order': '-date_modified',
                'systemsearch-0.table': 'System/Pools',
                'systemsearch-0.operation': 'is',
                'systemsearch-0.value': pool.name}))
        feed = lxml.etree.parse(urlopen(feed_url)).getroot()
        self.assertFalse(self.feed_contains_system(feed, 'nopool.system'))
        self.assertTrue(self.feed_contains_system(feed, 'inpool.system'))

    # https://bugzilla.redhat.com/show_bug.cgi?id=1217158
    def test_filter_by_group(self):
        # System groups became pools in Beaker 20.0 but we need to continue 
        # supporting System/Group search (mapped to pools) for old clients.
        with session.begin():
            pool = data_setup.create_system_pool()
            nopool = data_setup.create_system()
            inpool = data_setup.create_system()
            inpool.pools.append(pool)
        feed_url = urljoin(get_server_base(), '?' + urlencode({
                'tg_format': 'atom',
                'systemsearch-0.table': 'System/Group',
                'systemsearch-0.operation': 'is',
                'systemsearch-0.value': pool.name}))
        feed = lxml.etree.parse(urlopen(feed_url)).getroot()
        self.assertFalse(self.feed_contains_system(feed, nopool.fqdn))
        self.assertTrue(self.feed_contains_system(feed, inpool.fqdn))

    # https://bugzilla.redhat.com/show_bug.cgi?id=690063
    def test_xml_filter(self):
        with session.begin():
            module_key = Key.by_name(u'MODULE')
            with_module = data_setup.create_system()
            with_module.key_values_string.extend([
                    Key_Value_String(module_key, u'cciss'),
                    Key_Value_String(module_key, u'kvm')])
            without_module = data_setup.create_system()
        feed_url = urljoin(get_server_base(), '?' + urlencode({
                'tg_format': 'atom', 'list_tgp_order': '-date_modified',
                'xmlsearch': '<key_value key="MODULE" />'}))
        feed = lxml.etree.parse(urlopen(feed_url)).getroot()
        self.assert_(self.feed_contains_system(feed, with_module.fqdn))
        self.assert_(not self.feed_contains_system(feed, without_module.fqdn))

class SystemsBrowseTest(WebDriverTestCase):

    def setUp(self):
        self.browser = self.get_browser()

    def test_mine_systems(self):

        b = self.browser
        with session.begin():
            user = data_setup.create_user(password='password')
            system1 = data_setup.create_system()
            system2 = data_setup.create_system(status=SystemStatus.removed)
            system1.loaned = user
            system2.loaned = user

        login(b, user=user.user_name, password='password')
        b.get(urljoin(get_server_base(),'mine'))
        check_system_search_results(b, present=[system1], absent=[system2])
        self.assertEqual(
            b.find_element_by_class_name('item-count').text, 'Items found: 1')

class IpxeScriptHTTPTest(DatabaseTestCase):

    def setUp(self):
        with session.begin():
            self.lc = data_setup.create_labcontroller()
        self.orig_VirtManager = dynamic_virt.VirtManager
        dynamic_virt.VirtManager = DummyVirtManager
        DummyVirtManager.lab_controller = self.lc

    def tearDown(self):
        DummyVirtManager.lab_controller = None
        dynamic_virt.VirtManager = self.orig_VirtManager

    def test_unknown_uuid(self):
        response = requests.get(get_server_base() +
                'systems/by-uuid/%s/ipxe-script' % uuid.uuid4())
        self.assertEquals(response.status_code, 404)

    def test_invalid_uuid(self):
        response = requests.get(get_server_base() +
                'systems/by-uuid/blerg/ipxe-script')
        self.assertEquals(response.status_code, 404)

    def test_recipe_not_provisioned_yet(self):
        with session.begin():
            recipe = data_setup.create_recipe()
            data_setup.create_job_for_recipes([recipe])
            data_setup.mark_recipe_running(recipe, virt=True)
            # VM is created but recipe.provision() hasn't been called yet
        response = requests.get(get_server_base() +
                'systems/by-uuid/%s/ipxe-script' % recipe.resource.instance_id)
        self.assertEquals(response.status_code, 503)

    def test_recipe_provisioned(self):
        with session.begin():
            distro_tree = data_setup.create_distro_tree(
                    arch=u'x86_64', osmajor=u'Fedora20',
                    lab_controllers=[self.lc],
                    urls=[u'http://example.com/ipxe-test/F20/x86_64/os/'])
            recipe = data_setup.create_recipe(distro_tree=distro_tree)
            data_setup.create_job_for_recipes([recipe])
            data_setup.mark_recipe_waiting(recipe, virt=True,
                    lab_controller=self.lc)
            recipe.provision()
        response = requests.get(get_server_base() +
                'systems/by-uuid/%s/ipxe-script' % recipe.resource.instance_id)
        response.raise_for_status()
        self.assertEquals(response.text, """#!ipxe
kernel http://example.com/ipxe-test/F20/x86_64/os/pxeboot/vmlinuz console=tty0 console=ttyS0,115200n8 ks=%s noverifyssl netboot_method=ipxe
initrd http://example.com/ipxe-test/F20/x86_64/os/pxeboot/initrd
boot
""" % recipe.rendered_kickstart.link)

class SystemDetailsUpdateHTTPTest(DatabaseTestCase):
    """
    Directly tests the HTTP interface for updating system details
    """
    def setUp(self):
        with session.begin():
            self.owner = data_setup.create_user(password='theowner')
            self.system = data_setup.create_system(owner=self.owner, shared=False)
            self.policy = self.system.custom_access_policy
            self.policy.add_rule(everybody=True, permission=SystemPermission.reserve)
            self.privileged_group = data_setup.create_group()
            self.policy.add_rule(group=self.privileged_group,
                                 permission=SystemPermission.edit_system)

    def test_set_active_policy_from_pool(self):
        with session.begin():
            user = data_setup.create_user()
            pool = data_setup.create_system_pool()
            pool.systems.append(self.system)
            pool.access_policy.add_rule(
                permission=SystemPermission.edit_system, user=user)

        with session.begin():
            self.assertFalse(self.system.active_access_policy.grants
                             (user, SystemPermission.edit_system))

        s = requests.Session()
        s.post(get_server_base() + 'login', data={'user_name': self.owner.user_name,
                'password': 'theowner'}).raise_for_status()
        response = patch_json(get_server_base() +
                              'systems/%s/' % self.system.fqdn, session=s,
                              data={'active_access_policy': {'pool_name': pool.name}},
                         )
        response.raise_for_status()
        with session.begin():
            session.expire_all()
            self.assertTrue(self.system.active_access_policy.grants
                            (user, SystemPermission.edit_system))

        # attempt to set active policy to a pool policy when the system
        # is not in the pool
        with session.begin():
            pool = data_setup.create_system_pool()
            session.expire_all()
        response = patch_json(get_server_base() +
                              'systems/%s/' % self.system.fqdn, session=s,
                              data={'active_access_policy': {'pool_name': pool.name}},
                        )
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.text,
                          'To use a pool policy, the system must be in the pool first')

    def test_set_active_policy_to_custom_policy(self):
        with session.begin():
            user1 = data_setup.create_user()
            user2 = data_setup.create_user()
            self.system.custom_access_policy.add_rule(
                permission=SystemPermission.edit_system, user=user1)
            pool = data_setup.create_system_pool()
            pool.access_policy.add_rule(
                permission=SystemPermission.edit_system, user=user2)
            self.system.active_access_policy = pool.access_policy

        self.assertFalse(self.system.active_access_policy.grants 
                        (user1, SystemPermission.edit_system))
        self.assertTrue(self.system.active_access_policy.grants
                         (user2, SystemPermission.edit_system))

        s = requests.Session()
        s.post(get_server_base() + 'login', data={'user_name': self.owner.user_name,
                'password': 'theowner'}).raise_for_status()
        response = patch_json(get_server_base() +
                              'systems/%s/' % self.system.fqdn, session=s,
                              data={'active_access_policy': {'custom': True}},
                         )
        response.raise_for_status()
        with session.begin():
            session.expire_all()
            self.assertTrue(self.system.active_access_policy.grants \
                            (user1, SystemPermission.edit_system))

