#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pychamp.settings")

    from django.conf import settings
    import Cookie
    import django.test
    import HTMLParser
    import django.contrib.sessions.serializers
    import django.contrib
    import django.core.mail.backends.smtp
    import django.core.management.commands.sql
    import django.core.management.commands.sqlall
    import django.core.management.commands.sqlclear
    import django.core.management.commands.sqlinitialdata
    import django.core.management.commands.sqlsequencereset
    import django.template.loader
    import django.views.defaults
    import django.templatetags
    import googlecharts
    from googlecharts import templatetags
    from googlecharts.templatetags import googlecharts
    import django.core.serializers
    from django.core.serializers import json
    from django.templatetags import future

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)