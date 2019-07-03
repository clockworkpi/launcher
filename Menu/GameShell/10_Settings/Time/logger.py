import logzero

def get_logger():
    # Set a custom formatter
    log_format = '%(color)s[%(levelname)1.1s ' \
                    '%(asctime)s.%(msecs)03d %(module)s:%(lineno)d]' \
                    '%(end_color)s %(message)s'
    formatter = logzero.LogFormatter(fmt=log_format)
    logzero.setup_default_logger(formatter=formatter)

    logzero.logfile(
        'logzero.log',
        maxBytes=1e6,
        backupCount=3
    )
    return logzero.logger