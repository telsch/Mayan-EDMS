from __future__ import absolute_import, unicode_literals

from ..classes import NamespaceMigration


class TestNamespaceMigrationOne(NamespaceMigration):
    def smart_settings_test_setting_0001(self, value):
        return '{}_0001'.format(value)


class TestNamespaceMigrationTwo(NamespaceMigration):
    def smart_settings_test_setting_0001(self, value):
        return '{}_0001'.format(value)

    def smart_settings_test_setting_0002(self, value):
        return '{}_0002'.format(value)