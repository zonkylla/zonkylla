def before_all(context):
    context.config_file = 'zonkylla-test.cfg'
    context.cli_options = '--config=' + context.config_file
