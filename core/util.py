import logging
import logging.handlers
import os

def get_module_logger(modname, level=logging.DEBUG, store_file=False):
    global LOGGER
    LOGGER = logging.getLogger(modname)
    LOGGER.setLevel(level)

    # 共通フォーマット
    formatter = logging.Formatter(
        '%(asctime)s - %(module)s:%(lineno)d [%(levelname)s] %(message)s')
    formatter.default_msec_format = '%s.%03d'

    # 標準出力サポート
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    if store_file:
        # ディレクトリの確認
        log_dir = "log"
        if os.path.exists(log_dir) is False:
            os.mkdir(log_dir)

        # ファイル出力サポート
        fh = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, modname + ".log"),
            maxBytes=5000000,
            backupCount=5,
            encoding='utf8'
        )
        fh.setFormatter(formatter)
        LOGGER.addHandler(fh)

    return LOGGER

