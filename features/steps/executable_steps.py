from behave import given, when, then, step
import shutil
import subprocess
import sys

@given(u'we have zonkylla installed')
def step_impl(context):
    assert shutil.which('zonkylla') is not None

@when(u'we run "{command}"')
def step_impl(context, command):
    if context.cli_options:
        command = command + ' ' + context.cli_options
    result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))
    print(result.stderr.decode('utf-8'), file=sys.stderr)

@then(u'we see "{text}" on stdout')
def step_impl(context, text):
    assert text in context.stdout_capture.getvalue()

@then(u'we see "{text}" on stderr')
def step_impl(context, text):
    assert text in context.stderr_capture.getvalue()
